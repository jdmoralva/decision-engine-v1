from backend.app.application.ai.client import BaseHTTPAIModelClient
from backend.app.application.ai.contracts import AIModelRequest, AIModelResponse
from backend.app.application.ai.exceptions import AIProviderError


class OpenAIModelClient(BaseHTTPAIModelClient):
    def __init__(
        self,
        *,
        api_key: str,
        model_name: str,
        timeout_seconds: float,
        max_retries: int,
        http_client=None,
    ) -> None:
        super().__init__(
            provider="openai",
            model_name=model_name,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            http_client=http_client,
        )
        self._api_key = api_key

    def _build_http_request(self, request: AIModelRequest) -> tuple[str, dict[str, str], dict]:
        messages: list[dict[str, str]] = []
        if request.system_instruction:
            messages.append({"role": "system", "content": request.system_instruction})
        messages.append({"role": "user", "content": request.prompt_text})

        payload: dict[str, object] = {
            "model": self.model_name,
            "messages": messages,
        }
        if request.temperature is not None:
            payload["temperature"] = request.temperature
        if request.max_output_tokens is not None:
            payload["max_tokens"] = request.max_output_tokens

        return (
            "https://api.openai.com/v1/chat/completions",
            {
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            payload,
        )

    def _parse_http_response(self, payload: dict) -> AIModelResponse:
        try:
            choice = payload["choices"][0]
            output_text = str(choice["message"]["content"])
        except (KeyError, IndexError, TypeError) as exc:
            raise AIProviderError("OpenAI response payload is invalid") from exc

        return AIModelResponse(
            provider=self.provider,
            model_name=self.model_name,
            output_text=output_text,
            finish_reason=choice.get("finish_reason"),
            raw_response=payload,
        )
