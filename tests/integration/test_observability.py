import json
import os
import time

import httpx
import pytest

from scripts.env import load_env

pytestmark = pytest.mark.integration


def test_trace_correlation_metrics_and_sensitive_markers():
    load_env()
    trace_id = "abcdef0123456789abcdef0123456789"
    canary = "PRIVATE_OBSERVABILITY_CANARY"
    response = httpx.post(
        "http://localhost:8000/v1/chat/completions",
        headers={
            "Authorization": "Bearer " + os.environ["APP_A_TOKEN"],
            "traceparent": f"00-{trace_id}-1234567890abcdef-01",
            "x-private": canary,
        },
        json={"model": "local", "messages": [{"role": "user", "content": canary}]},
        timeout=135,
    )
    assert response.status_code == 200
    for _ in range(20):
        result = httpx.get(f"http://localhost:16686/api/traces/{trace_id}")
        if result.status_code == 200 and result.json().get("data"):
            data = result.json()["data"]
            services = {p["serviceName"] for t in data for p in t["processes"].values()}
            if {"platform-api", "platform-gateway"} <= services:
                break
        time.sleep(1)
    assert {"platform-api", "platform-gateway"} <= services
    serialized = json.dumps(data)
    assert canary not in serialized
    assert os.environ["APP_A_TOKEN"] not in serialized
    assert os.environ["APP_A_GATEWAY_KEY"] not in serialized
    assert "authorization" not in serialized.lower()
    for _ in range(15):
        metrics = httpx.get(
            "http://localhost:9090/api/v1/query", params={"query": "platform_tokens_total"}
        ).json()["data"]["result"]
        if metrics:
            break
        time.sleep(1)
    assert metrics
    for series in metrics:
        assert set(series["metric"]) <= {"__name__", "job", "instance", "model"}
    gateway = httpx.get(
        "http://localhost:9090/api/v1/query", params={"query": "gateway_calls_total"}
    ).json()["data"]["result"]
    assert gateway
    for series in gateway:
        assert set(series["metric"]) <= {"__name__", "job", "instance", "model", "status"}
