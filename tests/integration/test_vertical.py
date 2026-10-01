import hashlib
import os
import time
from datetime import UTC, datetime, timedelta

import httpx
import pytest

from scripts.bootstrap import MODELS, ensure_key
from scripts.env import load_env

pytestmark = pytest.mark.integration


def test_identity_usage_persistence_and_admin_isolation():
    load_env()
    base = os.getenv("GATEWAY_URL", "http://localhost:4000")
    with httpx.Client(
        base_url=base,
        timeout=135,
        headers={"Authorization": "Bearer " + os.environ["LITELLM_MASTER_KEY"]},
    ) as admin:
        key = os.environ["APP_A_GATEWAY_KEY"]
        ensure_key(admin, "app-a", key, MODELS)
        ensure_key(admin, "app-a", key, MODELS)
        with httpx.Client(
            base_url=base, timeout=135, headers={"Authorization": "Bearer " + key}
        ) as client:
            result = client.post(
                "/v1/chat/completions",
                json={
                    "model": "local",
                    "messages": [{"role": "user", "content": "PRIVATE_CANARY"}],
                    "max_tokens": 16,
                },
            )
            assert result.status_code == 200, f"Gateway status {result.status_code}"
            data = result.json()
            assert data["usage"]["total_tokens"] == 12
            assert client.post("/key/generate", json={}).status_code in (401, 403)
        request_id = data["id"]
        now = datetime.now(UTC)
        rows = []
        for _ in range(45):
            response = admin.get(
                "/spend/logs/v2",
                params={
                    "start_date": (now - timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S"),
                    "end_date": (now + timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M:%S"),
                    "page": 1,
                    "page_size": 100,
                },
            )
            assert response.status_code == 200
            rows = [r for r in response.json()["data"] if r["request_id"] == request_id]
            if rows:
                break
            time.sleep(2)
        assert len(rows) == 1, "Usage record did not persist within 90 seconds"
        row = rows[0]
        assert row["total_tokens"] == 12
        assert row["spend"] == 0
        assert "PRIVATE_CANARY" not in str(row)
        info = admin.get("/key/info", params={"key": key}).json()["info"]
        assert info["key_alias"] == "app-a"
        assert row["api_key"] == hashlib.sha256(key.encode()).hexdigest()
