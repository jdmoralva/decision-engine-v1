# Decision Engine PLD

## Resumen Ejecutivo

Este repositorio contiene la planificacion y la base documental para construir una nueva version del sistema de `PLD / solicitudes de credito`.

El objetivo es reemplazar la solucion legacy de `old-version/`, implementada como un monolito en `R + Plumber + HTML/jQuery`, por una arquitectura moderna con:

- backend en Python
- persistencia inicial en SQLite con opcion de migracion a SQL Server
- frontend web desacoplado
- autenticacion y autorizacion modernas
- motor de decisiones aislado de la UI y del framework web

El alcance actual del nuevo proyecto cubre solo el flujo `PLD / solicitudes de credito`.
El modulo de `Cobranzas` presente en `old-version/` queda fuera de alcance salvo instruccion explicita.

## Estado Actual

Hoy la raiz del repositorio no contiene todavia la implementacion nueva.
El estado real es:

- `old-version/` conserva la referencia funcional y tecnica del sistema legacy
- `SPEC.md` define la especificacion tecnica del nuevo sistema
- `docs/project/BACKLOG.md` traduce la especificacion a trabajo ejecutable
- `docs/project/ISSUES.md` organiza el backlog en issues operativos
- `docs/project/SPRINTS.md` propone la secuencia de ejecucion del MVP
- `docs/analysis/` queda reservado para levantamiento funcional y analisis del legado
- `docs/sessions/SESSIONS.md` guarda referencias cortas de sesiones previas
- `AGENTS.md` resume las restricciones y fuentes de verdad para futuras sesiones

En otras palabras, el proyecto esta en fase de definicion y preparacion tecnica, no de desarrollo implementado aun.

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

Segun el backlog y la planificacion actual, el siguiente paso prioritario es iniciar `Sprint 1` en `docs/project/SPRINTS.md`, comenzando por:

- `ISSUE-001` Cerrar alcance funcional del MVP en `docs/project/ISSUES.md`

Ese issue debe consolidar:

- el mapa completo del flujo PLD legado
- el catalogo de reglas de negocio observadas
- la resolucion de decisiones abiertas del SPEC, especialmente autenticacion, frontend, ZIP e historicos

Sin ese cierre, los issues tecnicos posteriores del MVP pueden quedar bloqueados.
