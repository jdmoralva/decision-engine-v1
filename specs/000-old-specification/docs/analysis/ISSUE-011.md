# ISSUE-011 - Implementar reglas y formulas PLD sobre motor multiproducto

## 1. Objetivo

Documentar el enfoque tecnico consolidado de `ISSUE-011`: implementar las reglas y formulas de `PLD` sobre un motor cuyo core permanezca agnostico al producto.

Este documento ya no reemplaza a `docs/SPEC.md`, `docs/DDR.md` ni a `docs/project/ISSUES.md`. Su funcion es preservar el detalle tecnico de diseno que sigue siendo util para implementar y validar `ISSUE-011`.

## 2. Decision central

`ISSUE-011` no debe interpretarse como la construccion de un `motor solo para PLD`.

La decision consolidada es:

- el core del motor permanece agnostico al producto
- los productos se registran por `product_code`
- cada producto puede definir uno o mas `workflow_code`
- cada workflow define sus variables, reglas, metricas y branching permitido
- `PLD` es el primer producto registrado, no la forma estructural del motor completo

## 3. Problema que se evita

Si `ISSUE-011` se implementa de forma literal y estrecha, existe el riesgo de hardcodear conceptos de `PLD` como `RCI`, `oferta`, `cuota`, `tasa`, `plazo` o `segmento` dentro del core del motor.

Este issue debe evitar ese resultado. Dichas metricas pertenecen al runtime del producto o workflow y no al contrato universal del motor.

## 4. Alcance efectivo del issue

`ISSUE-011` se limita al comportamiento del motor de evaluacion.

Incluye:

- reglas de elegibilidad
- derivacion de variables por workflow
- metricas opcionales del runtime `PLD`
- alertas y bloqueos relacionados con evaluacion
- versionado aplicado a la ejecucion
- `DecisionTrace`

Excluye:

- reglas de creacion de solicitud
- logica de bandeja operativa
- adjuntos
- generacion AI
- UI administrativa
- un DSL completo de reglas
- ejecucion runtime directa desde `rule_sets` o `rule_versions` persistidos en BD en esta fase

Quedan explicitamente fuera de `ISSUE-011` y del motor de evaluacion en esta fase:

- comentario obligatorio
- una solicitud por periodo
- monto solicitado mayor que la oferta

Estas reglas pertenecen al flujo de registro de solicitud y deben tratarse en issues posteriores.

## 5. Principios de diseno

1. El core del motor debe permanecer agnostico al producto.
2. Los productos deben registrarse, no hardcodearse en el contrato del core.
3. Los workflows son ciudadanos de primera clase y pueden variar dentro de un mismo producto.
4. Las variables definen que pueden consumir y producir las reglas.
5. Las metricas son capacidades opcionales de un producto o workflow, no campos universales del motor.
6. El versionado y la trazabilidad son obligatorios desde el primer modelo ejecutable.
7. En esta fase se prefiere configuracion estructurada en codigo sobre un runtime BRMS completo.

## 6. Modelo conceptual preservado

Las siguientes entidades conceptuales siguen siendo utiles para entender y validar la implementacion:

- `ProductDefinition`: producto registrado en el motor
- `WorkflowDefinition`: workflow ejecutable dentro de un producto
- `VariableDefinition`: variable declarada y validada por workflow
- `RuleDefinition`: regla estructurada con metadata explicita
- `ProductRuntime`: runtime compilado para una combinacion de producto y workflow

Campos conceptuales minimos relevantes:

- `ProductDefinition`: `product_code`, `name`, `is_active`, `supported_workflows`
- `WorkflowDefinition`: `workflow_code`, `product_code`, `name`, `description`, `pipeline_version`, `rule_pack_version`
- `VariableDefinition`: `variable_key`, `variable_kind`, `data_type`, `required`, `allowed_in_rules`, `persist_in_evidence`
- `RuleDefinition`: `rule_code`, `rule_type`, `product_code`, `workflow_code`, `consumes_variables`, `produces_variable` o `produces_effect`, `priority`, `version`
- `ProductRuntime`: estrategia de pipeline, nodos, catalogo de variables, reglas activas, proyeccion de salida y versiones aplicadas

## 7. Resolucion de runtime

La ejecucion debe resolverse por:

- `product_code`
- `workflow_code`
- conjunto de versiones resuelto

Flujo esperado:

1. Se resuelve el producto.
2. Se resuelve el workflow dentro del alcance del producto.
3. Se compila o carga el runtime del producto.
4. El runtime provee pipeline, nodos, versiones, catalogo de variables y reglas.
5. El orquestador del core ejecuta el runtime.
6. `DecisionTrace` captura workflow, nodos, evidencia, versiones, alertas, bloqueos y resultado final.

## 8. Variables y metricas opcionales

Las siguientes metricas no deben tratarse como salidas universales del motor:

- `segmento`
- `RCI`
- `oferta`
- `cuota`
- `tasa`
- `plazo`
- `ingreso_revisado`

Esto implica que:

- `PLD` puede producir `RCI`, `offered_amount`, `installment_amount`, `rate`, `term_months`
- otro producto puede producir `ltv`, `grace_period`, `coverage_ratio` u otras metricas
- el motor sigue siendo valido incluso cuando un workflow no produce valores equivalentes a PLD

Las reglas solo pueden referenciar variables declaradas en el catalogo activo del workflow.

## 9. Reglas en esta fase

Las reglas de `ISSUE-011` se implementan como definiciones estructuradas en codigo, no como texto libre ni como un DSL interpretado.

Esta fase elige intencionalmente:

- reglas deterministicas basadas en codigo
- metadata explicita por regla
- validacion en compilacion o arranque contra las definiciones de variables

Esta fase no elige todavia:

- expresiones runtime arbitrarias leidas desde texto en BD
- ejecucion de reglas completamente autorada por usuarios
- edicion dinamica desde UI administrativa

## 10. Versionado y trazabilidad

Cada ejecucion debe resolver y preservar:

- `product_code`
- `workflow_code`
- `rule_set_version`
- `parameter_version`
- `pipeline_version`
- timestamp de ejecucion
- actor que ejecuta

`DecisionTrace` debe registrar al menos:

- workflow ejecutado
- nodos ejecutados
- reglas aplicadas o efectos producidos
- variables consumidas cuando sean materiales para la decision
- variables derivadas cuando sean materiales para la decision
- alertas agregadas
- bloqueos agregados
- resultado final

Esto mantiene compatibilidad posterior con persistencia, explicacion AI, auditoria humana, replay y debugging.

## 11. Modelo de errores

La implementacion debe fallar temprano y de forma explicita ante configuraciones multiproducto invalidas.

Categorias conceptuales requeridas:

- producto desconocido
- workflow desconocido para un producto conocido
- variable desconocida referenciada por una regla
- definicion de regla invalida
- variable producida invalida
- topologia de workflow invalida
- version runtime no resoluble
- inputs requeridos faltantes para el workflow

Nombres ilustrativos utiles:

- `UnknownProductError`
- `UnknownWorkflowError`
- `UnknownVariableError`
- `InvalidRuleDefinitionError`
- `InvalidWorkflowTopologyError`
- `RuntimeResolutionError`

## 12. PLD como primer producto registrado

La frontera importante que debe preservarse es:

- `PLD` es el primer runtime concreto que usa la infraestructura
- `PLD` no es la forma del core del motor

Este issue debe probar la arquitectura registrando `PLD`, no haciendo que el motor sea sinonimo de `PLD`.

## 13. Plan tecnico en dos cortes

### Corte 1 - Infraestructura multiproducto + PLD registrado

Objetivo:

- establecer la base multiproducto del motor
- registrar `PLD` como primer producto
- validar la infraestructura de workflows, variables y reglas

Entregables esperados:

- modelo de registro de productos
- modelo de registro de workflows
- modelo de catalogo de variables
- definiciones estructuradas de reglas en codigo
- resolucion de runtime por producto y workflow
- `PLD` registrado como primer runtime
- propagacion de versiones hacia el resultado de ejecucion y la traza

### Corte 2 - Reglas reales de evaluacion PLD sobre la infraestructura

Objetivo:

- implementar las primeras reglas reales de evaluacion de `PLD` sobre la base multiproducto
- preparar un handoff estable hacia `ISSUE-012` y `ISSUE-014`

Entregables esperados:

- reglas de derivacion de variables de `PLD`
- reglas de elegibilidad de `PLD`
- reglas de calculo de metricas opcionales de `PLD`
- alertas y bloqueos de evaluacion de `PLD`
- refinamiento de la evidencia de `DecisionTrace`
- contrato estable de `product_result` para `PLD`

Este segundo corte sigue excluyendo reglas de registro de solicitud.

## 14. Estrategia de pruebas

Las pruebas se dividen en cuatro capas.

### 14.1 Pruebas de registry

- el registro de productos funciona
- el registro de workflows funciona
- la resolucion de runtime funciona para producto y workflow conocidos
- la resolucion de runtime falla correctamente para producto y workflow desconocidos

### 14.2 Pruebas de variables y definicion de reglas

- las variables se validan por producto y workflow
- las reglas solo pueden consumir variables declaradas
- las reglas solo pueden producir salidas o efectos declarados
- las definiciones invalidas de reglas fallan temprano

### 14.3 Pruebas de ejecucion runtime

- el workflow ejecuta el runtime correcto
- las metricas opcionales solo se producen cuando estan configuradas
- productos no-PLD siguen siendo validos sin metricas de PLD
- las versiones se propagan a `DecisionTrace` y al resultado

### 14.4 Pruebas del primer producto `PLD`

- `PLD` se resuelve correctamente como producto registrado
- los workflows de `PLD` se ejecutan a traves de la infraestructura generica
- las reglas de `PLD` producen salidas de evaluacion esperadas
- la traza de `PLD` permanece auditable y versionada

## 15. Riesgos y mitigacion

Riesgos principales:

- sobredisenar un BRMS completo demasiado pronto
- filtrar supuestos de `PLD` dentro del core del motor
- volver la estructura de reglas demasiado generica y perder claridad
- acoplar demasiado el comportamiento runtime a los contratos REST actuales
- mezclar reglas de evaluacion con reglas de registro de solicitud

Mitigacion:

- mantener reglas estructuradas en codigo en esta fase
- mantener el core generico y agnostico al producto
- mantener los workflows como pieza de primera clase
- mantener `product_result` flexible
- mantener fuera de alcance las reglas de registro de solicitud

## 16. Resultado esperado

Al cerrar `ISSUE-011`, el proyecto debe tener:

- una base multiproducto para el motor de decisiones
- productos registrables por `product_code`
- workflows registrables dentro de cada producto
- ejecucion de reglas acotada por variables
- metricas opcionales por producto y workflow
- ejecucion trazable y versionada
- `PLD` registrado como primer producto concreto

Todavia no debe tener un BRMS administrativo completo, pero si debe dejar un camino arquitectonico limpio hacia el mismo.
