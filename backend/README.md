# Backend

Backend bootstrap de `Decision Engine` con `FastAPI`, `SQLAlchemy` y `Alembic`.

## Requisitos

- Python 3.12+
- dependencias instaladas desde la raiz del proyecto

## Arranque local

```bash
python -m uvicorn backend.app.main:app --reload
```

## Endpoint base

- `GET /api/v1/health`

## Configuracion actual

Variables principales:

- `APP_NAME` - nombre del servicio
- `APP_ENV` - entorno actual
- `API_V1_PREFIX` - prefijo base de la API
- `DATABASE_URL` - conexion SQLAlchemy

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

## Migraciones

Configuracion Alembic disponible en:

- `backend/alembic.ini`
- `backend/alembic/env.py`
- `backend/alembic/versions/`

Ejemplo de upgrade manual:

```bash
python -m alembic -c backend/alembic.ini upgrade head
```

## Tests

Suite actual del backend:

```bash
python -m unittest backend.tests.test_settings backend.tests.test_health backend.tests.test_models backend.tests.test_migrations
```

## Alcance actual

Este backend todavia no incluye:

- autenticacion final
- RBAC operativo
- casos de uso PLD completos
- motor de decisiones funcional
- endpoints de negocio del MVP
