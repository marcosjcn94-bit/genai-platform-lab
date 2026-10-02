"""Ten sequential local Ollama requests; persist aggregate timing only."""

import json
import os
import statistics
import time
from datetime import UTC, datetime
from pathlib import Path

import httpx

from scripts.env import load_env


def main():
    load_env()
    samples = []
    failures = 0
    cold_start_seconds = None
    with httpx.Client(timeout=130, trust_env=False) as client:
        for index in range(10):
            started = time.perf_counter()
            try:
                response = client.post(
                    "http://localhost:8000/v1/chat/completions",
                    headers={"Authorization": "Bearer " + os.environ["APP_A_TOKEN"]},
                    json={
                        "model": "ollama",
                        "messages": [{"role": "user", "content": "Responda apenas: OK"}],
                        "max_tokens": 16,
                    },
                )
                response.raise_for_status()
                if response.json().get("model") != "qwen3:4b":
                    failures += 1
            except (httpx.HTTPError, ValueError):
                failures += 1
            elapsed = time.perf_counter() - started
            if index == 0:
                cold_start_seconds = elapsed
            else:
                samples.append(elapsed)
    result = {
        "scenario": "Ollama qwen3:4b via local gateway",
        "started_at": datetime.now(UTC).isoformat(),
        "requests": 10,
        "failures": failures,
        "cold_start_seconds": cold_start_seconds,
        "warm_requests": len(samples),
        "warm_p50_seconds": statistics.median(samples) if samples else None,
        "warm_p95_seconds": sorted(samples)[min(len(samples) - 1, 7)] if samples else None,
    }
    output = Path("artifacts/ollama-benchmark.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
