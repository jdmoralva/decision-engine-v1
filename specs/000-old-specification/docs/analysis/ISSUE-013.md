# ISSUE-013 - Implementar API de consulta PLD

## 1. Objetivo

Exponer la consulta de cliente y campanas PLD mediante una API desacoplada de HTML, autenticada y protegida por RBAC.

## 2. Fuentes revisadas

- `docs/project/ISSUES.md`
- `docs/project/SPRINTS.md`
- `docs/SPEC.md`
- `docs/analysis/ISSUE-001.md`
- `docs/analysis/ISSUE-002.md`
- `docs/analysis/ISSUE-009.md`
- `backend/app/main.py`
- `backend/app/api/schemas/contracts.py`
- `backend/app/api/routes/loan_consultations.py`
- `backend/app/application/loan_consultations.py`
- `backend/app/infrastructure/loan_consultations.py`
- `backend/app/security/dependencies.py`
- `backend/app/security/exceptions.py`
- `backend/tests/test_issue_013_consultations_api.py`

## 3. Contexto

- `ISSUE-013` abre el primer endpoint funcional del flujo PLD bajo el prefijo objetivo `/api/v1/loans/{product_code}/...`.
- El contrato del proyecto ya fijaba `POST /api/v1/loans/{product_code}/consultas` como endpoint objetivo para la consulta operativa.
- La implementacion debia evitar acoplar la API al HTML legacy, pero tambien evitar dejar la arquitectura centrada en `PLD` como unico producto.
- Para esta fase se adopto una fuente local de desarrollo como adaptador temporal, manteniendo el legacy solo como referencia funcional y no como runtime.

## 4. Implementacion consolidada

Se implemento una nueva capacidad de consulta por producto con separacion explicita entre API, aplicacion e infraestructura.

La implementacion incluye:

- endpoint `POST /api/v1/loans/{product_code}/consultas`
- contrato HTTP tipado para request y response de consulta
- servicio de aplicacion `LoanConsultationService`
- protocolo `LoanConsultationProvider` para desacoplar la fuente de datos por producto
- registry de proveedores por `product_code`
- adaptador local `InMemoryLoanConsultationProvider` para desarrollo
- validacion de producto activo contra `loan_products`
- proteccion RBAC con `consultar_cliente`
- respuestas de error estructuradas para `401`, `403` y `404` en endpoints protegidos por la capa de seguridad actual

## 5. Entregables implementados

- `backend/app/api/routes/loan_consultations.py`
- `backend/app/application/loan_consultations.py`
- `backend/app/infrastructure/loan_consultations.py`
- extension de `backend/app/api/schemas/contracts.py`
- registro del router en `backend/app/main.py`
- `backend/app/security/exceptions.py`
- ajuste de `backend/app/security/dependencies.py` para errores tipados
- `backend/tests/test_issue_013_consultations_api.py`

## 6. Diseno consolidado

### 6.1 Contrato de entrada

La consulta recibe un body minimo con:

- `document.document_type`
- `document.document_number`

El `product_code` se resuelve desde path, evitando duplicidad de fuente y manteniendo el contrato alineado con el resto de endpoints multiproducto del roadmap.

### 6.2 Contrato de salida

La respuesta devuelve JSON estructurado con:

- `product_code`
- `document`
- `customer`
- `campaigns`

Esto elimina cualquier dependencia de HTML, tablas o posiciones de columna del legacy.

### 6.3 Soporte multiproducto

Aunque el primer proveedor cargado es `PLD`, la capa de aplicacion no depende de clases ni rutas PLD-especificas. La seleccion del comportamiento se resuelve mediante un registry de `LoanConsultationProvider` indexado por `product_code`.

Con esto:

- la API mantiene un shape comun por producto
- la fuente de datos puede variar por producto
- la sustitucion del adaptador local por una fuente externa o persistida no exige cambiar el contrato HTTP

## 7. Seguridad y errores

La implementacion queda protegida por el permiso canonico `consultar_cliente`, ya definido en `ISSUE-009`.

Adicionalmente, durante la revision final de `ISSUE-013` se detecto que los endpoints protegidos devolvian `401/403` mediante `HTTPException` plana. Para alinear mejor el comportamiento con el contrato de errores estructurados del proyecto, se introdujeron excepciones tipadas de seguridad y handlers globales para:

- `AUTHENTICATION_REQUIRED`
- `INVALID_TOKEN`
- `FORBIDDEN`

En la propia consulta se devuelve ademas:

- `LOAN_PRODUCT_NOT_AVAILABLE`
- `CUSTOMER_NOT_FOUND`

## 8. Cobertura funcional del issue

`ISSUE-013` queda cubierto con:

- endpoint funcional bajo la jerarquia `/loans/{product_code}`
- respuesta JSON estructurada de cliente y campanas
- control de acceso por RBAC
- validacion de producto soportado y activo
- base desacoplada para evolucionar la fuente de consulta sin rehacer la capa API

No incluye todavia:

- integracion con fuente externa real
- persistencia operativa de la consulta como recurso independiente
- consulta enriquecida con validacion inicial de evaluacion (`validate1`)
- bandeja, evaluacion o registro de solicitud

## 9. Validacion automatizada

La implementacion queda respaldada por pruebas que verifican:

- exposicion del endpoint en OpenAPI
- publicacion de schemas de consulta
- acceso exitoso con `analista`
- rechazo sin autenticacion con error estructurado `401`
- rechazo de producto desconocido con error estructurado `404`

Suite directa del issue:

- `backend/tests/test_issue_013_consultations_api.py`

Regresion relevante ejecutada:

- `backend/tests/test_issue_013_consultations_api.py`
- `backend/tests/test_issue_002_openapi.py`
- `backend/tests/test_rbac.py`
- `backend/tests/test_auth.py`
- `backend/tests/test_health.py`

## 10. Evaluacion del resultado

La implementacion cumple correctamente el objetivo y los entregables de `ISSUE-013`.

Cumplimientos observados:

- existe el servicio de consulta PLD por API
- existe el endpoint `POST /api/v1/loans/{product_code}/consultas`
- el endpoint retorna datos de cliente y campanas en JSON estructurado
- la autorizacion se resuelve mediante el permiso canonico `consultar_cliente`
- los errores del flujo implementado quedan alineados con el contrato estructurado del proyecto
- la arquitectura no queda acoplada a `PLD` como unico producto, aunque `PLD` siga siendo el primer proveedor configurado

No se detecto un hallazgo bloqueante restante dentro del alcance de este issue.

## 11. Riesgos y notas abiertas

- La fuente actual es un adaptador local en memoria; sirve para desarrollo y contrato, pero no reemplaza la futura integracion real.
- El registry de proveedores hoy se reconstruye por request; es suficiente para esta fase, aunque puede refinarse cuando se formalice composicion de dependencias.
- La validacion funcional completa de datos y la integracion con la evaluacion real quedan para `ISSUE-014` y los issues del motor PLD.
