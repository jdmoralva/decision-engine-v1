# API Integration Contract

## Scope

Contrato de integración entre la nueva UI y los endpoints/backend existentes, más la delimitación explícita de lo que queda como mock o estado local de sesión.

## Backend-Backed Endpoints Used Directly

### Authentication

| Method | Path | UI Usage |
|---|---|---|
| `POST` | `/api/v1/auth/login` | inicio de sesión |
| `GET` | `/api/v1/me` | restauración de sesión, identidad y roles |

### Engine Admin Reads And Actions That Already Exist

| Method | Path | UI Usage |
|---|---|---|
| `GET` | `/api/v1/admin/engine/products` | listados administrativos cuando corresponda |
| `GET` | `/api/v1/admin/engine/products/{productCode}` | detalle administrativo de producto |
| `GET` | `/api/v1/admin/engine/products/{productCode}/workflows` | listados de workflows por producto |
| `GET` | `/api/v1/admin/engine/workflows/{workflowId}` | detalle de workflow gobernado |
| `GET` | `/api/v1/admin/engine/profiles/{roleCode}/permissions` | vista admin de permisos por perfil |
| `PUT` | `/api/v1/admin/engine/profiles/{roleCode}/permissions` | edición admin de permisos por perfil |

Reglas:

- solo se consumen en pantallas o contextos que respeten el RBAC real del backend
- la UI no debe reutilizar estos endpoints como si fueran catálogo público para todos los usuarios
- el estado backend `active` de workflows debe mostrarse en la UI como `Aprobado`

## UI Adapters

### Role To Service Adapter

Entrada:

- `me.roles[]` desde `GET /api/v1/me`

Salida:

- servicios visibles en español para la vista `Servicios`

Mapeo inicial:

- `analista`, `evaluador` -> `Bandeja de solicitudes`
- `admin`, `admin_negocio`, `admin_riesgos` -> `Bandeja de solicitudes`, `Motor de decisiones`, `Modelo de datos`

### Status Adapter

Entrada backend:

- `draft`
- `active`
- `retired`

Salida UI:

- `Borrador`
- `Aprobado`
- `Retirado`

## Session-Local Interfaces

Las siguientes capacidades no tienen todavía un contrato backend adecuado para esta spec y deben implementarse como estado local de sesión o mocks explícitos:

- catálogo público de productos para cualquier usuario autenticado
- catálogo público de servicios por usuario
- acciones de perfil para cambiar contraseña o consultar permisos propios aprobados
- CRUD/listado/aprobación de `channels`
- validación de compatibilidad workflow/parámetros para `channels`
- persistencia del canvas editable de workflow
- ejecución del workflow desde el canvas con historial visual
- pruebas AB `champion` vs `challenger`
- tabla `events` con últimas 50 consultas, filtros por periodo y cliente
- secciones `Data` de importación de datasets, relaciones, medidas y catálogos con el shape exacto de la spec
- soporte backend real para `Hipotecario`

## Contract Boundaries

1. La UI no debe presentar prototipos de sesión como artefactos publicados del motor.
2. La UI no debe exponer el término `pipeline` al usuario final; si se reutiliza `pipeline-strategies`, se hace mediante adaptación interna.
3. La UI no debe asumir que un endpoint admin es válido para usuarios no administrativos.
4. La sesión autenticada usa `localStorage`; el borrador visual usa `sessionStorage`.
5. Cualquier futura persistencia de `channels`, eventos o canvas requiere nuevo contrato backend antes de salir del modo prototipo.

## Testing Expectations

- mockear `POST /auth/login` y `GET /me` en pruebas de sesión y navegación
- mockear endpoints admin para pruebas de workspace gobernado
- probar explícitamente que usuarios no admin no ven servicios restringidos ni rutas admin
- probar que el borrador del canvas sobrevive recarga dentro de la misma sesión y se limpia al cerrar sesión
