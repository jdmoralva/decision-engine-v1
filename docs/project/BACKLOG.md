# BACKLOG - Decision Engine

## 0. Proposito

Este backlog convierte `docs/SPEC.md` en un plan de ejecucion tecnico. No reemplaza la especificacion original: la descompone en epicas, historias, tareas y criterios de aceptacion para construir la nueva plataforma `Decision Engine`, cuyo MVP inicial cubre `PLD / solicitudes de credito`.

## 1. Convenciones de trabajo

### Estados

- `todo`
- `in_progress`
- `blocked`
- `done`

### Prioridades

- `P0`: bloqueante para iniciar o entregar MVP
- `P1`: critico para MVP
- `P2`: importante pero posterior al nucleo
- `P3`: mejora o evolucion futura

### Estimacion sugerida

- `S`: hasta 1 dia
- `M`: 2 a 4 dias
- `L`: 1 semana
- `XL`: mas de 1 semana o requiere division adicional

### Definicion de terminado

Una tarea se considera terminada solo si:

- el cambio esta implementado
- existe validacion automatizada o evidencia verificable
- no rompe el flujo PLD existente definido para MVP
- la documentacion minima fue actualizada si aplica

---

## 2. Hitos

### Hito 1. Descubrimiento cerrado

Objetivo:

- congelar alcance, reglas y decisiones base del MVP

### Hito 2. Bootstrap de plataforma

Objetivo:

- dejar operativo el esqueleto tecnico de backend, frontend y base de datos

### Hito 3. Motor de decisiones funcional

Objetivo:

- aislar y reproducir las reglas criticas del flujo PLD

### Hito 4. Flujo PLD MVP completo

Objetivo:

- consulta, evaluacion, solicitud y bandeja funcionando punta a punta

### Hito 5. Seguridad, QA y salida

Objetivo:

- endurecer acceso, auditoria, pruebas y despliegue

---

## 3. Epicas y tareas ejecutables

## E1. Descubrimiento funcional y decisiones base

Prioridad: `P0`

### Historia E1-H1. Cerrar alcance del MVP

Resultado esperado:

- alcance funcional del MVP aprobado y sin ambiguedades mayores

Tareas:

- [x] `E1-T1` Documentar flujo PLD actual de punta a punta desde `old-version/api-build.R` y `old-version/script.js`.
  - Prioridad: `P0`
  - Estimacion: `M`
  - Dependencias: ninguna
  - Aceptacion: existe mapa de flujo con consulta, evaluacion, registro, bandeja, anulacion y cambio de estado.

- [x] `E1-T2` Listar reglas de negocio observadas en `validate1`, `validate2` y `grabasol`.
  - Prioridad: `P0`
  - Estimacion: `M`
  - Dependencias: `E1-T1`
  - Aceptacion: existe catalogo de reglas con nombre, descripcion, entrada, salida y condicion de bloqueo o alerta.

- [x] `E1-T3` Confirmar decisiones abiertas del SPEC con negocio o usuario.
  - Prioridad: `P0`
  - Estimacion: `M`
  - Dependencias: `E1-T1`
  - Aceptacion: quedan resueltas al menos autenticacion, frontend segun despliegue, modo de despliegue del motor, fuente oficial de reglas, gobierno del flujo configurable y lineamientos corporativos de seguridad/despliegue. El flujo ZIP se incluye en el alcance del MVP. La migracion de historicos queda descartada. Queda confirmado que se espera un segundo producto al finalizar el MVP.

- [x] `E1-T3a` Distinguir que capacidades son exclusivas de PLD y cuales deben quedar como base compartida para futuros productos de prestamo.
  - Prioridad: `P0`
  - Estimacion: `S`
  - Dependencias: `E1-T1`, `E1-T2`
  - Aceptacion: existe una separacion explicita entre reglas, datos y flujos especificos de PLD frente a capacidades de plataforma reutilizables.

- [x] `E1-T7` Definir roles operativos y reglas de aprobacion/rechazo posteriores al registro.
  - Prioridad: `P0`
  - Estimacion: `M`
  - Dependencias: `E1-T1`, `E1-T2`
  - Aceptacion: roles definidos con matriz de permisos (analista, evaluador, supervisor, admin). Reglas de aprobacion/rechazo documentadas con criterios, responsable y momento del flujo.

### Historia E1-H2. Definir contratos iniciales

Resultado esperado:

- contratos claros para evaluar, registrar y consultar solicitudes

Tareas:

- [x] `E1-T4` Definir payload de consulta PLD.
  - Prioridad: `P0`
  - Estimacion: `S`
  - Dependencias: `E1-T1`
  - Aceptacion: contrato documentado con campos, tipos, validaciones y errores esperados. Los contratos quedan documentados en OpenAPI.

- [x] `E1-T5` Definir payload de evaluacion del motor.
  - Prioridad: `P0`
  - Estimacion: `S`
  - Dependencias: `E1-T2`
  - Aceptacion: contrato documentado independiente de UI y de indices de tabla. Los contratos quedan documentados en OpenAPI.

- [x] `E1-T5b` Definir contrato de `DecisionTrace` y endpoint de consulta de trazas de evaluacion.
  - Prioridad: `P0`
  - Estimacion: `S`
  - Dependencias: `E1-T5`
  - Aceptacion: quedan definidos el payload minimo de `DecisionTrace`, su uso para AI y auditoria humana, y el contrato de `GET /api/v1/loans/{product_code}/evaluaciones/{evaluation_id}/trace`.

- [x] `E1-T5c` Definir restricciones de topologia y gobierno del pipeline configurable.
  - Prioridad: `P0`
  - Estimacion: `S`
  - Dependencias: `E1-T5`, `E1-T6d`
  - Aceptacion: queda definido que negocio administra reglas, parametros y secuencia del flujo bajo branching controlado, validacion de topologia y aprobacion separada para cambios de flujo.

- [x] `E1-T5a` Definir que campos del contrato son comunes a cualquier producto de prestamo y cuales son especificos de PLD.
  - Prioridad: `P1`
  - Estimacion: `S`
  - Dependencias: `E1-T5`
  - Aceptacion: el contrato deja clara la frontera entre datos compartidos de plataforma y datos particulares de PLD.

- [x] `E1-T6` Definir payload de registro de solicitud y de cambio de estado.
  - Prioridad: `P0`
  - Estimacion: `S`
  - Dependencias: `E1-T2`
  - Aceptacion: contratos aprobados y alineados con modelo de datos previsto. Los contratos quedan documentados en OpenAPI.

- [x] `E1-T6b` Definir contratos de inputs externos para cliente, campanas y deuda.
  - Prioridad: `P0`
  - Estimacion: `S`
  - Dependencias: `E1-T1`, `E1-T2`
  - Aceptacion: existen contratos documentados con campos, origen, validaciones y errores esperados para cada input externo consumido por el motor o por los casos de uso.

- [x] `E1-T6c` Definir snapshot minimo por evaluacion con solo los campos consumidos por el motor.
  - Prioridad: `P0`
  - Estimacion: `S`
  - Dependencias: `E1-T5`, `E1-T6b`
  - Aceptacion: queda definida la lista exacta de campos que se persisten como evidencia de entrada de cada evaluacion.

- [x] `E1-T6d` Definir fuente oficial de reglas y criterio de resolucion de discrepancias entre SPEC, legado y parametros.
  - Prioridad: `P0`
  - Estimacion: `S`
  - Dependencias: `E1-T2`
  - Aceptacion: queda explicito el orden de precedencia entre `docs/SPEC.md`, `old-version/api-build.R`, `ParametrosPLD-v3.xlsx` y decisiones funcionales cerradas.

---

## E2. Base tecnica del repositorio

Prioridad: `P0`

### Historia E2-H1. Estructura inicial del proyecto

Resultado esperado:

- repositorio listo para iniciar desarrollo paralelo de frontend y backend

Tareas:

- [x] `E2-T1` Crear estructura base `backend/`, `frontend/` y `docs/`.
  - Prioridad: `P0`
  - Estimacion: `S`
  - Dependencias: `E1-T3`
  - Aceptacion: estructura creada segun SPEC §3.5: `backend/app/{api,application,domain,infrastructure,security,config}/main.py` y `frontend/src/{app,features,components,services,routes}`. Carpetas con archivos base y convenciones minimas.

- [x] `E2-T2` Inicializar backend con FastAPI, configuracion por entornos y comando local de arranque.
  - Prioridad: `P0`
  - Estimacion: `M`
  - Dependencias: `E2-T1`
  - Aceptacion: backend levanta localmente con endpoint `health` utilizando el stack y las decisiones vigentes documentadas en `docs/SPEC.md`. Incluye `ruff` y `pyproject.toml` base.

- [x] `E2-T3` Inicializar frontend web segun el stack definido en `E1-T3`.
  - Prioridad: `P0`
  - Estimacion: `M`
  - Dependencias: `E1-T3`, `E2-T1`
  - Aceptacion: el frontend elegido levanta localmente con pagina base y queda alineado con las restricciones de despliegue acordadas.

- [ ] `E2-T4` Configurar linting, formateo y chequeos basicos para frontend y backend.
  - Prioridad: `P1`
  - Estimacion: `M`
  - Dependencias: `E2-T2`, `E2-T3`
  - Aceptacion: existen comandos reproducibles de validacion y formato.

### Historia E2-H2. Entorno y configuracion

Resultado esperado:

- configuracion clara por entorno y secretos desacoplados del codigo

Tareas:

- [x] `E2-T5` Definir estrategia de configuracion por entorno.
  - Prioridad: `P0`
  - Estimacion: `S`
  - Dependencias: `E2-T2`
  - Aceptacion: variables y fuentes de configuracion documentadas para `development`, `test`, `staging`, `production`.

- [ ] `E2-T6` Crear archivos de ejemplo de entorno sin secretos reales.
  - Prioridad: `P1`
  - Estimacion: `S`
  - Dependencias: `E2-T5`
  - Aceptacion: existen plantillas de entorno para backend y frontend.

- [ ] `E2-T7` Definir estrategia de logs estructurados y request id.
  - Prioridad: `P1`
  - Estimacion: `S`
  - Dependencias: `E2-T2`
  - Aceptacion: backend genera logs consistentes con correlacion minima.

---

## E3. Persistencia y modelo de datos

Prioridad: `P0`

### Historia E3-H1. Modelo inicial SQLite compatible con SQL Server

Resultado esperado:

- esquema base estable para MVP y portable a SQL Server

Tareas:

- [x] `E3-T1` Diseñar modelo relacional inicial para usuarios, evaluaciones, solicitudes, historial y auditoria.
  - Prioridad: `P0`
  - Estimacion: `M`
  - Dependencias: `E1-T6`
  - Aceptacion: existe diagrama o documento con tablas, relaciones y campos clave, incluyendo snapshots minimos de inputs externos consumidos por el motor, `decision_traces`, `pipeline_strategies` y `pipeline_nodes`.

- [x] `E3-T1a` Incorporar soporte base para clasificar solicitudes y reglas por producto de prestamo.
  - Prioridad: `P0`
  - Estimacion: `S`
  - Dependencias: `E3-T1`
  - Aceptacion: el modelo inicial contempla `loan_product` o equivalente sin exigir reestructura futura del esquema base.

- [x] `E3-T2` Implementar modelos SQLAlchemy iniciales.
  - Prioridad: `P0`
  - Estimacion: `M`
  - Dependencias: `E3-T1`, `E2-T2`
  - Aceptacion: modelos cargan correctamente y reflejan el diseno definido.

- [x] `E3-T3` Configurar Alembic y crear migracion inicial.
  - Prioridad: `P0`
  - Estimacion: `M`
  - Dependencias: `E3-T2`
  - Aceptacion: la base SQLite puede crearse desde cero con migraciones.

- [ ] `E3-T4` Revisar compatibilidad del esquema con SQL Server.
  - Prioridad: `P1`
  - Estimacion: `S`
  - Dependencias: `E3-T3`
  - Aceptacion: quedan documentadas incompatibilidades y ajustes requeridos.

### Historia E3-H2. Parametros del motor

Resultado esperado:

- parametros de reglas desacoplados del Excel en runtime

Tareas:

- [x] `E3-T5` Diseñar tablas para versionado de parametros del motor.
  - Prioridad: `P0`
  - Estimacion: `S`
  - Dependencias: `E1-T2`, `E3-T1`
  - Aceptacion: existen tablas o estructuras definidas para `rule_set`, `parameter_version`, `pipeline_strategy` y aprobacion de cambios de flujo.

- [x] `E3-T5a` Diseñar persistencia de `DecisionTrace` y versionado de pipeline por evaluacion.
  - Prioridad: `P0`
  - Estimacion: `S`
  - Dependencias: `E3-T1`, `E1-T5b`
  - Aceptacion: el modelo define `decision_traces`, `pipeline_version` por evaluacion y su relacion con AI, auditoria y consulta de trazas.

- [x] `E3-T6` Definir mapeo entre `ParametrosPLD-v3.xlsx` y tablas nuevas.
  - Prioridad: `P0`
  - Estimacion: `M`
  - Dependencias: `E3-T5`
  - Aceptacion: existe documento de equivalencia por hoja, columna y destino.

- [ ] `E3-T7` Implementar carga semilla inicial de parametros.
  - Prioridad: `P1`
  - Estimacion: `M`
  - Dependencias: `E3-T6`, `E3-T3`
  - Aceptacion: la base puede poblarse con parametros base sin depender de Excel en ejecucion.

---

## E4. Seguridad y control de acceso

Prioridad: `P0`

### Historia E4-H1. Autenticacion

Resultado esperado:

- usuarios autenticados por mecanismo moderno y no por IP

Tareas:

- [x] `E4-T1` Seleccionar mecanismo de autenticacion definitivo.
  - Prioridad: `P0`
  - Estimacion: `S`
  - Dependencias: `E1-T3`
  - Aceptacion: queda decidido `SSO` o `login interno temporal`.

- [x] `E4-T2` Implementar base de autenticacion en backend.
  - Prioridad: `P0`
  - Estimacion: `L`
  - Dependencias: `E4-T1`, `E2-T2`, `E3-T3`
  - Aceptacion: backend identifica usuario autenticado de forma consistente.

- [ ] `E4-T3` Implementar flujo de sesion o integracion frontend de autenticacion.
  - Prioridad: `P1`
  - Estimacion: `M`
  - Dependencias: `E4-T2`, `E2-T3`
  - Aceptacion: frontend conoce sesion actual y puede proteger rutas.

### Historia E4-H2. Autorizacion y auditoria

Resultado esperado:

- permisos por rol y acciones auditables

Tareas:

- [x] `E4-T4` Definir matriz de permisos por rol.
  - Prioridad: `P0`
  - Estimacion: `S`
  - Dependencias: `E1-T3`
  - Aceptacion: matriz aprobada para consultar, evaluar, registrar, anular y cambiar estado.

- [x] `E4-T5` Implementar RBAC en backend.
  - Prioridad: `P0`
  - Estimacion: `M`
  - Dependencias: `E4-T4`, `E4-T2`
  - Aceptacion: endpoints restringen acceso segun rol.

- [ ] `E4-T6` Implementar auditoria de acciones sensibles.
  - Prioridad: `P1`
  - Estimacion: `M`
  - Dependencias: `E3-T3`, `E4-T5`
  - Aceptacion: quedan auditadas evaluacion, registro, anulacion, cambio de estado y carga de parametros. Cada registro de auditoria incluye los campos de SPEC §4.5: usuario, rol, accion, entidad afectada, resultado, IP origen, request ID y trazabilidad IA si aplica.

- [ ] `E4-T7` Configurar controles de seguridad.
  - Prioridad: `P1`
  - Estimacion: `S`
  - Dependencias: `E2-T2`
  - Aceptacion: backend aplica HTTPS en entornos no locales, CORS restringido, validacion CSRF si aplica, proteccion contra SQL injection, almacenamiento seguro de secretos, rate limiting y cabeceras de seguridad (SPEC §4.4).

---

## E5. Motor de decisiones PLD

Prioridad: `P0`

### Historia E5-H1. Diseno desacoplado del motor

Resultado esperado:

- motor de decisiones independiente de FastAPI y de la UI

Tareas:

- [x] `E5-T1` Definir modelos de entrada y salida del motor.
  - Prioridad: `P0`
  - Estimacion: `S`
  - Dependencias: `E1-T5`
  - Aceptacion: contratos implementados y validados por pruebas, incluyendo versionado de reglas, parametros y pipeline.

- [x] `E5-T1a` Definir modelo estructurado de `DecisionTrace`.
  - Prioridad: `P0`
  - Estimacion: `S`
  - Dependencias: `E1-T5b`, `E5-T1`
  - Aceptacion: `DecisionTrace` define etapas o nodos ejecutados, versiones aplicadas, bloqueos, alertas y evidencia consumible por AI y auditoria humana.

- [x] `E5-T2` Crear modulo `decision_engine` con contratos internos de nodos, calculo y respuesta.
  - Prioridad: `P0`
  - Estimacion: `M`
  - Dependencias: `E5-T1`, `E2-T2`
  - Aceptacion: modulo aislado importable sin dependencias web. El motor expone funciones `async` para soportar peticiones concurrentes (SPEC §5.2).

- [x] `E5-T2b` Implementar orquestador base de `DecisionNode` con seleccion de `pipeline_strategy`.
  - Prioridad: `P0`
  - Estimacion: `M`
  - Dependencias: `E5-T2`, `E3-T5`
  - Aceptacion: el motor ejecuta nodos segun una estrategia versionada por producto, con branching controlado y validacion de topologia.

- [x] `E5-T2a` Diseñar el motor para seleccionar reglas por producto o conjunto de reglas.
  - Prioridad: `P0`
  - Estimacion: `S`
  - Dependencias: `E5-T2`
  - Aceptacion: la estructura del motor no asume que PLD sera el unico producto soportado.

- [ ] `E5-T3` Implementar versionado de reglas y parametros aplicados.
  - Prioridad: `P1`
  - Estimacion: `M`
  - Dependencias: `E3-T5`, `E5-T2`
  - Aceptacion: cada evaluacion expone `rule_set_version`, `parameter_version` y `pipeline_version`.

- [ ] `E5-T3a` Persistir `DecisionTrace` por evaluacion.
  - Prioridad: `P1`
  - Estimacion: `M`
  - Dependencias: `E3-T5a`, `E5-T1a`, `E5-T2b`
  - Aceptacion: cada evaluacion persiste una traza estructurada reutilizable por AI, auditoria y soporte operativo.

### Historia E5-H2. Reglas de negocio y formulas

Resultado esperado:

- calculo equivalente o intencionalmente ajustado respecto al legado

Tareas:

- [x] `E5-T4` Implementar normalizacion de entrada del flujo PLD.
  - Prioridad: `P0`
  - Estimacion: `S`
  - Dependencias: `E5-T2`
  - Aceptacion: entradas inconsistentes se transforman o rechazan de forma controlada.

- [ ] `E5-T5` Implementar reglas de elegibilidad y marcas de segmento.
  - Prioridad: `P0`
  - Estimacion: `M`
  - Dependencias: `E5-T4`, `E3-T7`
  - Aceptacion: motor reproduce marcas equivalentes para los casos canonicos.

- [ ] `E5-T6` Implementar calculo de RCI, oferta, cuota, tasa y plazo.
  - Prioridad: `P0`
  - Estimacion: `L`
  - Dependencias: `E5-T5`
  - Aceptacion: resultados comparables con la logica de `validate2` para casos de prueba definidos.

- [ ] `E5-T7` Implementar bloqueos y alertas de solicitud.
  - Prioridad: `P0`
  - Estimacion: `M`
  - Dependencias: `E5-T6`
  - Aceptacion: se reflejan restricciones como ingreso minimo, RCI maximo, oferta minima y monto solicitado.

- [ ] `E5-T8` Crear suite de pruebas de regresion del motor contra casos extraidos del legado.
  - Prioridad: `P0`
  - Estimacion: `L`
  - Dependencias: `E5-T6`, `E5-T7`
  - Aceptacion: existe bateria automatizada con casos representativos y resultados esperados.

---

## E6. Backend de casos de uso PLD

Prioridad: `P0`

### Historia E6-H1. Consulta de cliente y campanas

Resultado esperado:

- API de consulta PLD operativa y desacoplada de HTML

Tareas:

- [ ] `E6-T1` Definir servicio de consulta de cliente PLD.
  - Prioridad: `P0`
  - Estimacion: `S`
  - Dependencias: `E1-T4`, `E3-T3`
  - Aceptacion: servicio retorna datos de cliente y campanas en contrato estable.

- [ ] `E6-T2` Implementar endpoint `POST /api/v1/loans/{product_code}/consultas`.
  - Prioridad: `P0`
  - Estimacion: `M`
  - Dependencias: `E6-T1`, `E4-T5`
  - Aceptacion: endpoint devuelve datos esperados con errores estructurados.

### Historia E6-H2. Evaluacion PLD

Resultado esperado:

- API capaz de ejecutar evaluacion usando el motor aislado

Tareas:

- [ ] `E6-T3` Definir caso de uso de evaluacion.
  - Prioridad: `P0`
  - Estimacion: `S`
  - Dependencias: `E5-T8`
  - Aceptacion: caso de uso documentado y probado.

- [ ] `E6-T4` Implementar endpoint `POST /api/v1/loans/{product_code}/evaluaciones`.
  - Prioridad: `P0`
  - Estimacion: `M`
  - Dependencias: `E6-T3`, `E4-T5`
  - Aceptacion: endpoint persiste la evaluacion, la traza estructurada y retorna salida del motor.

- [ ] `E6-T4a` Implementar endpoint `GET /api/v1/loans/{product_code}/evaluaciones/{evaluation_id}/trace`.
  - Prioridad: `P1`
  - Estimacion: `S`
  - Dependencias: `E6-T4`, `E5-T3a`
  - Aceptacion: el endpoint retorna `DecisionTrace` estructurado con control de acceso y contrato estable para AI y auditoria humana.

### Historia E6-H3. Registro de solicitud

Resultado esperado:

- solicitud registrada con validaciones y trazabilidad

Tareas:

- [ ] `E6-T5` Implementar reglas de registro de solicitud usando salida del motor.
  - Prioridad: `P0`
  - Estimacion: `M`
  - Dependencias: `E5-T7`, `E3-T3`
  - Aceptacion: servicio rechaza y acepta solicitudes segun reglas definidas.

- [ ] `E6-T6` Implementar endpoint `POST /api/v1/loans/{product_code}/solicitudes`.
  - Prioridad: `P0`
  - Estimacion: `M`
  - Dependencias: `E6-T5`, `E4-T5`
  - Aceptacion: endpoint crea solicitud con estado inicial y registra auditoria.

### Historia E6-H4. Bandeja operativa

Resultado esperado:

- consulta y mantenimiento de solicitudes desde API

Tareas:

- [ ] `E6-T7` Implementar servicio de listado paginado y filtrado de solicitudes.
  - Prioridad: `P1`
  - Estimacion: `M`
  - Dependencias: `E6-T6`
  - Aceptacion: servicio filtra por periodo y otros campos basicos.

- [ ] `E6-T8` Implementar endpoint `GET /api/v1/loans/{product_code}/solicitudes`.
  - Prioridad: `P1`
  - Estimacion: `S`
  - Dependencias: `E6-T7`
  - Aceptacion: endpoint retorna bandeja desacoplada de HTML.

- [ ] `E6-T9` Implementar endpoint `POST /api/v1/loans/{product_code}/solicitudes/{id}/anular`.
  - Prioridad: `P1`
  - Estimacion: `S`
  - Dependencias: `E6-T6`, `E4-T5`
  - Aceptacion: solicitud cambia a estado anulado o equivalente con historial.

- [ ] `E6-T10` Implementar endpoint `POST /api/v1/loans/{product_code}/solicitudes/{id}/estado`.
  - Prioridad: `P1`
  - Estimacion: `S`
  - Dependencias: `E6-T6`, `E4-T5`
  - Aceptacion: estado cambia solo por roles autorizados y queda historizado.

- [ ] `E6-T11` Implementar endpoint `GET /api/v1/loans/{product_code}/solicitudes/export`.
  - Prioridad: `P1`
  - Estimacion: `M`
  - Dependencias: `E6-T8`
  - Aceptacion: exporta resultados en formato acordado sin depender del DOM.

- [ ] `E6-T12` Implementar endpoints de carga, listado y descarga de adjuntos ZIP por solicitud.
  - Prioridad: `P1`
  - Estimacion: `M`
  - Dependencias: `E6-T6`, `E4-T5`
  - Aceptacion: el backend permite cargar, listar y descargar ZIPs asociados a una solicitud utilizando `filesystem`, con control de acceso y trazabilidad.

---

## E7. Frontend del flujo PLD

Prioridad: `P1`

### Historia E7-H1. Base de aplicacion

Resultado esperado:

- aplicacion navegable con layout y manejo de sesion

Tareas:

- [ ] `E7-T1` Definir layout base, rutas y proveedor de estado de sesion.
  - Prioridad: `P1`
  - Estimacion: `M`
  - Dependencias: `E2-T3`, `E4-T3`
  - Aceptacion: app tiene estructura base, rutas protegidas y manejo de sesion.

- [ ] `E7-T2` Definir sistema visual inicial y componentes compartidos.
  - Prioridad: `P2`
  - Estimacion: `M`
  - Dependencias: `E2-T3`
  - Aceptacion: existen componentes base para formulario, tabla, alerta, badge y modal.

### Historia E7-H2. Pantalla de consulta y evaluacion

Resultado esperado:

- analista puede consultar y evaluar sin acoplamiento a tablas HTML

Tareas:

- [ ] `E7-T3` Implementar formulario de consulta PLD.
  - Prioridad: `P1`
  - Estimacion: `M`
  - Dependencias: `E6-T2`
  - Aceptacion: usuario consulta por documento y visualiza datos y campanas.

- [ ] `E7-T4` Implementar seleccion de campana y formulario de evaluacion.
  - Prioridad: `P1`
  - Estimacion: `M`
  - Dependencias: `E7-T3`, `E6-T4`
  - Aceptacion: usuario puede enviar datos complementarios al endpoint de evaluacion.

- [ ] `E7-T5` Implementar visualizacion estructurada de resultado de evaluacion.
  - Prioridad: `P1`
  - Estimacion: `M`
  - Dependencias: `E7-T4`
  - Aceptacion: resultado muestra oferta, RCI, alertas, bloqueos y version de reglas.

### Historia E7-H3. Registro y bandeja

Resultado esperado:

- solicitudes registradas y operadas desde UI moderna

Tareas:

- [ ] `E7-T6` Implementar formulario de registro de solicitud.
  - Prioridad: `P1`
  - Estimacion: `M`
  - Dependencias: `E6-T6`, `E7-T5`
  - Aceptacion: usuario registra solicitud desde una evaluacion valida.

- [ ] `E7-T7` Implementar pantalla de bandeja con filtros.
  - Prioridad: `P1`
  - Estimacion: `M`
  - Dependencias: `E6-T8`
  - Aceptacion: bandeja lista solicitudes por periodo y estado.

- [ ] `E7-T8` Implementar acciones de anular y cambiar estado segun rol.
  - Prioridad: `P1`
  - Estimacion: `M`
  - Dependencias: `E6-T9`, `E6-T10`, `E7-T7`
  - Aceptacion: UI habilita solo acciones permitidas y refleja cambios correctamente.

- [ ] `E7-T9` Implementar exportacion de bandeja.
  - Prioridad: `P1`
  - Estimacion: `S`
  - Dependencias: `E6-T11`, `E7-T7`
  - Aceptacion: usuario descarga el archivo acordado desde UI.

### Historia E7-H4. Adjuntos ZIP

Resultado esperado:

- usuarios autorizados gestionan adjuntos ZIP desde la solicitud

Tareas:

- [ ] `E7-T10` Implementar componentes frontend para carga, listado y descarga de ZIP.
  - Prioridad: `P1`
  - Estimacion: `M`
  - Dependencias: `E6-T12`, `E7-T6`
  - Aceptacion: el usuario autorizado puede cargar, listar y descargar ZIPs desde la UI de solicitud.

---

## E8. Migracion de parametros y datos legacy

Prioridad: `P1`

### Historia E8-H1. Parametros desde Excel

Resultado esperado:

- parametros legacy transformados a formato estable del sistema nuevo

Tareas:

- [ ] `E8-T1` Analizar hojas y columnas de `ParametrosPLD-v3.xlsx`.
  - Prioridad: `P1`
  - Estimacion: `M`
  - Dependencias: `E3-T6`
  - Aceptacion: documento de mapeo validado con negocio o usuario.

- [ ] `E8-T2` Implementar importador controlado de parametros desde Excel.
  - Prioridad: `P2`
  - Estimacion: `L`
  - Dependencias: `E8-T1`, `E3-T7`
  - Aceptacion: importador valida estructura, carga datos y versiona el lote.

### Historia E8-H2. Historicos

Resultado esperado:

- estrategia cerrada de base limpia y uso referencial del legacy

Tareas:

- [ ] `E8-T3` Documentar estrategia de base limpia y rol referencial del legado.
  - Prioridad: `P1`
  - Estimacion: `S`
  - Dependencias: `E1-T3`
  - Aceptacion: queda documentado que el MVP inicia con base limpia y que `old-version/API_DB.db` se usa solo como referencia funcional o analitica.

- [ ] `E8-T4` Documentar guia de consulta del legacy para validacion funcional y contraste de casos.
  - Prioridad: `P2`
  - Estimacion: `S`
  - Dependencias: `E8-T3`
  - Aceptacion: existe una guia corta para consultar datos legacy con fines de contraste sin convertirla en dependencia runtime del nuevo sistema.

---

## E9. Calidad, pruebas y observabilidad

Prioridad: `P0`

### Historia E9-H1. Pruebas automatizadas

Resultado esperado:

- cobertura razonable del motor y de los endpoints criticos

Tareas:

- [ ] `E9-T1` Configurar framework de pruebas backend.
  - Prioridad: `P0`
  - Estimacion: `S`
  - Dependencias: `E2-T2`
  - Aceptacion: backend ejecuta pruebas automatizadas localmente.

- [ ] `E9-T2` Configurar framework de pruebas frontend.
  - Prioridad: `P1`
  - Estimacion: `S`
  - Dependencias: `E2-T3`
  - Aceptacion: frontend ejecuta pruebas base localmente.

- [ ] `E9-T3` Implementar pruebas unitarias del motor.
  - Prioridad: `P0`
  - Estimacion: `L`
  - Dependencias: `E5-T8`, `E9-T1`
  - Aceptacion: formulas, bloqueos criticos, versionado de pipeline y generacion de `DecisionTrace` quedan cubiertos.

- [ ] `E9-T4` Implementar pruebas de integracion de API.
  - Prioridad: `P0`
  - Estimacion: `L`
  - Dependencias: `E6-T10`, `E9-T1`
  - Aceptacion: consulta, evaluacion, consulta de traza, registro y cambio de estado tienen pruebas de integracion.

- [ ] `E9-T5` Implementar pruebas E2E del flujo MVP.
  - Prioridad: `P1`
  - Estimacion: `L`
  - Dependencias: `E7-T8`, `E9-T2`
  - Aceptacion: existe al menos un flujo automatizado punta a punta.

### Historia E9-H2. Observabilidad

Resultado esperado:

- visibilidad minima del comportamiento del sistema

Tareas:

- [ ] `E9-T6` Implementar endpoint de health check y readiness.
  - Prioridad: `P1`
  - Estimacion: `S`
  - Dependencias: `E2-T2`
  - Aceptacion: existen endpoints de verificacion operativa.

- [ ] `E9-T7` Medir eventos clave en logs o metricas.
  - Prioridad: `P2`
  - Estimacion: `M`
  - Dependencias: `E2-T7`, `E4-T6`
  - Aceptacion: se registran al menos consulta, evaluacion, registro y error de negocio.

---

## E10. Despliegue y operacion

Prioridad: `P1`

### Historia E10-H1. Empaquetado y ejecucion

Resultado esperado:

- proyecto desplegable de forma repetible

Tareas:

- [ ] `E10-T1` Definir estrategia de ejecucion local y de despliegue.
  - Prioridad: `P1`
  - Estimacion: `S`
  - Dependencias: `E1-T3`
  - Aceptacion: queda decidido si se usara Docker, servicios directos o ambos.

- [ ] `E10-T2` Crear configuracion base de despliegue para backend y frontend.
  - Prioridad: `P1`
  - Estimacion: `M`
  - Dependencias: `E10-T1`, `E2-T2`, `E2-T3`
  - Aceptacion: existe receta reproducible de arranque por entorno no productivo.

- [ ] `E10-T3` Crear pipeline CI minima.
  - Prioridad: `P1`
  - Estimacion: `M`
  - Dependencias: `E2-T4`, `E9-T1`, `E9-T2`
  - Aceptacion: pipeline ejecuta lint y pruebas basicas en cada cambio.

### Historia E10-H2. Salida a produccion

Resultado esperado:

- checklist claro de paso a produccion

Tareas:

- [ ] `E10-T4` Definir checklist de salida a produccion.
  - Prioridad: `P1`
  - Estimacion: `S`
  - Dependencias: `E4-T7`, `E9-T5`, `E10-T2`
  - Aceptacion: checklist incluye seguridad, migraciones, rollback y monitoreo.

- [ ] `E10-T5` Documentar operacion basica y soporte inicial.
  - Prioridad: `P2`
  - Estimacion: `S`
  - Dependencias: `E10-T4`
  - Aceptacion: existe guia corta de arranque, diagnostico y recuperacion basica.

---

## E11. Preparacion multiproducto

Prioridad: `P1`

### Historia E11-H1. Base extensible de plataforma

Resultado esperado:

- la plataforma queda preparada para soportar nuevos tipos de prestamo sin reescritura de sus modulos compartidos

Tareas:

- [ ] `E11-T1` Definir nomenclatura compartida de dominio para productos de prestamo.
  - Prioridad: `P2`
  - Estimacion: `S`
  - Dependencias: `E1-T3a`
  - Aceptacion: los modulos compartidos usan terminologia neutral y no cerrada a PLD.

- [ ] `E11-T2` Definir estrategia de incorporacion de nuevos productos sobre el mismo motor y API.
  - Prioridad: `P1`
  - Estimacion: `M`
  - Dependencias: `E5-T2a`, `E3-T1a`
  - Aceptacion: existe una propuesta tecnica de extension sin romper contratos base ni seguridad compartida.

- [ ] `E11-T3` Validar onboarding tecnico de un segundo producto sobre el pipeline configurable.
  - Prioridad: `P1`
  - Estimacion: `M`
  - Dependencias: `E11-T2`, `E14-T7`
  - Aceptacion: existe evidencia tecnica de que un segundo producto puede configurarse con contratos compartidos, estrategia de pipeline propia y sin reestructurar el motor base.

---

## E12. Capacidades AI asistivas

Prioridad: `P1`

### Historia E12-H1. Fundaciones AI y Arquitectura

Resultado esperado:
- la arquitectura de la aplicacion soporta la integracion de LLMs de manera segura, aislada y auditable

Tareas:
- [x] `E12-T1` Definir politicas de seguridad y privacidad de datos para la capa de IA (minimizar/anonimizar datos sensibles).
  - Prioridad: `P0`
  - Estimacion: `S`
  - Dependencias: `E1-T3`
  - Aceptacion: existe un documento de politicas aprobado que define que datos del cliente pueden enviarse al LLM.
- [x] `E12-T2` Diseñar e implementar el modelo de datos para `ai_interactions` y `ai_prompt_templates`.
  - Prioridad: `P1`
  - Estimacion: `S`
  - Dependencias: `E3-T3`
  - Aceptacion: la base SQLite cuenta con las tablas necesarias y sus relaciones con evaluaciones y solicitudes.
- [x] `E12-T3` Implementar modulo backend cliente para conexion con LLM con manejo de timeouts, reintentos y seleccion configurable de proveedor activo.
  - Prioridad: `P1`
  - Estimacion: `M`
  - Dependencias: `E2-T2`
  - Aceptacion: servicio backend realiza llamadas de prueba al modelo de forma segura usando variables de entorno y permite seleccionar `OpenAI` o `Gemini` por configuracion externa.

### Historia E12-H2. Explicacion de evaluacion PLD (MVP)

Resultado esperado:
- el sistema genera explicaciones textuales precisas a partir de la salida estructurada de la evaluacion PLD

Tareas:
- [ ] `E12-T4` Diseñar prompts del sistema y plantillas estructuradas de contexto para el flujo de explicacion.
  - Prioridad: `P1`
  - Estimacion: `S`
  - Dependencias: `E12-T1`, `E5-T1`
  - Aceptacion: prompts escritos y probados que inyectan de forma estricta los indicadores del motor y restringen la alucinacion.
- [ ] `E12-T5` Implementar el endpoint `POST /api/v1/loans/{product_code}/evaluaciones/{evaluation_id}/explain`.
  - Prioridad: `P1`
  - Estimacion: `M`
  - Dependencias: `E6-T4`, `E12-T3`, `E12-T4`
  - Aceptacion: el endpoint consume la evaluacion, genera la explicacion, la persiste en `ai_interactions` y retorna el JSON correspondiente.
- [ ] `E12-T6` Desarrollar el componente UI en el frontend para visualizar la explicacion del caso y las sugerencias de accion.
  - Prioridad: `P1`
  - Estimacion: `M`
  - Dependencias: `E7-T5`, `E12-T5`
  - Aceptacion: panel colapsable visible tras evaluar, con texto claro, disclaimers y boton de re-intento ante errores de API.

### Historia E12-H3. Asistencia al registro e interacciones operativas (MVP)

Resultado esperado:
- capacidades AI operativas del MVP implementadas de forma auditable

Tareas:
- [ ] `E12-T7` Desarrollar logica de asistencia en el registro (consistencia de comentarios, alertas de omision).
  - Prioridad: `P1`
  - Estimacion: `M`
  - Dependencias: `E6-T6`, `E12-T3`
  - Aceptacion: endpoint `POST /api/v1/loans/{product_code}/solicitudes/{request_id}/assist` devuelve advertencias operativas si el comentario no sustenta adecuadamente el desvio.
- [ ] `E12-T8` Desarrollar briefing automatizado de bandeja de solicitudes.
  - Prioridad: `P1`
  - Estimacion: `M`
  - Dependencias: `E6-T8`, `E12-T3`
  - Aceptacion: endpoint `POST /api/v1/loans/{product_code}/bandeja/summary` genera resumen de la bandeja operativa para supervisores.

---

## E13. Event Sourcing de Decisiones

Prioridad: `P1`

### Historia E13-H1. Implementacion del event store

Resultado esperado:
- cada evaluacion y cambio de estado se persiste como evento inmutable

Tareas:
- [ ] `E13-T1` Diseñar e implementar el modelo de datos para `decision_events`.
  - Prioridad: `P1`
  - Estimacion: `S`
  - Dependencias: `E3-T3`
  - Aceptacion: tabla `decision_events` creada con indices y FK.
- [ ] `E13-T2` Implementar el servicio de event store con escritura de eventos y consulta por agregado.
  - Prioridad: `P1`
  - Estimacion: `M`
  - Dependencias: `E13-T1`, `E6-T3`
  - Aceptacion: cada evaluacion y cambio de estado genera un evento inmutable. Se puede consultar el timeline de un agregado.
- [ ] `E13-T3` Implementar endpoints de consulta de eventos (`GET /api/v1/events` y `GET /api/v1/events/{aggregate_id}/timeline`).
  - Prioridad: `P2`
  - Estimacion: `M`
  - Dependencias: `E13-T2`, `E4-T5`
  - Aceptacion: los endpoints retornan eventos ordenados con paginacion.

### Historia E13-H2. DecisionTrace de evaluaciones

Resultado esperado:
- cada evaluacion deja una traza estructurada consumible por AI y auditoria humana

Tareas:
- [ ] `E13-T4` Diseñar e implementar el modelo de datos para `decision_traces`.
  - Prioridad: `P1`
  - Estimacion: `S`
  - Dependencias: `E3-T5a`
  - Aceptacion: tabla o estructura `decision_traces` creada con relacion a evaluaciones y version de pipeline.
- [ ] `E13-T5` Implementar persistencia y consulta de `DecisionTrace` por evaluacion.
  - Prioridad: `P1`
  - Estimacion: `M`
  - Dependencias: `E13-T4`, `E6-T4`
  - Aceptacion: la traza se persiste al evaluar y puede consultarse por API con permisos adecuados.

---

## E14. Business Rules Management System (BRMS)

Prioridad: `P1`

### Historia E14-H1. Catalogacion y versionado de reglas

Resultado esperado:
- las reglas de negocio se almacenan en base de datos con versionado completo

Tareas:
- [ ] `E14-T1` Diseñar el modelo de datos para `rule_sets` y `rule_versions`.
  - Prioridad: `P1`
  - Estimacion: `M`
  - Dependencias: `E3-T3`
  - Aceptacion: tablas creadas con relaciones, indices y soporte para versionado y vigencia.
- [ ] `E14-T2` Implementar servicio de BRMS (CRUD de reglas, versionado, activacion/desactivacion).
  - Prioridad: `P1`
  - Estimacion: `L`
  - Dependencias: `E14-T1`
  - Aceptacion: el servicio permite crear, versionar, activar y desactivar conjuntos de reglas por producto.
- [ ] `E14-T3` Implementar endpoints de administracion de reglas.
  - Prioridad: `P2`
  - Estimacion: `M`
  - Dependencias: `E14-T2`, `E4-T5`
  - Aceptacion: CRUD completo de rule-sets y rule-versions disponible via API.
- [ ] `E14-T4` Migrar las reglas PLD actuales a la nueva estructura de rule_sets y rule_versions.
  - Prioridad: `P1`
  - Estimacion: `L`
  - Dependencias: `E14-T2`, `ISSUE-011`
  - Aceptacion: todas las reglas del motor PLD migradas a la nueva estructura y funcionando en pipeline.

### Historia E14-H2. Pipeline configurable por nodos

Resultado esperado:
- el motor de decisiones ejecuta un pipeline configurable por nodos gobernados

Tareas:
- [ ] `E14-T5` Definir la interfaz `DecisionNode` y el orquestador de pipeline.
  - Prioridad: `P1`
  - Estimacion: `M`
  - Dependencias: `E5-T1`
  - Aceptacion: interfaz definida, orquestador que ejecuta nodos con branching controlado, manejo de errores, rollback y validacion de topologia.
- [ ] `E14-T6` Refactorizar las reglas actuales del motor en 5 nodos base del pipeline (Preprocessing, Eligibility, Scoring, Decision Strategy, Post-processing).
  - Prioridad: `P1`
  - Estimacion: `XL`
  - Dependencias: `E14-T4`, `E14-T5`
  - Aceptacion: el motor ejecuta el pipeline completo para PLD, produce resultados equivalentes al actual y emite `DecisionTrace` estructurado.
- [ ] `E14-T7` Implementar tablas `pipeline_strategies` y `pipeline_nodes` y logica de seleccion de pipeline por producto.
  - Prioridad: `P2`
  - Estimacion: `M`
  - Dependencias: `E14-T6`
  - Aceptacion: cada producto puede definir su propio pipeline de nodos con orden, branching permitido y configuracion versionada.

- [ ] `E14-T7a` Implementar validacion de topologia y aprobacion de cambios de flujo.
  - Prioridad: `P1`
  - Estimacion: `M`
  - Dependencias: `E14-T7`, `E4-T5`
  - Aceptacion: ningun pipeline puede activarse sin pasar validaciones estructurales y sin aprobacion de supervisor cuando aplique.

### Historia E14-H3. UI Administrativa de Reglas y Flujo

Resultado esperado:
- administradores pueden gestionar reglas desde una interfaz web

Tareas:
- [ ] `E14-T8` Disenar e implementar el modulo frontend de administracion de reglas (CRUD basico).
  - Prioridad: `P1`
  - Estimacion: `L`
  - Dependencias: `E14-T3`, `E7-T1`
  - Aceptacion: admin puede listar, crear, editar y versionar reglas desde la UI.
- [ ] `E14-T9` Implementar sandbox de pruebas de reglas en la UI.
  - Prioridad: `P1`
  - Estimacion: `L`
  - Dependencias: `E14-T8`
  - Aceptacion: admin puede seleccionar casos de prueba historicos y simular el impacto de cambios en reglas y en flujo antes de activarlos.
- [ ] `E14-T10` Implementar flujo de aprobacion de cambios de reglas y flujo.
  - Prioridad: `P1`
  - Estimacion: `M`
  - Dependencias: `E14-T8`, `E4-T5`
  - Aceptacion: cambios a reglas activas y a pipelines activos requieren aprobacion de supervisor antes de aplicarse.

- [ ] `E14-T11` Implementar UI gobernada para administracion de `pipeline_strategies` y `pipeline_nodes`.
  - Prioridad: `P1`
  - Estimacion: `L`
  - Dependencias: `E14-T8`, `E14-T7`
  - Aceptacion: admin puede visualizar, editar y versionar la secuencia del flujo por producto sin crear grafos invalidos.

---

## 4. Backlog minimo del MVP

Las siguientes tareas forman el camino minimo para entregar el MVP:

- `E1-T1`
- `E1-T2`
- `E1-T3`
- `E1-T4`
- `E1-T5`
- `E1-T5b`
- `E1-T5c`
- `E1-T6`
- `E1-T6b`
- `E1-T6c`
- `E1-T6d`
- `E1-T7`
- `E2-T1`
- `E2-T2`
- `E2-T3`
- `E2-T7`
- `E2-T5`
- `E3-T1`
- `E3-T2`
- `E3-T3`
- `E3-T5`
- `E3-T5a`
- `E3-T6`
- `E3-T7`
- `E4-T1`
- `E4-T2`
- `E4-T3`
- `E4-T4`
- `E4-T5`
- `E4-T6`
- `E4-T7`
- `E5-T1`
- `E5-T1a`
- `E5-T2`
- `E5-T2b`
- `E5-T3a`
- `E5-T4`
- `E5-T5`
- `E5-T6`
- `E5-T7`
- `E5-T8`
- `E6-T1`
- `E6-T2`
- `E6-T3`
- `E6-T4`
- `E6-T4a`
- `E6-T5`
- `E6-T6`
- `E6-T7`
- `E6-T8`
- `E6-T9`
- `E6-T10`
- `E6-T11`
- `E6-T12`
- `E7-T1`
- `E7-T3`
- `E7-T4`
- `E7-T5`
- `E7-T6`
- `E7-T7`
- `E7-T8`
- `E7-T9`
- `E7-T10`
- `E8-T1`
- `E8-T2`
- `E8-T3`
- `E8-T4`
- `E9-T1`
- `E9-T2`
- `E9-T3`
- `E9-T4`
- `E9-T5`
- `E9-T6`
- `E10-T1`
- `E10-T2`
- `E10-T3`
- `E10-T4`
- `E12-T1`
- `E12-T2`
- `E12-T3`
- `E12-T4`
- `E12-T5`
- `E12-T6`
- `E12-T7`
- `E12-T8`
- `E13-T1`
- `E13-T2`
- `E13-T4`
- `E13-T5`
- `E14-T1`
- `E14-T2`
- `E14-T3`
- `E14-T4`
- `E14-T5`
- `E14-T6`
- `E14-T7`
- `E14-T7a`
- `E14-T8`
- `E14-T9`
- `E14-T10`
- `E14-T11`
- `E11-T1`
- `E11-T2`
- `E11-T3`

---

## 5. Backlog posterior al MVP

Tareas candidatas para una segunda fase:

- `E2-T4`
- `E2-T6`
- `E3-T4`
- `E5-T3`
- `E7-T2`
- `E9-T7`
- `E10-T5`
- `E13-T3`

---

## 6. Bloqueos abiertos

No conviene iniciar implementaciones sensibles sin resolver:

- mecanismo definitivo de autenticacion
- decision de frontend segun facilidades reales de despliegue
- contratos de inputs externos y snapshot minimo consumido por el motor
- fuente oficial de reglas si difiere del legado
- lineamientos corporativos de despliegue y seguridad

---

## 7. Siguiente corte recomendado

Primer sprint tecnico sugerido:

1. `E1-T1` a `E1-T7`
2. `E2-T1`, `E2-T2`, `E2-T3`, `E2-T5`
3. `E3-T1`, `E3-T2`, `E3-T3`
4. `E5-T1`, `E5-T2`

Con ese corte queda lista la base para empezar la implementacion real del flujo PLD.
