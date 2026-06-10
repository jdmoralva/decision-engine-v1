from typing import Any

from pydantic import BaseModel, Field


class AIModelRequest(BaseModel):
    prompt_text: str = Field(min_length=1)
    system_instruction: str | None = None
    temperature: float | None = None
    max_output_tokens: int | None = None
    metadata: dict[str, object] = Field(default_factory=dict)


class AIModelResponse(BaseModel):
    provider: str
    model_name: str
    output_text: str
    finish_reason: str | None = None
    raw_response: dict[str, Any] | None = None
