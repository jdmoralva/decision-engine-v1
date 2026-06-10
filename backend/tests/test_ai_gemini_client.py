import asyncio
import json
import sys
import unittest
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class GeminiModelClientTests(unittest.TestCase):
    def test_gemini_client_generates_text_from_response(self):
        from backend.app.application.ai.contracts import AIModelRequest
        from backend.app.application.ai.providers.gemini_client import GeminiModelClient

        captured = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["url"] = str(request.url)
            captured["body"] = json.loads(request.content.decode("utf-8"))
            return httpx.Response(
                status_code=200,
                json={
                    "candidates": [
                        {
                            "finishReason": "STOP",
                            "content": {
                                "parts": [{"text": "respuesta gemini"}],
                            },
                        }
                    ]
                },
            )

        client = GeminiModelClient(
            api_key="test-gemini-key",
            model_name="gemini-test",
            timeout_seconds=5.0,
            max_retries=2,
            http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
        )

        response = asyncio.run(
            client.generate(
                AIModelRequest(
                    prompt_text="resume el caso",
                    system_instruction="solo usa datos permitidos",
                )
            )
        )

        self.assertIn("key=test-gemini-key", captured["url"])
        self.assertEqual(captured["body"]["contents"][0]["parts"][0]["text"], "resume el caso")
        self.assertEqual(
            captured["body"]["systemInstruction"]["parts"][0]["text"],
            "solo usa datos permitidos",
        )
        self.assertEqual(response.provider, "gemini")
        self.assertEqual(response.model_name, "gemini-test")
        self.assertEqual(response.output_text, "respuesta gemini")

    def test_gemini_client_retries_on_server_error(self):
        from backend.app.application.ai.contracts import AIModelRequest
        from backend.app.application.ai.providers.gemini_client import GeminiModelClient

        attempts = {"count": 0}

        def handler(request: httpx.Request) -> httpx.Response:
            attempts["count"] += 1
            if attempts["count"] == 1:
                return httpx.Response(status_code=503, json={"error": {"message": "unavailable"}})
            return httpx.Response(
                status_code=200,
                json={
                    "candidates": [
                        {
                            "finishReason": "STOP",
                            "content": {"parts": [{"text": "ok after retry"}]},
                        }
                    ]
                },
            )

        client = GeminiModelClient(
            api_key="test-gemini-key",
            model_name="gemini-test",
            timeout_seconds=5.0,
            max_retries=2,
            http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
        )

        response = asyncio.run(client.generate(AIModelRequest(prompt_text="hola")))

        self.assertEqual(attempts["count"], 2)
        self.assertEqual(response.output_text, "ok after retry")
