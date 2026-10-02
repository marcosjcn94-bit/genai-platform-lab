import json
import os
import subprocess
import time

import httpx
import pytest

from scripts.env import load_env

pytestmark = pytest.mark.integration


def counts():
    result = subprocess.run(
        [
            "docker",
            "compose",
            "exec",
            "-T",
            "mock",
            "python",
            "-c",
            "import urllib.request; print(urllib.request.urlopen('http://localhost:8001/stats').read().decode())",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


@pytest.mark.parametrize(
    "model,status,expected,deadline",
    [
        ("fallback-demo", 200, {"fail": 2, "fallback-reserve": 1}, 20),
        ("failure-demo", 502, {"fail": 2, "fail-reserve": 2}, 20),
        ("timeout-demo", 200, {"slow": 2, "timeout-reserve": 1}, 130),
    ],
)
def test_actual_attempt_ceiling_and_deadline(model, status, expected, deadline):
    load_env()
    before = counts()
    started = time.monotonic()
    response = httpx.post(
        "http://localhost:8000/v1/chat/completions",
        headers={
            "Authorization": "Bearer " + os.environ["APP_A_TOKEN"],
            "x-litellm-num-retries": "999",
        },
        json={"model": model, "messages": [{"role": "user", "content": "Synthetic"}]},
        timeout=135,
    )
    elapsed = time.monotonic() - started
    after = counts()
    assert response.status_code == status
    assert elapsed < deadline
    for destination, expected_count in expected.items():
        assert after.get(destination, 0) - before.get(destination, 0) == expected_count
    assert sum(after.values()) - sum(before.values()) <= 4
    if status == 200:
        assert response.json()["model"] == "reserve"
