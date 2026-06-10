# ISSUE-008 - Definir e implementar autenticacion base

## 1. Objetivo

Seleccionar e implementar el mecanismo inicial de autenticacion.

## 2. Fuentes revisadas

- `docs/project/ISSUES.md`
- `docs/SPEC.md`
- `README.md`
- `backend/README.md`
- `backend/app/api/routes/auth.py`
- `backend/app/api/schemas/auth.py`
- `backend/app/application/auth.py`
- `backend/app/security/dependencies.py`
- `backend/app/security/passwords.py`
- `backend/app/security/tokens.py`
- `backend/tests/test_auth.py`

## 3. Contexto

- El MVP necesitaba una base de autenticacion funcional antes de implementar permisos completos y casos de uso de negocio.
- El nuevo sistema debia evitar dependencias del mecanismo legacy basado en IP o acoplamientos a HTML generado por backend.
- En esta etapa no era necesario cerrar la integracion con SSO o proveedor corporativo final.
- El objetivo del issue era dejar un mecanismo inicial operativo, testeable y desacoplado del frontend.

## 4. Decision de autenticacion adoptada

Se adopto una autenticacion base temporal para entorno local y de desarrollo con estas decisiones:

- login interno por `username` y `password`
- almacenamiento de password con hashing `pbkdf2_hmac`
- emision de token bearer firmado con HMAC
- resolucion del usuario autenticado a partir del token
- exposicion de `GET /api/v1/me` para identificar de forma consistente al usuario actual

Esta decision cumple la necesidad de bootstrap del MVP sin reintroducir autenticacion por IP y sin bloquear la futura sustitucion por un proveedor corporativo.

## 5. Implementacion consolidada

La autenticacion base del backend quedo implementada con un flujo simple y reproducible:

- `POST /api/v1/auth/login` valida credenciales y devuelve un token bearer
- `GET /api/v1/me` devuelve identidad y roles del usuario autenticado
- una dependencia de seguridad resuelve el contexto autenticado desde el token
- el backend puede restringir endpoints posteriores usando el contexto autenticado y sus roles

## 6. Entregables implementados

- Decision de autenticacion base documentada para el bootstrap del proyecto.
- Implementacion backend de autenticacion en `backend/app/api/routes/auth.py`.
- Esquemas de request y response en `backend/app/api/schemas/auth.py`.
- Logica de autenticacion y consulta de roles en `backend/app/application/auth.py`.
- Dependencia para usuario actual autenticado en `backend/app/security/dependencies.py`.
- Hashing y verificacion de passwords en `backend/app/security/passwords.py`.
- Emision y validacion de tokens firmados en `backend/app/security/tokens.py`.
- Validacion automatizada en `backend/tests/test_auth.py`.

## 7. Criterios de diseno consolidados

- La autenticacion queda desacoplada del frontend.
- La identificacion del usuario actual no depende de IP ni del legado.
- El mecanismo es suficientemente simple para desarrollo local y pruebas automatizadas.
- La implementacion deja una base compatible con posterior evolucion a SSO o proveedor corporativo.
- La seguridad de acceso queda separada de la logica de negocio PLD.

## 8. Validacion automatizada

La implementacion queda respaldada por pruebas que verifican:

- login correcto y entrega de bearer token
- recuperacion correcta del usuario autenticado en `GET /api/v1/me`
- rechazo de credenciales invalidas
- uso efectivo del contexto autenticado para restringir un endpoint protegido

## 9. Criterio de aceptacion

- El backend identifica al usuario autenticado.
- El mecanismo elegido queda documentado y operativo.

## 10. Notas de referencia

- La autenticacion actual es una base temporal del MVP y no constituye aun la integracion corporativa final.
- La matriz completa de permisos no pertenece a este issue y queda para `ISSUE-009`.
- La existencia de tokens firmados y del endpoint `me` deja lista la base para session handling en frontend y para los casos de uso protegidos del backend.

## 11. Cierre formal

`ISSUE-008` queda cerrado como definicion e implementacion de la autenticacion base del backend.

Queda consolidado:

- el mecanismo inicial de login por credenciales.
- la emision y validacion de bearer tokens firmados.
- la identificacion consistente del usuario actual.
- la base de seguridad necesaria para permisos y RBAC.
- la validacion automatizada del flujo principal de autenticacion.

Con este cierre, el equipo puede avanzar a `ISSUE-009` y a los casos de uso autenticados del MVP sin reabrir la autenticacion base.
