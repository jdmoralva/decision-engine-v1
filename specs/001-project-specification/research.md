# Research - Decision Engine MVP

## Decision 1: Adoptar la arquitectura de `specs/000-old-specification/docs/DDR.md` como baseline del MVP

- Decision: Mantener un monolito modular con frontend desacoplado, backend `FastAPI`, motor deterministico interno, persistencia relacional y AI asistiva fuera del camino critico.
- Rationale: El repositorio ya tiene bootstrap backend/frontend, un core de motor aislado y contratos REST iniciales. Separar a microservicios ahora agregaria complejidad operativa sin resolver ningun cuello de botella real del MVP.
- Alternatives considered:
  - Microservicios por dominio: descartado por sobrecosto y porque el equipo aun necesita converger contratos, persistencia y trazabilidad base.
  - Monolito sin limites internos: descartado por repetir el acoplamiento del legacy.

## Decision 2: Separar contrato HTTP por producto del contrato canonico interno del motor

- Decision: Mantener request/response HTTP especificos por producto en `api/schemas`, pero traducirlos con mappers a un contrato interno generico del motor resuelto por `product_code` y `workflow_code`.
- Rationale: El repo ya tiene esta direccion parcialmente implementada y `specs/000-old-specification/docs/DDR.md` la define como convergencia objetivo. Esto permite que `PLD` siga funcionando como contrato transicional sin contaminar el core multiproducto.
- Alternatives considered:
  - Un unico contrato REST universal desde ya: descartado porque `PLD` aun tiene payload y resultado especificos.
  - Contratos PLD hardcodeados tambien en el motor: descartado por romper la extensibilidad inmediata.

## Decision 3: Modelar administracion del motor con identidades estables y versiones publicables

- Decision: Usar identidades estables para producto y workflow, y versiones publicables e inmutables para workflow, pipeline, catalogo de variables y reglas activas.
- Rationale: La reproducibilidad exige que una evaluacion siempre pueda reconstruirse contra el mismo bundle de configuracion. Editar configuraciones activas en sitio rompe trazabilidad y contradice la spec aclarada.
- Alternatives considered:
  - Filas mutables con bandera `is_active`: descartado por riesgo de drift historico.
  - Una sola version opaca que mezcle variables, reglas y pipeline: descartado porque dificulta auditoria fina y reutilizacion.

## Decision 4: Publicar catalogos de variables por producto y vincularlos a workflows

- Decision: Definir variables en el nivel producto y publicar catalogos versionados que luego son seleccionados por cada version de workflow.
- Rationale: La spec ya fijo que las variables pertenecen al producto y que cada workflow reutiliza un subconjunto. Versionar el catalogo evita que cambios posteriores alteren evaluaciones previas.
- Alternatives considered:
  - Variables solo por workflow: descartado por duplicacion y peor gobierno.
  - Variables globales de plataforma: descartado porque la semantica y origen dependen del producto.

## Decision 5: Capturar origen permitido de variable como regla de configuracion administrable

- Decision: Cada variable declara si acepta datos desde `campaign_db`, `user_input` o ambos, y la evaluacion valida esta politica antes de ejecutar el motor.
- Rationale: La procedencia del dato afecta reglas, evidencia y auditoria. Debe ser una restriccion declarativa y no una convencion implicita del formulario o de una consulta ad hoc.
- Alternatives considered:
  - Decidir el origen libremente en cada evaluacion: descartado por ambiguedad y riesgo de inconsistencia.
  - Forzar una sola fuente para todas las variables: descartado porque no cubre el flujo real del MVP.

## Decision 6: Registrar eventos minimos de auditoria para administracion y runtime

- Decision: Registrar eventos append-only para crear, activar, retirar y versionar productos, workflows, reglas y pipelines, ademas de ejecutar evaluaciones, registrar solicitudes y operar adjuntos.
- Rationale: La spec y `specs/000-old-specification/docs/DDR.md` exigen trazabilidad completa. Los eventos permiten reconstruir quien cambio que, cuando y bajo que version opero una evaluacion o solicitud.
- Alternatives considered:
  - Auditar solo tablas finales: descartado por perder la secuencia de activacion y reemplazo.
  - Auditar solo runtime operativo: descartado porque deja ciegas las decisiones administrativas.

## Decision 7: Mantener AI asistiva como consumidor opcional de `DecisionTrace`

- Decision: La AI no interviene en la evaluacion deterministica ni en el registro de solicitudes; consume `DecisionTrace` y datos permitidos para explicar, resumir y sugerir.
- Rationale: Esta separacion ya esta documentada en el repo y minimiza impacto de fallas AI sobre el flujo principal.
- Alternatives considered:
  - AI inline durante la decision: descartado por riesgo funcional y auditabilidad deficiente.
  - Posponer toda AI fuera del MVP: descartado porque el alcance actual si la incluye como capacidad asistiva.
