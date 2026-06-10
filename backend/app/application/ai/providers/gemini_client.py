from backend.app.application.ai.client import BaseHTTPAIModelClient
from backend.app.application.ai.contracts import AIModelRequest, AIModelResponse
from backend.app.application.ai.exceptions import AIProviderError


class GeminiModelClient(BaseHTTPAIModelClient):
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
            provider="gemini",
            model_name=model_name,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            http_client=http_client,
        )
        self._api_key = api_key

    def _build_http_request(self, request: AIModelRequest) -> tuple[str, dict[str, str], dict]:
        payload: dict[str, object] = {
            "contents": [{"parts": [{"text": request.prompt_text}]}],
        }
        if request.system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": request.system_instruction}]
            }
        if request.temperature is not None or request.max_output_tokens is not None:
            payload["generationConfig"] = {}
            if request.temperature is not None:
                payload["generationConfig"]["temperature"] = request.temperature
            if request.max_output_tokens is not None:
                payload["generationConfig"]["maxOutputTokens"] = request.max_output_tokens

        return (
            f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self._api_key}",
            {"Content-Type": "application/json"},
            payload,
        )

    def _parse_http_response(self, payload: dict) -> AIModelResponse:
        try:
            candidate = payload["candidates"][0]
            output_text = str(candidate["content"]["parts"][0]["text"])
        except (KeyError, IndexError, TypeError) as exc:
            raise AIProviderError("Gemini response payload is invalid") from exc

        return AIModelResponse(
            provider=self.provider,
            model_name=self.model_name,
            output_text=output_text,
            finish_reason=candidate.get("finishReason"),
            raw_response=payload,
        )
