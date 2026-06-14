from __future__ import annotations

from backend.app.api.mappers.evaluations import map_api_request_to_engine_request
from backend.app.api.schemas.contracts import (
    ActorRef,
    AppliedVersions,
    DecisionTraceNode,
    DecisionTraceResponse,
    EvaluationRequest,
    EvaluationResponse,
    ExternalInputSnapshotItem,
)
from backend.app.application.ai.evaluation_explanations import EvaluationExplanationService
from backend.app.domain.decision_engine import (
    DecisionEngineOrchestrator,
    EngineDecisionEvidence,
    UnknownProductError,
    UnknownWorkflowError,
    build_persistence_backed_decision_engine_registry,
)
from backend.app.infrastructure.db.models import ProductVariable, VariableCatalogItem
from backend.app.infrastructure.db.session import get_session_factory
from backend.app.infrastructure.repositories.ai_interactions import AIInteractionsRepository
from backend.app.infrastructure.repositories.engine_admin import RuntimeBundle, SqlAlchemyEngineAdminRepository
from backend.app.infrastructure.repositories.evaluations import (
    PersistedEvaluationRecord,
    PersistedEvaluationSnapshotItem,
    PersistedEvaluationVersions,
    SqlAlchemyEvaluationsRepository,
)


class EvaluationValidationError(Exception):
    pass


class EvaluationNotFoundError(Exception):
    pass


class EvaluationRuntimeUnavailableError(Exception):
    pass


class EvaluationService:
    def __init__(self) -> None:
        session_factory = get_session_factory()
        self._session_factory = session_factory
        self._runtime_repository = SqlAlchemyEngineAdminRepository(session_factory)
        self._evaluations_repository = SqlAlchemyEvaluationsRepository(session_factory)
        self._explanation_service = EvaluationExplanationService(AIInteractionsRepository(session_factory))

    async def create_evaluation(
        self,
        *,
        product_code: str,
        payload: EvaluationRequest,
        actor_user_id: str,
        actor_username: str,
    ) -> EvaluationResponse:
        api_request, field_sources, source_keys = self._materialize_request(
            product_code=product_code,
            payload=payload,
            actor_user_id=actor_user_id,
            actor_username=actor_username,
        )
        engine_request = map_api_request_to_engine_request(api_request)
        bundle = self._runtime_repository.load_active_runtime_bundle(
            engine_request.product_code,
            engine_request.workflow_code,
        )
        if bundle is not None:
            self._validate_variable_origins(engine_request=engine_request, bundle=bundle, field_sources=field_sources)

        try:
            registry = build_persistence_backed_decision_engine_registry(self._session_factory)
            runtime = registry.resolve(engine_request.product_code, engine_request.workflow_code)
        except UnknownProductError as exc:
            raise EvaluationRuntimeUnavailableError(str(exc)) from exc
        except UnknownWorkflowError as exc:
            raise EvaluationRuntimeUnavailableError(str(exc)) from exc

        normalized_request = runtime.normalizer(engine_request)
        result = await DecisionEngineOrchestrator(runtime.nodes).evaluate(normalized_request, runtime.strategy)
        self._attach_evidence(result=result, request=normalized_request, field_sources=field_sources, source_keys=source_keys)

        persisted = self._evaluations_repository.create(
            request=normalized_request,
            result=result,
            versions=self._resolve_versions(bundle=bundle, result=result),
            executed_by=actor_user_id,
            snapshots=self._build_snapshots(result=result, request=normalized_request, field_sources=field_sources, source_keys=source_keys),
            human_summary=None,
        )
        summary = await self._explanation_service.summarize(
            evaluation_id=persisted.evaluation_id,
            actor_user_id=actor_user_id,
            request=normalized_request,
            result=result,
        )
        self._evaluations_repository.update_human_summary(
            evaluation_id=persisted.evaluation_id,
            human_summary=summary,
        )
        persisted = self._evaluations_repository.get_evaluation(
            evaluation_id=persisted.evaluation_id,
            product_code=persisted.product_code,
        ) or persisted
        return self._map_record_to_response(persisted)

    def get_evaluation(self, *, product_code: str, evaluation_id: str) -> EvaluationResponse:
        record = self._evaluations_repository.get_evaluation(
            evaluation_id=evaluation_id,
            product_code=product_code.strip().upper(),
        )
        if record is None:
            raise EvaluationNotFoundError(
                f"Evaluation '{evaluation_id}' was not found for product '{product_code.strip().upper()}'."
            )
        return self._map_record_to_response(record)

    def get_trace(self, *, product_code: str, evaluation_id: str) -> DecisionTraceResponse:
        record = self._evaluations_repository.get_trace(
            evaluation_id=evaluation_id,
            product_code=product_code.strip().upper(),
        )
        if record is None:
            raise EvaluationNotFoundError(
                f"Decision trace for evaluation '{evaluation_id}' was not found for product '{product_code.strip().upper()}'."
            )
        trace = record.engine_trace
        return DecisionTraceResponse(
            trace_id=record.decision_trace_id,
            evaluation_id=record.evaluation_id,
            product_code=record.product_code,
            applied_versions=AppliedVersions(
                rule_set_version=record.applied_versions.rule_set_version,
                parameter_version=trace.applied_versions.parameter_version,
                pipeline_version=record.applied_versions.pipeline_version,
            ),
            alerts=list(trace.alerts),
            blocks=list(trace.blocks),
            rules_applied=list(trace.rules_applied),
            consumed_variables=list(trace.consumed_variables),
            produced_variables=list(trace.produced_variables),
            produced_effects=list(trace.produced_effects),
            nodes_executed=[DecisionTraceNode(**node.model_dump()) for node in trace.nodes_executed],
            evidence=[
                ExternalInputSnapshotItem(
                    source_type=item.source_type,
                    source_key=item.source_key,
                    field_name=item.field_name,
                    field_value=item.field_value,
                    used_by_engine=True,
                )
                for item in trace.evidence
            ],
        )

    def _materialize_request(
        self,
        *,
        product_code: str,
        payload: EvaluationRequest,
        actor_user_id: str,
        actor_username: str,
    ) -> tuple[EvaluationRequest, dict[str, str], dict[str, str]]:
        product_context = {str(key): value for key, value in payload.product_context.items()}
        field_sources = {key: "campaign_db" for key in product_context}
        source_keys = {key: f"product_context:{key}" for key in product_context}

        for item in payload.external_inputs:
            field_name = item.field_name.strip().lower()
            product_context[field_name] = item.field_value
            field_sources[field_name] = item.source_type.strip().lower()
            source_keys[field_name] = item.source_key

        api_request = payload.model_copy(
            update={
                "product_code": product_code.strip().upper(),
                "requested_by": ActorRef(user_id=actor_user_id, username=actor_username),
                "product_context": product_context,
            }
        )
        return api_request, field_sources, source_keys

    def _validate_variable_origins(
        self,
        *,
        engine_request,
        bundle: RuntimeBundle,
        field_sources: dict[str, str],
    ) -> None:
        variables_by_id = {variable.id: variable for variable in bundle.variables}
        published_variables: dict[str, tuple[ProductVariable, VariableCatalogItem]] = {}
        for item in bundle.catalog_items:
            variable = variables_by_id.get(item.product_variable_id)
            if variable is not None:
                published_variables[variable.variable_key] = (variable, item)

        for variable_key, (variable, item) in published_variables.items():
            if item.is_required_in_runtime and variable_key not in engine_request.product_context:
                raise EvaluationValidationError(
                    f"Required variable '{variable_key}' is missing from the published runtime input."
                )

        for field_name, source_type in field_sources.items():
            published = published_variables.get(field_name)
            if published is None:
                continue
            variable, _item = published
            if not self._source_is_allowed(variable.allowed_sources, source_type):
                raise EvaluationValidationError(
                    f"Variable '{field_name}' does not allow source '{source_type}'."
                )

    def _source_is_allowed(self, allowed_sources: str, source_type: str) -> bool:
        normalized_allowed = (allowed_sources or "").strip().lower()
        normalized_source = (source_type or "").strip().lower()
        if normalized_allowed == "both":
            return normalized_source in {"campaign_db", "user_input"}
        return normalized_allowed == normalized_source

    def _attach_evidence(
        self,
        *,
        result,
        request,
        field_sources: dict[str, str],
        source_keys: dict[str, str],
    ) -> None:
        seen: set[str] = set()
        for field_name in result.decision_trace.consumed_variables:
            if field_name in seen or field_name not in request.product_context:
                continue
            seen.add(field_name)
            result.decision_trace.evidence.append(
                EngineDecisionEvidence(
                    source_type=field_sources.get(field_name, "campaign_db"),
                    source_key=source_keys.get(field_name, f"product_context:{field_name}"),
                    field_name=field_name,
                    field_value=str(request.product_context[field_name]),
                )
            )

    def _build_snapshots(
        self,
        *,
        result,
        request,
        field_sources: dict[str, str],
        source_keys: dict[str, str],
    ) -> list[PersistedEvaluationSnapshotItem]:
        snapshots: list[PersistedEvaluationSnapshotItem] = []
        seen: set[str] = set()
        for field_name in result.decision_trace.consumed_variables:
            if field_name in seen or field_name not in request.product_context:
                continue
            seen.add(field_name)
            snapshots.append(
                PersistedEvaluationSnapshotItem(
                    source_type=field_sources.get(field_name, "campaign_db"),
                    source_key=source_keys.get(field_name, f"product_context:{field_name}"),
                    field_name=field_name,
                    field_value=str(request.product_context[field_name]),
                )
            )
        return snapshots

    def _resolve_versions(
        self,
        *,
        bundle: RuntimeBundle | None,
        result,
    ) -> PersistedEvaluationVersions:
        return PersistedEvaluationVersions(
            workflow_version_id=None if bundle is None else bundle.workflow_version.id,
            variable_catalog_version_id=None if bundle is None else bundle.catalog_version.id,
            parameter_set_id=None if bundle is None else bundle.parameter_set.id,
            pipeline_version=result.applied_versions.pipeline_version or "",
            rule_set_version=result.applied_versions.rule_set_version or "",
        )

    def _map_record_to_response(self, record: PersistedEvaluationRecord) -> EvaluationResponse:
        return EvaluationResponse(
            evaluation_id=record.evaluation_id,
            product_code=record.product_code,
            eligible=record.eligible,
            alerts=list(record.engine_trace.alerts),
            blocks=list(record.engine_trace.blocks),
            applied_versions=AppliedVersions(
                rule_set_version=record.applied_versions.rule_set_version,
                parameter_version=record.engine_trace.applied_versions.parameter_version,
                pipeline_version=record.applied_versions.pipeline_version,
            ),
            decision_trace_id=record.decision_trace_id,
            product_result=record.product_result,
        )
