# SPEC - Nuevo Decision Engine PLD

## 0. Proposito del documento

Este documento define la especificacion tecnica inicial para construir una nueva version del sistema legado contenido en `old-version/`, limitada al flujo `PLD / solicitudes de credito`.

El objetivo es reemplazar la implementacion monolitica en R + HTML/jQuery por una solucion moderna, segura, mantenible y extensible, con backend en Python y persistencia soportada inicialmente sobre SQLite, con opcion de migracion a SQL Server.

Este documento toma como referencia funcional principal:

- `old-version/api-build.R`
- `old-version/script.js`
- `old-version/index.html`
- `old-version/bandeja.html`
- `old-version/API_DB.db`
- `old-version/ParametrosPLD-v3.xlsx`

---

## 1. Alcance funcional objetivo

### 1.1 Incluido en el nuevo sistema

El nuevo proyecto debe cubrir exclusivamente el flujo `PLD / solicitudes de credito`, incluyendo:

- consulta de cliente por tipo y numero de documento
- visualizacion de datos relevantes de cliente
- visualizacion de campanas u ofertas PLD disponibles
- seleccion de oferta a evaluar
- captura de datos complementarios para evaluacion
- recalculo de oferta segun reglas de negocio
- visualizacion del resultado de evaluacion
- registro de solicitud de credito
- consulta de bandeja de solicitudes por periodo
- anulacion de solicitud
- actualizacion de estado de solicitud
- exportacion de resultados de bandeja
- trazabilidad operativa y auditoria

### 1.2 Excluido del nuevo sistema

No forma parte de esta primera version:

- modulo de cobranzas
- aplicacion de campanas de cobranza
- endpoints equivalentes a `get_data`, `envio_sol1`, `envio_sol2`, `envio_sol3`, `bandeja_sol1`, `bandeja_sol2`
- dependencia de HTML generado por backend
- autenticacion basada en IP como mecanismo principal

### 1.3 Pendiente de confirmacion funcional

Los siguientes temas quedan abiertos hasta definicion del usuario o negocio:

- inclusion o eliminacion del flujo de carga y descarga de archivos ZIP
- necesidad de migrar historicos de la base actual
- definicion exacta de roles operativos
- reglas de aprobacion y rechazo posteriores al registro

---

## 2. Arquitectura objetivo recomendada

### 2.1 Principios

La nueva arquitectura debe cumplir los siguientes principios:

- separacion clara entre frontend, API, dominio y persistencia
- reglas de negocio aisladas del framework web
- contratos API tipados y versionados
- seguridad desacoplada de la red o de archivos de IPs
- compatibilidad con cambio de motor de base de datos
- facilidad para pruebas automatizadas

### 2.2 Arquitectura propuesta

Se propone una arquitectura modular de tres bloques:

1. `frontend web`
2. `backend API`
3. `motor de decisiones`

### 2.3 Frontend recomendado

Stack recomendado:

- React
- TypeScript
- Vite
- libreria de componentes por definir

Responsabilidades del frontend:

- autenticacion e identificacion del usuario
- formularios de consulta y evaluacion
- visualizacion de resultados
- bandeja de solicitudes
- exportacion de datos
- manejo de estados de carga, error y permisos

### 2.4 Backend recomendado

Stack recomendado:

- Python 3.12+
- FastAPI
- Pydantic
- SQLAlchemy 2.x
- Alembic

Responsabilidades del backend:

- exponer API REST
- autenticar y autorizar
- orquestar casos de uso
- persistir informacion
- invocar el motor de decisiones
- registrar auditoria

### 2.5 Motor de decisiones

Debe implementarse como modulo aislado dentro del backend en la primera version, con estructura lista para extraerse a servicio independiente si el crecimiento del sistema lo requiere.

Responsabilidades:

- evaluar elegibilidad
- recalcular oferta
- aplicar reglas de bloqueo
- generar alertas y observaciones
- versionar resultados

### 2.6 Despliegue inicial

Se recomienda un despliegue inicial simple:

- frontend estatico servido por Nginx o equivalente
- backend FastAPI detras de reverse proxy
- SQLite en entorno inicial o de desarrollo
- SQL Server como opcion de entorno productivo

---

## 3. Diseno logico por capas

### 3.1 Capa API

Responsable de:

- endpoints HTTP
- validacion de entrada
- serializacion de respuesta
- control de errores
- autenticacion
- autorizacion

### 3.2 Capa de aplicacion

Responsable de:

- casos de uso
- coordinacion de repositorios
- coordinacion del motor de decisiones
- validaciones de flujo
- reglas operativas no matematicas

### 3.3 Capa de dominio

Responsable de:

- entidades de negocio
- invariantes
- contratos del motor de decisiones
- reglas criticas

### 3.4 Capa de infraestructura

Responsable de:

- base de datos
- repositorios
- logging
- exportaciones
- adaptadores externos
- configuracion por entorno

### 3.5 Estructura sugerida de carpetas

```text
project/
  backend/
    app/
      api/
      application/
      domain/
      infrastructure/
      security/
      config/
      main.py
    alembic/
    tests/
  frontend/
    src/
      app/
      features/
      components/
      services/
      routes/
    tests/
  docs/
  old-version/
  SPEC.md
```

---

## 4. Seguridad moderna propuesta

### 4.1 Objetivo

Eliminar dependencia de listas de IP como mecanismo principal de acceso y reemplazarla por autenticacion y autorizacion modernas.

### 4.2 Autenticacion

Orden de preferencia:

1. SSO corporativo mediante OIDC o Azure AD
2. Integracion con Active Directory o LDAP
3. Login interno temporal con sesiones seguras

### 4.3 Autorizacion

Se recomienda RBAC con roles base:

- `analista`
- `evaluador`
- `supervisor`
- `admin`

Permisos de referencia:

- `analista`: consultar, evaluar, registrar solicitud
- `evaluador`: cambiar estado, revisar solicitudes
- `supervisor`: anular, aprobar, observar, rechazar
- `admin`: mantenimiento, parametros, auditoria, usuarios

### 4.4 Controles tecnicos obligatorios

- HTTPS en todos los entornos no locales
- expiracion de sesion o expiracion de tokens
- CORS restringido
- validacion estricta de payloads
- rate limiting
- logs estructurados
- almacenamiento seguro de secretos
- proteccion contra CSRF si se usan cookies de sesion
- encabezados de seguridad HTTP

### 4.5 Auditoria

Toda accion sensible debe registrar:

- usuario
- rol
- accion
- entidad afectada
- resultado
- fecha y hora
- IP origen
- identificador de request

---

## 5. Rediseno del motor de decisiones

### 5.1 Problema del sistema actual

En la version antigua, la logica de evaluacion esta acoplada a:

- handlers HTTP
- estructura de tablas HTML
- lectura por posicion de columnas en la UI
- archivos Excel usados en tiempo de ejecucion

### 5.2 Objetivo del nuevo motor

El motor debe ser:

- deterministico
- testeable
- independiente de la interfaz
- independiente de FastAPI
- parametrizable
- versionable

### 5.3 Contrato de entrada sugerido

```json
{
  "tipo_documento": "DNI",
  "numero_documento": "12345678",
  "campana": "PLD_48M",
  "marca_cliente": "CLIENTE",
  "perfil": "PERFIL 2",
  "marca_sunedu": "CON SUNEDU",
  "situacion_laboral": "DEP",
  "ingreso_validado": 4500,
  "deuda_reportada": 1200,
  "usuario": "jmorales"
}
```

### 5.4 Contrato de salida sugerido

```json
{
  "elegible": true,
  "segmento": "CS_DEP",
  "ingreso_revisado": 4500,
  "rci": 0.32,
  "oferta_calculada": 12500,
  "cuota_calculada": 420,
  "tasa": 0.35,
  "plazo": 48,
  "alertas": [],
  "bloqueos": [],
  "version_reglas": "pld-v1"
}
```

### 5.5 Componentes internos del motor

- normalizador de entrada
- validador de precondiciones
- evaluador de elegibilidad
- calculador de oferta
- evaluador de restricciones
- generador de alertas
- ensamblador de respuesta

### 5.6 Parametrizacion

La informacion de `ParametrosPLD-v3.xlsx` debe migrarse a una fuente versionada y controlada.

Opcion recomendada:

- tablas de parametros en base de datos

Opcion complementaria:

- importador administrativo desde Excel para cargar o actualizar parametros

### 5.7 Versionado de reglas

Cada evaluacion debe almacenar:

- version de reglas
- version de parametros
- timestamp
- usuario que ejecuto la evaluacion

---

## 6. Modelo de datos inicial sugerido

### 6.1 Objetivo del modelo

Separar correctamente:

- datos maestros
- parametros del motor
- eventos operativos
- solicitudes
- historial de estados
- trazabilidad

### 6.2 Entidades principales sugeridas

- `users`
- `roles`
- `user_roles`
- `clients`
- `pld_campaigns`
- `pld_rule_sets`
- `pld_rule_parameters`
- `pld_evaluations`
- `pld_evaluation_inputs`
- `pld_evaluation_results`
- `credit_requests`
- `credit_request_status_history`
- `audit_logs`

### 6.3 Campos minimos esperados

#### `credit_requests`

- `id`
- `document_type`
- `document_number`
- `campaign_code`
- `requested_amount`
- `comment`
- `customer_type`
- `profile_code`
- `segment_code`
- `employment_status`
- `validated_income`
- `rci`
- `offered_amount`
- `installment_amount`
- `term_months`
- `rate`
- `status`
- `created_by`
- `created_at`
- `cancelled_at`

#### `pld_evaluations`

- `id`
- `document_type`
- `document_number`
- `campaign_code`
- `rule_set_version`
- `parameter_version`
- `executed_by`
- `executed_at`

### 6.4 Compatibilidad de motor de base de datos

El modelo debe evitar:

- SQL dependiente del motor
- tipos no portables
- triggers complejos no equivalentes

Se debe priorizar compatibilidad entre:

- SQLite
- SQL Server

---

## 7. API objetivo sugerido

### 7.1 Convenciones

- prefijo `/api/v1`
- respuestas JSON consistentes
- errores estructurados
- nombres de campos estables
- contratos documentados con OpenAPI

### 7.2 Endpoints propuestos

#### Autenticacion y sesion

- `GET /api/v1/me`
- `POST /api/v1/auth/login` si no existe SSO
- `POST /api/v1/auth/logout` si aplica

#### Flujo PLD

- `POST /api/v1/pld/consultas`
- `POST /api/v1/pld/evaluaciones`
- `POST /api/v1/pld/solicitudes`
- `GET /api/v1/pld/solicitudes`
- `GET /api/v1/pld/solicitudes/{request_id}`
- `POST /api/v1/pld/solicitudes/{request_id}/anular`
- `POST /api/v1/pld/solicitudes/{request_id}/estado`
- `GET /api/v1/pld/solicitudes/export`

#### Administracion futura

- `GET /api/v1/pld/parametros`
- `POST /api/v1/pld/parametros/import`
- `GET /api/v1/audit`

### 7.3 Errores esperados

Estructura sugerida:

```json
{
  "error": {
    "code": "REQUEST_VALIDATION_ERROR",
    "message": "El monto solicitado excede la oferta.",
    "details": []
  }
}
```

---

## 8. Roadmap por fases

### Fase 0. Descubrimiento y cierre funcional

Entregables:

- inventario de reglas del flujo PLD
- catalogo de pantallas
- casos de uso definitivos
- matriz de roles y permisos

### Fase 1. Bootstrap tecnico

Entregables:

- repositorio base
- backend FastAPI
- frontend React
- configuracion de entornos
- pipeline inicial

### Fase 2. Persistencia y migraciones

Entregables:

- modelo de datos inicial
- migraciones Alembic
- compatibilidad SQLite
- guia de cambio a SQL Server

### Fase 3. Motor de decisiones

Entregables:

- contratos de entrada y salida
- motor desacoplado
- reglas base implementadas
- pruebas de regresion contra legado

### Fase 4. Casos de uso PLD

Entregables:

- consulta cliente
- evaluacion
- registro de solicitud
- bandeja
- anulacion
- cambio de estado

### Fase 5. Frontend funcional

Entregables:

- flujo de consulta
- flujo de evaluacion
- formulario de solicitud
- bandeja
- exportacion

### Fase 6. Seguridad y endurecimiento

Entregables:

- autenticacion
- RBAC
- auditoria completa
- rate limiting
- monitoreo base

### Fase 7. QA y validacion

Entregables:

- pruebas unitarias
- pruebas de integracion
- pruebas end-to-end
- validacion de negocio

### Fase 8. Despliegue

Entregables:

- build reproducible
- configuracion de despliegue
- documentacion operativa
- checklist de salida

---

## 9. Estrategia de migracion funcional

### 9.1 Fuente de verdad inicial

Mientras no exista documentacion oficial adicional, se tomara como fuente inicial de comportamiento:

- codigo R de `old-version/api-build.R`
- parametros de `old-version/ParametrosPLD-v3.xlsx`
- estructura de `old-version/API_DB.db`

### 9.2 Orden recomendado de migracion

1. consulta de cliente PLD
2. evaluacion y recalculo
3. registro de solicitud
4. bandeja operativa
5. cambio de estado y anulacion
6. exportacion
7. endurecimiento de seguridad

### 9.3 Estrategia de paridad funcional

Para cada caso de uso se recomienda:

- identificar insumos de entrada del sistema antiguo
- capturar salida esperada actual
- reproducir el resultado en la nueva implementacion
- documentar desviaciones intencionales

### 9.4 Migracion de datos

Decision pendiente:

- iniciar con base limpia
- migrar historicos seleccionados
- migrar historico completo

Si se migra historial, debe hacerse con scripts versionados y auditables.

---

## 10. Estrategia de pruebas

### 10.1 Pruebas unitarias

Cubrir como minimo:

- calculo de RCI
- calculo de oferta
- reglas de bloqueo
- validaciones de solicitud
- transformaciones de parametros

### 10.2 Pruebas de integracion

Cubrir:

- endpoints FastAPI
- persistencia SQLite
- permisos por rol
- historico de estados
- auditoria

### 10.3 Pruebas end-to-end

Cubrir:

- consulta
- evaluacion
- registro
- cambio de estado
- anulacion
- exportacion

### 10.4 Pruebas de regresion funcional

Se deben preparar casos de comparacion entre legado y nuevo sistema para:

- evaluaciones equivalentes
- restricciones de solicitud
- estados operativos

### 10.5 Pruebas no funcionales

Recomendadas:

- rendimiento base de consultas
- concurrencia en registro de solicitudes
- seguridad de autenticacion
- validacion de logs y auditoria

---

## 11. Riesgos principales

### 11.1 Riesgos funcionales

- reglas no documentadas fuera del codigo R
- ambiguedades en formulas o parametros Excel
- estados de negocio no formalizados

### 11.2 Riesgos tecnicos

- diferencias entre SQLite y SQL Server
- integracion tardia con identidad corporativa
- dependencia de datos legacy incompletos
- exceso de logica en frontend si no se controla el alcance

### 11.3 Riesgos operativos

- falta de usuarios negocio para validar paridad
- cambios de reglas durante el desarrollo
- ausencia de ambiente intermedio representativo

### 11.4 Mitigaciones sugeridas

- construir catalogo temprano de reglas
- fijar casos canonicos de prueba
- aislar motor de decisiones desde el inicio
- versionar parametros y formulas

---

## 12. Decisiones tempranas recomendadas

Estas decisiones deben cerrarse al inicio del proyecto:

1. `React + TypeScript` versus frontend server-side
2. proveedor de identidad corporativo o login temporal
3. inclusion o eliminacion del flujo ZIP
4. migracion o no de datos historicos
5. motor de decisiones como modulo interno o servicio separado
6. fuente oficial de reglas de negocio
7. lineamientos corporativos de despliegue y seguridad
8. definicion formal de roles
9. formato final de exportacion de bandeja
10. necesidad de trazabilidad avanzada o simple
11. politica de versionado de parametros del motor
12. criterio de aprobacion para salida a produccion

---

## 13. Especificaciones adicionales recomendadas

### 13.1 Requisitos no funcionales

- tiempo de respuesta de consulta menor a 3 segundos en condiciones normales
- tiempo de evaluacion menor a 2 segundos por solicitud estandar
- trazabilidad completa de acciones criticas
- disponibilidad acorde al horario operativo esperado
- exportaciones consistentes y reproducibles

### 13.2 Observabilidad

Se recomienda incluir desde el inicio:

- logs estructurados JSON
- metricas basicas de API
- correlacion por request id
- health checks

### 13.3 Configuracion por entorno

Definir al menos:

- `development`
- `test`
- `staging`
- `production`

Con configuraciones independientes para:

- base de datos
- autenticacion
- secretos
- CORS
- logging

### 13.4 Estrategia de importacion de parametros

Si se conserva Excel como origen operativo, debe existir:

- formato de plantilla controlado
- validacion previa de estructura
- importacion transaccional
- versionado del lote cargado
- rollback funcional ante carga invalida

### 13.5 Compatibilidad futura

El sistema debe quedar preparado para:

- migrar SQLite a SQL Server
- exponer el motor a otros canales
- incorporar administracion de parametros por UI
- soportar nuevas familias de reglas

---

## 14. Preguntas abiertas

Estas preguntas deben resolverse antes de cerrar el backlog definitivo:

1. El frontend sera SPA en React o renderizado desde backend.
2. Existe proveedor corporativo de identidad disponible.
3. El flujo ZIP debe permanecer o eliminarse.
4. Se migraran historicos desde `BaseSolicitudesTN`, `BaseValidacion` y `BaseConsultasTN`.
5. El motor de decisiones se desplegara junto al backend o por separado.
6. Existen reglas oficiales fuera del codigo legado y del Excel.
7. Hay lineamientos corporativos obligatorios para UI, seguridad, logs y despliegue.

---

## 15. Criterio de exito del MVP

El MVP se considerara exitoso si logra:

- reproducir el flujo PLD principal del legado
- desacoplar la evaluacion de la UI
- operar con autenticacion y autorizacion modernas
- registrar solicitudes con trazabilidad
- soportar SQLite sin bloquear futura migracion a SQL Server
- contar con pruebas automatizadas del motor de decisiones
- dejar una base tecnica lista para evolucion posterior
