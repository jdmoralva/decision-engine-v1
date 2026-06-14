# Quickstart - Decision Engine MVP Validation

## Purpose

Esta guia valida el MVP planeado de punta a punta para backend, frontend, administracion del motor y flujo operacional `PLD`.

## Prerequisites

- Python disponible en `.venv\Scripts\python`
- Node.js 20+ y npm 10+
- Dependencias backend y frontend instaladas
- Base local SQLite inicializable por Alembic

## Setup

### 1. Migrar base de datos

Desde la raiz del repo:

```bash
.venv\Scripts\python -m alembic -c backend/alembic.ini upgrade head
```

Resultado esperado:

- la base SQLite queda creada o actualizada
- no hay errores de migracion

### 2. Sembrar usuarios y roles de desarrollo

```bash
.venv\Scripts\python -m backend.app.infrastructure.db.seed
```

Resultado esperado:

- existen usuarios `admin`, `analista`, `evaluador`, `evaluador`

### 3. Levantar backend

```bash
.venv\Scripts\python -m uvicorn backend.app.main:app --reload
```

Resultado esperado:

- backend disponible en `http://127.0.0.1:8000`
- Swagger disponible en `http://127.0.0.1:8000/docs`

### 4. Levantar frontend

Desde `frontend/`:

```bash
npm run dev
```

Resultado esperado:

- frontend disponible en `http://127.0.0.1:5173`

## Validation Scenarios

### Scenario A - Autenticacion base

1. Iniciar sesion como `admin`.
2. Consultar `GET /api/v1/me`.

Resultado esperado:

- el usuario autenticado y sus roles se resuelven correctamente

### Scenario B - Administracion del motor

Prerequisito:

- sesion autenticada con permisos administrativos vigentes

1. Crear un producto en estado `draft`.
2. Crear variables para ese producto con origen `campaign_db`, `user_input` y `both`.
3. Crear un workflow `draft` para el producto.
4. Crear un catalogo de variables versionado y asignarlo al workflow.
5. Crear reglas `draft` y una estrategia de pipeline `draft`.
6. Activar catalogo, reglas, pipeline y workflow segun permisos autorizados.

Referencias:

- contrato administrativo: `contracts/engine-admin.openapi.yaml`
- modelo de datos: `data-model.md`

Resultado esperado:

- producto, workflow y reglas quedan auditados
- solo configuraciones `active` quedan disponibles para runtime

### Scenario C - Consulta y evaluacion `PLD`

Prerequisito:

- debe existir al menos un producto `active`, un workflow `active`, un catalogo de variables `active` y reglas/pipeline activas publicados desde el flujo administrativo

1. Ejecutar consulta `POST /api/v1/loans/PLD/consultas` con documento valido.
2. Ejecutar evaluacion `POST /api/v1/loans/PLD/evaluaciones` indicando `workflow_code` y datos complementarios.
3. Consultar `GET /api/v1/loans/PLD/evaluaciones/{evaluation_id}`.
4. Consultar `GET /api/v1/loans/PLD/evaluaciones/{evaluation_id}/trace`.

Referencias:

- contrato runtime: `contracts/runtime.openapi.yaml`
- bundle de versiones aplicado: `data-model.md`

Resultado esperado:

- la evaluacion usa solo configuraciones `active`
- la respuesta devuelve resultado estructurado y referencia de trace
- la trace conserva evidencia y versiones aplicadas

### Scenario D - Registro y gestion de solicitud

Prerequisito:

- debe existir una evaluacion valida previamente registrada

1. Crear solicitud desde una evaluacion valida.
2. Consultar solicitud por `request_id`.
3. Ejecutar una transicion de estado autorizada.
4. Cancelar una solicitud cuando el rol lo permita.

Resultado esperado:

- la solicitud queda vinculada a la evaluacion y al usuario creador
- el historial de estados se conserva completo

### Scenario E - Adjuntos ZIP y AI asistiva

Prerequisito:

- debe existir una solicitud registrada y consultable

1. Cargar un ZIP para una solicitud existente.
2. Listar y descargar el adjunto.
3. Solicitar explicacion AI para una evaluacion ya registrada.

Resultado esperado:

- los adjuntos se guardan con metadata y auditoria
- la AI responde a partir de `DecisionTrace`
- si la AI falla, la solicitud y la evaluacion siguen consultables

## Validation Commands

### Backend base

```bash
.venv\Scripts\python -m unittest backend.tests.test_settings backend.tests.test_health backend.tests.test_models backend.tests.test_migrations backend.tests.test_auth backend.tests.test_seed backend.tests.test_rbac backend.tests.test_issue_002_openapi backend.tests.test_decision_engine_contracts backend.tests.test_decision_engine_normalization backend.tests.test_decision_engine_pipeline backend.tests.test_decision_engine_registry backend.tests.test_evaluation_contract_mappers backend.tests.test_ai_settings backend.tests.test_ai_client_factory backend.tests.test_ai_openai_client backend.tests.test_ai_gemini_client
```

### Backend contract and integration suites

```bash
.venv\Scripts\python -m unittest backend.tests.contract.test_engine_admin_api backend.tests.contract.test_runtime_auth_and_evaluations backend.tests.contract.test_credit_requests_api backend.tests.contract.test_attachments_and_audit_api backend.tests.integration.test_engine_admin_flow backend.tests.integration.test_engine_admin_second_product backend.tests.integration.test_pld_runtime_flow backend.tests.integration.test_credit_request_flow backend.tests.integration.test_attachments_and_audit_flow
```

### Frontend base

```bash
npm run test
```

### Frontend MVP suites

Escenarios esperados dentro de la suite:

- `auth-flow`
- `engine-admin-flow`
- `consultation-flow`
- `evaluation-flow`
- `credit-request-flow`
- `queue-flow`
- `attachments-flow`
- `audit-timeline`

## Expected MVP Evidence

- contratos OpenAPI publicados para administracion y runtime
- evaluacion `PLD` reproducible con versiones persistidas
- solicitudes y transiciones auditadas
- adjuntos ZIP administrables
- AI asistiva opcional y fuera del camino critico
