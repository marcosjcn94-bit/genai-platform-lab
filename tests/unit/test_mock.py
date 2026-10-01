from fastapi.testclient import TestClient


def test_mock_reports_usage_without_echoing_prompt():
    from mock_provider.main import app

    client = TestClient(app)
    result = client.post(
        "/v1/chat/completions",
        json={"model": "primary", "messages": [{"role": "user", "content": "PRIVATE_CANARY"}]},
    )
    assert result.status_code == 200
    assert result.json()["usage"]["total_tokens"] == 12
    assert "PRIVATE_CANARY" not in result.text


def test_mock_failure_and_attempt_counter():
    from mock_provider.main import app

    client = TestClient(app)
    before = client.get("/stats").json().get("fail", 0)
    assert client.post("/v1/chat/completions", json={"model": "fail"}).status_code == 500
    assert client.get("/stats").json()["fail"] == before + 1
