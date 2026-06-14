from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import UTC, datetime, date, time
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from backend.app.infrastructure.db.models import CreditRequest, CreditRequestAttachment, CreditRequestStatusHistory, User


@dataclass(frozen=True)
class CreditRequestStatusHistoryRecord:
    status: str
    comment: str | None
    changed_by_user_id: str
    changed_by_username: str
    changed_at: str


@dataclass(frozen=True)
class CreditRequestAttachmentRecord:
    attachment_id: str
    original_filename: str
    mime_type: str
    uploaded_at: str


@dataclass(frozen=True)
class CreditRequestRecord:
    request_id: str
    product_code: str
    evaluation_id: str | None
    workflow_code: str | None
    document_type: str
    document_number: str
    campaign_code: str | None
    requested_amount: float
    comment: str
    created_by_user_id: str
    created_by_username: str
    status: str
    customer_name: str | None
    created_at: str
    updated_at: str
    offered_amount: float | None
    installment_amount: float | None
    term_months: int | None
    rate: float | None
    status_history: list[CreditRequestStatusHistoryRecord]
    attachments: list[CreditRequestAttachmentRecord]


@dataclass(frozen=True)
class CreditRequestQueueRecord:
    request_id: str
    product_code: str
    workflow_code: str | None
    evaluation_id: str | None
    document_type: str
    document_number: str
    customer_name: str | None
    status: str
    created_at: str
    updated_at: str
    available_actions: list[str]

    def with_available_actions(self, available_actions: list[str]) -> CreditRequestQueueRecord:
        return replace(self, available_actions=available_actions)


@dataclass(frozen=True)
class CreditRequestCreateData:
    product_code: str
    evaluation_id: str
    workflow_code: str | None
    document_type: str
    document_number: str
    campaign_code: str
    requested_amount: float
    comment: str
    created_by_user_id: str
    created_by_username: str
    customer_name: str | None
    offered_amount: float | None
    installment_amount: float | None
    term_months: int | None
    rate: float | None


@dataclass(frozen=True)
class CreditRequestTransitionData:
    request_id: str
    target_status: str
    comment: str | None
    changed_by_user_id: str
    changed_by_username: str


@dataclass(frozen=True)
class CreditRequestQueueFilters:
    product_code: str | None = None
    status: str | None = None
    document_number: str | None = None
    evaluation_id: str | None = None
    from_date: date | None = None
    to_date: date | None = None

    def to_dict(self) -> dict[str, str]:
        values: dict[str, str] = {}
        if self.product_code:
            values["product_code"] = self.product_code
        if self.status:
            values["status"] = self.status
        if self.document_number:
            values["document_number"] = self.document_number
        if self.evaluation_id:
            values["evaluation_id"] = self.evaluation_id
        if self.from_date:
            values["from_date"] = self.from_date.isoformat()
        if self.to_date:
            values["to_date"] = self.to_date.isoformat()
        return values


class SqlAlchemyCreditRequestsRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def create(self, data: CreditRequestCreateData) -> CreditRequestRecord:
        request_id = str(uuid4())
        now = datetime.now(UTC)
        with self._session_factory() as session:
            session.add(
                CreditRequest(
                    id=request_id,
                    loan_product_code=data.product_code,
                    evaluation_id=data.evaluation_id,
                    workflow_code=data.workflow_code,
                    document_type=data.document_type,
                    document_number=data.document_number,
                    campaign_code=data.campaign_code,
                    requested_amount=data.requested_amount,
                    comment=data.comment,
                    offered_amount=data.offered_amount,
                    installment_amount=data.installment_amount,
                    term_months=data.term_months,
                    rate=data.rate,
                    status="registrada",
                    created_by=data.created_by_user_id,
                    created_at=now,
                )
            )
            session.add(
                CreditRequestStatusHistory(
                    id=str(uuid4()),
                    request_id=request_id,
                    status="registrada",
                    comment=data.comment,
                    changed_by=data.created_by_user_id,
                    changed_at=now,
                )
            )
            session.commit()
        return self.get(request_id=request_id)

    def get(self, *, request_id: str) -> CreditRequestRecord | None:
        with self._session_factory() as session:
            request_row = session.get(CreditRequest, request_id)
            if request_row is None:
                return None
            return self._build_record(session, request_row)

    def list(self, *, filters: CreditRequestQueueFilters) -> list[CreditRequestQueueRecord]:
        with self._session_factory() as session:
            query = select(CreditRequest).order_by(CreditRequest.created_at.desc())
            if filters.product_code:
                query = query.where(CreditRequest.loan_product_code == filters.product_code)
            if filters.status:
                query = query.where(CreditRequest.status == filters.status)
            if filters.document_number:
                query = query.where(CreditRequest.document_number == filters.document_number)
            if filters.evaluation_id:
                query = query.where(CreditRequest.evaluation_id == filters.evaluation_id)
            if filters.from_date:
                query = query.where(CreditRequest.created_at >= datetime.combine(filters.from_date, time.min, tzinfo=UTC))
            if filters.to_date:
                query = query.where(CreditRequest.created_at <= datetime.combine(filters.to_date, time.max, tzinfo=UTC))

            rows = session.execute(query).scalars().all()
            return [self._build_queue_record(session, row) for row in rows]

    def transition(self, data: CreditRequestTransitionData) -> CreditRequestRecord:
        with self._session_factory() as session:
            request_row = session.get(CreditRequest, data.request_id)
            if request_row is None:
                raise LookupError(data.request_id)
            request_row.status = data.target_status
            if data.target_status == "anulada":
                request_row.cancelled_at = datetime.now(UTC)
            status_now = datetime.now(UTC)
            session.add(
                CreditRequestStatusHistory(
                    id=str(uuid4()),
                    request_id=request_row.id,
                    status=data.target_status,
                    comment=data.comment,
                    changed_by=data.changed_by_user_id,
                    changed_at=status_now,
                )
            )
            session.commit()
            session.refresh(request_row)
            return self._build_record(session, request_row)

    def _build_record(self, session: Session, row: CreditRequest) -> CreditRequestRecord:
        created_by_user = session.get(User, row.created_by)
        history_rows = list(
            session.execute(
                select(CreditRequestStatusHistory)
                .where(CreditRequestStatusHistory.request_id == row.id)
                .order_by(CreditRequestStatusHistory.changed_at.asc())
            ).scalars()
        )
        attachment_rows = list(
            session.execute(
                select(CreditRequestAttachment).where(CreditRequestAttachment.request_id == row.id)
            ).scalars()
        )
        updated_at = history_rows[-1].changed_at if history_rows else row.created_at
        return CreditRequestRecord(
            request_id=row.id,
            product_code=row.loan_product_code,
            evaluation_id=row.evaluation_id,
            workflow_code=row.workflow_code,
            document_type=row.document_type,
            document_number=row.document_number,
            campaign_code=row.campaign_code,
            requested_amount=float(row.requested_amount),
            comment=row.comment,
            created_by_user_id=row.created_by,
            created_by_username="" if created_by_user is None else created_by_user.username,
            status=row.status,
            customer_name=None,
            created_at=_isoformat(row.created_at),
            updated_at=_isoformat(updated_at),
            offered_amount=_float_or_none(row.offered_amount),
            installment_amount=_float_or_none(row.installment_amount),
            term_months=row.term_months,
            rate=_float_or_none(row.rate),
            status_history=[self._build_history_record(session, item) for item in history_rows],
            attachments=[
                CreditRequestAttachmentRecord(
                    attachment_id=item.id,
                    original_filename=item.original_filename,
                    mime_type=item.mime_type,
                    uploaded_at=_isoformat(item.uploaded_at),
                )
                for item in attachment_rows
            ],
        )

    def _build_queue_record(self, session: Session, row: CreditRequest) -> CreditRequestQueueRecord:
        history_rows = list(
            session.execute(
                select(CreditRequestStatusHistory)
                .where(CreditRequestStatusHistory.request_id == row.id)
                .order_by(CreditRequestStatusHistory.changed_at.asc())
            ).scalars()
        )
        updated_at = history_rows[-1].changed_at if history_rows else row.created_at
        return CreditRequestQueueRecord(
            request_id=row.id,
            product_code=row.loan_product_code,
            workflow_code=row.workflow_code,
            evaluation_id=row.evaluation_id,
            document_type=row.document_type,
            document_number=row.document_number,
            customer_name=None,
            status=row.status,
            created_at=_isoformat(row.created_at),
            updated_at=_isoformat(updated_at),
            available_actions=[],
        )

    def _build_history_record(self, session: Session, row: CreditRequestStatusHistory) -> CreditRequestStatusHistoryRecord:
        changed_by_user = session.get(User, row.changed_by)
        return CreditRequestStatusHistoryRecord(
            status=row.status,
            comment=row.comment,
            changed_by_user_id=row.changed_by,
            changed_by_username="" if changed_by_user is None else changed_by_user.username,
            changed_at=_isoformat(row.changed_at),
        )


def _isoformat(value: datetime) -> str:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _float_or_none(value: float | None) -> float | None:
    if value is None:
        return None
    return float(value)
