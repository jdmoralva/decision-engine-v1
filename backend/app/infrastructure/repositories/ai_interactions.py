from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy.orm import Session, sessionmaker

from backend.app.infrastructure.db.models import AIInteraction


@dataclass(frozen=True)
class AIInteractionWrite:
    user_id: str
    evaluation_id: str | None
    request_id: str | None
    context_type: str
    prompt_template_version: str
    input_payload: str
    model_name: str
    response_text: str


class AIInteractionsRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def create(self, data: AIInteractionWrite) -> AIInteraction:
        row = AIInteraction(
            id=str(uuid4()),
            user_id=data.user_id,
            evaluation_id=data.evaluation_id,
            request_id=data.request_id,
            context_type=data.context_type,
            prompt_template_version=data.prompt_template_version,
            input_payload=data.input_payload,
            model_name=data.model_name,
            response_text=data.response_text,
            created_at=datetime.now(UTC),
        )
        with self._session_factory() as session:
            session.add(row)
            session.commit()
            session.refresh(row)
        return row
