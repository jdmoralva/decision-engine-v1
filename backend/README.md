# Backend

Backend bootstrap de `Decision Engine` con `FastAPI`, `SQLAlchemy` y `Alembic`.

## Requisitos

- Python 3.12+
- dependencias instaladas desde la raiz del proyecto

## Arranque local

```bash
python -m uvicorn backend.app.main:app --reload
```

## Endpoints base

- `GET /api/v1/health`
- `POST /api/v1/auth/login`
- `GET /api/v1/me`
- `GET /api/v1/admin/health`

## Configuracion actual

Variables principales:

- `APP_NAME` - nombre del servicio
- `APP_ENV` - entorno actual
- `API_V1_PREFIX` - prefijo base de la API
- `DATABASE_URL` - conexion SQLAlchemy
- `AUTH_SECRET_KEY` - secreto de firma para tokens de acceso
- `ACCESS_TOKEN_EXPIRE_MINUTES` - expiracion del token temporal

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

Suite actual del backend:

```bash
python -m unittest backend.tests.test_settings backend.tests.test_health backend.tests.test_models backend.tests.test_migrations backend.tests.test_auth backend.tests.test_seed
```

## Autenticacion y RBAC actuales

El backend ya incluye una base de autenticacion temporal con:

- login interno por `username` y `password`
- hashing de password con `pbkdf2_hmac`
- token bearer firmado con HMAC
- identificacion consistente del usuario autenticado en `GET /api/v1/me`
- restriccion de endpoints por rol con una dependencia RBAC base

Roles verificados actualmente:

- `admin`
- `analista`

## Alcance actual

Este backend todavia no incluye:

- integracion con SSO o proveedor corporativo
- matriz completa de permisos del MVP
- casos de uso PLD completos
- motor de decisiones funcional
- endpoints de negocio del MVP
