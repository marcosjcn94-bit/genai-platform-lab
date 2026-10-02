"""Ten sequential local Ollama requests; persist aggregate timing only."""

import json
import os
import statistics
import time
from datetime import UTC, datetime
from pathlib import Path

import httpx

from scripts.env import load_env
from scripts.load_test import percentile


def main():
    load_env()
    samples = []
    failures = 0
    cold_start_seconds = None
    started_at = datetime.now(UTC).isoformat()
    with httpx.Client(timeout=130, trust_env=False) as client:
        for index in range(10):
            started = time.perf_counter()
            success = False
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
                success = response.json().get("model") == "qwen3:4b"
            except (httpx.HTTPError, ValueError):
                pass
            failures += int(not success)
            elapsed = time.perf_counter() - started
            if index == 0 and success:
                cold_start_seconds = elapsed
            elif index > 0 and success:
                samples.append(elapsed)
    result = {
        "scenario": "Ollama qwen3:4b via local gateway",
        "started_at": started_at,
        "requests": 10,
        "failures": failures,
        "cold_start_seconds": cold_start_seconds,
        "warm_requests": 9,
        "warm_successful_requests": len(samples),
        "warm_p50_seconds": statistics.median(samples) if samples else None,
        "warm_p95_seconds": percentile(samples, 0.95),
    }
    output = Path("artifacts/ollama-benchmark.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
