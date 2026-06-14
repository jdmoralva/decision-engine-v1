from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from io import StringIO

from sqlalchemy import select

from backend.app.api.mappers.credit_requests import (
    map_credit_request_detail_response,
    map_credit_request_queue_response,
    map_credit_request_response,
)
from backend.app.api.schemas.contracts import (
    CreditRequestCreateRequest,
    CreditRequestDetailResponse,
    CreditRequestQueueResponse,
    CreditRequestResponse,
    CreditRequestStatusTransitionRequest,
)
from backend.app.application.credit_requests.status_rules import (
    CreditRequestStatusRules,
    InvalidCreditRequestTransitionError,
    normalize_credit_request_status,
)
from backend.app.infrastructure.db.models import LoanEvaluation
from backend.app.infrastructure.db.session import get_session_factory
from backend.app.infrastructure.repositories.audit_events import AuditEventWrite, AuditEventWriter
from backend.app.infrastructure.repositories.credit_requests import (
    CreditRequestCreateData,
    CreditRequestQueueFilters,
    CreditRequestTransitionData,
    SqlAlchemyCreditRequestsRepository,
)
from backend.app.infrastructure.repositories.evaluations import SqlAlchemyEvaluationsRepository


class CreditRequestValidationError(Exception):
    pass


class CreditRequestNotFoundError(Exception):
    pass


class CreditRequestTransitionError(Exception):
    pass


@dataclass(frozen=True)
class CreditRequestExport:
    content: str
    filters: dict[str, str]


class CreditRequestService:
    def __init__(self) -> None:
        session_factory = get_session_factory()
        self._session_factory = session_factory
        self._repository = SqlAlchemyCreditRequestsRepository(session_factory)
        self._evaluations_repository = SqlAlchemyEvaluationsRepository(session_factory)
        self._audit_writer = AuditEventWriter(session_factory)
        self._status_rules = CreditRequestStatusRules()

    def create_credit_request(
        self,
        *,
        payload: CreditRequestCreateRequest,
        actor_user_id: str,
        actor_username: str,
    ) -> CreditRequestResponse:
        evaluation_row = self._load_evaluation(payload.evaluation_id)
        normalized_product_code = payload.product_code.strip().upper()
        if evaluation_row.loan_product_code != normalized_product_code:
            raise CreditRequestValidationError("The evaluation does not belong to the requested product.")
        if not evaluation_row.eligible:
            raise CreditRequestValidationError("The evaluation is not eligible for credit request registration.")
        if evaluation_row.document_type != payload.document.document_type or evaluation_row.document_number != payload.document.document_number:
            raise CreditRequestValidationError("The request document does not match the linked evaluation.")

        evaluation_record = self._evaluations_repository.get_evaluation(
            evaluation_id=evaluation_row.id,
            product_code=evaluation_row.loan_product_code,
        )
        if evaluation_record is None:
            raise CreditRequestValidationError("The linked evaluation evidence is not available.")

        record = self._repository.create(
            CreditRequestCreateData(
                product_code=normalized_product_code,
                evaluation_id=evaluation_row.id,
                workflow_code=evaluation_row.workflow_code,
                document_type=evaluation_row.document_type,
                document_number=evaluation_row.document_number,
                campaign_code=(payload.campaign_code or evaluation_row.campaign_code or "").strip(),
                requested_amount=payload.requested_amount,
                comment=payload.comment.strip(),
                created_by_user_id=actor_user_id,
                created_by_username=actor_username,
                customer_name=None,
                offered_amount=_float_or_none(evaluation_record.product_result.get("offered_amount")),
                installment_amount=_float_or_none(evaluation_record.product_result.get("installment_amount")),
                term_months=_int_or_none(evaluation_record.product_result.get("term_months")),
                rate=_float_or_none(evaluation_record.product_result.get("rate")),
            )
        )
        self._audit_writer.write(
            AuditEventWrite(
                aggregate_id=record.request_id,
                aggregate_type="credit_request",
                event_type="credit_request_created",
                event_payload=json.dumps(
                    {
                        "request_id": record.request_id,
                        "evaluation_id": record.evaluation_id,
                        "status": record.status,
                    }
                ),
                created_by=actor_user_id,
            )
        )
        return map_credit_request_response(record)

    def get_credit_request(self, *, request_id: str) -> CreditRequestDetailResponse:
        record = self._repository.get(request_id=request_id)
        if record is None:
            raise CreditRequestNotFoundError(f"Credit request '{request_id}' was not found.")
        return map_credit_request_detail_response(record)

    def list_credit_requests(
        self,
        *,
        filters: CreditRequestQueueFilters,
        actor_roles: list[str],
    ) -> CreditRequestQueueResponse:
        records = self._repository.list(filters=filters)
        queue_items = [
            record.with_available_actions(
                self._status_rules.available_actions(current_status=record.status, actor_roles=actor_roles)
            )
            for record in records
        ]
        return map_credit_request_queue_response(filters=filters.to_dict(), items=queue_items)

    def export_credit_requests(
        self,
        *,
        filters: CreditRequestQueueFilters,
        actor_roles: list[str],
        actor_user_id: str,
    ) -> CreditRequestExport:
        queue_response = self.list_credit_requests(filters=filters, actor_roles=actor_roles)
        buffer = StringIO()
        writer = csv.writer(buffer)
        filter_text = ";".join(f"{key}={value}" for key, value in queue_response.applied_filters.items())
        writer.writerow(["filtros_aplicados", filter_text])
        writer.writerow(
            [
                "request_id",
                "product_code",
                "workflow_code",
                "evaluation_id",
                "document_type",
                "document_number",
                "customer_name",
                "status",
                "created_at",
                "updated_at",
            ]
        )
        for item in queue_response.items:
            writer.writerow(
                [
                    item.request_id,
                    item.product_code,
                    item.workflow_code or "",
                    item.evaluation_id or "",
                    item.document.document_type,
                    item.document.document_number,
                    item.customer_name or "",
                    item.status,
                    item.created_at,
                    item.updated_at,
                ]
            )
        for item in queue_response.items:
            self._audit_writer.write(
                AuditEventWrite(
                    aggregate_id=item.request_id,
                    aggregate_type="credit_request",
                    event_type="credit_request_queue_exported",
                    event_payload=json.dumps(
                        {"filters": queue_response.applied_filters, "request_id": item.request_id}
                    ),
                    created_by=actor_user_id,
                )
            )
        return CreditRequestExport(content=buffer.getvalue(), filters=queue_response.applied_filters)

    def transition_credit_request(
        self,
        *,
        request_id: str,
        payload: CreditRequestStatusTransitionRequest,
        actor_user_id: str,
        actor_username: str,
        actor_roles: list[str],
    ) -> CreditRequestResponse:
        record = self._repository.get(request_id=request_id)
        if record is None:
            raise CreditRequestNotFoundError(f"Credit request '{request_id}' was not found.")
        try:
            target_status = self._status_rules.validate_transition(
                current_status=record.status,
                target_status=payload.target_status,
                actor_roles=actor_roles,
            )
        except InvalidCreditRequestTransitionError as exc:
            raise CreditRequestTransitionError(str(exc)) from exc

        updated = self._repository.transition(
            CreditRequestTransitionData(
                request_id=request_id,
                target_status=target_status,
                comment=payload.comment.strip() if payload.comment else None,
                changed_by_user_id=actor_user_id,
                changed_by_username=actor_username,
            )
        )
        self._audit_writer.write(
            AuditEventWrite(
                aggregate_id=updated.request_id,
                aggregate_type="credit_request",
                event_type="credit_request_status_changed",
                event_payload=json.dumps(
                    {"request_id": updated.request_id, "status": updated.status, "comment": payload.comment}
                ),
                created_by=actor_user_id,
            )
        )
        return map_credit_request_response(updated)

    def resolve_dynamic_permission(self, target_status: str) -> str:
        normalized = normalize_credit_request_status(target_status)
        return "anular_solicitud" if normalized == "anulada" else "cambiar_estado_solicitud"

    def _load_evaluation(self, evaluation_id: str | None) -> LoanEvaluation:
        if evaluation_id is None or not evaluation_id.strip():
            raise CreditRequestValidationError("A valid evaluation_id is required to register a credit request.")
        with self._session_factory() as session:
            evaluation = session.execute(
                select(LoanEvaluation).where(LoanEvaluation.id == evaluation_id.strip())
            ).scalar_one_or_none()
            if evaluation is None:
                raise CreditRequestValidationError(
                    f"Evaluation '{evaluation_id.strip()}' was not found for credit request registration."
                )
            return evaluation


def _float_or_none(value: object) -> float | None:
    if value is None:
        return None
    return float(value)


def _int_or_none(value: object) -> int | None:
    if value is None:
        return None
    return int(value)
