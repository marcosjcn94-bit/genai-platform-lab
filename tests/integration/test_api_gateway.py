import os
import time
from datetime import UTC, datetime, timedelta

import httpx
import pytest

from scripts.env import load_env
from scripts.report import export

pytestmark = pytest.mark.integration


def test_two_apps_and_fallback_reconcile():
    load_env()
    ids = {}
    start = datetime.now(UTC) - timedelta(seconds=1)
    with httpx.Client(base_url="http://localhost:8000", timeout=135) as api:
        assert api.get("/health/ready").status_code == 200
        for name in ("A", "B"):
            response = api.post(
                "/v1/chat/completions",
                headers={"Authorization": "Bearer " + os.environ[f"APP_{name}_TOKEN"]},
                json={"model": "local", "messages": [{"role": "user", "content": "Synthetic"}]},
            )
            assert response.status_code == 200, f"API status {response.status_code}"
            ids[response.json()["id"]] = "app-" + name.lower()
        fallback = api.post(
            "/v1/chat/completions",
            headers={"Authorization": "Bearer " + os.environ["APP_A_TOKEN"]},
            json={"model": "fallback-demo", "messages": [{"role": "user", "content": "Synthetic"}]},
        )
        assert fallback.status_code == 200
        assert fallback.json()["model"] == "reserve"
        ids[fallback.json()["id"]] = "app-a"
    with httpx.Client(
        base_url="http://localhost:4000",
        timeout=30,
        headers={"Authorization": "Bearer " + os.environ["LITELLM_MASTER_KEY"]},
    ) as admin:
        for _ in range(45):
            report = export(admin, start, datetime.now(UTC) + timedelta(seconds=1))
            matched = {e["record_id"]: e for e in report["events"] if e["record_id"] in ids}
            if len(matched) == 3:
                break
            time.sleep(2)
        assert len(matched) == 3
        for identifier, application in ids.items():
            assert matched[identifier]["application"] == application
            assert matched[identifier]["total_tokens"] == 12
