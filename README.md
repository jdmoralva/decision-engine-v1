# Decision Engine

## Resumen Ejecutivo

Este repositorio contiene la planificacion y la base documental para construir una nueva version de `Decision Engine`, una plataforma "AI-Powered" de gestion y decision para productos de prestamo.

El objetivo es reemplazar la solucion legacy de `old-version/`, un monolito en `R + Plumber + HTML/jQuery`, por una arquitectura moderna con:

- backend en Python (FastAPI + Pydantic v2)
- persistencia inicial en SQLite con opcion de migracion a SQL Server
- frontend web desacoplado (React + TypeScript + Vite)
- autenticacion y autorizacion modernas (RBAC)
- motor de decisiones deterministico aislado de la UI y del framework web
- pipeline de etapas intercambiables (Preprocessing, Eligibility, Scoring, Decision Strategy, Post-processing)
- event sourcing inmutable para trazabilidad total de decisiones
- BRMS (Business Rules Management System) con versionado, simulacion y UI administrativa
- capa AI asistiva para explicacion de evaluaciones, resumen de casos y sugerencias de accion

`PLD` significa `Prestamo de Libre Disponibilidad` y constituye el primer producto del MVP.
La arquitectura objetivo esta disenada para soportar otros tipos de prestamo en el futuro sin rehacer la plataforma base. El modulo de `Cobranzas` presente en `old-version/` queda fuera de alcance salvo instruccion explicita.

## Estado Actual

Hoy la raiz del repositorio no contiene todavia la implementacion nueva.
El estado real es:

- `old-version/` conserva la referencia funcional y tecnica del sistema legacy
- `SPEC.md` define la especificacion tecnica completa: arquitectura (pipeline de etapas, event sourcing, BRMS, AI), modelo de datos, API, entorno de desarrollo (versiones exactas, dependencias) y roadmap por fases
- `docs/project/BACKLOG.md` organiza el trabajo en 14 epicas (E1-E14) con tareas ejecutables, prioridades y dependencias
- `docs/project/ISSUES.md` descompone el backlog en 34 issues operativos asignados a sprints
- `docs/project/SPRINTS.md` secuencia la ejecucion en 7 sprints (Sprint 1-7), desde descubrimiento hasta BRMS y UI administrativa
- `docs/analysis/` reservado para levantamiento funcional y analisis del legado
- `docs/sessions/SESSIONS.md` guarda referencias cortas de sesiones previas
- `AGENTS.md` resume las restricciones y fuentes de verdad para futuras sesiones

Decisiones funcionales ya cerradas:
- El flujo de carga y descarga de archivos ZIP se **incluye** en el alcance del MVP
- La migracion de historicos queda **descartada**; se inicia con base limpia
- Los roles operativos (analista, evaluador, supervisor, admin) seran definidos con matriz de permisos en ISSUE-001
- Las reglas de aprobacion y rechazo posteriores al registro seran documentadas en ISSUE-001
- Sin pendientes funcionales abiertos en este momento

El proyecto se encuentra en fase de definicion y preparacion tecnica, listo para iniciar el Sprint 1.

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

- Especificacion: `SPEC.md`
- Backlog: `docs/project/BACKLOG.md`
- Issues: `docs/project/ISSUES.md`
- Sprints: `docs/project/SPRINTS.md`
- Analisis funcional: `docs/analysis/`
- Registro de sesiones: `docs/sessions/SESSIONS.md`
- Guia operativa para agentes: `AGENTS.md`
- Sistema legacy de referencia: `old-version/`

## Siguiente Paso Pendiente

El siguiente paso prioritario es iniciar `Sprint 1`, comenzando por:

- `ISSUE-001` Cerrar alcance funcional del MVP, incluyendo roles operativos y reglas de aprobacion/rechazo

Sin ese cierre, los issues tecnicos posteriores del MVP pueden quedar bloqueados.
