import asyncio
import json
import sys
import unittest
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class OpenAIModelClientTests(unittest.TestCase):
    def test_openai_client_generates_text_from_chat_response(self):
        from backend.app.application.ai.contracts import AIModelRequest
        from backend.app.application.ai.providers.openai_client import OpenAIModelClient

        captured = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["url"] = str(request.url)
            captured["authorization"] = request.headers.get("Authorization")
            captured["body"] = json.loads(request.content.decode("utf-8"))
            return httpx.Response(
                status_code=200,
                json={
                    "id": "chatcmpl-1",
                    "choices": [
                        {
                            "finish_reason": "stop",
                            "message": {"content": "respuesta openai"},
                        }
                    ],
                },
            )

        transport = httpx.MockTransport(handler)
        client = OpenAIModelClient(
            api_key="test-openai-key",
            model_name="gpt-test",
            timeout_seconds=5.0,
            max_retries=2,
            http_client=httpx.AsyncClient(transport=transport),
        )

        response = asyncio.run(
            client.generate(
                AIModelRequest(
                    prompt_text="explica la evaluacion",
                    system_instruction="usa grounding estricto",
                )
            )
        )

        self.assertEqual(captured["authorization"], "Bearer test-openai-key")
        self.assertEqual(captured["body"]["model"], "gpt-test")
        self.assertEqual(captured["body"]["messages"][0]["role"], "system")
        self.assertEqual(captured["body"]["messages"][1]["content"], "explica la evaluacion")
        self.assertEqual(response.provider, "openai")
        self.assertEqual(response.model_name, "gpt-test")
        self.assertEqual(response.output_text, "respuesta openai")

    def test_openai_client_retries_on_temporary_failure(self):
        from backend.app.application.ai.contracts import AIModelRequest
        from backend.app.application.ai.providers.openai_client import OpenAIModelClient

        attempts = {"count": 0}

        def handler(request: httpx.Request) -> httpx.Response:
            attempts["count"] += 1
            if attempts["count"] == 1:
                return httpx.Response(status_code=429, json={"error": {"message": "rate limit"}})
            return httpx.Response(
                status_code=200,
                json={
                    "choices": [
                        {
                            "finish_reason": "stop",
                            "message": {"content": "ok after retry"},
                        }
                    ]
                },
            )

        client = OpenAIModelClient(
            api_key="test-openai-key",
            model_name="gpt-test",
            timeout_seconds=5.0,
            max_retries=2,
            http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
        )

        response = asyncio.run(client.generate(AIModelRequest(prompt_text="hola")))

        self.assertEqual(attempts["count"], 2)
        self.assertEqual(response.output_text, "ok after retry")
