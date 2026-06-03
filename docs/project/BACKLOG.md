# BACKLOG - Decision Engine PLD

## 0. Proposito

Este backlog convierte `SPEC.md` en un plan de ejecucion tecnico. No reemplaza la especificacion original: la descompone en epicas, historias, tareas y criterios de aceptacion para construir el nuevo sistema `PLD / solicitudes de credito`.

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

- [ ] `E1-T1` Documentar flujo PLD actual de punta a punta desde `old-version/api-build.R` y `old-version/script.js`.
  - Prioridad: `P0`
  - Estimacion: `M`
  - Dependencias: ninguna
  - Aceptacion: existe mapa de flujo con consulta, evaluacion, registro, bandeja, anulacion y cambio de estado.

- [ ] `E1-T2` Listar reglas de negocio observadas en `validate1`, `validate2` y `grabasol`.
  - Prioridad: `P0`
  - Estimacion: `M`
  - Dependencias: `E1-T1`
  - Aceptacion: existe catalogo de reglas con nombre, descripcion, entrada, salida y condicion de bloqueo o alerta.

- [ ] `E1-T3` Confirmar decisiones abiertas del SPEC con negocio o usuario.
  - Prioridad: `P0`
  - Estimacion: `M`
  - Dependencias: `E1-T1`
  - Aceptacion: quedan resueltas al menos autenticacion, frontend, ZIP, historicos y modo de despliegue del motor.

### Historia E1-H2. Definir contratos iniciales

Resultado esperado:

- contratos claros para evaluar, registrar y consultar solicitudes

Tareas:

- [ ] `E1-T4` Definir payload de consulta PLD.
  - Prioridad: `P0`
  - Estimacion: `S`
  - Dependencias: `E1-T1`
  - Aceptacion: contrato documentado con campos, tipos, validaciones y errores esperados.

- [ ] `E1-T5` Definir payload de evaluacion del motor.
  - Prioridad: `P0`
  - Estimacion: `S`
  - Dependencias: `E1-T2`
  - Aceptacion: contrato documentado independiente de UI y de indices de tabla.

- [ ] `E1-T6` Definir payload de registro de solicitud y de cambio de estado.
  - Prioridad: `P0`
  - Estimacion: `S`
  - Dependencias: `E1-T2`
  - Aceptacion: contratos aprobados y alineados con modelo de datos previsto.

---

## E2. Base tecnica del repositorio

Prioridad: `P0`

### Historia E2-H1. Estructura inicial del proyecto

Resultado esperado:

- repositorio listo para iniciar desarrollo paralelo de frontend y backend

Tareas:

- [ ] `E2-T1` Crear estructura base `backend/`, `frontend/` y `docs/`.
  - Prioridad: `P0`
  - Estimacion: `S`
  - Dependencias: `E1-T3`
  - Aceptacion: carpetas creadas con archivos base y convenciones minimas.

- [ ] `E2-T2` Inicializar backend con FastAPI, configuracion por entornos y comando local de arranque.
  - Prioridad: `P0`
  - Estimacion: `M`
  - Dependencias: `E2-T1`
  - Aceptacion: backend levanta localmente con endpoint `health`.

- [ ] `E2-T3` Inicializar frontend con React, TypeScript y Vite.
  - Prioridad: `P0`
  - Estimacion: `M`
  - Dependencias: `E1-T3`, `E2-T1`
  - Aceptacion: frontend levanta localmente con pagina base.

- [ ] `E2-T4` Configurar linting, formateo y chequeos basicos para frontend y backend.
  - Prioridad: `P1`
  - Estimacion: `M`
  - Dependencias: `E2-T2`, `E2-T3`
  - Aceptacion: existen comandos reproducibles de validacion y formato.

### Historia E2-H2. Entorno y configuracion

Resultado esperado:

- configuracion clara por entorno y secretos desacoplados del codigo

Tareas:

- [ ] `E2-T5` Definir estrategia de configuracion por entorno.
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

- [ ] `E3-T1` Diseñar modelo relacional inicial para usuarios, evaluaciones, solicitudes, historial y auditoria.
  - Prioridad: `P0`
  - Estimacion: `M`
  - Dependencias: `E1-T6`
  - Aceptacion: existe diagrama o documento con tablas, relaciones y campos clave.

- [ ] `E3-T2` Implementar modelos SQLAlchemy iniciales.
  - Prioridad: `P0`
  - Estimacion: `M`
  - Dependencias: `E3-T1`, `E2-T2`
  - Aceptacion: modelos cargan correctamente y reflejan el diseno definido.

- [ ] `E3-T3` Configurar Alembic y crear migracion inicial.
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

- [ ] `E3-T5` Diseñar tablas para versionado de parametros del motor.
  - Prioridad: `P0`
  - Estimacion: `S`
  - Dependencias: `E1-T2`, `E3-T1`
  - Aceptacion: existen tablas o estructuras definidas para `rule_set` y `parameter_version`.

- [ ] `E3-T6` Definir mapeo entre `ParametrosPLD-v3.xlsx` y tablas nuevas.
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

- [ ] `E4-T1` Seleccionar mecanismo de autenticacion definitivo.
  - Prioridad: `P0`
  - Estimacion: `S`
  - Dependencias: `E1-T3`
  - Aceptacion: queda decidido `SSO` o `login interno temporal`.

- [ ] `E4-T2` Implementar base de autenticacion en backend.
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

- [ ] `E4-T4` Definir matriz de permisos por rol.
  - Prioridad: `P0`
  - Estimacion: `S`
  - Dependencias: `E1-T3`
  - Aceptacion: matriz aprobada para consultar, evaluar, registrar, anular y cambiar estado.

- [ ] `E4-T5` Implementar RBAC en backend.
  - Prioridad: `P0`
  - Estimacion: `M`
  - Dependencias: `E4-T4`, `E4-T2`
  - Aceptacion: endpoints restringen acceso segun rol.

- [ ] `E4-T6` Implementar auditoria de acciones sensibles.
  - Prioridad: `P1`
  - Estimacion: `M`
  - Dependencias: `E3-T3`, `E4-T5`
  - Aceptacion: quedan auditadas evaluacion, registro, anulacion, cambio de estado y carga de parametros.

- [ ] `E4-T7` Configurar rate limiting y cabeceras de seguridad.
  - Prioridad: `P1`
  - Estimacion: `S`
  - Dependencias: `E2-T2`
  - Aceptacion: backend aplica limites y endurecimiento basico documentado.

---

## E5. Motor de decisiones PLD

Prioridad: `P0`

### Historia E5-H1. Diseno desacoplado del motor

Resultado esperado:

- motor de decisiones independiente de FastAPI y de la UI

Tareas:

- [ ] `E5-T1` Definir modelos de entrada y salida del motor.
  - Prioridad: `P0`
  - Estimacion: `S`
  - Dependencias: `E1-T5`
  - Aceptacion: contratos implementados y validados por pruebas.

- [ ] `E5-T2` Crear modulo `decision_engine` con capas internas de validacion, calculo y respuesta.
  - Prioridad: `P0`
  - Estimacion: `M`
  - Dependencias: `E5-T1`, `E2-T2`
  - Aceptacion: modulo aislado importable sin dependencias web.

- [ ] `E5-T3` Implementar versionado de reglas y parametros aplicados.
  - Prioridad: `P1`
  - Estimacion: `M`
  - Dependencias: `E3-T5`, `E5-T2`
  - Aceptacion: cada evaluacion expone `rule_set_version` y `parameter_version`.

### Historia E5-H2. Reglas de negocio y formulas

Resultado esperado:

- calculo equivalente o intencionalmente ajustado respecto al legado

Tareas:

- [ ] `E5-T4` Implementar normalizacion de entrada del flujo PLD.
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

- [ ] `E6-T2` Implementar endpoint `POST /api/v1/pld/consultas`.
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

- [ ] `E6-T4` Implementar endpoint `POST /api/v1/pld/evaluaciones`.
  - Prioridad: `P0`
  - Estimacion: `M`
  - Dependencias: `E6-T3`, `E4-T5`
  - Aceptacion: endpoint persiste la evaluacion y retorna salida del motor.

### Historia E6-H3. Registro de solicitud

Resultado esperado:

- solicitud registrada con validaciones y trazabilidad

Tareas:

- [ ] `E6-T5` Implementar reglas de registro de solicitud usando salida del motor.
  - Prioridad: `P0`
  - Estimacion: `M`
  - Dependencias: `E5-T7`, `E3-T3`
  - Aceptacion: servicio rechaza y acepta solicitudes segun reglas definidas.

- [ ] `E6-T6` Implementar endpoint `POST /api/v1/pld/solicitudes`.
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

- [ ] `E6-T8` Implementar endpoint `GET /api/v1/pld/solicitudes`.
  - Prioridad: `P1`
  - Estimacion: `S`
  - Dependencias: `E6-T7`
  - Aceptacion: endpoint retorna bandeja desacoplada de HTML.

- [ ] `E6-T9` Implementar endpoint `POST /api/v1/pld/solicitudes/{id}/anular`.
  - Prioridad: `P1`
  - Estimacion: `S`
  - Dependencias: `E6-T6`, `E4-T5`
  - Aceptacion: solicitud cambia a estado anulado o equivalente con historial.

- [ ] `E6-T10` Implementar endpoint `POST /api/v1/pld/solicitudes/{id}/estado`.
  - Prioridad: `P1`
  - Estimacion: `S`
  - Dependencias: `E6-T6`, `E4-T5`
  - Aceptacion: estado cambia solo por roles autorizados y queda historizado.

- [ ] `E6-T11` Implementar endpoint de exportacion de bandeja.
  - Prioridad: `P2`
  - Estimacion: `M`
  - Dependencias: `E6-T8`
  - Aceptacion: exporta resultados en formato acordado sin depender del DOM.

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
  - Prioridad: `P2`
  - Estimacion: `S`
  - Dependencias: `E6-T11`, `E7-T7`
  - Aceptacion: usuario descarga el archivo acordado desde UI.

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

- estrategia cerrada para conservar o no historicos

Tareas:

- [ ] `E8-T3` Definir politica de migracion historica.
  - Prioridad: `P1`
  - Estimacion: `S`
  - Dependencias: `E1-T3`
  - Aceptacion: decision formal sobre base limpia o migracion parcial/completa.

- [ ] `E8-T4` Implementar scripts de migracion historica si aplica.
  - Prioridad: `P2`
  - Estimacion: `L`
  - Dependencias: `E8-T3`, `E3-T3`
  - Aceptacion: historicos migran con trazabilidad y validaciones basicas.

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
  - Aceptacion: formulas y bloqueos criticos quedan cubiertos.

- [ ] `E9-T4` Implementar pruebas de integracion de API.
  - Prioridad: `P0`
  - Estimacion: `L`
  - Dependencias: `E6-T10`, `E9-T1`
  - Aceptacion: consulta, evaluacion, registro y cambio de estado tienen pruebas de integracion.

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

## 4. Backlog minimo del MVP

Las siguientes tareas forman el camino minimo para entregar el MVP:

- `E1-T1`
- `E1-T2`
- `E1-T3`
- `E1-T4`
- `E1-T5`
- `E1-T6`
- `E2-T1`
- `E2-T2`
- `E2-T3`
- `E2-T5`
- `E3-T1`
- `E3-T2`
- `E3-T3`
- `E3-T5`
- `E3-T6`
- `E3-T7`
- `E4-T1`
- `E4-T2`
- `E4-T4`
- `E4-T5`
- `E5-T1`
- `E5-T2`
- `E5-T4`
- `E5-T5`
- `E5-T6`
- `E5-T7`
- `E5-T8`
- `E6-T1`
- `E6-T2`
- `E6-T3`
- `E6-T4`
- `E6-T5`
- `E6-T6`
- `E6-T7`
- `E6-T8`
- `E6-T9`
- `E6-T10`
- `E7-T1`
- `E7-T3`
- `E7-T4`
- `E7-T5`
- `E7-T6`
- `E7-T7`
- `E7-T8`
- `E9-T1`
- `E9-T3`
- `E9-T4`
- `E10-T1`
- `E10-T2`

---

## 5. Backlog posterior al MVP

Tareas candidatas para una segunda fase:

- `E2-T4`
- `E2-T6`
- `E2-T7`
- `E3-T4`
- `E4-T3`
- `E4-T6`
- `E4-T7`
- `E5-T3`
- `E6-T11`
- `E7-T2`
- `E7-T9`
- `E8-T2`
- `E8-T4`
- `E9-T2`
- `E9-T5`
- `E9-T6`
- `E9-T7`
- `E10-T3`
- `E10-T4`
- `E10-T5`

---

## 6. Bloqueos abiertos

No conviene iniciar implementaciones sensibles sin resolver:

- mecanismo definitivo de autenticacion
- uso o eliminacion del flujo ZIP
- politica de migracion historica
- fuente oficial de reglas si difiere del legado
- lineamientos corporativos de despliegue y seguridad

---

## 7. Siguiente corte recomendado

Primer sprint tecnico sugerido:

1. `E1-T1` a `E1-T6`
2. `E2-T1`, `E2-T2`, `E2-T3`, `E2-T5`
3. `E3-T1`, `E3-T2`, `E3-T3`
4. `E5-T1`, `E5-T2`

Con ese corte queda lista la base para empezar la implementacion real del flujo PLD.
