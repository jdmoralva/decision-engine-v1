from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy.orm import Session, sessionmaker

from backend.app.infrastructure.db.models import AdministrativeAuditEvent


@dataclass(frozen=True)
class AuditEventWrite:
    aggregate_id: str
    aggregate_type: str
    event_type: str
    event_payload: str
    created_by: str


class AuditEventWriter:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def write(self, event: AuditEventWrite) -> AdministrativeAuditEvent:
        row = AdministrativeAuditEvent(
            event_id=str(uuid4()),
            aggregate_id=event.aggregate_id,
            aggregate_type=event.aggregate_type,
            event_type=event.event_type,
            event_payload=event.event_payload,
            created_by=event.created_by,
            created_at=datetime.now(UTC),
        )
        with self._session_factory() as session:
            session.add(row)
            session.commit()
            session.refresh(row)
        return row
