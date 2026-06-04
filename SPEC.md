# SPEC - Decision Engine

## 0. Proposito del documento

Este documento define la especificacion tecnica inicial para construir una nueva version del sistema legado contenido en `old-version/`, como una plataforma de gestion y decision "AI-Powered" para productos de prestamo, incorporando capacidades de inteligencia artificial de manera asistiva y auditable.

El objetivo es reemplazar la implementacion monolitica en R + HTML/jQuery por una solucion moderna, segura, mantenible y extensible, con backend en Python y persistencia soportada inicialmente sobre SQLite, con opcion de migracion a SQL Server.

`PLD` significa `Prestamo de Libre Disponibilidad` y constituye el primer producto que se implementara en la nueva plataforma.

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

El MVP del nuevo proyecto debe cubrir exclusivamente el flujo `PLD / solicitudes de credito`, incluyendo:

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
- carga y descarga de archivos ZIP adjuntos a la solicitud
- visualizacion de archivos cargados
- trazabilidad operativa y auditoria
- explicacion asistida de la evaluacion mediante inteligencia artificial
- resumen del caso y sugerencias de siguientes pasos generados por IA

### 1.2 Vision futura de la plataforma

Aunque el MVP se limita a `PLD`, la arquitectura del nuevo sistema debe quedar preparada para soportar otros tipos de prestamo en el futuro (hipotecarios, descuento por planillas, etc.).

Esto implica que los componentes compartidos deben diseniarse de forma reutilizable para:

- multiples productos de prestamo
- distintos conjuntos de reglas parametrizables
- variantes de formularios y validaciones por producto
- evolucion independiente de parametros y politicas por tipo de prestamo
- distintos dashboards de monitoreo operativo

### 1.3 Capacidades AI del MVP y evolucion

El sistema incorpora IA bajo un modelo puramente asistivo (copiloto).

#### Incluido en el MVP:
- **Bandeja inteligente:** priorizacion automatica de solicitudes basada en IA.
- **Copiloto de registro:** asistencia en la redaccion de comentarios y chequeo de consistencia de la solicitud.
- **Explicacion de evaluacion:** traduccion de la salida estructurada del motor (RCI, limites, bloqueos) a lenguaje natural claro para el analista.
- **Resumen de caso:** un briefing conciso de los indicadores clave y fortalezas del cliente.
- **Sugerencias de accion:** recomendaciones sobre que datos ajustar o que paso operativo seguir ante un bloqueo o alerta.

#### Excluido del MVP (Fases futuras):
- **Copiloto de reglas:** herramienta para que negocio simule y entienda el impacto de cambios en las politicas.
- **Decisiones automaticas:** la IA nunca tomara la decision de aprobar o rechazar directamente.

### 1.4 Excluido del nuevo sistema

No forma parte de esta primera version:

- modulo de cobranzas
- aplicacion de campanas de cobranza
- endpoints equivalentes a `get_data`, `envio_sol1`, `envio_sol2`, `envio_sol3`, `bandeja_sol1`, `bandeja_sol2`
- dependencia de HTML generado por backend
- autenticacion basada en IP como mecanismo principal
- migracion de historicos desde la base de datos del sistema legado

### 1.5 Pendiente de confirmacion funcional

Los siguientes temas quedan abiertos hasta definicion del usuario o negocio:

- (sin pendientes en este momento)

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
- capacidad de incorporar nuevos tipos de prestamo sin redisenar los modulos compartidos

### 2.2 Arquitectura propuesta

Se propone una arquitectura modular de cuatro bloques:

1. `frontend web`
2. `backend API`
3. `motor de decisiones`
4. `asistente AI (modulo asistivo)`

Los modulos compartidos de esta arquitectura no deben asumir que `PLD` sera el unico producto del sistema.

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
- carga y descarga de archivos ZIP
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
- invocar asistencia con IA
- registrar auditoria

### 2.5 Motor de decisiones

Debe implementarse como modulo aislado dentro del backend en la primera version, con estructura lista para extraerse a servicio independiente si el crecimiento del sistema lo requiere.

Responsabilidades:

- seleccionar el conjunto de reglas aplicable segun producto o contexto
- evaluar elegibilidad
- recalcular oferta
- aplicar reglas de bloqueo
- generar alertas y observaciones
- versionar resultados
- registrar auditoria

En el MVP, `PLD` sera el primer conjunto de reglas implementado, pero el contrato del motor debe permitir agregar otros productos sin redefinir la base del modulo.

El motor de decisiones es **100% determinista** y no utiliza IA. El modulo AI consume la salida estructurada de este motor para generar explicaciones, garantizando que el calculo matematico y las politicas duras sean siempre auditablemente exactas y reproducibles.

### 2.6 Despliegue inicial

Se recomienda un despliegue inicial simple:

- frontend estatico servido por Nginx o equivalente
- backend FastAPI detras de reverse proxy
- funciones async para soportar consultas concurrentes o paralelas
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

Los conceptos compartidos del dominio deben modelarse como primitivas de plataforma cuando no sean exclusivos de PLD.

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

1. Login interno temporal con sesiones seguras 
2. Integracion con Active Directory o LDAP
3. SSO corporativo mediante OIDC o Azure AD

### 4.3 Autorizacion

Se recomienda RBAC con roles base:

- `analista`
- `evaluador`
- `supervisor`
- `admin`

Permisos de referencia:

- `analista`: consultar, registrar solicitud, anular solicitud
- `evaluador`: consultar, anular solicitud, aprobar, observar, rechazar
- `supervisor`: consultar, cambiar estado, romper reglas del motor
- `admin`: mantenimiento, parametros, auditoria, usuarios

Cada rol debe tener niveles de autonomia diferenciados para la aprobación de solicitudes por montos de prestamo, resultado del motor de decisiones, entre otros.

### 4.4 Controles tecnicos obligatorios

- HTTPS en todos los entornos no locales
- expiracion de sesion o expiracion de tokens
- CORS restringido
- validacion estricta de payloads
- rate limiting
- logs estructurados
- almacenamiento seguro de secretos
- proteccion contra CSRF si se usan cookies de sesion
. proteccion contra SQL injection
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
- trazabilidad IA si aplica

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
- extensible mediante pipeline de etapas intercambiables
- utilizar funciones async para peticiones múltiples

### 5.3 Contrato de entrada sugerido

```json
{
  "tipo_documento": "DNI",
  "numero_documento": "12345678",
  "producto": "PLD",
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

### 5.5 Arquitectura de Pipeline de Etapas

El motor se organiza como un pipeline secuencial de etapas independientes. Cada etapa recibe un contexto, lo procesa y lo pasa a la siguiente. Esto permite probar, modificar o reemplazar etapas sin afectar al resto.

#### Etapas del pipeline

1. **Preprocessing:** Normaliza datos de entrada, enriquece con informacion historica del cliente y calcula campos derivados (ingreso revisado, deuda total ajustada).
2. **Eligibility:** Aplica reglas duras de elegibilidad (ingreso minimo, edad maxima, documentacion requerida). Si falla, se detiene el pipeline con rechazo.
3. **Scoring Layer:** Calcula indicadores financieros (RCI, capacidad de pago, score de riesgo), asigna segmento y perfil de cliente.
4. **Decision Strategy:** Aplica la estrategia de negocio (aprobacion, rechazo, referencia a supervisor) segun las reglas de producto, el segmento y los scores calculados.
5. **Post-processing:** Genera alertas operativas, formatea la respuesta y emite eventos de decision al event store.

Cada etapa implementa una interfaz comun (`DecisionStage`) que expone:
- `name`: identificador unico de la etapa
- `execute(context: DecisionContext) -> DecisionContext`: metodo de ejecucion
- `rollback(context: DecisionContext) -> None`: metodo de reversion opcional

El pipeline se configura por producto mediante una estrategia (`pipeline_strategy`) que define que etapas ejecutar y en que orden.

### 5.6 Event Sourcing de Decisiones

Cada decision generada por el motor se persiste como un **evento inmutable** en un event store. Esto proporciona trazabilidad total, capacidad de reproduccion (replay) y auditoria forense.

Tipos de evento:
- `EVALUATION_REQUESTED`: se inicia una evaluacion
- `ELIGIBILITY_PASSED` / `ELIGIBILITY_FAILED`: resultado de elegibilidad
- `SCORING_COMPLETED`: scores calculados
- `DECISION_MADE`: decision final (aprobado, rechazado, referido)
- `REQUEST_REGISTERED`: solicitud creada
- `REQUEST_STATUS_CHANGED`: cambio de estado operativo

Cada evento contiene:
- `event_id` (UUID)
- `aggregate_id` (UUID de la entidad raiz: evaluacion o solicitud)
- `event_type` (string)
- `event_data` (JSON con datos del momento)
- `version` (int, incrementa por agregado)
- `created_by` (FK a users)
- `created_at` (timestamp)

### 5.7 Parametrizacion

La informacion de `ParametrosPLD-v3.xlsx` debe migrarse a una fuente versionada y controlada.

Opciones recomendadas:

- tablas de parametros en base de datos
- Interface de creacion de dimensiones y reglas de negocio
- UI de creacion de pipeline drag and drop

Opcion complementaria:

- importador administrativo desde Excel para cargar o actualizar parametros según un formato establecido

### 5.8 Versionado de reglas

Cada evaluacion debe almacenar:

- version de reglas
- version de parametros
- timestamp
- usuario que ejecuto la evaluacion

### 5.9 Business Rules Management System (BRMS)

Las reglas de negocio se almacenan en base de datos y son gestionables mediante una interfaz administrativa con control de versiones.

#### Componentes del BRMS:
- **Rule catalog:** repositorio central de todas las reglas, clasificadas por tipo (eligibilidad, scoring, estrategia, bloqueo) y por producto.
- **Rule versions:** cada modificacion crea una nueva version. Las reglas activas se determinan por producto + fecha efectiva.
- **Rule sets:** agrupaciones de reglas que se activan/desactivan como unidad para un producto y periodo determinado.
- **Testing sandbox:** entorno aislado donde el administrador puede probar una regla o conjunto de reglas contra casos historicos antes de activarla.
- **Approval workflow:** los cambios a reglas en produccion requieren aprobacion de un supervisor antes de su activacion.

#### UI Administrativa:
- CRUD de reglas con editor estructurado (condiciones, acciones, parametros)
- Vista de versionado y comparacion de cambios entre versiones
- Simulador de reglas con casos de prueba
- Dashboard de reglas activas por producto

### 5.10 Estrategia AI e Integracion

La capa AI se implementa como un servicio del backend que interactua con LLMs mediante tecnicas de *grounding* estricto.

#### Principios de Diseno AI:
1. **No-Autonomia:** La IA recomienda y explica; la decision final es del usuario y el calculo es del motor determinista.
2. **Grounding estricto:** El prompt se alimenta unicamente de la ficha del cliente, las reglas aplicadas y el resultado del motor. No se permite que el modelo infiera datos que no esten explicitamente en el payload.
3. **Explicabilidad auditable:** Toda respuesta generada por la IA debe poder rastrearse al prompt, modelo, datos de entrada y version de reglas utilizadas.
4. **Aislamiento:** Si el servicio de IA falla o se desactiva, el flujo principal de consulta, evaluacion y registro de solicitudes determinista debe seguir funcionando al 100%.

---

## 6. Modelo de datos inicial sugerido

### 6.1 Objetivo del modelo

Separar correctamente:

- catalogo de productos de prestamo
- datos maestros
- parametros del motor
- eventos operativos
- interacciones y trazas de la IA
- solicitudes
- historial de estados
- trazabilidad

### 6.2 Entidades principales sugeridas

- `users`
- `roles`
- `user_roles`
- `loan_products`
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
- `ai_interactions`
- `ai_prompt_templates`
- `decision_events`
- `rule_sets`
- `rule_versions`
- `pipeline_strategies`

### 6.3 Campos minimos esperados

#### `credit_requests`

- `id`
- `loan_product_code`
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
- `loan_product_code`
- `document_type`
- `document_number`
- `campaign_code`
- `rule_set_version`
- `parameter_version`
- `executed_by`
- `executed_at`

#### `ai_interactions`
- `id` (UUID)
- `user_id` (FK a `users`)
- `evaluation_id` (FK a `pld_evaluations`, opcional)
- `request_id` (FK a `credit_requests`, opcional)
- `context_type` (VARCHAR: 'evaluation_explanation', 'request_check', 'sprint_briefing')
- `prompt_template_version` (VARCHAR)
- `input_payload` (JSON: datos de entrada estructurados pasados al modelo)
- `model_name` (VARCHAR: identificador del LLM usado)
- `response_text` (TEXT: salida generada por la IA)
- `created_at` (TIMESTAMP)

#### `decision_events`
- `event_id` (UUID, PK)
- `aggregate_id` (UUID)
- `aggregate_type` (VARCHAR: 'evaluation', 'credit_request')
- `event_type` (VARCHAR)
- `event_data` (JSON)
- `version` (INT)
- `created_by` (FK a `users`)
- `created_at` (TIMESTAMP)

Indices:
- `(aggregate_id, version)` unico
- `(aggregate_type, created_at)` para consultas por periodo

#### `rule_sets`
- `id` (UUID, PK)
- `loan_product_code` (FK a `loan_products`)
- `name` (VARCHAR)
- `description` (TEXT)
- `effective_from` (TIMESTAMP)
- `effective_to` (TIMESTAMP, nullable)
- `is_active` (BOOLEAN)
- `created_by` (FK a `users`)
- `created_at` (TIMESTAMP)

#### `rule_versions`
- `id` (UUID, PK)
- `rule_set_id` (FK a `rule_sets`)
- `version_number` (INT)
- `rule_type` (VARCHAR: 'eligibility', 'scoring', 'strategy', 'blocking')
- `condition_expression` (JSON: definicion estructurada de la condicion)
- `action_expression` (JSON: definicion estructurada de la accion)
- `parameters` (JSON: valores parametrizables de la regla)
- `status` (VARCHAR: 'draft', 'active', 'deprecated')
- `change_notes` (TEXT)
- `approved_by` (FK a `users`, nullable)
- `created_by` (FK a `users`)
- `created_at` (TIMESTAMP)

### 6.4 Compatibilidad de motor de base de datos

El modelo debe evitar:

- SQL dependiente del motor
- tipos no portables
- triggers complejos no equivalentes

Se debe priorizar compatibilidad entre:

- SQLite
- SQL Server

### 6.5 Consideracion de multiproducto

El modelo inicial debe permitir distinguir entre:

- datos comunes a cualquier producto de prestamo
- datos especificos de PLD
- reglas y parametros por producto

El MVP puede tener tablas y servicios especificos de PLD, pero no debe impedir la introduccion posterior de otros productos bajo la misma plataforma.

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

- `POST /api/v1/loans/{product_code}/consultas`
- `POST /api/v1/loans/{product_code}/evaluaciones`
- `POST /api/v1/loans/{product_code}/evaluaciones/{evaluation_id}/explain`
- `POST /api/v1/loans/{product_code}/solicitudes`
- `GET /api/v1/loans/{product_code}/solicitudes`
- `GET /api/v1/loans/{product_code}/solicitudes/{request_id}`
- `POST /api/v1/loans/{product_code}/solicitudes/{request_id}/anular`
- `POST /api/v1/loans/{product_code}/solicitudes/{request_id}/estado`
- `GET /api/v1/loans/{product_code}/solicitudes/export`
- `POST /api/v1/loans/{product_code}/solicitudes/{request_id}/assist`
- `POST /api/v1/loans/{product_code}/bandeja/summary`

#### Consideracion futura de API

Aunque el MVP expone endpoints bajo el segmento `{product_code}`, la API interna y sus contratos base deben quedar listos para incorporar otros productos de prestamo sin redisenar autenticacion, auditoria, manejo de errores ni capacidades compartidas.

#### Administracion futura

- `GET /api/v1/loans/{product_code}/parametros`
- `POST /api/v1/loans/{product_code}/parametros/import`
- `GET /api/v1/loans/{product_code}/rule-sets`
- `POST /api/v1/loans/{product_code}/rule-sets`
- `GET /api/v1/loans/{product_code}/rule-sets/{rule_set_id}/versions`
- `POST /api/v1/loans/{product_code}/rule-sets/{rule_set_id}/versions`
- `PUT /api/v1/loans/{product_code}/rule-sets/{rule_set_id}/activate`
- `POST /api/v1/loans/{product_code}/rule-sets/{rule_set_id}/sandbox-test`
- `GET /api/v1/events?aggregate_type={type}&aggregate_id={id}`
- `GET /api/v1/events/{aggregate_id}/timeline`
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
- definicion de fronteras entre capacidades exclusivas de PLD y capacidades compartidas de plataforma

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
- soporte base para clasificar solicitudes y reglas por producto

### Fase 3. Motor de decisiones

Entregables:

- contratos de entrada y salida
- motor desacoplado
- reglas base implementadas
- pruebas de regresion contra legado
- base lista para agregar nuevos conjuntos de reglas por producto

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

### Fase 9. Extension a nuevos productos

Entregables futuros:

- incorporacion de nuevos tipos de prestamo
- nuevos conjuntos de reglas sobre el mismo motor
- evoluciones de UI y API sin romper el MVP PLD

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

Decision tomada:

- se inicia con base limpia (sin migracion historica)
- los historicos del sistema legado se conservan unicamente como referencia en `old-version/API_DB.db`

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
- modelar conceptos compartidos con enfoque multiproducto desde la primera iteracion

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
13. estrategia para incorporar nuevos tipos de prestamo sin rehacer contratos compartidos

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
- soportar nuevos productos de prestamo ademas de PLD

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
- dejar definidos los puntos de extension necesarios para soportar otros tipos de prestamo en futuras fases
