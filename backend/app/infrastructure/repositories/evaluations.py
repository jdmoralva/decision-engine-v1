from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from backend.app.domain.decision_engine import EngineDecisionTrace, EngineEvaluationRequest, EngineEvaluationResult
from backend.app.infrastructure.db.models import DecisionTrace, EvaluationInputSnapshot, LoanEvaluation


@dataclass(frozen=True)
class PersistedEvaluationVersions:
    workflow_version_id: str | None
    variable_catalog_version_id: str | None
    parameter_set_id: str | None
    pipeline_version: str
    rule_set_version: str


@dataclass(frozen=True)
class PersistedEvaluationSnapshotItem:
    source_type: str
    source_key: str
    field_name: str
    field_value: str


@dataclass(frozen=True)
class PersistedEvaluationRecord:
    evaluation_id: str
    product_code: str
    workflow_code: str | None
    eligible: bool
    applied_versions: PersistedEvaluationVersions
    decision_trace_id: str
    product_result: dict[str, object]
    engine_trace: EngineDecisionTrace
    human_summary: str | None


class SqlAlchemyEvaluationsRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def create(
        self,
        *,
        request: EngineEvaluationRequest,
        result: EngineEvaluationResult,
        versions: PersistedEvaluationVersions,
        executed_by: str,
        snapshots: list[PersistedEvaluationSnapshotItem],
        human_summary: str | None,
    ) -> PersistedEvaluationRecord:
        evaluation_id = str(uuid4())
        trace_id = result.decision_trace.trace_id
        now = datetime.now(UTC)
        campaign_code = str(request.product_context.get("campaign_code", "") or "")

        trace_payload = json.dumps(
            {
                "trace": result.decision_trace.model_dump(mode="json"),
                "product_result": result.product_result,
            }
        )

        with self._session_factory() as session:
            session.add(
                LoanEvaluation(
                    id=evaluation_id,
                    loan_product_code=request.product_code,
                    workflow_code=request.workflow_code,
                    workflow_version_id=versions.workflow_version_id,
                    variable_catalog_version_id=versions.variable_catalog_version_id,
                    parameter_set_id=versions.parameter_set_id,
                    document_type=request.document.document_type,
                    document_number=request.document.document_number,
                    campaign_code=campaign_code,
                    rule_set_version=versions.rule_set_version,
                    parameter_version=result.applied_versions.parameter_version or "",
                    pipeline_version=versions.pipeline_version,
                    decision_outcome=result.decision_trace.final_outcome,
                    eligible=result.eligible,
                    executed_by=executed_by,
                    executed_at=now,
                )
            )
            session.add(
                DecisionTrace(
                    id=trace_id,
                    evaluation_id=evaluation_id,
                    pipeline_version=versions.pipeline_version,
                    trace_payload=trace_payload,
                    human_summary=human_summary,
                    created_at=now,
                )
            )
            for snapshot in snapshots:
                session.add(
                    EvaluationInputSnapshot(
                        id=str(uuid4()),
                        evaluation_id=evaluation_id,
                        source_type=snapshot.source_type,
                        source_key=snapshot.source_key,
                        field_name=snapshot.field_name,
                        field_value=snapshot.field_value,
                        created_at=now,
                    )
                )
            session.commit()

        return self.get_evaluation(evaluation_id=evaluation_id, product_code=request.product_code)

    def get_evaluation(self, *, evaluation_id: str, product_code: str) -> PersistedEvaluationRecord | None:
        with self._session_factory() as session:
            evaluation = session.execute(
                select(LoanEvaluation).where(
                    LoanEvaluation.id == evaluation_id,
                    LoanEvaluation.loan_product_code == product_code,
                )
            ).scalar_one_or_none()
            if evaluation is None:
                return None
            trace_row = session.execute(
                select(DecisionTrace).where(DecisionTrace.evaluation_id == evaluation_id)
            ).scalar_one_or_none()
            if trace_row is None:
                return None

        return self._build_record(evaluation=evaluation, trace_row=trace_row)

    def get_trace(self, *, evaluation_id: str, product_code: str) -> PersistedEvaluationRecord | None:
        return self.get_evaluation(evaluation_id=evaluation_id, product_code=product_code)

    def update_human_summary(self, *, evaluation_id: str, human_summary: str) -> None:
        with self._session_factory() as session:
            trace_row = session.execute(
                select(DecisionTrace).where(DecisionTrace.evaluation_id == evaluation_id)
            ).scalar_one_or_none()
            if trace_row is None:
                return
            trace_row.human_summary = human_summary
            session.commit()

    def _build_record(
        self,
        *,
        evaluation: LoanEvaluation,
        trace_row: DecisionTrace,
    ) -> PersistedEvaluationRecord:
        payload = json.loads(trace_row.trace_payload or "{}")
        trace_payload = payload.get("trace", {})
        product_result = payload.get("product_result", {})
        engine_trace = EngineDecisionTrace(**trace_payload)
        return PersistedEvaluationRecord(
            evaluation_id=evaluation.id,
            product_code=evaluation.loan_product_code,
            workflow_code=evaluation.workflow_code,
            eligible=bool(evaluation.eligible),
            applied_versions=PersistedEvaluationVersions(
                workflow_version_id=evaluation.workflow_version_id,
                variable_catalog_version_id=evaluation.variable_catalog_version_id,
                parameter_set_id=evaluation.parameter_set_id,
                pipeline_version=evaluation.pipeline_version,
                rule_set_version=evaluation.rule_set_version,
            ),
            decision_trace_id=trace_row.id,
            product_result=product_result,
            engine_trace=engine_trace,
            human_summary=trace_row.human_summary,
        )
