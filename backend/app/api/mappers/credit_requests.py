from backend.app.api.schemas.contracts import (
    ActorRef,
    CreditRequestAttachmentSummary,
    CreditRequestDetailResponse,
    CreditRequestQueueItem,
    CreditRequestQueueResponse,
    CreditRequestResponse,
    CreditRequestStatusHistoryEntry,
    DocumentRef,
)
from backend.app.infrastructure.repositories.credit_requests import (
    CreditRequestAttachmentRecord,
    CreditRequestQueueRecord,
    CreditRequestRecord,
    CreditRequestStatusHistoryRecord,
)


def map_credit_request_response(record: CreditRequestRecord) -> CreditRequestResponse:
    return CreditRequestResponse(
        request_id=record.request_id,
        product_code=record.product_code,
        evaluation_id=record.evaluation_id,
        workflow_code=record.workflow_code,
        status=record.status,
        document=DocumentRef(
            document_type=record.document_type,
            document_number=record.document_number,
        ),
        campaign_code=record.campaign_code,
        requested_amount=record.requested_amount,
        comment=record.comment,
        created_by=ActorRef(user_id=record.created_by_user_id, username=record.created_by_username),
    )


def map_credit_request_detail_response(record: CreditRequestRecord) -> CreditRequestDetailResponse:
    base = map_credit_request_response(record)
    return CreditRequestDetailResponse(
        **base.model_dump(),
        customer_name=record.customer_name,
        created_at=record.created_at,
        updated_at=record.updated_at,
        offered_amount=record.offered_amount,
        installment_amount=record.installment_amount,
        term_months=record.term_months,
        rate=record.rate,
        status_history=[_map_history_item(item) for item in record.status_history],
        attachments=[_map_attachment_item(item) for item in record.attachments],
    )


def map_credit_request_queue_response(
    *,
    filters: dict[str, str],
    items: list[CreditRequestQueueRecord],
) -> CreditRequestQueueResponse:
    return CreditRequestQueueResponse(
        applied_filters=filters,
        items=[
            CreditRequestQueueItem(
                request_id=item.request_id,
                product_code=item.product_code,
                workflow_code=item.workflow_code,
                evaluation_id=item.evaluation_id,
                document=DocumentRef(
                    document_type=item.document_type,
                    document_number=item.document_number,
                ),
                customer_name=item.customer_name,
                status=item.status,
                created_at=item.created_at,
                updated_at=item.updated_at,
                available_actions=list(item.available_actions),
            )
            for item in items
        ],
    )


def _map_history_item(item: CreditRequestStatusHistoryRecord) -> CreditRequestStatusHistoryEntry:
    return CreditRequestStatusHistoryEntry(
        status=item.status,
        comment=item.comment,
        changed_by=ActorRef(user_id=item.changed_by_user_id, username=item.changed_by_username),
        changed_at=item.changed_at,
    )


def _map_attachment_item(item: CreditRequestAttachmentRecord) -> CreditRequestAttachmentSummary:
    return CreditRequestAttachmentSummary(
        attachment_id=item.attachment_id,
        original_filename=item.original_filename,
        mime_type=item.mime_type,
        uploaded_at=item.uploaded_at,
    )
