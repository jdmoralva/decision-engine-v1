from __future__ import annotations

import json
import logging

from backend.app.application.ai.contracts import AIModelRequest
from backend.app.application.ai.exceptions import AIServiceError
from backend.app.application.ai.factory import build_ai_model_client
from backend.app.application.observability import log_event
from backend.app.config.settings import get_settings
from backend.app.domain.decision_engine import EngineEvaluationRequest, EngineEvaluationResult
from backend.app.infrastructure.repositories.ai_interactions import AIInteractionWrite, AIInteractionsRepository


logger = logging.getLogger("decision_engine.ai")


class EvaluationExplanationService:
    def __init__(self, ai_repository: AIInteractionsRepository) -> None:
        self._ai_repository = ai_repository

    async def summarize(
        self,
        *,
        evaluation_id: str,
        actor_user_id: str,
        request: EngineEvaluationRequest,
        result: EngineEvaluationResult,
    ) -> str:
        fallback_summary = self._build_fallback_summary(request=request, result=result)
        payload = {
            "product_code": request.product_code,
            "workflow_code": request.workflow_code,
            "document": request.document.model_dump(),
            "applied_versions": result.applied_versions.model_dump(),
            "eligible": result.eligible,
            "alerts": result.alerts,
            "blocks": result.blocks,
            "product_result": result.product_result,
        }
        response_text = fallback_summary
        model_name = "fallback"

        try:
            client = build_ai_model_client(get_settings())
            response = await client.generate(
                AIModelRequest(
                    prompt_text=(
                        "Resume la evaluacion de credito en espanol, con foco en elegibilidad, "
                        "alertas y oferta calculada."
                    ),
                    system_instruction="Responde solo con un resumen operacional breve y auditable.",
                    metadata=payload,
                )
            )
            response_text = response.output_text.strip() or fallback_summary
            model_name = response.model_name
        except AIServiceError as exc:
            log_event(
                logger,
                logging.WARNING,
                "ai_degraded",
                evaluation_id=evaluation_id,
                actor_user_id=actor_user_id,
                provider=get_settings().ai_provider,
                reason=str(exc),
            )
            response_text = fallback_summary
            model_name = "fallback"
        except Exception as exc:
            log_event(
                logger,
                logging.WARNING,
                "ai_degraded",
                evaluation_id=evaluation_id,
                actor_user_id=actor_user_id,
                provider=get_settings().ai_provider,
                reason=str(exc),
            )
            response_text = fallback_summary
            model_name = "fallback"

        self._ai_repository.create(
            AIInteractionWrite(
                user_id=actor_user_id,
                evaluation_id=evaluation_id,
                request_id=None,
                context_type="evaluation_summary",
                prompt_template_version="evaluation-summary:v1",
                input_payload=json.dumps(payload),
                model_name=model_name,
                response_text=response_text,
            )
        )
        return response_text

    def _build_fallback_summary(
        self,
        *,
        request: EngineEvaluationRequest,
        result: EngineEvaluationResult,
    ) -> str:
        offered_amount = result.product_result.get("offered_amount")
        return (
            f"Evaluacion {request.product_code}/{request.workflow_code}: "
            f"eligible={result.eligible}, alerts={len(result.alerts)}, blocks={len(result.blocks)}, "
            f"offered_amount={offered_amount}."
        )
