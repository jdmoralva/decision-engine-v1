# Backend

Backend del nuevo `Decision Engine` con `FastAPI`, `SQLAlchemy`, `Alembic` y un modulo de dominio `decision_engine` aislado del framework web.

## Requisitos

- Python 3.12+
- dependencias instaladas desde la raiz del proyecto

## Arranque local

```bash
.venv\Scripts\python -m uvicorn backend.app.main:app --reload
```

## Mapa de modulos MVP

- `backend/app/api/`: borde HTTP, rutas REST, schemas y mappers.
- `backend/app/application/`: casos de uso y orquestacion.
- `backend/app/application/ai/`: integracion AI opcional fuera del camino critico.
- `backend/app/application/engine_admin/`: servicios del motor administrable.
- `backend/app/application/evaluations/`: evaluaciones runtime y trazabilidad asociada.
- `backend/app/application/credit_requests/`: solicitudes de credito, estados y adjuntos.
- `backend/app/domain/decision_engine/`: motor deterministico aislado de FastAPI.
- `backend/app/infrastructure/db/`: ORM, sesiones y seed local.
- `backend/app/infrastructure/repositories/`: repositorios SQLAlchemy y adaptadores de persistencia.
- `backend/app/infrastructure/files/`: almacenamiento y procesamiento de archivos operativos.
- `backend/app/security/`: autenticacion temporal, RBAC y dependencias de seguridad.

## Endpoints actuales

- `GET /api/v1/health`
- `POST /api/v1/auth/login`
- `GET /api/v1/me`
- `GET /api/v1/admin/health`
- `GET /api/v1/admin/rules`
- `POST /api/v1/loans/{product_code}/consultas`
- `POST /api/v1/loans/{product_code}/evaluaciones`
- `GET /api/v1/loans/{product_code}/evaluaciones/{evaluation_id}`
- `GET /api/v1/loans/{product_code}/evaluaciones/{evaluation_id}/trace`
- `POST /api/v1/credit-requests`
- `GET /api/v1/credit-requests/{request_id}`
- `POST /api/v1/credit-requests/{request_id}/status-transitions`

El endpoint `POST /api/v1/loans/{product_code}/consultas` ya expone una consulta operativa autenticada por producto usando un adaptador local de desarrollo, desacoplado de la UI y del legacy como runtime.

Los endpoints de negocio de evaluacion y solicitudes ya existen como contratos REST y controlan autenticacion/autorizacion, pero todavia responden `501` mientras se implementan los casos de uso funcionales.

## Configuracion actual

Variables principales:

- `APP_NAME` - nombre del servicio
- `APP_ENV` - entorno actual
- `API_V1_PREFIX` - prefijo base de la API
- `DATABASE_URL` - conexion SQLAlchemy
- `AUTH_SECRET_KEY` - secreto de firma para tokens de acceso
- `ACCESS_TOKEN_EXPIRE_MINUTES` - expiracion del token temporal
- `AI_ENABLED` - habilita o deshabilita la capa AI
- `AI_PROVIDER` - proveedor activo (`openai` o `gemini`)
- `AI_TIMEOUT_SECONDS` - timeout por llamada AI
- `AI_MAX_RETRIES` - reintentos base frente a timeout o fallas temporales
- `OPENAI_API_KEY` - clave del proveedor OpenAI
- `OPENAI_MODEL_NAME` - modelo activo de OpenAI
- `GEMINI_API_KEY` - clave del proveedor Gemini
- `GEMINI_MODEL_NAME` - modelo activo de Gemini

Valor por defecto de base de datos:

```text
sqlite+pysqlite:///./decision_engine.db
```

## Modelo de datos inicial

El backend ya incluye un modelo nucleo para el MVP con estas tablas base:

- `users`
- `roles`
- `user_roles`
- `loan_products`
- `credit_requests`
- `credit_request_status_history`
- `loan_evaluations`
- `evaluation_input_snapshots`
- `decision_traces`
- `decision_events`
- `rule_sets`
- `rule_versions`
- `pipeline_strategies`
- `pipeline_nodes`
- `ai_interactions`
- `ai_prompt_templates`

## Motor de decisiones base

El backend ya incluye el paquete de dominio `backend/app/domain/decision_engine/` con:

- contratos internos del motor con `Pydantic`
- `DecisionTrace` estructurado
- normalizacion base de entradas
- `DecisionNode`, `PipelineStrategy` y `DecisionEngineOrchestrator`
- validacion topologica con deteccion de ciclos
- registry multiproducto por `product_code`

Este modulo se puede importar sin dependencias de FastAPI y constituye el cierre tecnico de `ISSUE-010`.

En el borde HTTP tambien existen adaptadores finos entre los schemas REST y el contrato interno del motor en:

- `backend/app/api/mappers/evaluations.py`

## Capa AI base

El backend ya incluye el modulo `backend/app/application/ai/` con:

- contrato base `AIModelClient`
- contratos neutrales `AIModelRequest` y `AIModelResponse`
- clientes concretos para `OpenAI` y `Gemini`
- factory por proveedor activo fijo
- carga de configuracion AI desde entorno o `.env`
- manejo base de timeout y reintentos para fallas temporales

Esta base constituye el cierre tecnico de `ISSUE-034` y deja preparada la integracion de explicaciones y resumenes AI de sprints posteriores.

## Migraciones

Configuracion Alembic disponible en:

- `backend/alembic.ini`
- `backend/alembic/env.py`
- `backend/alembic/versions/`

Ejemplo de upgrade manual:

```bash
python -m alembic -c backend/alembic.ini upgrade head
```

## Semilla local de usuarios y roles

Para probar login rapido en desarrollo:

```bash
python -m backend.app.infrastructure.db.seed
```

Usuarios creados por defecto:

- `admin` / `admin123`
- `analista` / `analista123`
- `evaluador` / `evaluador123`
- `supervisor` / `supervisor123`

## Tests

Suite base del backend:

```bash
.venv\Scripts\python -m unittest backend.tests.test_settings backend.tests.test_health backend.tests.test_models backend.tests.test_migrations backend.tests.test_auth backend.tests.test_seed
```

Suite ampliada relevante al estado actual:

```bash
.venv\Scripts\python -m unittest backend.tests.test_settings backend.tests.test_health backend.tests.test_models backend.tests.test_migrations backend.tests.test_auth backend.tests.test_seed backend.tests.test_rbac backend.tests.test_issue_002_openapi backend.tests.test_decision_engine_contracts backend.tests.test_decision_engine_normalization backend.tests.test_decision_engine_pipeline backend.tests.test_decision_engine_registry backend.tests.test_evaluation_contract_mappers backend.tests.test_ai_settings backend.tests.test_ai_client_factory backend.tests.test_ai_openai_client backend.tests.test_ai_gemini_client
```

Comandos locales de validacion rapida:

```bash
.venv\Scripts\python -m alembic -c backend/alembic.ini upgrade head
.venv\Scripts\python -m backend.app.infrastructure.db.seed
.venv\Scripts\python -m unittest backend.tests.test_issue_013_consultations_api
```

## Autenticacion y RBAC actuales

El backend ya incluye una base de autenticacion temporal con:

- login interno por `username` y `password`
- hashing de password con `pbkdf2_hmac`
- token bearer firmado con HMAC
- identificacion consistente del usuario autenticado en `GET /api/v1/me`
- restriccion de endpoints por rol con una dependencia RBAC base
- proteccion por accion de negocio para evaluaciones, trazas, solicitudes y endpoints administrativos

Roles verificados actualmente:

- `admin`
- `analista`
- `evaluador`
- `supervisor`

## Alcance actual

Este backend todavia no incluye:

- integracion con SSO o proveedor corporativo
- la logica de negocio PLD real sobre el motor
- integracion del endpoint de evaluacion con el motor y persistencia real de resultados
- casos de uso PLD completos
- bandeja operativa, adjuntos ZIP y capacidades AI del MVP

## Estado resumido

Hoy el backend ya tiene:

- bootstrap FastAPI operativo
- configuracion por entorno
- autenticacion temporal
- RBAC base del MVP
- ORM y migraciones
- contratos REST iniciales publicados en OpenAPI
- modulo aislado del motor de decisiones listo para evolucionar con productos concretos
- servicio base de conexion a LLM listo para `OpenAI` y `Gemini`

El siguiente paso natural del backend es `ISSUE-011`: implementar la logica y formulas reales de `PLD` sobre el core del motor.
