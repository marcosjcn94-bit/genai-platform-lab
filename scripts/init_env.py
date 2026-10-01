"""Cria segredos locais uma única vez, sem exibi-los."""

import secrets
from pathlib import Path


def main():
    target = Path(".env")
    if target.exists():
        print(".env já existe; preservado.")
        return
    names = [
        "POSTGRES_PASSWORD",
        "LITELLM_MASTER_KEY",
        "APP_A_TOKEN",
        "APP_B_TOKEN",
        "APP_A_GATEWAY_KEY",
        "APP_B_GATEWAY_KEY",
        "METRICS_TOKEN",
        "GRAFANA_PASSWORD",
    ]
    with target.open("x", encoding="utf-8") as stream:
        for name in names:
            prefix = "sk-" if "KEY" in name else ""
            stream.write(f"{name}={prefix}{secrets.token_hex(24)}\n")
    print(".env criado; valores não exibidos.")


if __name__ == "__main__":
    main()
