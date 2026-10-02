"""Administrative export, always derived from LiteLLM spend logs."""

import argparse
import csv
import hashlib
import json
import os
from collections import defaultdict
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import httpx

from scripts.env import load_env

NUMERIC = ("prompt_tokens", "completion_tokens", "total_tokens", "duration_ms", "spend")


def utc(value):
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None or result.utcoffset().total_seconds() != 0:
        raise ValueError("Explicit UTC timestamp required")
    return result


def source_time(value):
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return result.replace(tzinfo=UTC) if result.tzinfo is None else result.astimezone(UTC)


def normalize(row, identities):
    start = source_time(row["startTime"])
    end = source_time(row["endTime"]) if row.get("endTime") else None
    status = row.get("status")
    if status not in {"success", "failure"}:
        status = None
    event = {
        "record_id": row["request_id"],
        "timestamp": start.isoformat(),
        "application": identities.get(row.get("api_key"), "unattributed"),
        "model": row.get("model") or "unknown",
        "status": status,
        "duration_ms": max(0, (end - start).total_seconds() * 1000) if end else None,
        "spend": str(Decimal(str(row["spend"]))) if row.get("spend") is not None else None,
    }
    for field in ("prompt_tokens", "completion_tokens", "total_tokens"):
        event[field] = row.get(field)
    return event


def collect(client, start, end, identities):
    if start.tzinfo is None or end.tzinfo is None or start >= end:
        raise ValueError("Invalid UTC interval")
    events, seen, fingerprints = [], {}, set()
    for page in range(1, 10001):
        response = client.get(
            "/spend/logs/v2",
            params={
                "start_date": start.astimezone(UTC).strftime("%Y-%m-%d %H:%M:%S"),
                "end_date": end.astimezone(UTC).strftime("%Y-%m-%d %H:%M:%S"),
                "page": page,
                "page_size": 1000,
            },
        )
        response.raise_for_status()
        rows = response.json()["data"]
        if not isinstance(rows, list):
            raise ValueError("Invalid source response")
        if not rows:
            return sorted(events, key=lambda item: (item["timestamp"], item["record_id"]))
        fingerprint = tuple(r["request_id"] for r in rows)
        if fingerprint in fingerprints:
            raise ValueError("Pagination did not advance")
        fingerprints.add(fingerprint)
        for row in rows:
            event = normalize(row, identities)
            if not start <= source_time(event["timestamp"]) < end:
                continue
            identifier = event["record_id"]
            if identifier in seen:
                if seen[identifier] != event:
                    raise ValueError("Conflicting duplicate; rerun a closed interval")
                continue
            seen[identifier] = event
            events.append(event)
    raise ValueError("Pagination safety limit reached; choose smaller UTC intervals")


def aggregate(events):
    groups = defaultdict(list)
    for event in events:
        groups[(event["application"], event["model"])].append(event)
    result = []
    for (application, model), rows in sorted(groups.items()):
        item = {"application": application, "model": model, "requests": len(rows)}
        known_status = [r["status"] for r in rows if r.get("status") is not None]
        item["status_known"] = len(known_status)
        item["errors"] = sum(s == "failure" for s in known_status) if known_status else None
        for field in NUMERIC:
            values = [Decimal(str(r[field])) for r in rows if r.get(field) is not None]
            item[field + "_known"] = len(values)
            total = sum(values, Decimal(0)) if values else None
            item[field] = (
                str(total)
                if field == "spend" and total is not None
                else (
                    float(total)
                    if field == "duration_ms" and total is not None
                    else (int(total) if total is not None else None)
                )
            )
        item["latency_mean_ms"] = (
            item["duration_ms"] / item["duration_ms_known"] if item["duration_ms_known"] else None
        )
        result.append(item)
    return result


def identities_from_gateway(client):
    result = {}
    for name in ("A", "B"):
        key = os.environ[f"APP_{name}_GATEWAY_KEY"]
        response = client.get("/key/info", params={"key": key})
        response.raise_for_status()
        alias = response.json()["info"]["key_alias"]
        if alias != "app-" + name.lower():
            raise ValueError("Persisted application identity mismatch")
        result[hashlib.sha256(key.encode()).hexdigest()] = alias
    return result


def export(client, start, end, application=None):
    events = collect(client, start, end, identities_from_gateway(client))
    if application:
        events = [r for r in events if r["application"] == application]
    return {
        "schema_version": 1,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "extracted_at": datetime.now(UTC).isoformat(),
        "coverage": {
            "state": "available",
            "source": "LiteLLM /spend/logs/v2",
            "records": len(events),
            "unattributed": sum(r["application"] == "unattributed" for r in events),
            "finality": "provisional: asynchronous persistence; rerun closed intervals",
            "failures": "only failures persisted by the gateway",
        },
        "events": events,
        "aggregates": aggregate(events),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", required=True, type=utc)
    parser.add_argument("--end", required=True, type=utc)
    parser.add_argument("--application", choices=["app-a", "app-b"])
    parser.add_argument("--output", type=Path, default=Path("artifacts/usage"))
    args = parser.parse_args()
    load_env()
    with httpx.Client(
        base_url=os.getenv("GATEWAY_URL", "http://localhost:4000"),
        timeout=30,
        headers={"Authorization": "Bearer " + os.environ["LITELLM_MASTER_KEY"]},
    ) as client:
        report = export(client, args.start, args.end, args.application)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(".tmp")
    temporary.write_text(json.dumps(report, indent=2), encoding="utf-8")
    temporary.replace(args.output.with_suffix(".json"))
    fields = ["application", "model", "requests", "status_known", "errors"]
    for field in NUMERIC:
        fields.extend([field + "_known", field])
    fields.append("latency_mean_ms")
    with args.output.with_suffix(".csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(report["aggregates"])
    print(json.dumps(report["coverage"]))


if __name__ == "__main__":
    try:
        main()
    except (httpx.HTTPError, ValueError, KeyError, TypeError):
        raise SystemExit(
            "Relatório indisponível; saída anterior não representa esta execução."
        ) from None
