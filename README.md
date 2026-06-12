# Decision Engine

## Resumen Ejecutivo

Este repositorio contiene la planificacion y la base documental para construir una nueva version de `Decision Engine`, una plataforma "AI-Powered" de gestion y decision para productos de prestamo.

El objetivo es reemplazar la solucion legacy de `old-version/`, un monolito en `R + Plumber + HTML/jQuery`, por una arquitectura moderna con:

- backend en Python (FastAPI + Pydantic v2)
- persistencia inicial en SQLite con opcion de migracion a SQL Server
- frontend web desacoplado (Vite + React + TypeScript, servido como assets estaticos)
- autenticacion y autorizacion modernas (RBAC)
- motor de decisiones deterministico aislado de la UI y del framework web
- pipeline de etapas intercambiables (Preprocessing, Eligibility, Scoring, Decision Strategy, Post-processing)
- event sourcing inmutable para trazabilidad total de decisiones
- BRMS (Business Rules Management System) con versionado, simulacion y UI administrativa
- capa AI asistiva para explicacion de evaluaciones, resumen de casos y sugerencias de accion

`PLD` significa `Prestamo de Libre Disponibilidad` y constituye el primer producto del MVP.
La arquitectura objetivo esta disenada para soportar otros tipos de prestamo en el futuro sin rehacer la plataforma base. El modulo de `Cobranzas` presente en `old-version/` queda fuera de alcance salvo instruccion explicita.

## Estado Actual

La raiz del repositorio ya contiene la base tecnica nueva del MVP.
El estado real es:

- `old-version/` conserva la referencia funcional y tecnica del sistema legacy
- `backend/` ya contiene el bootstrap FastAPI, configuracion, autenticacion base, RBAC inicial, ORM, migraciones, contratos API iniciales y el modulo aislado base del motor de decisiones
- `frontend/` ya contiene el bootstrap `Vite + React + TypeScript` con arranque local y sesion basica

## Estado de Implementacion

- Backend FastAPI base operativo con `GET /api/v1/health`, autenticacion temporal y RBAC base del MVP
- Modelo de datos inicial definido en SQLAlchemy y validado con migraciones Alembic
- Contratos REST iniciales publicados en OpenAPI para `evaluations`, `credit-requests` y `decision-trace`
- Modulo `backend/app/domain/decision_engine/` implementado como core aislado del motor con contratos internos, normalizacion, pipeline por nodos, branching controlado, validacion de ciclos y registry multiproducto
- Adaptadores finos entre la API REST y el contrato interno del motor implementados en `backend/app/api/mappers/evaluations.py`
- Servicio base de conexion a LLM implementado con proveedor activo configurable entre `OpenAI` y `Gemini`, carga de claves desde entorno o `.env`, timeout y reintentos
- Frontend bootstrap operativo con login local y restauracion basica de sesion

## Referencias Clave

- Especificacion: `specs/001-project-specification/spec.md`
- Planificación: `specs/001-project-specification/plan.md`
- Tasks: `specs/001-project-specification/tasks.md`
- Guia operativa para agentes: `AGENTS.md`
- Sistema legacy de referencia: `old-version/`

## Arranque Rapido Local

Backend desde la raiz:

```bash
.venv\Scripts\python -m uvicorn backend.app.main:app --reload
```

Frontend desde `frontend/`:

```bash
npm install
npm run dev
```

URLs locales:

- Frontend: `http://127.0.0.1:5173/`
- Swagger backend: `http://127.0.0.1:8000/docs`

