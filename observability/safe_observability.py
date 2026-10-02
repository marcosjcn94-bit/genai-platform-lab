"""LiteLLM callback: emit only enumerated fields; never serialize kwargs."""

import os

from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import SpanKind
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from prometheus_client import CollectorRegistry, Counter, Histogram, start_http_server

from litellm.integrations.custom_logger import CustomLogger

KNOWN = {
    "primary",
    "reserve",
    "fail",
    "fail-reserve",
    "slow",
    "fallback-reserve",
    "timeout-reserve",
    "failure-reserve",
    "qwen3:4b",
    "llama3.2:3b",
}


class SafeObserver(CustomLogger):
    def __init__(self):
        super().__init__()
        registry = CollectorRegistry()
        self.calls = Counter(
            "gateway_calls_total", "Observed provider calls", ["model", "status"], registry=registry
        )
        self.tokens = Counter(
            "gateway_tokens_total", "Known response tokens", ["model"], registry=registry
        )
        self.duration = Histogram(
            "gateway_call_seconds",
            "Provider duration",
            ["model", "status"],
            registry=registry,
            buckets=(0.01, 0.1, 1, 5, 10, 30, 60, 130),
        )
        start_http_server(9091, registry=registry)
        endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
        provider = TracerProvider(resource=Resource.create({"service.name": "platform-gateway"}))
        if endpoint:
            provider.add_span_processor(
                BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint.rstrip("/") + "/v1/traces"))
            )
        self.tracer = provider.get_tracer("safe-gateway")
        self.provider = provider

    def emit(self, kwargs, response, start, end, status):
        name = str(kwargs.get("model", "")).split("/", 1)[-1]
        model = name if name in KNOWN else "unknown"
        seconds = max(0, (end - start).total_seconds())
        self.calls.labels(model, status).inc()
        self.duration.labels(model, status).observe(seconds)
        params = kwargs.get("litellm_params") or {}
        request = params.get("proxy_server_request") or {}
        headers = request.get("headers") or {}
        context = TraceContextTextMapPropagator().extract(
            {"traceparent": headers.get("traceparent", "")}
        )
        span = self.tracer.start_span(
            "gateway.inference",
            context=context,
            kind=SpanKind.SERVER,
            start_time=int(start.timestamp() * 1e9),
            attributes={"model": model, "status": status},
        )
        usage = getattr(response, "usage", None)
        tokens = getattr(usage, "total_tokens", None)
        if isinstance(tokens, int) and tokens >= 0:
            self.tokens.labels(model).inc(tokens)
            span.set_attribute("tokens", tokens)
        span.end(end_time=int(end.timestamp() * 1e9))

    async def async_log_success_event(self, kwargs, response_obj, start_time, end_time):
        self.emit(kwargs, response_obj, start_time, end_time, "success")

    async def async_log_failure_event(self, kwargs, response_obj, start_time, end_time):
        self.emit(kwargs, response_obj, start_time, end_time, "failure")


observer = SafeObserver()
