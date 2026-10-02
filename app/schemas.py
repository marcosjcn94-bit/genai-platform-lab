from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

MODELS = (
    "local",
    "reserve",
    "fallback-demo",
    "failure-demo",
    "timeout-demo",
    "ollama",
    "ollama-reserve",
)
Alias = Literal[
    "local", "reserve", "fallback-demo", "failure-demo", "timeout-demo", "ollama", "ollama-reserve"
]


class Message(BaseModel):
    model_config = ConfigDict(extra="forbid")
    role: Literal["system", "user", "assistant"]
    content: Annotated[str, Field(min_length=1, max_length=32768)]


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    model: Alias = "local"
    messages: Annotated[list[Message], Field(min_length=1, max_length=20)]
    max_tokens: Annotated[int, Field(strict=True, ge=1, le=256)] = 128


class Usage(BaseModel):
    prompt_tokens: int = Field(ge=0)
    completion_tokens: int = Field(ge=0)
    total_tokens: int = Field(ge=0)


class ResponseMessage(BaseModel):
    role: Literal["assistant"]
    content: str


class Choice(BaseModel):
    index: int
    message: ResponseMessage
    finish_reason: str | None


class ChatResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    choices: list[Choice]
    usage: Usage
