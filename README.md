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
- `docs/SPEC.md` define la especificacion tecnica del proyecto: arquitectura (pipeline de etapas, event sourcing, BRMS, AI), modelo de datos, API, lineamientos de stack y roadmap por fases
- `docs/project/BACKLOG.md` organiza el trabajo en 14 epicas (E1-E14) con tareas ejecutables, prioridades y dependencias
- `docs/project/ISSUES.md` descompone el backlog en 40 issues operativos asignados a sprints
- `docs/project/SPRINTS.md` secuencia la ejecucion en 7 sprints (Sprint 1-7), desde descubrimiento hasta cierre del MVP con BRMS, pipeline configurable y UI administrativa
- `backend/` ya contiene el bootstrap FastAPI, configuracion, autenticacion base, RBAC inicial, ORM, migraciones y contratos API iniciales
- `frontend/` ya contiene el bootstrap `Vite + React + TypeScript` con arranque local y sesion basica
- `docs/analysis/` contiene los cierres funcionales y tecnicos de los issues priorizados
- `docs/sessions/SESSIONS.md` guarda referencias cortas de sesiones previas
- `AGENTS.md` resume las restricciones y fuentes de verdad para futuras sesiones

Decisiones funcionales ya cerradas:
- El frontend del MVP se implementa con `Vite + React + TypeScript` y se despliega como assets estaticos compatibles con un reverse proxy o Nginx equivalente
- El flujo de carga y descarga de archivos ZIP se **incluye** en el alcance del MVP
- La migracion de historicos queda **descartada**; se inicia con base limpia
- El MVP mantiene las capacidades AI asistivas definidas en `docs/SPEC.md`
- `Event Store`, `BRMS`, `pipeline configurable` y `UI administrativa de reglas` forman parte del MVP
- El almacenamiento inicial de archivos ZIP se implementara sobre `filesystem`
- Los snapshots de evaluacion persistiran solo los campos efectivamente consumidos por el motor

El proyecto ya cerró la decision de frontend y parte del bootstrap tecnico.
`Sprint 1` consolido la base de contratos, estructura y stack inicial; aun quedan por completar los flujos funcionales del MVP.

## Estado de Implementacion

- Backend FastAPI base operativo con `GET /api/v1/health`, autenticacion temporal y RBAC inicial
- Modelo de datos inicial definido en SQLAlchemy y validado con migraciones Alembic
- Contratos REST iniciales publicados en OpenAPI para `evaluations`, `credit-requests` y `decision-trace`
- Frontend bootstrap operativo con login local y restauracion basica de sesion
- La logica de negocio PLD completa, la bandeja operativa, el registro real de solicitudes y las evaluaciones aun no estan implementadas

## Arquitectura del Motor de Decisiones

```
Input → [Preprocessing] → [Eligibility] → [Scoring Layer] → [Decision Strategy] → [Post-processing] → Output
         ↑                                                            ↓
         └────────────── Event Store (inmutable) ──────────────────────┘
                        ↓
         [AI Layer] → Explicacion asistiva + sugerencias
                        ↓
         [BRMS] → Reglas versionadas en BD + UI Administrativa
```

## Referencias Clave

- Especificacion: `docs/SPEC.md`
- Backlog: `docs/project/BACKLOG.md`
- Issues: `docs/project/ISSUES.md`
- Sprints: `docs/project/SPRINTS.md`
- Analisis funcional: `docs/analysis/`
- Registro de sesiones: `docs/sessions/SESSIONS.md`
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

## Siguiente Paso Pendiente

El siguiente paso prioritario es continuar con los issues funcionales del MVP, comenzando por:

- `ISSUE-010` Crear modulo aislado del motor de decisiones
- `ISSUE-011` Implementar reglas y formulas del motor PLD
- `ISSUE-013` Implementar API de consulta PLD
- `ISSUE-014` Implementar API de evaluacion PLD

Sin ese avance, los flujos funcionales del MVP siguen incompletos aunque el bootstrap tecnico ya este listo.
