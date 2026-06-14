# Decision Engine

## Resumen

`Decision Engine` es la nueva implementacion del MVP para productos de prestamo. Reemplaza progresivamente al sistema legacy en `old-version/`, pero sin heredar su arquitectura.

Stack actual:

- backend `FastAPI` + `SQLAlchemy` + `Alembic`
- frontend `Vite` + `React` + `TypeScript`
- persistencia inicial en `SQLite`
- motor de decisiones deterministico y aislado del borde HTTP
- autenticacion moderna con usuarios, roles y permisos

`PLD` (`Prestamo de Libre Disponibilidad`) es el primer producto implementado. `Cobranzas` queda fuera de alcance salvo pedido explicito.

## Estado Real Del Repo

Este repositorio ya no es solo documentacion. Tiene una base ejecutable en desarrollo activo.

Hoy existe:

- backend operativo en `backend/`
- frontend operativo en `frontend/`
- migraciones y modelos de base de datos
- autenticacion con login y resolucion de sesion
- administracion del motor con productos, workflows, variables, parametros, pipeline, reglas y permisos por perfil
- consulta de cliente/campanas para `PLD`

Hoy todavia estan como contrato sin implementacion runtime completa:

- evaluaciones
- solicitudes de credito
- trazas de decision recuperables via API
- flujos AI fuera del camino critico

## Arquitectura Base

- `backend/app/main.py`: entrypoint `FastAPI`
- `backend/app/domain/decision_engine/`: motor deterministico aislado
- `backend/app/application/engine_admin/`: administracion gobernada del runtime
- `backend/app/infrastructure/db/`: modelos, sesion y seed local
- `frontend/src/App.tsx`: login, restauracion de sesion y panel admin inicial
- `old-version/`: referencia funcional y de reglas del sistema anterior

Principios que gobiernan la implementacion:

- plataforma multiproducto primero
- motor deterministico separado de HTTP, UI y AI
- configuracion y evidencia versionadas
- seguridad moderna con trazabilidad completa
- AI asistiva, nunca autonoma

Referencia: `.specify/memory/constitution.md`

## API Disponible Hoy

Rutas activas o expuestas en `backend/app/main.py`:

- `GET /api/v1/health`
- `POST /api/v1/auth/login`
- `GET /api/v1/me`
- `POST /api/v1/loans/{product_code}/consultas`
- `GET /api/v1/admin/health`
- `POST /api/v1/admin/engine/products`
- `POST /api/v1/admin/engine/products/{productCode}/activation`
- `POST /api/v1/admin/engine/products/{productCode}/retirement`
- `DELETE /api/v1/admin/engine/products/{productCode}`
- `POST /api/v1/admin/engine/products/{productCode}/workflows`
- `POST /api/v1/admin/engine/products/{productCode}/variables`
- `POST /api/v1/admin/engine/products/{productCode}/variable-catalogs`
- `POST /api/v1/admin/engine/products/{productCode}/parameter-sets`
- `POST /api/v1/admin/engine/products/{productCode}/pipeline-strategies`
- `POST /api/v1/admin/engine/workflows/{workflowId}/rules`
- `POST /api/v1/admin/engine/workflows/{workflowId}/versions`
- `GET /api/v1/admin/engine/profiles/{roleCode}/permissions`
- `PUT /api/v1/admin/engine/profiles/{roleCode}/permissions`

Tambien existen contratos publicados pero hoy responden `501 Not Implemented`:

- `POST /api/v1/loans/{product_code}/evaluaciones`
- `GET /api/v1/loans/{product_code}/evaluaciones/{evaluation_id}`
- `GET /api/v1/loans/{product_code}/evaluaciones/{evaluation_id}/trace`
- `POST /api/v1/credit-requests`
- `GET /api/v1/credit-requests/{request_id}`
- `POST /api/v1/credit-requests/{request_id}/status-transitions`

## Consulta Demo Disponible

La unica implementacion de negocio completa hoy es la consulta de prestamos en `PLD` usando un provider local en memoria.

Happy path local incorporado:

- producto: `PLD`
- documento: `DNI`
- numero: `12345678`

La consulta devuelve un cliente demo y al menos una campana (`PLD_48M`).

## Estructura Del Repo

```text
backend/
  app/
    api/
    application/
    config/
    domain/
    infrastructure/
    security/
    main.py
  alembic/
  tests/

frontend/
  src/
  package.json
  vite.config.ts

old-version/
specs/
AGENTS.md
README.md
pyproject.toml
```

## Requisitos

- Python `3.12+`
- Node.js compatible con `Vite 5`
- entorno virtual `.venv` en la raiz

Dependencias declaradas:

- backend: `fastapi`, `uvicorn`, `sqlalchemy`, `alembic`, `httpx`
- frontend: `react`, `react-dom`, `vite`, `typescript`, `vitest`

## Arranque Local

### 1. Backend

Instala dependencias del backend dentro de tu `.venv` segun tu flujo habitual y luego ejecuta:

```bash
.venv\Scripts\python -m alembic -c backend/alembic.ini upgrade head
.venv\Scripts\python -m backend.app.infrastructure.db.seed
.venv\Scripts\python -m uvicorn backend.app.main:app --reload
```

### 2. Frontend

Desde `frontend/`:

```bash
npm install
npm run dev
```

Desde la raiz:

```bash
.venv\Scripts\python scripts/frontend_init.py
```

## URLs Locales

- frontend: `http://127.0.0.1:5173/`
- backend API: `http://127.0.0.1:8000/`
- OpenAPI/Swagger: `http://127.0.0.1:8000/docs`

El frontend usa proxy Vite para `/api/*` hacia `http://127.0.0.1:8000`.

## Usuarios Locales Semilla

El seed local crea roles y usuarios iniciales.

- `admin / admin123`
- `analista / analista123`
- `evaluador / evaluador123`
- `auditor / auditor123`
- `negocio / negocio123`
- `riesgos / riesgos123`
- `plataforma / plataforma123`

La pantalla principal del frontend hoy arranca orientada a login y panel administrativo basico.

## Tests Y Verificacion

Backend:

```bash
.venv\Scripts\python -m unittest backend.tests.test_issue_013_consultations_api
```

Frontend desde `frontend/`:

```bash
npm run test
npm run build
```

## Configuracion Y Entorno

- `backend/app/config/settings.py` auto-carga el archivo `.env` en la raiz del repo
- puedes cambiar el archivo de entorno con `DECISION_ENGINE_ENV_FILE`
- no imprimas ni subas `.env`; puede contener secretos reales
- `get_settings()`, `get_engine()` y `get_session_factory()` usan cache
- los tests que cambian entorno o base deben limpiar caches con `clear_settings_cache()` y `clear_database_caches()`

Base por defecto:

- `DATABASE_URL=sqlite+pysqlite:///./decision_engine.db`

## Documentacion Relacionada

- especificacion: `specs/001-project-specification/spec.md`
- plan: `specs/001-project-specification/plan.md`
- tasks: `specs/001-project-specification/tasks.md`
- guia operativa para agentes: `AGENTS.md`
- constitucion del proyecto: `.specify/memory/constitution.md`

## Notas Importantes

- Usa `old-version/api-build.R` como referencia principal cuando necesites comportamiento legacy.
- No reintroducir autenticacion por IP, HTML renderizado por backend ni dependencia runtime de Excel o estructura DOM.
