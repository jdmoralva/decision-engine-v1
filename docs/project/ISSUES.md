# ISSUES - Decision Engine

## Proposito

Este archivo convierte `BACKLOG.md` en una estructura de issues lista para gestion operativa. Cada issue agrupa una unidad de trabajo razonablemente entregable, manteniendo trazabilidad con epicas y tareas del backlog del MVP PLD y de la base futura multiproducto.

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
- Backlog origen: `E1-T1`, `E1-T2`, `E1-T3`
- Dependencias: ninguna

### Objetivo

Cerrar el alcance real del MVP PLD, consolidando flujo actual, reglas observadas y decisiones abiertas, y distinguiendo lo especifico de PLD frente a lo que debe quedar reutilizable para futuros productos de prestamo.

### Entregables

- mapa del flujo PLD legado
- catalogo de reglas de negocio observadas
- resolucion de decisiones abiertas del SPEC
- separacion entre capacidades exclusivas de PLD y capacidades de plataforma compartida
- definicion exacta de roles operativos con responsabilidades y permisos (analista, evaluador, supervisor, admin)
- reglas de aprobacion y rechazo posteriores al registro (quien, cuando y bajo que condiciones)

### Criterios de aceptacion

- existe un mapa del flujo completo de consulta, evaluacion, solicitud, bandeja, anulacion y cambio de estado
- existe un catalogo de reglas con nombre, condicion, entradas, salidas y efecto
- quedan resueltas las decisiones sobre autenticacion, frontend, ZIP, historicos y despliegue del motor
- queda explicito que partes del diseno deben permanecer neutrales para soportar otros tipos de prestamo en el futuro
- roles operativos definidos (analista, evaluador, supervisor, admin) con matriz de permisos por accion
- reglas de aprobacion y rechazo documentadas: criterios, responsable y momento del flujo en que aplican

---

## ISSUE-002 - Definir contratos iniciales del dominio y API

- Tipo: Analysis / Design
- Prioridad: `P0`
- Sprint sugerido: `Sprint 1`
- Backlog origen: `E1-T4`, `E1-T5`, `E1-T6`
- Dependencias: `ISSUE-001`

### Objetivo

Definir los contratos de consulta, evaluacion, registro de solicitud y cambio de estado desacoplados de la UI.

### Entregables

- payload de consulta PLD
- payload de evaluacion
- payload de registro de solicitud
- payload de cambio de estado
- contratos de error estructurados

### Criterios de aceptacion

- contratos documentados con campos, tipos y validaciones
- contratos no dependen de posiciones de tabla ni de HTML
- contratos son consistentes con el modelo de datos objetivo
- los contratos distinguen entre campos comunes a la plataforma y campos especificos de PLD

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

- carpetas `backend/`, `frontend/`, `docs/`
- archivos base del repositorio
- convenciones minimas documentadas

### Criterios de aceptacion

- la estructura existe en la raiz del proyecto
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
- archivo `requirements.txt` y `pyproject.toml` segun SPEC.md Seccion 2.7

### Criterios de aceptacion

- el backend levanta localmente
- el endpoint `health` responde correctamente
- existe estructura base para configuracion por entorno
- las versiones de FastAPI, Pydantic (v2) y demas paquetes son las definidas en SPEC.md Seccion 2.7.2
- el linter `ruff` esta integrado y pasa sin advertencias en la inicializacion

---

## ISSUE-005 - Inicializar frontend con React y TypeScript

- Tipo: Frontend
- Prioridad: `P0`
- Sprint sugerido: `Sprint 1`
- Backlog origen: `E2-T3`
- Dependencias: `ISSUE-001`, `ISSUE-003`

### Objetivo

Crear la aplicacion frontend base con React, TypeScript y Vite.

### Entregables

- app frontend inicial
- pagina base funcional
- configuracion de arranque local
- archivo `package.json` base segun SPEC.md Seccion 2.7

### Criterios de aceptacion

- el frontend levanta localmente
- existe una pagina inicial navegable
- las dependencias de React, TypeScript, React Query y Tailwind CSS coinciden con SPEC.md Seccion 2.7.4

---

## ISSUE-006 - Diseñar modelo de datos inicial

- Tipo: Data Design
- Prioridad: `P0`
- Sprint sugerido: `Sprint 1`
- Backlog origen: `E3-T1`, `E3-T5`, `E3-T6`
- Dependencias: `ISSUE-002`

### Objetivo

Definir el esquema base de persistencia y el mapeo de parametros del motor.

### Entregables

- modelo relacional inicial
- entidades principales del MVP
- diseno de versionado de parametros
- mapeo del Excel a estructuras persistentes
- soporte base para clasificacion por producto de prestamo

### Criterios de aceptacion

- existe documento o diagrama de tablas y relaciones
- existe mapeo de `ParametrosPLD-v3.xlsx` a tablas nuevas
- el modelo evita dependencias innecesarias del motor de base de datos
- el esquema inicial no obliga a redisenar tablas compartidas al agregar nuevos productos de prestamo

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
- middleware o dependencias de autorizacion
- proteccion de endpoints por rol

### Criterios de aceptacion

- roles permiten o restringen consultar, evaluar, registrar, anular y cambiar estado
- endpoints criticos fallan correctamente sin permisos

---

## ISSUE-010 - Crear modulo aislado del motor de decisiones

- Tipo: Domain / Engine
- Prioridad: `P0`
- Sprint sugerido: `Sprint 2`
- Backlog origen: `E5-T1`, `E5-T2`, `E5-T4`
- Dependencias: `ISSUE-002`, `ISSUE-004`

### Objetivo

Crear el modulo base del motor de decisiones desacoplado de FastAPI y de la UI.

### Entregables

- contratos de entrada y salida del motor
- paquete `decision_engine`
- normalizacion base de entradas
- estrategia para seleccionar reglas por producto o conjunto de reglas

### Criterios de aceptacion

- el modulo puede importarse sin dependencias web
- el contrato del motor es estable y testeable
- la estructura no asume que PLD sera el unico producto soportado

---

## ISSUE-011 - Implementar reglas y formulas del motor PLD

- Tipo: Domain / Engine
- Prioridad: `P0`
- Sprint sugerido: `Sprint 3`
- Backlog origen: `E5-T5`, `E5-T6`, `E5-T7`, `E5-T3`
- Dependencias: `ISSUE-007`, `ISSUE-010`

### Objetivo

Implementar elegibilidad, segmento, RCI, oferta, cuota, tasa, plazo, alertas y bloqueos.

### Entregables

- reglas de elegibilidad
- formulas de calculo
- bloqueos y alertas
- versionado de reglas y parametros

### Criterios de aceptacion

- el motor produce resultados comparables al legado para casos definidos
- cada evaluacion registra version de reglas y parametros

---

## ISSUE-012 - Crear suite de regresion del motor

- Tipo: QA / Engine
- Prioridad: `P0`
- Sprint sugerido: `Sprint 3`
- Backlog origen: `E5-T8`, `E9-T1`, `E9-T3`
- Dependencias: `ISSUE-011`

### Objetivo

Construir pruebas automatizadas del motor contra casos representativos del legado.

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
- Sprint sugerido: `Sprint 3`
- Backlog origen: `E6-T1`, `E6-T2`
- Dependencias: `ISSUE-007`, `ISSUE-009`

### Objetivo

Exponer la consulta de cliente y campanas PLD mediante API desacoplada de HTML.

### Entregables

- servicio de consulta PLD
- endpoint `POST /api/v1/loans/{product_code}/consultas`

### Criterios de aceptacion

- el endpoint retorna datos de cliente y campanas en JSON estructurado
- los errores son consistentes con el contrato definido

---

## ISSUE-014 - Implementar API de evaluacion PLD

- Tipo: Backend
- Prioridad: `P0`
- Sprint sugerido: `Sprint 3`
- Backlog origen: `E6-T3`, `E6-T4`
- Dependencias: `ISSUE-011`, `ISSUE-012`, `ISSUE-009`

### Objetivo

Exponer la evaluacion del motor como caso de uso persistido.

### Entregables

- caso de uso de evaluacion
- endpoint `POST /api/v1/loans/{product_code}/evaluaciones`
- persistencia de evaluaciones

### Criterios de aceptacion

- el endpoint ejecuta el motor y retorna la salida esperada
- la evaluacion queda persistida con versionado y usuario

---

## ISSUE-015 - Implementar API de registro de solicitud

- Tipo: Backend
- Prioridad: `P0`
- Sprint sugerido: `Sprint 4`
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
- Sprint sugerido: `Sprint 4`
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

## ISSUE-023 - Exportacion de bandeja

- Tipo: Backend / Frontend
- Prioridad: `P2`
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

## ISSUE-024 - Importador de parametros desde Excel

- Tipo: Admin / Data
- Prioridad: `P2`
- Sprint sugerido: `Sprint 6`
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

## ISSUE-025 - Migracion historica desde legacy

- Tipo: Data Migration
- Prioridad: `P2`
- Sprint sugerido: `Sprint 6`
- Backlog origen: `E8-T3`, `E8-T4`
- Dependencias: `ISSUE-001`, `ISSUE-007`

### Objetivo

Ejecutar la estrategia definida para conservar o migrar historicos del sistema legado.

### Entregables

- decision formal de migracion
- scripts de carga historica si aplica
- validacion de consistencia

### Criterios de aceptacion

- la migracion historica, si aplica, es repetible y auditada
- queda documentado el alcance exacto de los datos migrados

---

## ISSUE-026 - Definir base multiproducto de la plataforma

- Tipo: Architecture
- Prioridad: `P2`
- Sprint sugerido: `Sprint 6`
- Backlog origen: `E11-T1`, `E11-T2`
- Dependencias: `ISSUE-001`, `ISSUE-006`, `ISSUE-010`

### Objetivo

Dejar definida la estrategia tecnica para incorporar otros tipos de prestamo sobre la misma plataforma sin comprometer el MVP PLD.

### Entregables

- nomenclatura compartida de dominio
- estrategia de extension del motor por producto
- lineamientos de extension de API y persistencia

### Criterios de aceptacion

- la estrategia evita hardcode estructural de PLD en modulos compartidos
- queda claro como introducir nuevos productos sin romper contratos base ni seguridad compartida

---

## ISSUE-027 - Definir politicas de seguridad y contratos AI

- Tipo: Security / Architecture
- Prioridad: `P0`
- Sprint sugerido: `Sprint 1`
- Backlog origen: `E12-T1`, `E12-T2`
- Dependencias: `ISSUE-001`, `ISSUE-006`

### Objetivo
Definir que datos pueden procesarse, que politicas de privacidad aplican y estructurar las tablas de auditoria AI.

### Entregables
- documento de politicas de datos AI
- modelos SQLAlchemy para `ai_interactions` y `ai_prompt_templates`
- migracion de base de datos asociada

### Criterios de aceptacion
- la base SQLite puede generar las tablas de interaccion de IA
- queda explicito que datos del cliente se omiten o anonimizan antes de enviar al modelo

---

## ISSUE-028 - Implementar servicio base de conexion a LLM

- Tipo: Backend / Platform
- Prioridad: `P0`
- Sprint sugerido: `Sprint 2`
- Backlog origen: `E12-T3`
- Dependencias: `ISSUE-004`, `ISSUE-027`

### Objetivo
Crear el cliente de integracion con el proveedor del modelo de lenguaje, aislando fallas y reintentos.

### Entregables
- clase cliente `AIModelClient`
- variables de entorno configuradas
- pruebas unitarias de integracion

### Criterios de aceptacion
- el backend puede conectarse de manera exitosa con el LLM usando configuracion externa
- un fallo de red o timeout del LLM no bloquea el arranque o ejecucion de calculos deterministas

---

## ISSUE-029 - Desarrollar el servicio de explicacion de evaluacion PLD

- Tipo: Backend
- Prioridad: `P1`
- Sprint sugerido: `Sprint 3`
- Backlog origen: `E12-T4`, `E12-T5`
- Dependencias: `ISSUE-014`, `ISSUE-028`

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

## ISSUE-030 - Implementar panel de explicacion AI en frontend

- Tipo: Frontend
- Prioridad: `P1`
- Sprint sugerido: `Sprint 4`
- Backlog origen: `E12-T6`
- Dependencias: `ISSUE-018`, `ISSUE-029`

### Objetivo
Mostrar al analista de credito la explicacion y sugerencias del caso de forma clara e interactiva.

### Entregables
- componente `EvaluationAIExplanationPanel`
- integracion en el flujo post-evaluacion
- disclaimers y controles de error

### Criterios de aceptacion
- tras una evaluacion exitosa, el panel muestra la explicacion generada por IA
- los textos AI estan visualmente diferenciados de los datos duros calculados por el motor
- ante caidas de red del modulo AI, el analista puede re-intentar la explicacion sin tener que volver a calcular la evaluacion

---

## ISSUE-031 - Implementar event store de decisiones

- Tipo: Backend / Data
- Prioridad: `P1`
- Sprint sugerido: `Sprint 5`
- Backlog origen: `E13-T1`, `E13-T2`
- Dependencias: `ISSUE-007`, `ISSUE-014`

### Objetivo
Implementar el almacenamiento inmutable de eventos de decision con capacidad de consulta por agregado.

### Entregables
- modelo SQLAlchemy para `decision_events`
- servicio de event store con escritura y consulta
- integracion con el motor de decisiones para emitir eventos en cada etapa del pipeline

### Criterios de aceptacion
- cada evaluacion y cambio de estado genera un evento inmutable en `decision_events`
- se puede consultar el timeline completo de cualquier evaluacion o solicitud
- los eventos incluyen version, usuario y timestamp

---

## ISSUE-032 - Implementar BRMS: catalogacion de reglas

- Tipo: Backend / Engine
- Prioridad: `P1`
- Sprint sugerido: `Sprint 6`
- Backlog origen: `E14-T1`, `E14-T2`
- Dependencias: `ISSUE-007`, `ISSUE-011`

### Objetivo
Almacenar las reglas de negocio en base de datos con versionado completo y vigencia por producto.

### Entregables
- modelo SQLAlchemy para `rule_sets` y `rule_versions`
- servicio CRUD de reglas con versionado
- migracion de reglas PLD actuales al nuevo esquema

### Criterios de aceptacion
- las reglas del motor PLD se cargan desde `rule_versions` y no desde codigo fijo
- cada cambio genera una nueva version sin perder la anterior
- los rule_sets pueden activarse/desactivarse por periodo

---

## ISSUE-033 - Refactorizar motor a pipeline de etapas

- Tipo: Engine / Architecture
- Prioridad: `P1`
- Sprint sugerido: `Sprint 6`
- Backlog origen: `E14-T5`, `E14-T6`, `E14-T7`
- Dependencias: `ISSUE-010`, `ISSUE-032`

### Objetivo
Reestructurar el motor de decisiones como un pipeline configurable de etapas independientes.

### Entregables
- interfaz `DecisionStage` y orquestador de pipeline
- 5 etapas implementadas: Preprocessing, Eligibility, Scoring, Decision Strategy, Post-processing
- tabla `pipeline_strategies` con seleccion de pipeline por producto

### Criterios de aceptacion
- el pipeline ejecuta las 5 etapas secuencialmente para PLD
- cada etapa es independiente y testeable por separado
- los resultados son equivalentes a la implementacion anterior
- se puede configurar un pipeline diferente por producto

---

## ISSUE-034 - UI Administrativa de Reglas

- Tipo: Frontend
- Prioridad: `P2`
- Sprint sugerido: `Sprint 7`
- Backlog origen: `E14-T8`, `E14-T9`, `E14-T10`
- Dependencias: `ISSUE-017`, `ISSUE-032`

### Objetivo
Interfaz web para que administradores gestionen reglas de negocio con versionado, simulacion y flujo de aprobacion.

### Entregables
- CRUD de rule-sets y rule-versions en frontend
- sandbox de pruebas con casos historicos
- flujo de aprobacion de cambios (borrador → pending_approval → activo)

### Criterios de aceptacion
- admin puede listar, crear, editar y versionar reglas desde UI
- admin puede simular cambios en reglas contra casos historicos antes de activarlos
- cambios a reglas activas requieren aprobacion de un supervisor
