# ISSUE-009 - Definir permisos e implementar RBAC

## 1. Objetivo

Definir la matriz de permisos del sistema e implementarla en backend.

## 2. Fuentes revisadas

- `docs/project/ISSUES.md`
- `docs/project/BACKLOG.md`
- `docs/SPEC.md`
- `docs/analysis/ISSUE-001.md`
- `docs/analysis/ISSUE-008.md`
- `backend/app/security/dependencies.py`
- `backend/app/security/permissions.py`
- `backend/app/api/routes/admin.py`
- `backend/app/api/routes/auth.py`
- `backend/app/api/routes/evaluations.py`
- `backend/app/api/routes/credit_requests.py`
- `backend/app/infrastructure/db/seed.py`
- `backend/tests/test_auth.py`
- `backend/tests/test_rbac.py`

## 3. Contexto

- `ISSUE-008` ya dejo operativa la autenticacion base del backend.
- El MVP requiere control de acceso por rol para separar acciones operativas, de supervision y de administracion.
- La autorizacion no debe depender de la UI ni de reglas implícitas del legacy.
- La matriz de permisos debe servir como contrato comun para backend y frontend.

## 4. Enfoque adoptado

Se adopta una matriz canonica por `accion de negocio` en lugar de una matriz por endpoint HTTP.

Este enfoque permite:

- expresar permisos con lenguaje funcional del MVP
- reutilizar la misma matriz en backend y frontend
- mapear multiples endpoints a una misma capacidad operativa
- evitar acoplar la autorizacion a rutas o detalles tecnicos que pueden cambiar

Los endpoints del sistema deben mapearse a estas acciones canonicas al implementar o ampliar los casos de uso.

## 5. Roles base del sistema

Los roles base del MVP son:

- `analista`
- `evaluador`
- `supervisor`
- `admin`

Estos roles ya existen en la semilla de identidad del backend y forman la base del modelo RBAC.

## 6. Acciones canonicas de negocio

La matriz RBAC del MVP se define sobre las siguientes acciones:

- `consultar_cliente`
- `evaluar_oferta`
- `consultar_evaluacion`
- `consultar_trace`
- `registrar_solicitud`
- `consultar_solicitud`
- `anular_solicitud`
- `cambiar_estado_solicitud`
- `exportar_bandeja`
- `gestionar_adjuntos`
- `consultar_resumen_ai`
- `explicar_evaluacion_ai`
- `administrar_reglas`
- `administrar_pipeline`
- `administrar_parametros`
- `administrar_usuarios`
- `consultar_auditoria`

## 7. Matriz propuesta de roles y permisos

| Accion | Analista | Evaluador | Supervisor | Admin |
|---|---|---|---|---|
| `consultar_cliente` | Si | Si | Si | Si |
| `evaluar_oferta` | Si | Si | Si | Si |
| `consultar_evaluacion` | Si | Si | Si | Si |
| `consultar_trace` | No | Si | Si | Si |
| `registrar_solicitud` | Si | No | Si | Si |
| `consultar_solicitud` | Si | Si | Si | Si |
| `anular_solicitud` | Si | Si | Si | Si |
| `cambiar_estado_solicitud` | No | Si | Si | Si |
| `exportar_bandeja` | Si | Si | Si | Si |
| `gestionar_adjuntos` | Si | Si | Si | Si |
| `consultar_resumen_ai` | No | No | Si | Si |
| `explicar_evaluacion_ai` | Si | Si | Si | Si |
| `administrar_reglas` | No | No | No | Si |
| `administrar_pipeline` | No | No | No | Si |
| `administrar_parametros` | No | No | No | Si |
| `administrar_usuarios` | No | No | No | Si |
| `consultar_auditoria` | No | No | Si | Si |

## 8. Lectura funcional por rol

### `analista`

- consulta cliente y ofertas
- ejecuta evaluaciones
- registra solicitudes
- puede anular solicitudes
- gestiona adjuntos
- exporta su vista operativa
- no cambia estados posteriores ni administra configuracion

### `evaluador`

- consulta cliente y evaluaciones
- revisa trazas de decision
- puede cambiar estado de solicitudes
- puede anular solicitudes
- no administra reglas, pipeline ni usuarios

### `supervisor`

- mantiene capacidades operativas amplias
- puede cambiar estado de solicitudes
- puede consultar trazas y auditoria
- puede usar resumen AI de bandeja
- no administra reglas ni pipeline en esta definicion base

### `admin`

- tiene acceso total operativo y administrativo
- administra reglas, pipeline, parametros y usuarios
- conserva acceso a auditoria y a todas las acciones del flujo

## 9. Reglas de diseno obligatorias

- `cambiar_estado_solicitud` requiere validacion doble: permiso por rol y transicion valida de estado.
- `consultar_trace` se separa de `consultar_evaluacion` para no exponer evidencia interna a todos los roles por defecto.
- `consultar_resumen_ai` se restringe a `supervisor` y `admin` por tratarse de una vista agregada de bandeja.
- `administrar_reglas`, `administrar_pipeline` y `administrar_parametros` quedan reservadas a `admin` en el MVP base.
- Las futuras aprobaciones gobernadas sobre reglas o pipeline no reemplazan el control RBAC; lo complementan.

## 10. Mapeo inicial esperado a endpoints

Este issue define permisos por accion de negocio. La implementacion backend debe mapearlos a endpoints conforme se habiliten los casos de uso.

Mapeo inicial esperado:

- `POST /api/v1/loans/{product_code}/consultas` -> `consultar_cliente`
- `POST /api/v1/loans/{product_code}/evaluaciones` -> `evaluar_oferta`
- `GET /api/v1/loans/{product_code}/evaluaciones/{evaluation_id}` -> `consultar_evaluacion`
- `GET /api/v1/loans/{product_code}/evaluaciones/{evaluation_id}/trace` -> `consultar_trace`
- `POST /api/v1/credit-requests` -> `registrar_solicitud`
- `GET /api/v1/credit-requests/{request_id}` -> `consultar_solicitud`
- `POST /api/v1/credit-requests/{request_id}/status-transitions` -> `anular_solicitud` cuando `target_status=cancelled`
- `POST /api/v1/credit-requests/{request_id}/status-transitions` -> `cambiar_estado_solicitud` para las demas transiciones
- exportacion de bandeja -> `exportar_bandeja`
- endpoints de adjuntos ZIP -> `gestionar_adjuntos`
- endpoint AI de explicacion -> `explicar_evaluacion_ai`
- endpoint AI de resumen de bandeja -> `consultar_resumen_ai`
- endpoints administrativos de reglas -> `administrar_reglas`
- endpoints administrativos de pipeline -> `administrar_pipeline`
- endpoints administrativos de parametros -> `administrar_parametros`
- endpoints administrativos de usuarios -> `administrar_usuarios`
- endpoints de auditoria -> `consultar_auditoria`

## 11. Estado actual de implementacion

El backend ya cuenta con:

- autenticacion base operativa
- resolucion del usuario actual autenticado
- helper base `require_roles(...)`
- matriz ejecutable de permisos en `backend/app/security/permissions.py`
- helper `require_permission(...)` para aplicar RBAC por accion de negocio
- proteccion por permiso en endpoints administrativos y de negocio ya expuestos
- endpoint administrativo base de reglas protegido para `administrar_reglas`
- autorizacion diferenciada en `status-transitions` para distinguir anulacion de otros cambios de estado
- cobertura automatizada de permisos por rol y accion

Con esta base, los endpoints actuales del backend ya respetan la matriz canonica en los puntos implementados para consulta, evaluacion, registro, anulacion, cambio de estado, trazas y administracion de reglas.

## 12. Criterio de aceptacion

- Los roles permiten o restringen consultar, evaluar, registrar, anular, cambiar estado y administrar reglas.
- Los endpoints criticos fallan correctamente sin permisos.

## 13. Notas de referencia

- Este documento fija la matriz canonica de permisos del MVP.
- La implementacion backend puede comenzar con helpers por rol y evolucionar hacia permisos por accion mas expresivos, siempre que respete esta matriz.
- La UI debe consumir esta misma definicion para mostrar u ocultar acciones operativas.
- La falta temporal de algunos endpoints no invalida esta matriz; define el contrato que debe respetarse al implementarlos.

## 14. Validacion automatizada

La implementacion queda respaldada por pruebas que verifican:

- restriccion de acceso administrativo por rol
- restriccion de consulta de `DecisionTrace`
- restriccion de registro de solicitudes por rol
- proteccion de anulacion de solicitudes mediante `status-transitions`
- restriccion de cambio de estado por rol
- acceso permitido a endpoints protegidos cuando el rol si tiene permiso, aun cuando el caso de uso siga en `501`

La suite relevante queda cubierta en:

- `backend/tests/test_auth.py`
- `backend/tests/test_rbac.py`

## 15. Cierre formal

`ISSUE-009` queda cerrado como definicion e implementacion base del RBAC del backend para el MVP.

Queda consolidado:

- el enfoque RBAC por accion de negocio
- el conjunto de roles base del sistema
- la matriz de permisos del MVP
- las reglas de diseno para autorizacion sensible
- la matriz ejecutable de permisos en backend
- la proteccion efectiva de endpoints actuales por accion de negocio
- la cobertura automatizada de autorizacion por rol

Con este cierre, el equipo puede continuar con los casos de uso del MVP y extender nuevos endpoints reutilizando la misma matriz canonica sin reabrir la definicion base de permisos.
