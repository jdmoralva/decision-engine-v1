# Tasks: Decision Engine MVP

**Input**: Design documents from `/specs/001-project-specification/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Include automated test tasks whenever the change affects decision engine logic, API contracts, persistence, security, RBAC, auditability, or AI traceability. Treat tests as mandatory for this MVP.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (`[US1]`, `[US2]`, `[US3]`, `[US4]`)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare the repo for MVP slices aligned with the plan.

- [ ] T001 Create backend module folders `backend/app/application/engine_admin`, `backend/app/application/evaluations`, `backend/app/application/credit_requests`, `backend/app/infrastructure/repositories`, and `backend/app/infrastructure/files`
- [ ] T002 Create backend test folders `backend/tests/contract` and `backend/tests/integration`
- [ ] T003 [P] Create frontend feature folders `frontend/src/features/auth`, `frontend/src/features/engine-admin`, `frontend/src/features/loan-consultations`, `frontend/src/features/evaluations`, `frontend/src/features/credit-requests`, and `frontend/src/features/attachments`
- [ ] T004 [P] Update `backend/README.md` and `frontend/README.md` with the MVP module map and local validation commands

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T005 Evolve product persistence as the single source of truth in `backend/app/infrastructure/db/models.py` by extending `LoanProduct` and adding workflow, variable catalog, parameter set, pipeline strategy/node, rule assignment, attachment, AI interaction, and audit entities
- [ ] T006 Create Alembic migration for product source-of-truth, engine admin, attachment, and AI traceability tables in `backend/alembic/versions/20260611_0002_engine_admin_runtime.py`
- [ ] T007 [P] Create repository interfaces and SQLAlchemy implementations for engine admin aggregates, including parameters and pipeline configuration, in `backend/app/infrastructure/repositories/engine_admin.py`
- [ ] T008 [P] Create repository interfaces and SQLAlchemy implementations for evaluations and traces in `backend/app/infrastructure/repositories/evaluations.py`
- [ ] T009 [P] Create repository interfaces and SQLAlchemy implementations for credit requests, status history, and queue exports in `backend/app/infrastructure/repositories/credit_requests.py`
- [ ] T010 Define shared admin and runtime Pydantic schemas in `backend/app/api/schemas/engine_admin.py`, including parameters, pipeline configuration, export filters, and audit query contracts, and refine shared runtime/auth schemas in `backend/app/api/schemas/contracts.py` and `backend/app/api/schemas/auth.py`
- [ ] T011 [P] Implement shared audit event writer reusing or extending `backend/app/infrastructure/db/models.py` and expose it from `backend/app/infrastructure/repositories/audit_events.py`
- [ ] T012 [P] Extend RBAC permissions and dependency wiring for engine administration, evaluations, credit requests, exports, and attachments in `backend/app/security/permissions.py` and `backend/app/security/dependencies.py`
- [ ] T013 Build runtime loader services that resolve `product_code`, `workflow_code`, active workflow version, variable catalog, parameter set, rules, and pipeline in `backend/app/application/engine_admin/runtime_loader.py`
- [ ] T014 Refactor engine bootstrap to support persistence-backed runtime registration in `backend/app/domain/decision_engine/bootstrap.py` and `backend/app/domain/decision_engine/registry.py`
- [ ] T014A [P] Implement AI interaction persistence and repository access in `backend/app/infrastructure/repositories/ai_interactions.py`
- [ ] T015 [P] Add foundational tests for migrations, repositories, runtime loading, source-of-truth product semantics, parameter/pipeline activation constraints, and RBAC in `backend/tests/test_models.py`, `backend/tests/test_migrations.py`, `backend/tests/test_decision_engine_registry.py`, and `backend/tests/test_rbac.py`

**Checkpoint**: Foundation ready - user story implementation can now begin.

---

## Phase 3: User Story 4 - Administrar productos, workflows, variables, parametros, pipeline y reglas del motor (Priority: P1) 🎯 MVP Foundation Story

**Goal**: Permitir a usuarios autorizados crear, versionar, activar y retirar productos, workflows, catalogos de variables, parametros, estrategias de pipeline y reglas sin cambios de codigo en las capas compartidas.

**Independent Test**: Un usuario autorizado crea un producto `draft`, registra variables y un catalogo versionado, publica parametros, crea un workflow con pipeline y reglas, activa la configuracion completa, intenta editar un workflow activo y el sistema obliga a crear una nueva version, dejando trazabilidad de todas las acciones.

### Tests for User Story 4 ⚠️

- [ ] T016 [P] [US4] Add contract tests for admin product, workflow, variable catalog, parameter, pipeline, and rule endpoints in `backend/tests/contract/test_engine_admin_api.py`
- [ ] T017 [P] [US4] Add integration tests for lifecycle transitions, activation guards, parameter/pipeline dependencies, and workflow version immutability in `backend/tests/integration/test_engine_admin_flow.py`
- [ ] T018 [P] [US4] Add regression tests for second-product onboarding without shared-layer code changes in `backend/tests/integration/test_engine_admin_second_product.py`

### Implementation for User Story 4

- [ ] T019 [P] [US4] Implement engine admin application services for products, workflows, variable catalogs, parameter sets, pipeline strategies, and rules in `backend/app/application/engine_admin/service.py`
- [ ] T020 [P] [US4] Implement lifecycle validation and activation guard rules, including parameter and pipeline reference checks, in `backend/app/application/engine_admin/activation_rules.py`
- [ ] T021 [P] [US4] Implement workflow versioning service in `backend/app/application/engine_admin/workflow_versions.py`
- [ ] T022 [US4] Implement engine admin routes for products, workflows, variable catalogs, parameter sets, pipeline strategies, and rules in `backend/app/api/routes/engine_admin.py`
- [ ] T023 [US4] Implement admin request/response mappers in `backend/app/api/mappers/engine_admin.py`
- [ ] T024 [US4] Implement engine admin frontend service client in `frontend/src/services/engine-admin-api.ts`
- [ ] T025 [P] [US4] Implement product, workflow, and pipeline admin UI in `frontend/src/features/engine-admin/ProductsPage.tsx`, `frontend/src/features/engine-admin/WorkflowsPage.tsx`, and `frontend/src/features/engine-admin/PipelinePage.tsx`
- [ ] T026 [P] [US4] Implement variable catalog, parameter set, and rule admin UI in `frontend/src/features/engine-admin/VariablesPage.tsx`, `frontend/src/features/engine-admin/ParametersPage.tsx`, and `frontend/src/features/engine-admin/RulesPage.tsx`
- [ ] T027 [US4] Add frontend tests for engine admin lifecycle, parameter publication, pipeline activation, and versioning in `frontend/tests/engine-admin-flow.test.tsx`

**Checkpoint**: Motor administrable funcional y testeable de manera independiente.

---

## Phase 4: User Story 1 - Consultar y evaluar una oferta de credito (Priority: P1) 🎯 MVP Runtime Story

**Goal**: Permitir consulta por producto y evaluacion `PLD` con runtime persistido, `DecisionTrace` reproducible, autenticacion operativa y explicacion AI opcional con fallback seguro.

**Independent Test**: Un analista inicia sesion, restaura sesion, consulta `POST /api/v1/loans/PLD/consultas`, ejecuta `POST /api/v1/loans/PLD/evaluaciones`, obtiene `GET /api/v1/loans/PLD/evaluaciones/{evaluation_id}` y `GET /api/v1/loans/PLD/evaluaciones/{evaluation_id}/trace`, con versiones persistidas y sin dependencia del legacy aun cuando la AI falle.

### Tests for User Story 1 ⚠️

- [ ] T028 [P] [US1] Add contract tests for login/session bootstrap and runtime consultation/evaluation endpoints in `backend/tests/contract/test_runtime_auth_and_evaluations.py`
- [ ] T029 [P] [US1] Add integration tests for consultation, evaluation execution, trace retrieval, variable-origin enforcement, effective-version persistence, and AI fallback in `backend/tests/integration/test_pld_runtime_flow.py`
- [ ] T030 [P] [US1] Add mapper and determinism regression tests for product-specific HTTP contracts in `backend/tests/test_evaluation_contract_mappers.py` and `backend/tests/test_decision_engine_pipeline.py`

### Implementation for User Story 1

- [ ] T031 [P] [US1] Implement frontend login/session bootstrap in `frontend/src/features/auth/LoginPage.tsx`, `frontend/src/features/auth/auth-service.ts`, and `frontend/src/session-storage.ts`
- [ ] T032 [P] [US1] Implement consultation application service orchestration in `backend/app/application/loan_consultations.py`
- [ ] T033 [P] [US1] Implement evaluation application service with runtime loading, variable-origin validation, snapshot capture, effective-version persistence, and AI fallback handling in `backend/app/application/evaluations/service.py`
- [ ] T034 [P] [US1] Refine product-specific to generic engine mapping in `backend/app/api/mappers/evaluations.py`
- [ ] T035 [US1] Implement consultation route behavior in `backend/app/api/routes/loan_consultations.py`
- [ ] T036 [US1] Implement evaluation and trace routes in `backend/app/api/routes/evaluations.py`
- [ ] T037 [US1] Persist applied workflow, variable catalog, parameter set, rule set, and pipeline versions in `backend/app/infrastructure/repositories/evaluations.py`
- [ ] T038 [US1] Implement AI explanation and summary orchestration with explicit fallback and `ai_interactions` persistence in `backend/app/application/ai/evaluation_explanations.py`
- [ ] T039 [US1] Add frontend service client for consultations and evaluations in `frontend/src/services/runtime-api.ts`
- [ ] T040 [P] [US1] Implement consultation UI flow in `frontend/src/features/loan-consultations/ConsultationPage.tsx` and `frontend/src/features/loan-consultations/consultation-form.tsx`
- [ ] T041 [P] [US1] Implement evaluation UI flow and trace viewer in `frontend/src/features/evaluations/EvaluationPage.tsx`, `frontend/src/features/evaluations/evaluation-form.tsx`, and `frontend/src/features/evaluations/trace-panel.tsx`
- [ ] T042 [US1] Wire auth, consultation, and evaluation routes in `frontend/src/App.tsx` and `frontend/src/main.tsx`
- [ ] T043 [US1] Add frontend tests for login, consultation, and evaluation user journeys in `frontend/tests/auth-flow.test.tsx`, `frontend/tests/consultation-flow.test.tsx`, and `frontend/tests/evaluation-flow.test.tsx`

**Checkpoint**: User Story 1 fully functional and testable independently.

---

## Phase 5: User Story 2 - Registrar y gestionar una solicitud (Priority: P2)

**Goal**: Permitir registrar solicitudes desde evaluaciones validas, consultar detalle, mantener historial de estados, operar la bandeja con permisos y exportar resultados.

**Independent Test**: Un analista o supervisor crea una solicitud desde una evaluacion valida, consulta su detalle, ejecuta una transicion autorizada, verifica el historial y exporta la bandeja sin afectar la reproducibilidad de la evaluacion origen.

### Tests for User Story 2 ⚠️

- [ ] T044 [P] [US2] Add contract tests for `POST /api/v1/credit-requests`, `GET /api/v1/credit-requests/{request_id}`, `POST /api/v1/credit-requests/{request_id}/status-transitions`, and `CSV UTF-8` queue export endpoints with applied filters in `backend/tests/contract/test_credit_requests_api.py`
- [ ] T045 [P] [US2] Add integration tests for request registration, status transitions, forbidden transitions, and queue export with filter echoing in `backend/tests/integration/test_credit_request_flow.py`

### Implementation for User Story 2

- [ ] T046 [P] [US2] Implement credit request application services in `backend/app/application/credit_requests/service.py`
- [ ] T047 [P] [US2] Implement credit request persistence, status history writes, evaluation linkage, and `CSV UTF-8` queue export support with audit metadata in `backend/app/infrastructure/repositories/credit_requests.py`
- [ ] T048 [US2] Implement credit request, queue, and export routes in `backend/app/api/routes/credit_requests.py`
- [ ] T049 [US2] Add request status transition validation and role-specific rules in `backend/app/application/credit_requests/status_rules.py`
- [ ] T050 [US2] Implement request detail, queue, export, and filter-echo schemas/mappers in `backend/app/api/schemas/contracts.py` and `backend/app/api/mappers/credit_requests.py`
- [ ] T051 [US2] Add queue, request, and export services for the frontend in `frontend/src/services/credit-requests-api.ts`
- [ ] T052 [P] [US2] Implement request registration UI in `frontend/src/features/credit-requests/CreditRequestPage.tsx` and `frontend/src/features/credit-requests/request-form.tsx`
- [ ] T053 [P] [US2] Implement operational queue UI, export action, and status actions in `frontend/src/features/credit-requests/QueuePage.tsx` and `frontend/src/features/credit-requests/status-actions.tsx`
- [ ] T054 [US2] Add frontend tests for request creation, queue management, and export in `frontend/tests/credit-request-flow.test.tsx` and `frontend/tests/queue-flow.test.tsx`

**Checkpoint**: User Stories 1 and 2 both work independently.

---

## Phase 6: User Story 3 - Administrar adjuntos y auditoria (Priority: P3)

**Goal**: Permitir gestionar adjuntos ZIP y consultar evidencia/auditoria operacional y administrativa del caso.

**Independent Test**: Un usuario autorizado carga y descarga un ZIP asociado a una solicitud, mientras un auditor puede revisar la traza de evaluacion y los eventos relevantes del caso sin romper permisos ni historico.

### Tests for User Story 3 ⚠️

- [ ] T055 [P] [US3] Add contract tests for attachment upload, metadata/listing, ZIP content listing, download, and audit retrieval endpoints in `backend/tests/contract/test_attachments_and_audit_api.py`
- [ ] T056 [P] [US3] Add integration tests for ZIP lifecycle, ZIP manifest visualization, audit events, and AI-failure-safe retrieval in `backend/tests/integration/test_attachments_and_audit_flow.py`

### Implementation for User Story 3

- [ ] T057 [P] [US3] Implement filesystem ZIP storage and ZIP manifest extraction service in `backend/app/infrastructure/files/zip_storage.py`
- [ ] T058 [P] [US3] Implement attachment metadata repository and audit persistence in `backend/app/infrastructure/repositories/attachments.py`
- [ ] T059 [US3] Implement attachment upload, list, ZIP content listing, and download application services in `backend/app/application/credit_requests/attachments_service.py`
- [ ] T060 [US3] Implement attachment and paginated audit routes with `evaluation_id` and `request_id` filters in `backend/app/api/routes/attachments.py` and `backend/app/api/routes/audit.py`
- [ ] T061 [US3] Extend frontend service clients for attachments and audit trace access in `frontend/src/services/attachments-api.ts` and `frontend/src/services/audit-api.ts`
- [ ] T062 [P] [US3] Implement attachment management UI with metadata and ZIP content listing in `frontend/src/features/attachments/AttachmentsPanel.tsx` and `frontend/src/features/attachments/upload-form.tsx`
- [ ] T063 [P] [US3] Implement audit timeline UI in `frontend/src/features/attachments/AuditTimeline.tsx`
- [ ] T064 [US3] Add frontend tests for attachments and audit timeline in `frontend/tests/attachments-flow.test.tsx` and `frontend/tests/audit-timeline.test.tsx`

**Checkpoint**: All user stories independently functional.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories.

- [ ] T065 [P] Update OpenAPI examples and generated contract fixtures in `specs/001-project-specification/contracts/runtime.openapi.yaml`, `specs/001-project-specification/contracts/engine-admin.openapi.yaml`, and `backend/tests/contract/fixtures/`
- [ ] T066 Harden observability, structured logging, request tracing, and AI degradation logging in `backend/app/main.py`, `backend/app/config/settings.py`, and `backend/app/application/`
- [ ] T067 [P] Add regression coverage for versioning, active-state enforcement, parameter/pipeline governance, second-product extensibility, AI traceability, and auditability in `backend/tests/integration/test_engine_admin_versioning.py` and `backend/tests/integration/test_runtime_reproducibility.py`
- [ ] T068 [P] Add frontend regression coverage for session persistence and role-gated navigation in `frontend/tests/session-storage.test.ts` and `frontend/tests/navigation-guards.test.tsx`
- [ ] T069 Run and document end-to-end validation from `specs/001-project-specification/quickstart.md`, including export, adjuntos, auditoria, AI fallback, and p95 checks, in a project execution report
- [ ] T069A [P] Implement automated performance validation tests for p95 targets (`SC-012`) in `backend/tests/integration/test_performance_validation.py` using a mock or local database baseline and synthetic operational workload
- [ ] T069B [P] Create automated validation suite for ZIP content visual listing (`FR-012`, `SC-005`) in `backend/tests/integration/test_zip_manifest_validation.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 4 (Phase 3)**: Depends on Foundational completion - establishes admin-managed runtime
- **User Story 1 (Phase 4)**: Depends on Foundational completion and on the runtime published through US4
- **User Story 2 (Phase 5)**: Depends on US1 evaluation persistence
- **User Story 3 (Phase 6)**: Depends on US1 trace persistence and US2 request persistence
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **US4**: Can start after Phase 2 - no dependency on later stories
- **US1**: Depends on US4 because evaluations must consume administrable products, workflows, variables, parameters, pipeline, and rules
- **US2**: Depends on US1 evaluation persistence because requests must link to valid evaluations
- **US3**: Depends on US2 request persistence and US1 trace/audit persistence

### Within Each User Story

- Tests MUST be written and fail before implementation
- Persistence and models before application services
- Application services before routes and UI wiring
- Backend contracts before frontend integration

### Parallel Opportunities

- T003-T004 can run in parallel after T001-T002
- T007-T014A and T015 can run in parallel once T005-T006 are complete where file ownership does not collide
- In US4, T016-T018 can run together; T019-T021 can run in parallel; T025-T026 can run in parallel
- In US1, T028-T030 can run together; T031-T034 can run in parallel; T040-T041 can run in parallel
- In US2, T044-T045 can run together; T046-T047 can run in parallel; T052-T053 can run in parallel
- In US3, T055-T056 can run together; T057-T058 can run in parallel; T062-T063 can run in parallel

---

## Parallel Example: User Story 4

```bash
# Launch US4 backend-first tests together
Task: "Add contract tests for admin product, workflow, variable catalog, parameter, pipeline, and rule endpoints in backend/tests/contract/test_engine_admin_api.py"
Task: "Add integration tests for lifecycle transitions, activation guards, parameter/pipeline dependencies, and workflow version immutability in backend/tests/integration/test_engine_admin_flow.py"
Task: "Add regression tests for second-product onboarding without shared-layer code changes in backend/tests/integration/test_engine_admin_second_product.py"

# Launch US4 admin UI tasks together after backend contracts stabilize
Task: "Implement product, workflow, and pipeline admin UI in frontend/src/features/engine-admin/ProductsPage.tsx, frontend/src/features/engine-admin/WorkflowsPage.tsx, and frontend/src/features/engine-admin/PipelinePage.tsx"
Task: "Implement variable catalog, parameter set, and rule admin UI in frontend/src/features/engine-admin/VariablesPage.tsx, frontend/src/features/engine-admin/ParametersPage.tsx, and frontend/src/features/engine-admin/RulesPage.tsx"
```

---

## Implementation Strategy

### MVP First

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 4
4. Complete Phase 4: User Story 1
5. Stop and validate administracion del motor + consulta/evaluacion/trace como MVP funcional

### Incremental Delivery

1. Complete Setup + Foundational
2. Add User Story 4 and validate administracion del motor
3. Add User Story 1 and validate runtime MVP
4. Add User Story 2 and validate registro, bandeja y exportacion
5. Add User Story 3 and validate adjuntos y auditoria
6. Finish with Phase 7 hardening and quickstart validation

### Parallel Team Strategy

1. Team completes Setup + Foundational together
2. One stream builds US4 backend/admin UI while another prepares shared auth/runtime frontend scaffolding
3. After US4 stabilizes, one stream takes US1 runtime, then US2 request flows, while another takes US3 attachment/audit flows

---

## Notes

- Every task follows the required checklist format with checkbox, task ID, optional `[P]`, required story label in story phases, and exact file paths.
- Tests are mandatory in this feature because the MVP touches determinism, contracts, persistence, RBAC, auditability, fallback AI, and multiproduct extensibility.
- Prefer completing US4 + US1 as the first deployable MVP increment before opening US2 and US3 in parallel.
