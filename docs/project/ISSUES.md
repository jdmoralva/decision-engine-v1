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

### Criterios de aceptacion

- existe un mapa del flujo completo de consulta, evaluacion, solicitud, bandeja, anulacion y cambio de estado
- existe un catalogo de reglas con nombre, condicion, entradas, salidas y efecto
- quedan resueltas las decisiones sobre autenticacion, frontend, ZIP, historicos y despliegue del motor
- queda explicito que partes del diseno deben permanecer neutrales para soportar otros tipos de prestamo en el futuro

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

### Criterios de aceptacion

- el backend levanta localmente
- el endpoint `health` responde correctamente
- existe estructura base para configuracion por entorno

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

### Criterios de aceptacion

- el frontend levanta localmente
- existe una pagina inicial navegable

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
- endpoint `POST /api/v1/pld/consultas`

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
- endpoint `POST /api/v1/pld/evaluaciones`
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
- endpoint `POST /api/v1/pld/solicitudes`
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
- endpoint de bandeja
- endpoint de anulacion
- endpoint de cambio de estado
- historial de estados

### Criterios de aceptacion

- la bandeja puede filtrarse al menos por periodo
- la anulacion y el cambio de estado respetan permisos
- el historial de cambios queda persistido

---

## ISSUE-017 - Construir base del frontend y manejo de sesion

- Tipo: Frontend
- Prioridad: `P1`
- Sprint sugerido: `Sprint 4`
- Backlog origen: `E7-T1`, `E4-T3`
- Dependencias: `ISSUE-005`, `ISSUE-008`

### Objetivo

Preparar la app frontend con rutas, layout y manejo de sesion.

### Entregables

- layout base
- rutas protegidas
- proveedor de sesion

### Criterios de aceptacion

- la app conoce al usuario autenticado
- las rutas protegidas se comportan correctamente

---

## ISSUE-018 - Implementar UI de consulta y evaluacion PLD

- Tipo: Frontend
- Prioridad: `P1`
- Sprint sugerido: `Sprint 4`
- Backlog origen: `E7-T3`, `E7-T4`, `E7-T5`
- Dependencias: `ISSUE-013`, `ISSUE-014`, `ISSUE-017`

### Objetivo

Permitir al usuario consultar cliente, seleccionar campana y visualizar evaluacion.

### Entregables

- formulario de consulta PLD
- seleccion de campana
- formulario de evaluacion
- vista de resultado de evaluacion

### Criterios de aceptacion

- el usuario puede completar el flujo hasta obtener una evaluacion valida
- la UI no depende de indices de tabla ni de HTML inyectado

---

## ISSUE-019 - Implementar UI de registro y bandeja

- Tipo: Frontend
- Prioridad: `P1`
- Sprint sugerido: `Sprint 5`
- Backlog origen: `E7-T6`, `E7-T7`, `E7-T8`
- Dependencias: `ISSUE-015`, `ISSUE-016`, `ISSUE-018`

### Objetivo

Completar en frontend el registro de solicitud y la bandeja operativa con acciones por rol.

### Entregables

- formulario de registro de solicitud
- pantalla de bandeja
- accion de anular
- accion de cambio de estado

### Criterios de aceptacion

- el usuario puede registrar solicitud desde una evaluacion valida
- la bandeja refleja estados y permisos reales

---

## ISSUE-020 - Implementar auditoria, logs y endurecimiento basico

- Tipo: Security / Observability
- Prioridad: `P1`
- Sprint sugerido: `Sprint 5`
- Backlog origen: `E2-T7`, `E4-T6`, `E4-T7`, `E9-T6`, `E9-T7`
- Dependencias: `ISSUE-009`, `ISSUE-015`, `ISSUE-016`

### Objetivo

Agregar auditabilidad y controles operativos minimos al MVP.

### Entregables

- logs estructurados
- auditoria de acciones sensibles
- health checks
- rate limiting
- cabeceras de seguridad base

### Criterios de aceptacion

- acciones sensibles quedan auditadas
- el sistema expone endpoints de salud
- existen controles basicos de endurecimiento

---

## ISSUE-021 - Implementar pruebas de integracion y E2E del MVP

- Tipo: QA
- Prioridad: `P1`
- Sprint sugerido: `Sprint 5`
- Backlog origen: `E9-T2`, `E9-T4`, `E9-T5`
- Dependencias: `ISSUE-018`, `ISSUE-019`

### Objetivo

Cubrir el flujo MVP con pruebas de API y al menos un flujo punta a punta.

### Entregables

- pruebas de integracion de API
- pruebas frontend base
- prueba E2E del flujo principal

### Criterios de aceptacion

- consulta, evaluacion, registro y cambio de estado tienen cobertura automatizada
- existe al menos un escenario E2E estable

---

## ISSUE-022 - Preparar despliegue inicial y CI

- Tipo: DevOps
- Prioridad: `P1`
- Sprint sugerido: `Sprint 5`
- Backlog origen: `E10-T1`, `E10-T2`, `E10-T3`, `E10-T4`, `E10-T5`
- Dependencias: `ISSUE-004`, `ISSUE-005`, `ISSUE-021`

### Objetivo

Dejar lista la ejecucion reproducible, pipeline minima y checklist de salida.

### Entregables

- estrategia de ejecucion local y despliegue
- configuracion base de despliegue
- pipeline CI minima
- checklist de salida a produccion
- guia basica operativa

### Criterios de aceptacion

- el proyecto puede levantarse de forma repetible
- la pipeline ejecuta validaciones minimas
- existe checklist de salida con rollback y monitoreo

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

- endpoint de exportacion
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
