import asyncio
import hmac
import os
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from opentelemetry import trace
from opentelemetry.trace import SpanKind
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from pydantic import ValidationError
from starlette.exceptions import HTTPException
from starlette.responses import Response

from app.middleware import BoundaryMiddleware, error
from app.schemas import ChatRequest, ChatResponse
from app.telemetry import Metrics, safe_model, setup_tracing


def create_app(transport=None):
    metrics = Metrics()

    @asynccontextmanager
    async def lifespan(application):
        values = {
            k: os.environ[k]
            for k in (
                "APP_A_TOKEN",
                "APP_B_TOKEN",
                "APP_A_GATEWAY_KEY",
                "APP_B_GATEWAY_KEY",
                "METRICS_TOKEN",
            )
        }
        if any(not v for v in values.values()) or len(set(values.values())) != len(values):
            raise RuntimeError("Distinct nonempty credentials required")
        application.state.credentials = values
        setup_tracing()
        async with httpx.AsyncClient(
            base_url=os.getenv("GATEWAY_URL", "http://gateway:4000"),
            timeout=130,
            transport=transport,
            trust_env=False,
        ) as client:
            application.state.client = client
            yield

    application = FastAPI(title="GenAI Platform Lab", version="0.1.0", lifespan=lifespan)
    application.add_middleware(BoundaryMiddleware, metrics=metrics)

    @application.exception_handler(RequestValidationError)
    async def validation_error(request, exc):
        return error(422, "invalid_request", request.state.request_id)

    @application.exception_handler(HTTPException)
    async def http_error(request, exc):
        return error(exc.status_code, "request_rejected", request.state.request_id)

    @application.get("/health/live")
    async def live():
        return {"status": "ok"}

    @application.get("/health/ready")
    async def ready(request: Request):
        try:
            result = await application.state.client.get("/health/readiness", timeout=5)
            if result.status_code == 200 and result.json().get("db") == "connected":
                return {"status": "ready"}
        except (httpx.HTTPError, ValueError):
            pass
        return error(503, "dependencies_unavailable", request.state.request_id)

    @application.get("/metrics", include_in_schema=False)
    async def expose_metrics(request: Request):
        expected = "Bearer " + application.state.credentials["METRICS_TOKEN"]
        if not hmac.compare_digest(
            request.headers.get("authorization", "").encode(), expected.encode()
        ):
            return error(401, "unauthorized", request.state.request_id)
        return Response(generate_latest(metrics.registry), media_type=CONTENT_TYPE_LATEST)

    @application.post("/v1/chat/completions", response_model=ChatResponse)
    async def chat(body: ChatRequest, request: Request):
        key = None
        incoming = request.headers.get("authorization", "").encode()
        for name in ("A", "B"):
            expected = ("Bearer " + application.state.credentials[f"APP_{name}_TOKEN"]).encode()
            if hmac.compare_digest(incoming, expected):
                key = application.state.credentials[f"APP_{name}_GATEWAY_KEY"]
        if key is None:
            return error(401, "unauthorized", request.state.request_id)
        tracer = trace.get_tracer("platform-api")
        propagator = TraceContextTextMapPropagator()
        context = propagator.extract({"traceparent": request.headers.get("traceparent", "")})
        with tracer.start_as_current_span(
            "chat",
            context=context,
            kind=SpanKind.SERVER,
            record_exception=False,
            set_status_on_exception=False,
        ):
            headers = {"Authorization": "Bearer " + key}
            with tracer.start_as_current_span(
                "gateway.chat",
                kind=SpanKind.CLIENT,
                record_exception=False,
                set_status_on_exception=False,
            ):
                propagator.inject(headers)
                try:
                    async with asyncio.timeout(130):
                        result = await application.state.client.post(
                            "/v1/chat/completions", json=body.model_dump(), headers=headers
                        )
                    result.raise_for_status()
                    response = ChatResponse.model_validate(result.json())
                    served = result.headers.get("x-litellm-model-name", response.model)
                    raw_model = served.split("/", 1)[-1]
                    response.model = {
                        "fallback-reserve": "reserve",
                        "timeout-reserve": "reserve",
                        "ollama-reserve": "llama3.2:3b",
                    }.get(raw_model, safe_model(raw_model))
                except (TimeoutError, httpx.TimeoutException):
                    return error(504, "gateway_timeout", request.state.request_id)
                except (httpx.HTTPError, ValueError, ValidationError):
                    return error(502, "gateway_unavailable", request.state.request_id)
            model = safe_model(response.model)
            metrics.tokens.labels(model).inc(response.usage.total_tokens)
            if model in {"reserve", "llama3.2:3b"} and body.model not in {
                "reserve",
                "ollama-reserve",
            }:
                metrics.fallbacks.labels(model).inc()
            return response

    return application


app = create_app()
