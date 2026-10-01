import httpx
import pytest

from scripts.bootstrap import ensure_key


def test_bootstrap_does_not_duplicate_existing_identity():
    calls = []

    def server(req):
        calls.append(req.method)
        return httpx.Response(
            200,
            json={
                "info": {
                    "key_alias": "app-a",
                    "models": ["local"],
                    "allowed_routes": ["/chat/completions", "/v1/chat/completions"],
                }
            },
        )

    with httpx.Client(transport=httpx.MockTransport(server), base_url="http://gateway") as client:
        ensure_key(client, "app-a", "sk-synthetic", ["local"])
    assert calls == ["GET"]


def test_bootstrap_does_not_create_after_auth_failure():
    def server(req):
        return httpx.Response(401)

    with httpx.Client(transport=httpx.MockTransport(server), base_url="http://gateway") as client:
        with pytest.raises(httpx.HTTPStatusError):
            ensure_key(client, "app-a", "sk-synthetic", ["local"])
