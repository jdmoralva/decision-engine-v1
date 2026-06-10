from abc import ABC, abstractmethod

import httpx

from backend.app.application.ai.contracts import AIModelRequest, AIModelResponse
from backend.app.application.ai.exceptions import AIProviderError, AITemporaryError, AITimeoutError


class AIModelClient(ABC):
    @abstractmethod
    async def generate(self, request: AIModelRequest) -> AIModelResponse:
        raise NotImplementedError


class BaseHTTPAIModelClient(AIModelClient):
    def __init__(
        self,
        *,
        provider: str,
        model_name: str,
        timeout_seconds: float,
        max_retries: int,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.provider = provider
        self.model_name = model_name
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self._http_client = http_client or httpx.AsyncClient()

    @abstractmethod
    def _build_http_request(self, request: AIModelRequest) -> tuple[str, dict[str, str], dict]:
        raise NotImplementedError

    @abstractmethod
    def _parse_http_response(self, payload: dict) -> AIModelResponse:
        raise NotImplementedError

    async def generate(self, request: AIModelRequest) -> AIModelResponse:
        url, headers, payload = self._build_http_request(request)
        last_status_code: int | None = None

        for attempt in range(self.max_retries + 1):
            try:
                response = await self._http_client.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout_seconds,
                )
            except httpx.TimeoutException as exc:
                if attempt >= self.max_retries:
                    raise AITimeoutError(
                        f"Timed out calling {self.provider} after retries"
                    ) from exc
                continue

            last_status_code = response.status_code
            if response.status_code in {429, 500, 502, 503, 504}:
                if attempt >= self.max_retries:
                    raise AITemporaryError(
                        f"Temporary {self.provider} error after retries"
                    )
                continue

            if response.status_code >= 400:
                raise AIProviderError(
                    f"{self.provider} returned non-success status {response.status_code}"
                )

            return self._parse_http_response(response.json())

        raise AITemporaryError(
            f"Temporary {self.provider} error after retries (status={last_status_code})"
        )
