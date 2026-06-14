# Implementation Plan: Decision Engine MVP

**Branch**: `[no-branch-detected]` | **Date**: 2026-06-11 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-project-specification/spec.md`

**Propagated**: 2026-06-13 — Updated from spec.md refinement

## Summary

Implementar el MVP de `Decision Engine` adoptando la arquitectura de `specs/000-old-specification/docs/DDR.md` como linea base: monolito modular con backend `FastAPI`, frontend `React`, motor deterministico aislado del framework web y un modelo administrable para productos, workflows, variables, parametros, reglas, estrategias de pipeline y perfiles/permisos. El plan prioriza primero habilitar la administracion persistida y gobernada del motor, incluyendo trazabilidad de interacciones AI, y luego completar el flujo operacional `PLD` de punta a punta sin perder la base multiproducto ya iniciada en el repositorio. La decision arquitectonica principal es mantener la separacion entre contratos HTTP por producto y contrato canonico interno del motor, mientras la administracion del motor evoluciona hacia persistencia gobernada y versionada en lugar de registros hardcodeados, incluyendo la gestion operativa de perfiles y permisos.

## Technical Context

**Language/Version**: Python 3.12+ backend, TypeScript 5.x frontend

**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy 2.x, Alembic, React 18, Vite, Vitest

**Storage**: SQLite inicial, filesystem para ZIP, compatibilidad futura con SQL Server

**Testing**: `unittest` en backend, `vitest` en frontend, validacion contractual via OpenAPI y tests de mapeo/flujo

**Target Platform**: Servidor Linux o Windows con backend HTTP y frontend estatico servido detras de reverse proxy

**Project Type**: Web application con backend API, frontend SPA y motor de decisiones embebido

**Performance Goals**: en la validacion de endurecimiento del MVP y con AI deshabilitada, `POST /consultas` debe cumplir `p95 <= 2s` y `POST /evaluaciones` debe cumplir `p95 <= 4s` sobre una suite operativa base reproducible: SQLite local, datos semilla, 5 iteraciones de calentamiento por endpoint y luego 30 consultas validas + 30 evaluaciones validas con concurrencia 1 y payloads deterministas; con AI habilitada, la degradacion aceptable del flujo principal debe seguir permitiendo fallback sin bloquear la operacion.

**Constraints**: motor 100% deterministico; sin edicion directa de workflows activos; productos/workflows/reglas/parametros/pipeline versionados y auditables; sin autenticacion por IP; sin HTML generado por backend; compatibilidad SQLite primero; AI opcional, desacoplada y trazable por modelo/template/payload permitido (subconjunto filtrado no sensible); matriz RBAC verificable para analista, evaluador, auditor, administrador, administrador de negocio, administrador de riesgos y administrador; eliminacion administrativa de productos, workflows y reglas restringida a riesgos salvo borradores `draft` eliminables por negocio; administracion de perfiles y permisos persistida, auditable y de vigencia inmediata como mecanismo operativo, con autorizacion resuelta contra permisos persistidos en cada request protegido y sin depender de matrices hardcodeadas para cambios rutinarios

**Scale/Scope**: un MVP funcional `PLD` con soporte para un segundo producto cercano, multiples workflows por producto, decenas de variables por producto, cientos de reglas por workflow y trazabilidad completa de evaluaciones y solicitudes

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Multiproduct boundaries: PASS. El plan mantiene `product_code` y `workflow_code` como dimensiones de primer nivel y evita consolidar contratos estructurales `PLD` en capas compartidas.
- Deterministic engine isolation: PASS. El motor permanece aislado del borde HTTP, de la UI y de la AI; la AI consume solo salidas estructuradas.
- Versioning and governance: PASS. Productos, workflows, reglas, parametros y estrategias de pipeline usan `draft -> active -> retired`; workflows activos son inmutables y se reemplazan por nuevas versiones.
- Security and audit impacts: PASS. El plan incorpora RBAC administrativo, auditoria append-only y trazabilidad de activaciones, retiros, evaluaciones, exportaciones e interacciones AI.
- AI optionality: PASS. Ningun cambio del motor depende de AI para evaluar o registrar solicitudes.
- Persistence compatibility: PASS. El modelo objetivo sigue siendo compatible con SQLite y prepara migracion futura a SQL Server.

## Project Structure

### Documentation (this feature)

```text
specs/001-project-specification/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── execution-report.md
├── contracts/
│   ├── engine-admin.openapi.yaml
│   └── runtime.openapi.yaml
└── tasks.md
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── api/
│   │   ├── mappers/
│   │   ├── routes/
│   │   └── schemas/
│   ├── application/
│   │   ├── ai/
│   │   ├── engine_admin/
│   │   ├── evaluations/
│   │   ├── credit_requests/
│   │   └── loan_consultations.py
│   ├── domain/
│   │   └── decision_engine/
│   ├── infrastructure/
│   │   ├── db/
│   │   ├── files/
│   │   ├── repositories/
│   │   └── loan_consultations.py
│   ├── security/
│   ├── config/
│   └── main.py
├── alembic/
└── tests/
    ├── contract/
    ├── integration/
    └── existing unittest modules

frontend/
├── src/
│   ├── app/
│   ├── features/
│   │   ├── auth/
│   │   ├── loan-consultations/
│   │   ├── evaluations/
│   │   ├── credit-requests/
│   │   ├── engine-admin/
│   │   └── attachments/
│   ├── components/
│   ├── routes/
│   └── services/
└── tests/
```

**Structure Decision**: Se adopta la estructura web application ya presente en el repositorio. No se separa el motor en microservicio durante el MVP; en su lugar se profundiza el monolito modular propuesto por `specs/000-old-specification/docs/DDR.md`, agregando modulos de aplicacion e infraestructura para administracion del motor, evaluaciones, solicitudes, adjuntos y AI asistiva.

## Implementation Phases

### Phase 0 - Research and baseline decisions

1. Confirmar la adopcion del monolito modular de `specs/000-old-specification/docs/DDR.md` como arquitectura oficial del MVP.
2. Cerrar el patron de contrato doble: contratos HTTP por producto en `api/` y contrato interno generico del motor en `domain/decision_engine/`.
3. Definir el modelo administrativo minimo versionable para productos, workflows, catalogos de variables, parametros, reglas y estrategias de pipeline.
4. Definir eventos minimos de auditoria, snapshot minimo de evidencia para reproducibilidad, matriz RBAC por rol/accion con segregacion de funciones para activaciones criticas, reglas explicitas de eliminacion por rol/estado, administracion persistida de perfiles/permisos con vigencia inmediata y autorizacion reevaluada por request, e interacciones AI trazables por modelo/template/payload.

### Phase 1 - Domain and persistence design

1. Extender el modelo de datos actual con entidades administrativas de motor en vez de seguir hardcodeando runtimes en bootstrap.
2. Definir las relaciones entre producto, workflow, version de workflow, variable, origen de variable, parametro, regla y estrategia de pipeline.
3. Diseñar contratos API canonicos para administracion del motor y para operaciones runtime del MVP.
4. Definir guia quickstart para validar administracion, evaluacion, solicitudes, detalle, exportacion, adjuntos y trazabilidad.

### Phase 2 - Backend implementation slices

1. Slice A: persistencia y repositorios de administracion del motor.
2. Slice B: endpoints administrativos, versionado, activacion gobernada, eliminacion gobernada y RBAC para productos, workflows, variables, parametros, estrategias de pipeline, catalogos, reglas y perfiles/permisos.
3. Slice C: integracion de evaluaciones `PLD` con runtime persistido, autenticacion frontend y `DecisionTrace` real.
4. Slice D: solicitudes de credito, detalle, historial de estado, bandeja, exportacion y adjuntos ZIP.
5. Slice E: AI asistiva fuera del camino critico con fallback verificado y persistencia trazable de interacciones.

### Phase 3 - Frontend MVP flows

1. Login y contexto de usuario.
2. Pantallas admin para productos, workflows, variables, parametros, estrategias de pipeline, catalogos y reglas.
3. Consulta cliente/campana por producto.
4. Evaluacion y explicacion de resultados.
5. Registro de solicitud, detalle, bandeja operativa, exportacion, adjuntos y timeline de auditoria.

### Phase 4 - Validation and hardening

1. Contratos OpenAPI y tests de mapeo por producto.
2. Tests de determinismo, versionado, fallback AI, trazabilidad AI y trazabilidad de versiones efectivas.
3. Validaciones end-to-end del flujo `PLD`, de administracion del motor, exportacion de bandeja y visualizacion de adjuntos ZIP.
4. Validacion de extensibilidad con un segundo producto no hardcodeado.
5. Revision de observabilidad, autorizacion contra la matriz RBAC ampliada y la segregacion de funciones, compatibilidad SQLite, evidencia TDD por slice y objetivos p95 del MVP sobre la suite operativa base canonica.

## Architecture Decisions For This Plan

1. **Adoptar DDR.md como baseline**. La mejor alternativa sigue siendo el monolito modular con motor interno aislado; no hay evidencia en el repo para justificar microservicios ni un BRMS externo en el MVP.
2. **Introducir versionado publicable del workflow**. Un workflow activo no se edita; se crea una nueva version con referencias resueltas a pipeline, reglas y catalogo de variables.
3. **Mantener contratos REST por producto en el borde**. `PLD` puede seguir teniendo contratos transicionales propios, pero el contrato interno del motor permanece generico y canonico.
4. **Versionar catalogos de variables**. Para sostener reproducibilidad, las variables definidas a nivel producto se publican en catalogos versionados consumidos por cada version de workflow.
5. **Versionar parametros como artefacto de primer nivel**. Los parametros del motor no quedan implícitos en reglas o bootstrap; se publican en versiones auditables reutilizables por workflow.
6. **Persistir evidencia minima y bundle de versiones aplicado**. Cada evaluacion debe guardar referencias a `workflow_version`, `variable_catalog_version`, `parameter_set_version`, versiones publicadas de reglas y `pipeline_version`, mas snapshot de los campos realmente consumidos.
7. **Gobernar el pipeline como configuracion administrable**. Estrategias y nodos del pipeline deben versionarse, validarse topologicamente y activarse bajo control separado del runtime.
8. **Trazar cada asistencia AI**. Toda explicacion, resumen o sugerencia AI debe persistir modelo, template, payload permitido, respuesta, fallback y referencias al bundle de versiones del motor.
9. **Usar una sola fuente de verdad de producto**. La tabla persistida de producto del MVP debe servir tanto al runtime del motor como a solicitudes de credito; no se mantendran dos registros paralelos con semantica divergente.
10. **Incluir autenticacion frontend como parte del MVP operativo**. La restauracion de sesion y el acceso por rol se implementan como requisito operativo, no como detalle posterior.
11. **Administrar perfiles y permisos fuera del codigo compartido**. La matriz inicial puede existir como bootstrap tecnico, pero la operacion normal debe resolver altas y bajas de permisos desde un modulo persistido, auditable y de aplicacion inmediata, con reevaluacion de autorizacion en cada request protegido.

## Post-Design Constitution Check

- Multiproduct boundaries: PASS. Los contratos runtime y administrativos propuestos separan identidad de producto, workflow y versiones publicadas.
- Deterministic engine isolation: PASS. La persistencia nueva alimenta el motor, pero no mezcla UI ni HTTP dentro del dominio.
- Versioning and governance: PASS. El diseño formaliza draft/active/retired, versionado inmutable para workflows activos y eliminacion gobernada por rol/estado para productos, workflows y reglas.
- Security and audit impacts: PASS. El plan exige RBAC por accion, restricciones explicitas de eliminacion administrativa, administracion persistida de perfiles/permisos con vigencia inmediata, reevaluacion de autorizacion por request y eventos auditables para todas las operaciones administrativas clave y para interacciones AI relevantes.
- AI optionality: PASS. La fase AI queda desacoplada y posterior al flujo critico.
- Persistence compatibility: PASS. El diseño se apoya en tablas relacionales simples y payloads serializados compatibles con SQLite.

## Complexity Tracking

No constitution violations identified.
