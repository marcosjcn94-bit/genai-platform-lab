"""Idempotent key bootstrap; never print credentials or raw gateway errors."""

import os

import httpx

from scripts.env import load_env

MODELS = [
    "local",
    "reserve",
    "fallback-demo",
    "failure-demo",
    "timeout-demo",
    "ollama",
    "ollama-reserve",
]
ROUTES = ["/chat/completions", "/v1/chat/completions"]


def ensure_key(client, alias, key, models):
    response = client.get("/key/info", params={"key": key})
    if response.status_code == 404:
        result = client.post(
            "/key/generate",
            json={
                "key": key,
                "key_alias": alias,
                "models": models,
                "allowed_routes": ROUTES,
                "rpm_limit": 1200,
                "tpm_limit": 100000,
            },
        )
        result.raise_for_status()
        return
    response.raise_for_status()
    info = response.json()["info"]
    if info.get("key_alias") != alias:
        raise ValueError("Persisted identity mismatch")
    if set(info.get("models", [])) != set(models) or info.get("allowed_routes") != ROUTES:
        raise ValueError("Persisted key policy mismatch; administrative migration required")


def main():
    load_env()
    with httpx.Client(
        base_url=os.getenv("GATEWAY_URL", "http://localhost:4000"),
        timeout=30,
        headers={"Authorization": "Bearer " + os.environ["LITELLM_MASTER_KEY"]},
    ) as client:
        for name in ["A", "B"]:
            ensure_key(client, "app-" + name.lower(), os.environ[f"APP_{name}_GATEWAY_KEY"], MODELS)
    print("Identidades e políticas verificadas: app-a, app-b.")


if __name__ == "__main__":
    try:
        main()
    except (httpx.HTTPError, ValueError, KeyError):
        raise SystemExit(
            "Bootstrap indisponível: confira gateway, segredos e política persistida."
        ) from None
