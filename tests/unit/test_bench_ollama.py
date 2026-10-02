import json
from types import SimpleNamespace

import httpx
import pytest

from scripts import bench_ollama


@pytest.mark.parametrize("failed", [None, 0, 5, "all"])
def test_benchmark_percentiles_include_only_successful_primary_responses(
    monkeypatch, tmp_path, failed
):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("APP_A_TOKEN", "synthetic")
    monkeypatch.setattr(bench_ollama, "load_env", lambda: None)
    clock = iter(value for index in range(10) for value in (100 * index, 101 * index + 1))
    monkeypatch.setattr(bench_ollama, "time", SimpleNamespace(perf_counter=lambda: next(clock)))
    called = []

    def provider(request):
        index = len(called)
        called.append(request)
        model = "reserve" if failed == "all" or index == failed else "qwen3:4b"
        return httpx.Response(200, json={"model": model})

    client = httpx.Client
    monkeypatch.setattr(
        bench_ollama.httpx,
        "Client",
        lambda **kwargs: client(transport=httpx.MockTransport(provider), **kwargs),
    )
    bench_ollama.main()
    result = json.loads((tmp_path / "artifacts/ollama-benchmark.json").read_text())
    assert result["requests"] == len(called) == 10
    assert result["failures"] == (10 if failed == "all" else int(failed is not None))
    assert result["warm_requests"] == 9
    assert result["warm_successful_requests"] == (0 if failed == "all" else 8 if failed == 5 else 9)
    assert result["warm_p95_seconds"] == (None if failed == "all" else 10)
    assert result["cold_start_seconds"] == (None if failed in (0, "all") else 1)
