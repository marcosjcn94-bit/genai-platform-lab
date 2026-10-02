"""Generate the local Prometheus credential file without displaying it."""

import os
from pathlib import Path

from scripts.env import load_env


def main():
    load_env()
    Path("secrets").mkdir(exist_ok=True)
    Path("secrets/metrics_token").write_text(os.environ["METRICS_TOKEN"], encoding="utf-8")
    print("Arquivo de credencial interna preparado.")


if __name__ == "__main__":
    main()
