from backend.app.domain.decision_engine.contracts import EngineEvaluationRequest
from backend.app.domain.decision_engine.exceptions import EngineValidationError


def _require_non_blank(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise EngineValidationError(f"{field_name} must not be blank")
    return normalized


def normalize_evaluation_request(request: EngineEvaluationRequest) -> EngineEvaluationRequest:
    product_code = _require_non_blank(request.product_code, "product_code").upper()
    workflow_code = _require_non_blank(request.workflow_code, "workflow_code")
    document_type = _require_non_blank(
        request.document.document_type, "document.document_type"
    ).upper()
    document_number = _require_non_blank(
        request.document.document_number, "document.document_number"
    )
    username = _require_non_blank(request.requested_by.username, "requested_by.username")

    external_inputs = [
        item.model_copy(
            update={
                "source_type": _require_non_blank(
                    item.source_type, "external_inputs.source_type"
                ).lower(),
                "source_key": _require_non_blank(item.source_key, "external_inputs.source_key"),
                "field_name": _require_non_blank(
                    item.field_name, "external_inputs.field_name"
                ).lower(),
                "field_value": item.field_value.strip(),
            }
        )
        for item in request.external_inputs
    ]

    return request.model_copy(
        update={
            "product_code": product_code,
            "workflow_code": workflow_code,
            "document": request.document.model_copy(
                update={
                    "document_type": document_type,
                    "document_number": document_number,
                }
            ),
            "requested_by": request.requested_by.model_copy(update={"username": username}),
            "external_inputs": external_inputs,
        }
    )
