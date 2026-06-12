# ISSUES - Decision Engine

## Proposito

Este archivo convierte `BACKLOG.md` en una estructura de issues lista para gestion operativa. Cada issue agrupa una unidad de trabajo entregable, manteniendo trazabilidad con el backlog del MVP PLD y con la base multiproducto ya iniciada en la implementacion.

## Convenciones

- Estado inicial sugerido: `todo`
- Prioridad: `P0`, `P1`, `P2`, `P3`
- Sprint: referencia a `SPRINTS.md`
- Dependencias: issues que deben cerrarse antes

---

## ISSUE-001 - Cerrar alcance funcional del MVP

- Tipo: Discovery
- Prioridad: `P0`
- Sprint sugerido: `Sprint 1`
- Backlog origen: `E1-T1`, `E1-T2`, `E1-T3`, `E1-T3a`, `E1-T7`, `E1-T6b`, `E1-T6c`, `E1-T6d`
- Dependencias: ninguna

### Objetivo

Cerrar el alcance real del MVP PLD, consolidando flujo actual, reglas observadas, decisiones abiertas, gobierno del flujo configurable y separacion entre capacidades propias de PLD y capacidades compartidas de plataforma.

### Entregables

- mapa del flujo PLD legacy
- catalogo de reglas de negocio observadas
- definicion de roles operativos y reglas de aprobacion/rechazo
- decision abierta de frontend segun despliegue
- contratos de inputs externos y snapshot minimo
- criterio de fuente oficial de reglas
- decision de gobierno del flujo configurable y horizonte del segundo producto

### Criterios de aceptacion

- existe un mapa del flujo completo de consulta, evaluacion, solicitud, bandeja, anulacion y cambio de estado
- existe un catalogo de reglas con nombre, condicion, entradas, salidas y efecto
- quedan resueltas las decisiones sobre autenticacion, frontend segun despliegue, despliegue del motor, fuente oficial de reglas y lineamientos corporativos relevantes
- queda resuelto el gobierno del flujo configurable y la expectativa de un segundo producto al finalizar el MVP
- queda explicita la separacion entre capacidades exclusivas de PLD y capacidades compartidas
- quedan definidos los roles operativos y las reglas de aprobacion/rechazo posteriores al registro

---

## ISSUE-002 - Definir contratos iniciales del dominio y API

- Tipo: Analysis / Design
- Prioridad: `P0`
- Sprint sugerido: `Sprint 1`
- Backlog origen: `E1-T4`, `E1-T5`, `E1-T5a`, `E1-T5b`, `E1-T5c`, `E1-T6`, `E1-T6b`, `E1-T6c`
- Dependencias: `ISSUE-001`

### Objetivo

Definir los contratos de consulta, evaluacion, traza de evaluacion, registro, cambio de estado, inputs externos y snapshot minimo desacoplados de la UI.

### Entregables

- payload de consulta PLD
- payload de evaluacion
- payload de `DecisionTrace`
- payload de registro de solicitud
- payload de cambio de estado
- contratos de inputs externos para cliente, campanas y deuda
- criterios de snapshot minimo por evaluacion
- contratos de error estructurados
- documentacion OpenAPI de los contratos

### Criterios de aceptacion

- contratos documentados con campos, tipos, validaciones y errores esperados
- contratos no dependen de posiciones de tabla ni de HTML
- contratos son consistentes con el modelo de datos objetivo
- los contratos quedan documentados en OpenAPI
- queda explicito que solo se persisten como snapshot los campos efectivamente consumidos por el motor
- queda definido el contrato de traza consumible por AI y auditoria humana

---

## ISSUE-003 - Bootstrap del repositorio y estructura base

- Tipo: Platform
- Prioridad: `P0`
- Sprint sugerido: `Sprint 1`
- Backlog origen: `E2-T1`
- Dependencias: `ISSUE-001`

### Objetivo

Crear la estructura base del proyecto nuevo separando backend, frontend y documentacion.

### Entregables

- estructura `backend/app/{api,application,domain,infrastructure,security,config}/main.py`
- estructura `frontend/src/{app,features,components,services,routes}`
- carpetas `backend/`, `frontend/`, `docs/`
- archivos base del repositorio
- convenciones minimas documentadas

### Criterios de aceptacion

- la estructura en `backend/` y `frontend/` sigue el arbol definido en SPEC §3.5
- la separacion entre nuevo sistema y `old-version/` es explicita

---

## ISSUE-004 - Inicializar backend con FastAPI

- Tipo: Backend
- Prioridad: `P0`
- Sprint sugerido: `Sprint 1`
- Backlog origen: `E2-T2`, `E2-T5`
- Dependencias: `ISSUE-003`

### Objetivo

Levantar el backend base con FastAPI, configuracion por entorno y endpoint de salud.

### Entregables

- proyecto FastAPI funcional
- configuracion base por entorno
- endpoint `health`
- archivo `pyproject.toml` base

### Criterios de aceptacion

- el backend levanta localmente
- el endpoint `health` responde correctamente
- existe estructura base para configuracion por entorno
- `ruff` queda integrado desde la inicializacion

---

## ISSUE-005 - Seleccionar e inicializar frontend web segun estrategia de despliegue

- Tipo: Frontend / Architecture
- Prioridad: `P0`
- Sprint sugerido: `Sprint 1`
- Backlog origen: `E2-T3`
- Dependencias: `ISSUE-001`, `ISSUE-003`

### Objetivo

Comparar opciones tecnicas de frontend segun despliegue y dejar inicializado el stack elegido para el MVP.

### Entregables

- comparativa tecnica de opciones de frontend y despliegue
- decision documentada del stack elegido
- app frontend inicial
- pagina base funcional
- configuracion de arranque local

### Criterios de aceptacion

- el stack elegido queda justificado segun despliegue previsto
- existe una base ejecutable del frontend seleccionado
- el stack no compromete la separacion entre UI, backend y motor

---

## ISSUE-006 - Diseñar modelo de datos inicial

- Tipo: Data Design
- Prioridad: `P0`
- Sprint sugerido: `Sprint 1`
- Backlog origen: `E3-T1`, `E3-T1a`, `E3-T5`, `E3-T5a`, `E3-T6`
- Dependencias: `ISSUE-002`

### Objetivo

Definir el esquema base de persistencia del MVP, incluyendo parametros del motor, configuracion de pipeline, `DecisionTrace` y snapshot minimo de inputs externos.

### Entregables

- modelo relacional inicial
- entidades principales del MVP
- diseno de versionado de parametros
- diseno de versionado de pipeline y trazas de decision
- mapeo del Excel a estructuras persistentes
- soporte base para clasificacion por producto
- snapshot minimo de inputs externos consumidos por el motor

### Criterios de aceptacion

- existe documento o diagrama de tablas y relaciones
- existe mapeo de `ParametrosPLD-v3.xlsx` a tablas nuevas
- el modelo evita dependencias innecesarias del motor de base de datos
- el esquema deja trazabilidad de los inputs externos efectivamente utilizados en cada evaluacion
- el esquema contempla `pipeline_strategies`, `pipeline_nodes` y `decision_traces`

---

## ISSUE-007 - Implementar ORM y migracion inicial

- Tipo: Backend / Data
- Prioridad: `P0`
- Sprint sugerido: `Sprint 2`
- Backlog origen: `E3-T2`, `E3-T3`
- Dependencias: `ISSUE-004`, `ISSUE-006`

### Objetivo

Implementar el modelo en SQLAlchemy y habilitar migraciones con Alembic.

### Entregables

- modelos SQLAlchemy iniciales
- configuracion Alembic
- migracion inicial funcional

### Criterios de aceptacion

- la base SQLite se crea desde cero con migraciones
- los modelos reflejan el diseno aprobado

---

## ISSUE-008 - Definir e implementar autenticacion base

- Tipo: Security
- Prioridad: `P0`
- Sprint sugerido: `Sprint 2`
- Backlog origen: `E4-T1`, `E4-T2`
- Dependencias: `ISSUE-001`, `ISSUE-004`, `ISSUE-007`

### Objetivo

Seleccionar e implementar el mecanismo inicial de autenticacion.

### Entregables

- decision de autenticacion documentada
- implementacion backend de autenticacion
- identificacion consistente del usuario actual

### Criterios de aceptacion

- el backend identifica al usuario autenticado
- el mecanismo elegido queda documentado y operativo

---

## ISSUE-009 - Definir permisos e implementar RBAC

- Tipo: Security
- Prioridad: `P0`
- Sprint sugerido: `Sprint 2`
- Backlog origen: `E4-T4`, `E4-T5`
- Dependencias: `ISSUE-008`

### Objetivo

Definir la matriz de permisos del sistema e implementarla en backend.

### Entregables

- matriz de roles y permisos
- dependencias o middleware de autorizacion
- proteccion de endpoints por rol

### Criterios de aceptacion

- roles permiten o restringen consultar, evaluar, registrar, anular, cambiar estado y administrar reglas
- endpoints criticos fallan correctamente sin permisos

---

## ISSUE-010 - Crear modulo aislado del motor de decisiones

- Tipo: Domain / Engine
- Prioridad: `P0`
- Sprint sugerido: `Sprint 2`
- Backlog origen: `E5-T1`, `E5-T2`, `E5-T2a`, `E5-T4`
- Dependencias: `ISSUE-002`, `ISSUE-004`

### Objetivo

Crear el modulo base del motor de decisiones desacoplado de FastAPI y de la UI, preparado para pipeline configurable por nodos.

### Entregables

- contratos de entrada y salida del motor
- contrato base de `DecisionTrace`
- paquete `decision_engine`
- normalizacion base de entradas
- estrategia para seleccionar reglas por producto o conjunto de reglas
- orquestador base de nodos y estrategia de pipeline

### Criterios de aceptacion

- el modulo puede importarse sin dependencias web
- el contrato del motor es estable y testeable
- el motor expone funciones `async` para soportar peticiones concurrentes (SPEC §5.2)
- la estructura no asume que PLD sera el unico producto soportado
- existe soporte base para `DecisionNode`, `pipeline_strategy` y branching controlado

---

## ISSUE-011 - Implementar reglas y formulas PLD sobre motor multiproducto

- Tipo: Domain / Engine
- Prioridad: `P0`
- Sprint sugerido: `Sprint 4`
- Backlog origen: `E5-T5`, `E5-T6`, `E5-T7`, `E5-T3`, `E5-T3a`
- Dependencias: `ISSUE-007`, `ISSUE-010`

### Objetivo

Implementar elegibilidad, segmento, RCI, oferta, cuota, tasa, plazo, alertas y bloqueos del runtime `PLD` sobre un motor cuyo core permanezca agnostico al producto.

### Entregables

- reglas de elegibilidad
- formulas de calculo
- bloqueos y alertas
- versionado de reglas y parametros aplicados
- versionado de pipeline y `DecisionTrace`
- preservacion del desacoplamiento entre core generico y metricas especificas de `PLD`
- compatibilidad con reglas declarativas cargables desde configuracion persistida del motor

### Criterios de aceptacion

- el motor produce resultados comparables al legacy para casos definidos
- cada evaluacion registra version de reglas, parametros, pipeline y traza estructurada
- metricas como `RCI`, `oferta`, `cuota`, `tasa` y `plazo` no quedan hardcodeadas como contrato universal del core

---

## ISSUE-012 - Crear suite de regresion del motor

- Tipo: QA / Engine
- Prioridad: `P0`
- Sprint sugerido: `Sprint 4`
- Backlog origen: `E5-T8`, `E9-T1`, `E9-T3`
- Dependencias: `ISSUE-011`

### Objetivo

Construir pruebas automatizadas del motor contra casos representativos del legacy.

### Entregables

- dataset de casos canonicos
- pruebas unitarias del motor
- comparativos de salida esperada

### Criterios de aceptacion

- formulas y bloqueos criticos quedan cubiertos por pruebas
- los casos canonicos pasan consistentemente

---

## ISSUE-013 - Implementar API de consulta PLD

- Tipo: Backend
- Prioridad: `P0`
- Sprint sugerido: `Sprint 4`
- Backlog origen: `E6-T1`, `E6-T2`
- Dependencias: `ISSUE-007`, `ISSUE-009`

- Estado documental actual: `reopened`
- Referencia de implementacion previa: `docs/analysis/ISSUE-013.md`
- Nota: la implementacion existente sera reevaluada luego del `Sprint 3` de saneamiento para validar su encaje con las nuevas especificaciones administrativas del motor.

### Objetivo

Exponer la consulta de cliente y campanas PLD mediante API desacoplada de HTML y alineada con la jerarquia multiproducto por `product_code`.

### Entregables

- servicio de consulta PLD
- endpoint `POST /api/v1/loans/{product_code}/consultas`

### Criterios de aceptacion

- el endpoint retorna datos de cliente y campanas en JSON estructurado
- los errores son consistentes con el contrato definido
- la implementacion no acopla la capa de aplicacion a `PLD` como unico producto posible
- la solucion resultante permanece coherente con el baseline saneado de productos, workflows, variables y fuentes declarativas del motor

---

## ISSUE-014 - Implementar API de evaluacion PLD

- Tipo: Backend
- Prioridad: `P0`
- Sprint sugerido: `Sprint 4`
- Backlog origen: `E6-T3`, `E6-T4`, `E6-T4a`
- Dependencias: `ISSUE-011`, `ISSUE-012`, `ISSUE-009`

### Objetivo

Exponer la evaluacion del motor como caso de uso persistido, junto con su traza estructurada, reutilizando la base multiproducto ya existente en dominio y contratos.

### Entregables

- caso de uso de evaluacion
- endpoint `POST /api/v1/loans/{product_code}/evaluaciones`
- endpoint `GET /api/v1/loans/{product_code}/evaluaciones/{evaluation_id}/trace`
- persistencia de evaluaciones
- persistencia y consulta de `DecisionTrace`

### Criterios de aceptacion

- el endpoint ejecuta el motor y retorna la salida esperada
- la evaluacion queda persistida con versionado, usuario y snapshot minimo
- la traza de evaluacion puede consultarse por API con permisos adecuados

---

## ISSUE-015 - Implementar API de registro de solicitud

- Tipo: Backend
- Prioridad: `P0`
- Sprint sugerido: `Sprint 5`
- Backlog origen: `E6-T5`, `E6-T6`
- Dependencias: `ISSUE-014`

### Objetivo

Registrar solicitudes de credito con validaciones de negocio y trazabilidad.

### Entregables

- servicio de registro
- endpoint `POST /api/v1/loans/{product_code}/solicitudes`
- estado inicial de solicitud

### Criterios de aceptacion

- el endpoint acepta solicitudes validas y rechaza invalidas segun reglas
- se registra auditoria minima del evento

---

## ISSUE-016 - Implementar bandeja y mantenimiento de solicitudes

- Tipo: Backend
- Prioridad: `P1`
- Sprint sugerido: `Sprint 5`
- Backlog origen: `E6-T7`, `E6-T8`, `E6-T9`, `E6-T10`
- Dependencias: `ISSUE-015`

### Objetivo

Exponer la bandeja de solicitudes y las acciones de anulacion y cambio de estado.

### Entregables

- listado paginado o filtrado de solicitudes
- endpoint `GET /api/v1/loans/{product_code}/solicitudes`
- endpoint `POST /api/v1/loans/{product_code}/solicitudes/{id}/anular`
- endpoint `POST /api/v1/loans/{product_code}/solicitudes/{id}/estado`
- historial de estados

### Criterios de aceptacion

- la bandeja puede filtrarse al menos por periodo
- la anulacion y el cambio de estado respetan permisos
- el historial de cambios queda persistido

---

## ISSUE-017 - Construir base del frontend y manejo de sesion

- Tipo: Frontend
- Prioridad: `P1`
- Sprint sugerido: `Sprint 5`
- Backlog origen: `E7-T1`, `E4-T3`
- Dependencias: `ISSUE-005`, `ISSUE-008`

### Objetivo

Construir la base navegable del frontend elegido, con manejo de sesion y proteccion de rutas.

### Entregables

- layout base de la aplicacion
- proveedor de sesion
- rutas protegidas
- integracion inicial con autenticacion y permisos

### Criterios de aceptacion

- la aplicacion reconoce la sesion actual
- existen rutas protegidas por autenticacion
- la base del frontend soporta permisos y crecimiento del flujo PLD

---

## ISSUE-018 - Implementar UI de consulta y evaluacion PLD

- Tipo: Frontend
- Prioridad: `P1`
- Sprint sugerido: `Sprint 5`
- Backlog origen: `E7-T3`, `E7-T4`, `E7-T5`
- Dependencias: `ISSUE-017`, `ISSUE-013`, `ISSUE-014`

### Objetivo

Permitir consulta, evaluacion y visualizacion estructurada del resultado PLD desde la UI.

### Entregables

- formulario de consulta
- seleccion de campana y formulario de evaluacion
- vista de resultado de evaluacion

### Criterios de aceptacion

- el usuario puede consultar por documento y evaluar una oferta
- la UI muestra oferta, RCI, alertas, bloqueos y version de reglas
- el flujo no depende de tablas HTML legacy

---

## ISSUE-019 - Implementar UI de registro y bandeja

- Tipo: Frontend
- Prioridad: `P1`
- Sprint sugerido: `Sprint 6`
- Backlog origen: `E7-T6`, `E7-T7`, `E7-T8`
- Dependencias: `ISSUE-018`, `ISSUE-016`

### Objetivo

Completar el flujo frontend de registro de solicitud, bandeja operativa y acciones por rol.

### Entregables

- formulario de registro
- pantalla de bandeja con filtros
- acciones de anulacion y cambio de estado segun rol

### Criterios de aceptacion

- el usuario puede registrar solicitudes desde la UI
- la bandeja lista solicitudes por periodo y estado
- la UI respeta permisos por rol en acciones operativas

---

## ISSUE-020 - Implementar auditoria, logs y endurecimiento basico

- Tipo: Security / Observability
- Prioridad: `P1`
- Sprint sugerido: `Sprint 6`
- Backlog origen: `E2-T7`, `E4-T6`, `E4-T7`, `E9-T6`, `E9-T7`
- Dependencias: `ISSUE-009`, `ISSUE-016`

### Objetivo

Activar auditoria de acciones sensibles, logs estructurados y controles de seguridad.

### Entregables

- auditoria de acciones criticas
- request id y logs estructurados
- controles de seguridad: HTTPS en entornos no locales, CORS restringido, validacion CSRF si aplica, proteccion contra SQL injection, almacenamiento seguro de secretos, rate limiting y cabeceras de seguridad (SPEC §4.4)
- health checks operativos

### Criterios de aceptacion

- evaluacion, registro, anulacion, cambio de estado, adjuntos ZIP y administracion de reglas quedan auditados
- cada registro de auditoria incluye los campos de SPEC §4.5: usuario, rol, accion, entidad afectada, resultado, IP origen, request ID y trazabilidad IA si aplica
- el backend emite logs correlacionables por request id
- existen controles de seguridad documentados y operativos segun SPEC §4.4

---

## ISSUE-021 - Implementar pruebas de integracion y E2E del MVP

- Tipo: QA
- Prioridad: `P1`
- Sprint sugerido: `Sprint 6`
- Backlog origen: `E9-T4`, `E9-T5`
- Dependencias: `ISSUE-019`, `ISSUE-020`

### Objetivo

Cubrir el MVP con pruebas automatizadas de integracion y al menos un flujo E2E estable.

### Entregables

- pruebas de integracion de API
- pruebas E2E del flujo principal
- evidencia automatizada de regresion del MVP

### Criterios de aceptacion

- consulta, evaluacion, registro y cambio de estado tienen pruebas de integracion
- la consulta de `DecisionTrace` queda cubierta por integracion
- existe al menos un flujo E2E punta a punta estable

---

## ISSUE-022 - Preparar despliegue inicial y CI

- Tipo: Platform / DevOps
- Prioridad: `P1`
- Sprint sugerido: `Sprint 6`
- Backlog origen: `E10-T1`, `E10-T2`, `E10-T3`, `E10-T4`
- Dependencias: `ISSUE-004`, `ISSUE-005`, `ISSUE-021`

### Objetivo

Preparar la receta reproducible de despliegue inicial y la automatizacion minima de CI del proyecto.

### Entregables

- estrategia de ejecucion local y despliegue
- configuracion base por entorno no productivo
- pipeline CI minima
- checklist de salida

### Criterios de aceptacion

- existe una receta reproducible de arranque para backend y frontend
- la CI ejecuta validaciones y pruebas base
- el checklist de salida cubre migraciones, seguridad, rollback y monitoreo

---

## ISSUE-023 - Implementar backend de adjuntos ZIP

- Tipo: Backend
- Prioridad: `P1`
- Sprint sugerido: `Sprint 5`
- Backlog origen: `E6-T12`
- Dependencias: `ISSUE-015`, `ISSUE-009`

### Objetivo

Habilitar carga, listado y descarga de adjuntos ZIP por solicitud usando `filesystem`.

### Entregables

- estrategia documentada de almacenamiento ZIP
- endpoint de carga de ZIP
- endpoint de listado de adjuntos
- endpoint de descarga de adjuntos

### Criterios de aceptacion

- los ZIP quedan asociados a una solicitud
- el almacenamiento usa `filesystem` con naming, limites y permisos definidos
- la operacion queda auditada y protegida por rol

---

## ISSUE-024 - Implementar UI de adjuntos ZIP

- Tipo: Frontend
- Prioridad: `P1`
- Sprint sugerido: `Sprint 6`
- Backlog origen: `E7-T10`
- Dependencias: `ISSUE-019`, `ISSUE-023`

### Objetivo

Exponer en la UI la carga, consulta y descarga de adjuntos ZIP por solicitud.

### Entregables

- componentes de carga de ZIP
- listado de adjuntos de una solicitud
- accion de descarga

### Criterios de aceptacion

- el usuario autorizado puede cargar, listar y descargar ZIPs desde la UI
- la experiencia respeta permisos y muestra errores operativos de forma clara

---

## ISSUE-025 - Implementar asistencia AI al registro

- Tipo: Backend / AI
- Prioridad: `P1`
- Sprint sugerido: `Sprint 6`
- Backlog origen: `E12-T7`
- Dependencias: `ISSUE-015`, `ISSUE-034`

### Objetivo

Agregar asistencia AI al registro de solicitud para revisar consistencia del comentario y advertir omisiones.

### Entregables

- endpoint `POST /api/v1/loans/{product_code}/solicitudes/{request_id}/assist`
- plantilla de prompt para asistencia de registro
- persistencia de interacciones AI

### Criterios de aceptacion

- el endpoint devuelve advertencias operativas y sugerencias de accion
- la interaccion queda auditada en `ai_interactions`
- una falla AI no bloquea el flujo determinista de registro

---

## ISSUE-026 - Implementar briefing AI de bandeja

- Tipo: Backend / AI
- Prioridad: `P1`
- Sprint sugerido: `Sprint 6`
- Backlog origen: `E12-T8`
- Dependencias: `ISSUE-016`, `ISSUE-034`

### Objetivo

Generar un resumen AI de la bandeja operativa para uso de supervisores.

### Entregables

- endpoint `POST /api/v1/loans/{product_code}/bandeja/summary`
- plantilla de prompt para briefing operativo
- persistencia de la interaccion AI

### Criterios de aceptacion

- el endpoint genera resumen de bandeja sin alterar datos operativos
- la respuesta queda trazada y auditada
- un fallo del modulo AI no afecta la consulta normal de bandeja

---

## ISSUE-027 - Definir contratos de inputs externos y snapshot minimo

- Tipo: Analysis / Data Design
- Prioridad: `P0`
- Sprint sugerido: `Sprint 1`
- Backlog origen: `E1-T6b`, `E1-T6c`
- Dependencias: `ISSUE-001`

### Objetivo

Formalizar los inputs externos de cliente, campanas y deuda, y definir el snapshot minimo que se persiste por evaluacion.

### Entregables

- contratos de inputs externos
- validaciones y errores esperados
- lista de campos persistidos como snapshot minimo

### Criterios de aceptacion

- queda explicito que solo se persisten los campos consumidos por el motor
- los contratos diferencian origen externo, uso operativo y trazabilidad de evaluacion

---

## ISSUE-028 - Formalizar fuente oficial de reglas y tratamiento de discrepancias

- Tipo: Analysis / Governance
- Prioridad: `P0`
- Sprint sugerido: `Sprint 1`
- Backlog origen: `E1-T6d`
- Dependencias: `ISSUE-001`

### Objetivo

Definir la precedencia entre `docs/SPEC.md`, legacy, Excel de parametros y decisiones funcionales cerradas.

### Entregables

- criterio de fuente oficial de reglas
- politica de discrepancias documentada
- ruta de aprobacion para cambios funcionales

### Criterios de aceptacion

- existe un orden de precedencia claro entre fuentes
- el equipo puede resolver discrepancias sin bloquear implementacion del motor

---

## ISSUE-029 - Exportacion de bandeja

- Tipo: Backend / Frontend
- Prioridad: `P1`
- Sprint sugerido: `Sprint 6`
- Backlog origen: `E6-T11`, `E7-T9`
- Dependencias: `ISSUE-016`, `ISSUE-019`

### Objetivo

Agregar exportacion desacoplada del DOM para la bandeja de solicitudes.

### Entregables

- endpoint `GET /api/v1/loans/{product_code}/solicitudes/export`
- accion de descarga en UI

### Criterios de aceptacion

- el usuario puede descargar la bandeja en el formato acordado
- la generacion del archivo no depende de tablas renderizadas en el navegador

---

## ISSUE-030 - Importador de parametros desde Excel

- Tipo: Admin / Data
- Prioridad: `P2`
- Sprint sugerido: `Sprint 7`
- Backlog origen: `E8-T1`, `E8-T2`
- Dependencias: `ISSUE-006`, `ISSUE-007`

### Objetivo

Permitir cargar parametros del motor desde Excel de forma controlada y versionada.

### Entregables

- analisis formal de hojas y columnas
- importador validado
- versionado del lote cargado

### Criterios de aceptacion

- el importador valida estructura antes de persistir
- la carga deja trazabilidad del lote y de la version generada

---

## ISSUE-031 - Documentar estrategia de base limpia y referencia legacy

- Tipo: Data Strategy
- Prioridad: `P1`
- Sprint sugerido: `Sprint 7`
- Backlog origen: `E8-T3`, `E8-T4`
- Dependencias: `ISSUE-001`

### Objetivo

Dejar formalizada la estrategia de base limpia del MVP y el uso del legacy solo como referencia funcional y analitica.

### Entregables

- documento de base limpia
- criterio de uso referencial de `old-version/API_DB.db`
- guia de contraste funcional contra legacy

### Criterios de aceptacion

- queda documentado que no habra migracion historica en el MVP
- el alcance del uso referencial del legacy queda acotado y no se convierte en dependencia runtime

---

## ISSUE-032 - Definir y validar base multiproducto de la plataforma

- Tipo: Architecture
- Prioridad: `P1`
- Sprint sugerido: `Sprint 3`
- Backlog origen: `E11-T1`, `E11-T2`, `E11-T3`, `E11-T4`, `E11-T5`, `E11-T6`
- Dependencias: `ISSUE-001`, `ISSUE-006`, `ISSUE-010`

### Objetivo

Consolidar y validar la estrategia tecnica para incorporar otros tipos de prestamo sobre la misma plataforma, partiendo de una base multiproducto ya presente en el repositorio sin comprometer el MVP PLD.

### Entregables

- nomenclatura compartida de dominio
- estrategia de extension del motor por producto
- lineamientos de extension de API y persistencia
- evidencia tecnica de onboarding de un segundo producto
- definicion del ciclo `draft -> active` para productos y workflows
- definicion del catalogo de variables por producto y de la herencia hacia workflows
- definicion de fuentes declarativas de input (`campaign_db`, `user_input`, `derived`, `constant`)

### Criterios de aceptacion

- la estrategia evita hardcode estructural de PLD en modulos compartidos
- queda claro como introducir nuevos productos sin romper contratos base ni seguridad compartida
- queda validado tecnicamente que un segundo producto puede convivir con el pipeline configurable del MVP
- la documentacion distingue entre fundaciones ya implementadas y capacidades aun pendientes de administracion o onboarding real
- queda definido que productos y workflows no requieren aprobacion de TI para su alta, pero si validacion y activacion posterior por negocio o riesgos autorizados

---

## ISSUE-033 - Definir politicas de seguridad y diseno de contratos AI

- Tipo: Security / Architecture
- Prioridad: `P0`
- Sprint sugerido: `Sprint 1`
- Backlog origen: `E12-T1`, `E12-T2`
- Dependencias: `ISSUE-001`, `ISSUE-006`

### Objetivo

Definir que datos pueden procesarse, que politicas de privacidad aplican y como se disena la persistencia auditable de interacciones AI.

### Entregables

- documento de politicas de datos AI
- diseno logico de `ai_interactions` y `ai_prompt_templates`
- reglas de minimizacion de datos para prompts y respuestas

### Criterios de aceptacion

- queda explicito que datos del cliente se omiten o anonimizan antes de enviar al modelo
- queda aprobado el diseno de persistencia AI para implementarlo junto al ORM y las migraciones

---

## ISSUE-034 - Implementar servicio base de conexion a LLM

- Tipo: Backend / Platform
- Prioridad: `P0`
- Sprint sugerido: `Sprint 2`
- Backlog origen: `E12-T3`
- Dependencias: `ISSUE-004`, `ISSUE-033`

### Objetivo

Crear el cliente de integracion con el proveedor del modelo de lenguaje, aislando fallas y reintentos.

### Entregables

- clase cliente `AIModelClient`
- variables de entorno configuradas
- pruebas unitarias de integracion

### Criterios de aceptacion

- el backend puede conectarse de manera exitosa con el LLM usando configuracion externa
- un fallo de red o timeout del LLM no bloquea el arranque ni la ejecucion de calculos deterministas

---

## ISSUE-035 - Desarrollar el servicio de explicacion de evaluacion PLD

- Tipo: Backend
- Prioridad: `P1`
- Sprint sugerido: `Sprint 4`
- Backlog origen: `E12-T4`, `E12-T5`
- Dependencias: `ISSUE-014`, `ISSUE-034`

### Objetivo

Implementar el endpoint que traduce una evaluacion PLD a texto explicativo y sugerencias.

### Entregables

- plantilla de prompt para explicacion PLD
- endpoint `POST /api/v1/loans/{product_code}/evaluaciones/{evaluation_id}/explain`
- persistencia de la interaccion en `ai_interactions`

### Criterios de aceptacion

- el endpoint devuelve la explicacion en JSON
- toda invocacion exitosa se registra en base de datos para auditoria
- el prompt restringe la alucinacion forzando el uso exclusivo de los datos inyectados

---

## ISSUE-036 - Implementar integracion frontend de capacidades AI del MVP

- Tipo: Frontend
- Prioridad: `P1`
- Sprint sugerido: `Sprint 6`
- Backlog origen: `E12-T6`
- Dependencias: `ISSUE-018`, `ISSUE-019`, `ISSUE-025`, `ISSUE-026`, `ISSUE-035`

### Objetivo

Mostrar en la UI las capacidades AI del MVP de forma clara e interactiva, sin mezclar datos duros del motor con contenido generado.

### Entregables

- componente `EvaluationAIExplanationPanel`
- integracion AI en registro de solicitud
- integracion AI para resumen de bandeja
- disclaimers y controles de error

### Criterios de aceptacion

- tras una evaluacion exitosa, la UI muestra la explicacion generada por IA
- la UI expone asistencia AI en registro y resumen AI en bandeja donde corresponda
- los textos AI estan visualmente diferenciados de los datos duros calculados por el motor
- ante caidas de red del modulo AI, el usuario puede reintentar la operacion AI sin repetir el calculo determinista

---

## ISSUE-037 - Implementar event store y DecisionTrace de decisiones

- Tipo: Backend / Data
- Prioridad: `P1`
- Sprint sugerido: `Sprint 6`
- Backlog origen: `E13-T1`, `E13-T2`, `E13-T4`, `E13-T5`
- Dependencias: `ISSUE-007`, `ISSUE-014`, `ISSUE-016`

### Objetivo

Implementar el almacenamiento inmutable de eventos de decision y la traza estructurada de evaluaciones sobre fundaciones de modelo ya existentes.

### Entregables

- integracion operativa de modelos SQLAlchemy ya existentes para `decision_events`
- integracion operativa de modelos SQLAlchemy ya existentes para `decision_traces`
- servicio de event store con escritura y consulta
- integracion con evaluaciones y cambios de estado del MVP
- integracion de `DecisionTrace` con evaluaciones y AI

### Criterios de aceptacion

- cada evaluacion y cambio de estado genera un evento inmutable en `decision_events`
- se puede consultar el timeline completo de cualquier evaluacion o solicitud
- los eventos incluyen version, usuario y timestamp
- cada evaluacion persiste un `DecisionTrace` estructurado reutilizable por AI y auditoria humana

---

## ISSUE-038 - Implementar BRMS: productos, workflows, variables, reglas y configuracion de flujo

- Tipo: Backend / Engine
- Prioridad: `P1`
- Sprint sugerido: `Sprint 7`
- Backlog origen: `E14-T1`, `E14-T2`, `E14-T3`, `E14-T4`
- Dependencias: `ISSUE-007`, `ISSUE-011`

### Objetivo

Almacenar y administrar productos, workflows, variables, reglas de negocio y configuracion gobernada de flujo en base de datos con versionado completo y vigencia por producto, aprovechando fundaciones de modelo ya existentes.

### Entregables

- activacion funcional de modelos SQLAlchemy ya existentes para `rule_sets` y `rule_versions`
- activacion funcional de modelos SQLAlchemy ya existentes para `pipeline_strategies` y `pipeline_nodes`
- alta administrable de productos y workflows en estado `draft`
- catalogo administrable de variables por producto
- reglas declarativas en JSON/DSL restringido por workflow
- resolucion de herencia de variables y reglas entre producto y workflow
- endpoints y servicio CRUD de reglas con versionado
- migracion de reglas PLD actuales al nuevo esquema

### Criterios de aceptacion

- las reglas del motor PLD se cargan desde `rule_versions` y no desde codigo fijo
- cada cambio genera una nueva version sin perder la anterior
- los rule sets pueden activarse y desactivarse por periodo
- las estrategias de pipeline quedan versionadas y sujetas a validacion de topologia
- productos y workflows pueden registrarse sin aprobacion de TI y quedan inactivos hasta su activacion por negocio o riesgos autorizados
- el catalogo de variables pertenece al producto y los workflows pueden heredar variables y reglas base con resolucion explicita
- las variables de `campaign_db` se resuelven desde tablas internas del sistema nuevo

---

## ISSUE-039 - Refactorizar motor a pipeline configurable por nodos

- Tipo: Engine / Architecture
- Prioridad: `P1`
- Sprint sugerido: `Sprint 8`
- Backlog origen: `E14-T5`, `E14-T6`, `E14-T7`, `E14-T7a`
- Dependencias: `ISSUE-010`, `ISSUE-038`

### Objetivo

Completar la convergencia del motor de decisiones hacia un pipeline configurable por nodos gobernados sobre una base de orquestacion y topologia ya implementada.

### Entregables

- consolidacion de la interfaz `DecisionNode` y del orquestador de pipeline ya existentes
- 5 nodos base implementados: Preprocessing, Eligibility, Scoring, Decision Strategy, Post-processing
- seleccion operativa de pipeline por producto desde persistencia
- validacion de topologia y branching controlado ya integradas al flujo administrable
- integracion del runtime con catalogo de variables por producto, herencia hacia workflow y reglas declarativas resueltas por version activa

### Criterios de aceptacion

- el pipeline ejecuta los 5 nodos base para PLD
- cada nodo es independiente y testeable por separado
- los resultados son equivalentes a la implementacion anterior
- se puede configurar un pipeline diferente por producto sin permitir grafos invalidos
- la evaluacion resuelve correctamente producto, workflow, variables heredadas, fuentes de input y reglas activas antes de ejecutar el pipeline

---

## ISSUE-040 - UI Administrativa de Productos, Workflows, Variables, Reglas y Flujo

- Tipo: Frontend
- Prioridad: `P1`
- Sprint sugerido: `Sprint 8`
- Backlog origen: `E14-T8`, `E14-T9`, `E14-T10`, `E14-T11`
- Dependencias: `ISSUE-017`, `ISSUE-038`, `ISSUE-039`

### Objetivo

Exponer una interfaz web para que administradores de negocio y riesgos gestionen productos, workflows, variables, reglas de negocio y secuencia del flujo con versionado, simulacion y flujo de activacion.

### Entregables

- CRUD de `rule_sets` y `rule_versions` en frontend
- CRUD de productos y workflows
- CRUD de variables por producto y configuracion de fuentes de input
- UI gobernada de `pipeline_strategies` y `pipeline_nodes`
- sandbox de pruebas con casos historicos

### Criterios de aceptacion

- negocio o riesgos puede crear productos y workflows en `draft` y activarlos desde la UI sin aprobacion de TI
- la UI permite administrar variables por producto y visualizar su herencia hacia workflows
- la UI permite definir reglas declarativas bajo el DSL restringido soportado por backend
- la simulacion soporta inputs mixtos provenientes de `campaign_db` y `user_input`
- admin puede listar, crear, editar y versionar reglas desde UI
- admin puede simular cambios en reglas y flujo contra casos historicos antes de activarlos
- cambios a reglas activas y pipelines activos requieren aprobacion de un supervisor

---

## ISSUE-041 - Alinear modelo de datos y contratos base del motor con nuevas especificaciones administrativas

- Tipo: Architecture / Data / Engine
- Prioridad: `P0`
- Sprint sugerido: `Sprint 3`
- Backlog origen: `E11-T4`, `E11-T5`, `E11-T6`
- Dependencias: `ISSUE-006`, `ISSUE-007`, `ISSUE-010`, `ISSUE-032`

### Objetivo

Sanear la brecha entre el modelo actual del repositorio y las nuevas especificaciones del motor administrable, alineando contratos y persistencia base para productos, workflows, variables, fuentes de input y ciclo `draft -> active`.

### Entregables

- definicion de entidades canonicas para `workflow_definitions` y `variable_definitions`
- definicion de campos faltantes en `loan_evaluations`, `decision_traces` y estrategias de pipeline para soportar `workflow_code` y versionado adicional
- definicion de contratos base para variables por producto y fuentes declarativas de input
- alineacion documental entre persistencia, contratos y trazabilidad del motor

### Criterios de aceptacion

- existe una ruta clara y consistente para representar productos, workflows y variables sin hardcode
- queda explicito como persistir el ciclo `draft -> active` para productos y workflows
- quedan definidos los contratos minimos para `campaign_db`, `user_input`, `derived` y `constant`
- la especificacion resultante no contradice el core multiproducto ya implementado

---

## ISSUE-042 - Alinear runtime base del motor con productos, workflows, variables y fuentes declarativas

- Tipo: Engine / Architecture
- Prioridad: `P0`
- Sprint sugerido: `Sprint 3`
- Backlog origen: `E14-T4a`, `E14-T4b`, `E14-T4c`, `E14-T4d`
- Dependencias: `ISSUE-010`, `ISSUE-032`, `ISSUE-041`

### Objetivo

Definir y dejar preparado el baseline tecnico para que el runtime del motor pueda resolver producto, workflow, catalogo de variables, herencia y fuentes declarativas antes de continuar con nuevas funcionalidades PLD sobre supuestos desactualizados.

### Entregables

- definicion de resolucion de runtime con herencia de variables y reglas desde producto hacia workflow
- definicion del punto de integracion del JSON/DSL restringido de reglas con el runtime del motor
- validaciones minimas para activacion de productos, workflows, variables y reglas
- estrategia de trazabilidad de fuentes consumidas por evaluacion

### Criterios de aceptacion

- el baseline del runtime resuelve de forma coherente `product_code`, `workflow_code`, variables heredadas y reglas activas
- queda definida la secuencia de validacion previa a la activacion de configuraciones administrables
- `DecisionTrace` y snapshot de evaluacion contemplan las fuentes materiales consumidas por el motor
- el equipo puede continuar con implementaciones PLD sin seguir ampliando brechas contra las nuevas especificaciones
