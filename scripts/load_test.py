"""Bounded async local mock load; records aggregate measurements only."""

import argparse
import asyncio
import json
import os
import platform
import time
from datetime import UTC, datetime
from pathlib import Path

import httpx

from scripts.env import load_env


def percentile(values, p):
    ordered = sorted(values)
    return (
        ordered[min(len(ordered) - 1, max(0, int(len(ordered) * p + 0.99) - 1))]
        if ordered
        else None
    )


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration", type=int, default=60)
    parser.add_argument("--concurrency", type=int, default=4)
    parser.add_argument("--output", type=Path, default=Path("artifacts/load"))
    args = parser.parse_args()
    if not 1 <= args.duration <= 60 or not 1 <= args.concurrency <= 4:
        parser.error("duration and concurrency exceed local limits")
    load_env()
    latencies, statuses = [], []
    deadline = time.monotonic() + args.duration
    async with httpx.AsyncClient(timeout=10, trust_env=False) as client:

        async def call():
            started = time.perf_counter()
            try:
                response = await client.post(
                    "http://localhost:8000/v1/chat/completions",
                    headers={"Authorization": "Bearer " + os.environ["APP_A_TOKEN"]},
                    json={
                        "model": "local",
                        "messages": [{"role": "user", "content": "Synthetic"}],
                        "max_tokens": 16,
                    },
                )
                statuses.append(response.status_code)
            except httpx.HTTPError:
                statuses.append(0)
            latencies.append(time.perf_counter() - started)

        async def worker():
            while time.monotonic() < deadline:
                await call()

        await asyncio.gather(*(worker() for _ in range(args.concurrency)))
    errors = sum(s < 200 or s >= 400 for s in statuses)
    result = {
        "scenario": "deterministic local mock",
        "started_at": datetime.now(UTC).isoformat(),
        "duration_target_seconds": args.duration,
        "concurrency": args.concurrency,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "cpu_count": os.cpu_count(),
        "requests": len(statuses),
        "errors": errors,
        "error_rate": errors / len(statuses) if statuses else None,
        "latency_seconds": {
            "p50": percentile(latencies, 0.50),
            "p95": percentile(latencies, 0.95),
            "max": max(latencies) if latencies else None,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.with_suffix(".json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result))


if __name__ == "__main__":
    asyncio.run(main())
