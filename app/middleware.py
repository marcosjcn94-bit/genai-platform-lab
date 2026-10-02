import time
import uuid

from fastapi.responses import JSONResponse

ROUTES = {
    "/v1/chat/completions",
    "/health/live",
    "/health/ready",
    "/metrics",
    "/docs",
    "/openapi.json",
    "/docs/oauth2-redirect",
}


def error(status, code, request_id):
    return JSONResponse(
        {"error": {"code": code, "message": code.replace("_", " "), "request_id": request_id}},
        status_code=status,
    )


class BoundaryMiddleware:
    def __init__(self, app, metrics):
        self.app = app
        self.metrics = metrics

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        request_id = uuid.uuid4().hex
        scope.setdefault("state", {})["request_id"] = request_id
        route = scope["path"] if scope["path"] in ROUTES else "other"
        method = scope["method"] if scope["method"] in {"GET", "POST"} else "other"
        started = time.monotonic()
        status = 500

        async def measured_send(message):
            nonlocal status
            if message["type"] == "http.response.start":
                status = message["status"]
                message.setdefault("headers", []).append((b"x-request-id", request_id.encode()))
            await send(message)

        try:
            chunks = []
            size = 0
            while True:
                message = await receive()
                if message["type"] == "http.disconnect":
                    return
                size += len(message.get("body", b""))
                if size > 32768:
                    await error(413, "payload_too_large", request_id)(scope, receive, measured_send)
                    return
                chunks.append(message.get("body", b""))
                if not message.get("more_body", False):
                    break
            delivered = False

            async def replay():
                nonlocal delivered
                if not delivered:
                    delivered = True
                    return {"type": "http.request", "body": b"".join(chunks), "more_body": False}
                return await receive()

            await self.app(scope, replay, measured_send)
        finally:
            self.metrics.requests.labels(route, method, str(status)).inc()
            self.metrics.latency.labels(route, method, str(status)).observe(
                time.monotonic() - started
            )
