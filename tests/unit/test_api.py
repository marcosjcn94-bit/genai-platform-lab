import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import create_app

BODY = {"model": "local", "messages": [{"role": "user", "content": "PRIVATE_CANARY"}]}
RESPONSE = {
    "id": "chat-1",
    "object": "chat.completion",
    "created": 1,
    "model": "primary",
    "choices": [
        {"index": 0, "message": {"role": "assistant", "content": "OK"}, "finish_reason": "stop"}
    ],
    "usage": {"prompt_tokens": 8, "completion_tokens": 4, "total_tokens": 12},
}


@pytest.fixture
def setup(monkeypatch):
    for name, value in {
        "APP_A_TOKEN": "external-a",
        "APP_B_TOKEN": "external-b",
        "APP_A_GATEWAY_KEY": "internal-a",
        "APP_B_GATEWAY_KEY": "internal-b",
        "METRICS_TOKEN": "metrics-secret",
    }.items():
        monkeypatch.setenv(name, value)
    calls = []

    def upstream(req):
        calls.append(req)
        if req.url.path == "/health/readiness":
            return httpx.Response(200, json={"db": "connected"})
        return httpx.Response(
            200, json=RESPONSE, headers={"x-litellm-model-name": "openai/primary"}
        )

    return calls, httpx.MockTransport(upstream)


def test_auth_identity_and_header_allowlist(setup):
    calls, transport = setup
    with TestClient(create_app(transport=transport)) as client:
        assert client.post("/v1/chat/completions", json=BODY).status_code == 401
        assert (
            client.post(
                "/v1/chat/completions", json=BODY, headers={"Authorization": "Bearer wrong"}
            ).status_code
            == 401
        )
        for external, internal in [("external-a", "internal-a"), ("external-b", "internal-b")]:
            response = client.post(
                "/v1/chat/completions",
                json=BODY,
                headers={
                    "Authorization": "Bearer " + external,
                    "x-litellm-num-retries": "999",
                    "x-private": "PRIVATE_CANARY",
                },
            )
            assert response.status_code == 200
            assert response.json()["usage"]["total_tokens"] == 12
            assert calls[-1].headers["authorization"] == "Bearer " + internal
            assert "x-litellm-num-retries" not in calls[-1].headers
            assert "x-private" not in calls[-1].headers


@pytest.mark.parametrize(
    "change",
    [
        {"app_id": "app-b"},
        {"stream": True},
        {"max_tokens": 257},
        {"max_tokens": True},
        {"model": "paid-provider"},
        {"messages": []},
        {"messages": [{"role": "user", "content": {"secret": "PRIVATE_CANARY"}}]},
        {"messages": [{"role": "tool", "content": "PRIVATE_CANARY"}]},
    ],
)
def test_rejects_unsafe_payload_without_echo(setup, change):
    calls, transport = setup
    with TestClient(create_app(transport=transport)) as client:
        response = client.post(
            "/v1/chat/completions",
            json=BODY | change,
            headers={"Authorization": "Bearer external-a"},
        )
        assert response.status_code == 422
        assert "PRIVATE_CANARY" not in response.text
        assert calls == []


def test_limits_streamed_body_and_private_metrics(setup):
    _, transport = setup
    with TestClient(create_app(transport=transport)) as client:
        response = client.post(
            "/v1/chat/completions",
            content=iter([b"x" * 17000] * 2),
            headers={"Authorization": "Bearer external-a"},
        )
        assert response.status_code == 413
        assert client.get("/metrics").status_code == 401
        assert (
            client.get("/metrics", headers={"Authorization": "Bearer metrics-secret"}).status_code
            == 200
        )


def test_health_without_inference(setup):
    calls, transport = setup
    with TestClient(create_app(transport=transport)) as client:
        assert client.get("/health/live").status_code == 200
        assert calls == []
        assert client.get("/health/ready").status_code == 200
        assert [c.url.path for c in calls] == ["/health/readiness"]


@pytest.mark.parametrize("failure,expected", [("http", 502), ("timeout", 504), ("bad_json", 502)])
def test_gateway_errors_are_safe_and_never_retried(setup, failure, expected):
    calls = []

    def upstream(req):
        calls.append(req)
        if failure == "timeout":
            raise httpx.ReadTimeout("PRIVATE_CANARY", request=req)
        if failure == "bad_json":
            return httpx.Response(200, text="PRIVATE_CANARY")
        return httpx.Response(500, text="PRIVATE_CANARY")

    with TestClient(create_app(transport=httpx.MockTransport(upstream))) as client:
        response = client.post(
            "/v1/chat/completions", json=BODY, headers={"Authorization": "Bearer external-a"}
        )
        assert response.status_code == expected
        assert "PRIVATE_CANARY" not in response.text
        assert len(calls) == 1
        assert response.json()["error"]["request_id"]


def test_provider_metadata_is_removed_and_serving_model_exposed(setup):
    body = dict(RESPONSE)
    body["model"] = "local"
    body["choices"] = [
        {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "OK",
                "provider_specific_fields": {"private": "PRIVATE_CANARY"},
            },
            "finish_reason": "stop",
        }
    ]
    transport = httpx.MockTransport(
        lambda req: httpx.Response(
            200, json=body, headers={"x-litellm-model-name": "openai/reserve"}
        )
    )
    with TestClient(create_app(transport=transport)) as client:
        response = client.post(
            "/v1/chat/completions", json=BODY, headers={"Authorization": "Bearer external-a"}
        )
        assert response.status_code == 200
        assert response.json()["model"] == "reserve"
        assert "PRIVATE_CANARY" not in response.text
