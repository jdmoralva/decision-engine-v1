---

description: "Task list for Plataforma Visual de Decisión de Crédito"
---

# Tasks: Plataforma Visual de Decisión de Crédito

**Input**: Design documents from `/specs/002-credit-decision-workspace/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Frontend tests are required here because the feature changes autenticación visible, restauración de sesión, navegación protegida, RBAC en UI y contratos de integración con endpoints existentes.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g. `US1`, `US2`, `US3`)
- Each task includes the exact file path to change

## Path Conventions

- Frontend application code lives in `frontend/src/`
- Frontend automated tests live in `frontend/tests/`
- Backend smoke-contract checks remain in `backend/tests/`
- Feature planning artifacts live in `specs/002-credit-decision-workspace/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare the frontend workspace for route-based navigation, new feature modules, and test support.

- [X] T001 Update routing and workspace dependencies in `frontend/package.json`
- [X] T002 [P] Add shared render and storage helpers in `frontend/tests/test-utils.tsx`
- [X] T003 [P] Prepare shared app entry styling hooks in `frontend/src/main.tsx` and `frontend/src/styles.css`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Create the shared app shell, session plumbing, product/service adapters, and session-backed workspace persistence used by all stories.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T004 Create application shell and session context in `frontend/src/app/AppShell.tsx`, `frontend/src/app/session-context.tsx`, and `frontend/src/routes/app-router.tsx`
- [ ] T005 [P] Create shared platform catalog types and adapters in `frontend/src/features/platform/catalog-types.ts`, `frontend/src/features/platform/service-visibility.ts`, and `frontend/src/features/platform/status-labels.ts`
- [ ] T006 [P] Create seeded product and service catalog data in `frontend/src/features/platform/platform-seed-data.ts`
- [ ] T007 [P] Create workspace session storage primitives in `frontend/src/features/decision-workspace/workspace-types.ts` and `frontend/src/features/decision-workspace/workspace-session.ts`
- [ ] T008 Refactor top-level bootstrap to the new shell in `frontend/src/App.tsx`

**Checkpoint**: Foundation ready. Authenticated routing, product/service adapters, and workspace draft persistence primitives are available for story work.

---

## Phase 3: User Story 1 - Iniciar sesion y explorar productos (Priority: P1) 🎯 MVP

**Goal**: Deliver login obligatorio, restauración de sesión válida, and a product catalog showing `PLD` and `Hipotecario` with product actions and navigation entry points.

**Independent Test**: Abrir la aplicación, verificar que la primera vista es `Inicio de sesión`, autenticar con un usuario semilla y confirmar que se muestran `PLD` y `Hipotecario` con sus acciones de tarjeta sin romper la navegación al producto.

### Tests for User Story 1

> **NOTE**: Write these tests first, confirm they fail, then implement the story.

- [ ] T009 [P] [US1] Extend login and session restore coverage in `frontend/tests/auth-flow.test.tsx`
- [ ] T010 [P] [US1] Add product catalog journey coverage in `frontend/tests/product-catalog-flow.test.tsx`

### Implementation for User Story 1

- [ ] T011 [US1] Update authenticated login and restore behavior in `frontend/src/features/auth/auth-service.ts`, `frontend/src/features/auth/LoginPage.tsx`, and `frontend/src/session-storage.ts`
- [ ] T012 [P] [US1] Implement the product catalog UI in `frontend/src/features/product-catalog/ProductCatalogPage.tsx` and `frontend/src/features/product-catalog/ProductCard.tsx`
- [ ] T013 [US1] Wire the `#/login` and `#/productos` routes in `frontend/src/routes/app-router.tsx` and `frontend/src/app/AppShell.tsx`
- [ ] T014 [US1] Implement product quick actions, three-dot menu behavior, and desktop-first catalog styling in `frontend/src/features/product-catalog/ProductCatalogPage.tsx` and `frontend/src/styles.css`

**Checkpoint**: User Story 1 should be fully functional and testable on its own.

---

## Phase 4: User Story 2 - Ver y abrir servicios (Priority: P2)

**Goal**: Deliver a role-aware service catalog for each product with breadcrumb context and navigation into a service workspace.

**Independent Test**: Ingresar a un producto con distintos roles, verificar que la pantalla `Servicios` muestra la grilla permitida por rol y abrir una tarjeta para entrar al espacio del servicio.

### Tests for User Story 2

- [ ] T015 [P] [US2] Add role-based service catalog coverage in `frontend/tests/service-catalog-flow.test.tsx`
- [ ] T016 [P] [US2] Extend guarded route coverage for product and service navigation in `frontend/tests/navigation-guards.test.tsx`

### Implementation for User Story 2

- [ ] T017 [P] [US2] Implement the service catalog UI, including placeholder-only delete affordances on service cards, in `frontend/src/features/service-catalog/ServiceCatalogPage.tsx` and `frontend/src/features/service-catalog/ServiceCard.tsx`
- [ ] T018 [US2] Implement role visibility and Spanish service labels in `frontend/src/features/platform/service-visibility.ts` and `frontend/src/features/service-catalog/ServiceCatalogPage.tsx`
- [ ] T019 [US2] Wire product-to-service navigation, breadcrumb state, and responsive services layout in `frontend/src/routes/app-router.tsx`, `frontend/src/app/AppShell.tsx`, and `frontend/src/styles.css`

**Checkpoint**: User Stories 1 and 2 should both work independently.

---

## Phase 5: User Story 3 - Diseñar flujos de decisión (Priority: P3)

**Goal**: Deliver the `Motor de decisiones` workspace with sidebar sections, workflow canvas, node inspector, session-scoped editing, the `active` to `Aprobado` UI mapping for governed workflows, and the explicit split between backend-governed data and session-local prototypes.

**Independent Test**: Abrir `Motor de decisiones`, verificar sidebar, canvas e inspector, mover o seleccionar nodos, modificar el borrador del flujo, recargar la pestaña y confirmar que el estado del lienzo se conserva durante la sesión.

### Tests for User Story 3

- [ ] T020 [P] [US3] Add workspace shell and node interaction coverage in `frontend/tests/decision-workspace-flow.test.tsx`
- [ ] T021 [P] [US3] Add session-backed workspace persistence coverage in `frontend/tests/decision-workspace-session.test.ts`
- [ ] T022 [P] [US3] Add channel, testing, and events coverage in `frontend/tests/decision-workspace-catalogs.test.tsx`
- [ ] T023 [P] [US3] Add parameters, data section, and profile action coverage in `frontend/tests/decision-workspace-admin-sections.test.tsx`

### Implementation for User Story 3

- [ ] T024 [P] [US3] Implement workspace reducer, seeded workflow model, and sub-workflow node support in `frontend/src/features/decision-workspace/workspace-reducer.ts`, `frontend/src/features/decision-workspace/workspace-context.tsx`, and `frontend/src/features/decision-workspace/workflow-seed-data.ts`
- [ ] T025 [P] [US3] Implement the workspace shell UI in `frontend/src/features/decision-workspace/DecisionWorkspacePage.tsx`, `frontend/src/features/decision-workspace/WorkspaceSidebar.tsx`, `frontend/src/features/decision-workspace/WorkspaceCanvas.tsx`, and `frontend/src/features/decision-workspace/NodeInspector.tsx`
- [ ] T026 [US3] Implement session-backed selection, movement, add/remove node, connection, zoom, viewport, and execution-log actions in `frontend/src/features/decision-workspace/workspace-reducer.ts` and `frontend/src/features/decision-workspace/workspace-session.ts`
- [ ] T027 [US3] Integrate backend workflow and profile reads with `active` to `Aprobado` UI mapping in `frontend/src/services/engine-admin-api.ts`, `frontend/src/features/platform/status-labels.ts`, and `frontend/src/features/decision-workspace/workspace-api-adapters.ts`
- [ ] T028 [US3] Implement channels, `Aprobado` workflow selection backed by backend `active`, parameter multiselect, and compatibility validation states in `frontend/src/features/decision-workspace/ChannelPanel.tsx`, `frontend/src/features/decision-workspace/workspace-api-adapters.ts`, and `frontend/src/features/decision-workspace/DecisionWorkspacePage.tsx`
- [ ] T029 [US3] Implement workflows, testing, and events sections with session-local prototypes in `frontend/src/features/decision-workspace/WorkflowCatalogPanel.tsx`, `frontend/src/features/decision-workspace/TestingPanel.tsx`, `frontend/src/features/decision-workspace/EventsPanel.tsx`, and `frontend/src/features/decision-workspace/DecisionWorkspacePage.tsx`
- [ ] T030 [US3] Implement `Parámetros` and `Data` section panels with risk-role edit restrictions and placeholder governance messaging in `frontend/src/features/decision-workspace/ParametersPanel.tsx`, `frontend/src/features/decision-workspace/DataPanel.tsx`, and `frontend/src/features/decision-workspace/DecisionWorkspacePage.tsx`
- [ ] T031 [US3] Implement profile actions with mock/local behavior for `cambiar contraseña` and `consultar permisos aprobados`, plus real logout, Spanish submodule navigation, and workspace responsive styling in `frontend/src/features/decision-workspace/ProfileMenu.tsx`, `frontend/src/features/decision-workspace/DecisionWorkspacePage.tsx`, and `frontend/src/styles.css`

**Checkpoint**: All three user stories should now be independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, documentation alignment, and build/test hardening across the feature.

- [ ] T032 [P] Update validation notes and expected evidence in `specs/002-credit-decision-workspace/quickstart.md`
- [ ] T033 Run and fix frontend regression coverage in `frontend/tests/auth-flow.test.tsx`, `frontend/tests/product-catalog-flow.test.tsx`, `frontend/tests/service-catalog-flow.test.tsx`, `frontend/tests/decision-workspace-flow.test.tsx`, `frontend/tests/decision-workspace-session.test.ts`, `frontend/tests/decision-workspace-catalogs.test.tsx`, and `frontend/tests/decision-workspace-admin-sections.test.tsx`
- [ ] T034 [P] Run and fix build/config compatibility in `frontend/package.json`, `frontend/vite.config.ts`, `frontend/vite.config.js`, and `frontend/vite.config.d.ts`
- [ ] T035 [P] Run backend auth and RBAC smoke alignment in `backend/tests/test_auth.py`, `backend/tests/test_rbac.py`, and `backend/tests/contract/test_engine_admin_api.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1: Setup**: No dependencies
- **Phase 2: Foundational**: Depends on Phase 1 and blocks all story work
- **Phase 3: US1**: Depends on Phase 2
- **Phase 4: US2**: Depends on Phase 2 and builds on authenticated product navigation introduced in US1
- **Phase 5: US3**: Depends on Phase 2 and on service-opening flow from US2
- **Phase 6: Polish**: Depends on all implemented stories

### User Story Dependencies

- **US1 (P1)**: First deliverable and MVP baseline
- **US2 (P2)**: Requires authenticated navigation into a selected product from US1
- **US3 (P3)**: Requires service-entry routing from US2 and shared session/workspace primitives from Phase 2; includes all workspace submodules (`channels`, `workflows`, `testing`, `events`, `Parámetros`, and `Data`)

### Within Each User Story

- Tests must be written and observed failing before implementation
- Route and state primitives come before page wiring
- Core UI behavior comes before styling polish
- Session-backed workspace behavior comes before backend/session-local adapter integration
- Channel validation and status mapping must be implemented before polishing admin submodule UX

### Parallel Opportunities

- `T002` and `T003` can run in parallel after `T001`
- `T005`, `T006`, and `T007` can run in parallel in Phase 2
- `T009` and `T010` can run in parallel for US1
- `T012` can proceed in parallel with `T011` once foundational routing exists
- `T015` and `T016` can run in parallel for US2
- `T017` can run in parallel with part of `T018` after foundational adapters exist
- `T020`, `T021`, `T022`, and `T023` can run in parallel for US3
- `T024` and `T025` can run in parallel once US2 routing is complete
- `T029` and `T030` can run in parallel after `T027` and `T028`
- `T034` and `T035` can run in parallel during polish

---

## Parallel Example: User Story 1

```bash
Task: "Extend login and session restore coverage in frontend/tests/auth-flow.test.tsx"
Task: "Add product catalog journey coverage in frontend/tests/product-catalog-flow.test.tsx"

Task: "Implement the product catalog UI in frontend/src/features/product-catalog/ProductCatalogPage.tsx and frontend/src/features/product-catalog/ProductCard.tsx"
Task: "Update authenticated login and restore behavior in frontend/src/features/auth/auth-service.ts, frontend/src/features/auth/LoginPage.tsx, and frontend/src/session-storage.ts"
```

## Parallel Example: User Story 2

```bash
Task: "Add role-based service catalog coverage in frontend/tests/service-catalog-flow.test.tsx"
Task: "Extend guarded route coverage for product and service navigation in frontend/tests/navigation-guards.test.tsx"

Task: "Implement the service catalog UI in frontend/src/features/service-catalog/ServiceCatalogPage.tsx and frontend/src/features/service-catalog/ServiceCard.tsx"
Task: "Implement role visibility and Spanish service labels in frontend/src/features/platform/service-visibility.ts and frontend/src/features/service-catalog/ServiceCatalogPage.tsx"
```

## Parallel Example: User Story 3

```bash
Task: "Add workspace shell and node interaction coverage in frontend/tests/decision-workspace-flow.test.tsx"
Task: "Add session-backed workspace persistence coverage in frontend/tests/decision-workspace-session.test.ts"
Task: "Add channel, testing, and events coverage in frontend/tests/decision-workspace-catalogs.test.tsx"
Task: "Add parameters, data section, and profile action coverage in frontend/tests/decision-workspace-admin-sections.test.tsx"

Task: "Implement workspace reducer, seeded workflow model, and sub-workflow node support in frontend/src/features/decision-workspace/workspace-reducer.ts, frontend/src/features/decision-workspace/workspace-context.tsx, and frontend/src/features/decision-workspace/workflow-seed-data.ts"
Task: "Implement the workspace shell UI in frontend/src/features/decision-workspace/DecisionWorkspacePage.tsx, frontend/src/features/decision-workspace/WorkspaceSidebar.tsx, frontend/src/features/decision-workspace/WorkspaceCanvas.tsx, and frontend/src/features/decision-workspace/NodeInspector.tsx"
```

---

## Implementation Strategy

### MVP First

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1) only.
3. Validate login, session restore, and product catalog behavior with the independent US1 tests.
4. Demo the MVP before moving to service and workspace layers.

### Incremental Delivery

1. Build shared shell, routing, and adapters once.
2. Add US1 for authenticated product entry.
3. Add US2 for service discovery and opening.
4. Add US3 for the decision-workspace experience.
5. Finish with regression, build, and smoke validation.

### Parallel Team Strategy

1. One engineer handles Phase 1 and Phase 2 foundations.
2. Once Phase 2 completes:
   - Engineer A can drive US1 product entry.
   - Engineer B can prepare US2 service catalog tests and UI.
   - Engineer C can prepare US3 reducer/canvas tests and workspace shell.
3. Integrate in priority order `US1 -> US2 -> US3`.

---

## Notes

- All tasks use the required checklist format.
- Every story phase includes explicit independent test criteria.
- Tests are included because this feature changes auth-visible UI, route guards, role-based visibility, and session persistence behavior.
- The task list preserves the constitution boundary between multiproduct UI, deterministic backend logic, and session-local prototyping.
