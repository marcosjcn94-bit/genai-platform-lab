"""Only explicitly allowed attributes are emitted; no automatic HTTP capture."""

import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from prometheus_client import CollectorRegistry, Counter, Histogram

KNOWN_MODELS = {
    "primary",
    "reserve",
    "qwen3:4b",
    "llama3.2:3b",
    "fallback-reserve",
    "timeout-reserve",
    "failure-reserve",
}


def safe_model(model):
    return model if model in KNOWN_MODELS else "unknown"


def setup_tracing():
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if endpoint and not isinstance(trace.get_tracer_provider(), TracerProvider):
        provider = TracerProvider(resource=Resource.create({"service.name": "platform-api"}))
        provider.add_span_processor(
            BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint.rstrip("/") + "/v1/traces"))
        )
        trace.set_tracer_provider(provider)


class Metrics:
    def __init__(self):
        self.registry = CollectorRegistry()
        self.requests = Counter(
            "platform_requests_total",
            "HTTP requests",
            ["route", "method", "status"],
            registry=self.registry,
        )
        self.latency = Histogram(
            "platform_request_seconds",
            "HTTP latency",
            ["route", "method", "status"],
            registry=self.registry,
            buckets=(0.01, 0.05, 0.1, 0.5, 1, 5, 10, 30, 60, 130),
        )
        self.tokens = Counter(
            "platform_tokens_total", "Gateway reported tokens", ["model"], registry=self.registry
        )
        self.fallbacks = Counter(
            "platform_fallbacks_total",
            "Responses served by reserve",
            ["model"],
            registry=self.registry,
        )
