from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from backend.app.infrastructure.db.models import AdministrativeAuditEvent, CreditRequest, CreditRequestAttachment, User


@dataclass(frozen=True)
class AttachmentRecord:
    attachment_id: str
    request_id: str
    storage_path: str
    original_filename: str
    mime_type: str
    uploaded_at: str
    uploaded_by_user_id: str
    uploaded_by_username: str


@dataclass(frozen=True)
class AttachmentCreateData:
    attachment_id: str
    request_id: str
    storage_path: str
    original_filename: str
    mime_type: str
    uploaded_by_user_id: str


@dataclass(frozen=True)
class AuditEventRecord:
    event_id: str
    aggregate_id: str
    aggregate_type: str
    event_type: str
    event_payload: dict[str, object]
    created_by_user_id: str
    created_by_username: str
    created_at: str


class SqlAlchemyAttachmentsRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def next_attachment_id(self) -> str:
        return str(uuid4())

    def create(self, data: AttachmentCreateData) -> AttachmentRecord:
        now = datetime.now(UTC)
        with self._session_factory() as session:
            session.add(
                CreditRequestAttachment(
                    id=data.attachment_id,
                    request_id=data.request_id,
                    storage_path=data.storage_path,
                    original_filename=data.original_filename,
                    mime_type=data.mime_type,
                    uploaded_by=data.uploaded_by_user_id,
                    uploaded_at=now,
                )
            )
            session.commit()
        record = self.get(request_id=data.request_id, attachment_id=data.attachment_id)
        if record is None:
            raise LookupError(data.attachment_id)
        return record

    def get(self, *, request_id: str, attachment_id: str) -> AttachmentRecord | None:
        with self._session_factory() as session:
            row = session.execute(
                select(CreditRequestAttachment).where(
                    CreditRequestAttachment.id == attachment_id,
                    CreditRequestAttachment.request_id == request_id,
                )
            ).scalar_one_or_none()
            if row is None:
                return None
            return self._build_attachment_record(session, row)

    def list(self, *, request_id: str) -> list[AttachmentRecord]:
        with self._session_factory() as session:
            rows = list(
                session.execute(
                    select(CreditRequestAttachment)
                    .where(CreditRequestAttachment.request_id == request_id)
                    .order_by(CreditRequestAttachment.uploaded_at.desc())
                ).scalars()
            )
            return [self._build_attachment_record(session, row) for row in rows]

    def request_exists(self, *, request_id: str) -> bool:
        with self._session_factory() as session:
            return session.get(CreditRequest, request_id) is not None

    def list_audit_events(
        self,
        *,
        request_id: str | None,
        evaluation_id: str | None,
        page: int,
        page_size: int,
    ) -> tuple[int, list[AuditEventRecord]]:
        with self._session_factory() as session:
            rows = list(
                session.execute(
                    select(AdministrativeAuditEvent).order_by(AdministrativeAuditEvent.created_at.desc())
                ).scalars()
            )
            filtered = [
                self._build_audit_record(session, row)
                for row in rows
                if _matches_filter(row.event_payload, request_id=request_id, evaluation_id=evaluation_id, aggregate_id=row.aggregate_id)
            ]
            start = max(page - 1, 0) * page_size
            end = start + page_size
            return len(filtered), filtered[start:end]

    def _build_attachment_record(self, session: Session, row: CreditRequestAttachment) -> AttachmentRecord:
        user = session.get(User, row.uploaded_by)
        return AttachmentRecord(
            attachment_id=row.id,
            request_id=row.request_id,
            storage_path=row.storage_path,
            original_filename=row.original_filename,
            mime_type=row.mime_type,
            uploaded_at=_isoformat(row.uploaded_at),
            uploaded_by_user_id=row.uploaded_by,
            uploaded_by_username="" if user is None else user.username,
        )

    def _build_audit_record(self, session: Session, row: AdministrativeAuditEvent) -> AuditEventRecord:
        user = session.get(User, row.created_by)
        payload = json.loads(row.event_payload or "{}")
        return AuditEventRecord(
            event_id=row.event_id,
            aggregate_id=row.aggregate_id,
            aggregate_type=row.aggregate_type,
            event_type=row.event_type,
            event_payload=payload if isinstance(payload, dict) else {},
            created_by_user_id=row.created_by,
            created_by_username="" if user is None else user.username,
            created_at=_isoformat(row.created_at),
        )


def _matches_filter(
    payload_text: str,
    *,
    request_id: str | None,
    evaluation_id: str | None,
    aggregate_id: str,
) -> bool:
    if not request_id and not evaluation_id:
        return True

    matches_request = False
    if request_id:
        matches_request = aggregate_id == request_id or f'"request_id": "{request_id}"' in payload_text

    matches_evaluation = False
    if evaluation_id:
        matches_evaluation = aggregate_id == evaluation_id or f'"evaluation_id": "{evaluation_id}"' in payload_text

    return matches_request or matches_evaluation


def _isoformat(value: datetime) -> str:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")
