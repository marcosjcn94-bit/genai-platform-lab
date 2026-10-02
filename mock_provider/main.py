"""Provedor determinístico, acessível somente na rede do laboratório."""

import asyncio
import time
import uuid
from collections import Counter

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()
attempts = Counter()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/stats")
def stats():
    return dict(attempts)


@app.post("/v1/chat/completions")
async def completion(request: Request):
    body = await request.json()
    model = body.get("model", "primary")
    if model not in {
        "primary",
        "reserve",
        "fail",
        "slow",
        "fail-reserve",
        "fallback-reserve",
        "timeout-reserve",
        "failure-reserve",
    }:
        return JSONResponse({"error": {"message": "Unknown model"}}, status_code=400)
    attempts[model] += 1
    if model in {"fail", "fail-reserve"}:
        return JSONResponse({"error": {"message": "Synthetic failure"}}, status_code=500)
    if model == "slow":
        await asyncio.sleep(35)
    return {
        "id": "chatcmpl-" + uuid.uuid4().hex,
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": "Synthetic OK"},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 8, "completion_tokens": 4, "total_tokens": 12},
    }
