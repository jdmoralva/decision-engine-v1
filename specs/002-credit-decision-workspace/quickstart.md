# Quickstart - Validación de la Plataforma Visual de Decisión de Crédito

## Purpose

Validar de punta a punta el flujo planeado de login, catálogo de productos, catálogo de servicios por rol y workspace visual del `Motor de decisiones`.

## Prerequisites

- Python disponible en `.venv\Scripts\python`
- Node.js compatible con Vite 5
- Dependencias frontend instaladas en `frontend/`
- Base local migrada y usuarios semilla cargados

## Setup

### 1. Migrar y sembrar backend

Desde la raíz:

```bash
.venv\Scripts\python -m alembic -c backend/alembic.ini upgrade head
.venv\Scripts\python -m backend.app.infrastructure.db.seed
```

Resultado esperado:

- backend listo con usuarios locales semilla
- credenciales disponibles como `admin / admin123`, `analista / analista123`, `evaluador / evaluador123`, `riesgos / riesgos123`

### 2. Levantar backend

```bash
.venv\Scripts\python -m uvicorn backend.app.main:app --reload
```

Resultado esperado:

- API disponible en `http://127.0.0.1:8000`
- `POST /api/v1/auth/login` y `GET /api/v1/me` responden correctamente

### 3. Levantar frontend

Desde `frontend/`:

```bash
npm install
npm run dev
```

Resultado esperado:

- frontend disponible en `http://127.0.0.1:5173`
- las llamadas a `/api/*` pasan por el proxy Vite

## Validation Scenarios

### Scenario A - Login obligatorio y restauración de sesión

1. Abrir `http://127.0.0.1:5173` en una pestaña nueva.
2. Verificar que la primera vista visible es `Inicio de sesión`.
3. Ingresar con `admin / admin123`.
4. Recargar la página.

Referencias:

- contrato de navegación: `contracts/ui-navigation.md`
- contrato de integración: `contracts/api-integration.md`

Resultado esperado:

- sin sesión no se ven productos ni workspace
- tras login exitoso se restaura la sesión con `/api/v1/me`
- tras recarga, la sesión vuelve a mostrarse si el token sigue siendo válido

### Scenario B - Catálogo de productos

1. Con sesión activa, entrar a la vista `Productos`.
2. Confirmar que aparecen `PLD` y `Hipotecario`.
3. Abrir el menú contextual de cada tarjeta.
4. Seleccionar un producto.

Referencias:

- entidad `Producto`: `data-model.md`
- navegación esperada: `contracts/ui-navigation.md`

Resultado esperado:

- se muestran ambos productos semilla
- cada tarjeta expone accesos rápidos y menú de tres puntos
- el menú no interfiere con la acción principal de abrir el producto

### Scenario C - Visibilidad de servicios por rol

1. Iniciar sesión como `analista`.
2. Abrir `PLD` y observar la vista `Servicios`.
3. Cerrar sesión e iniciar como `riesgos`.
4. Repetir la apertura de `PLD`.

Referencias:

- contrato de visibilidad por rol: `contracts/ui-navigation.md`
- matriz de integración y RBAC: `contracts/api-integration.md`

Resultado esperado:

- `analista` solo ve `Bandeja de solicitudes`
- `riesgos` ve `Bandeja de solicitudes`, `Motor de decisiones` y `Modelo de datos`
- la visibilidad es igual para `PLD` e `Hipotecario`

### Scenario D - Workspace visual de Motor de decisiones

1. Iniciar sesión como `riesgos` o `admin`.
2. Entrar a `PLD` > `Motor de decisiones`.
3. Confirmar que el sidebar muestra `Reglas de Negocio`, `Parámetros` y `Data`.
4. Abrir `workflows` y seleccionar un workflow o el flujo de ejemplo.
5. Seleccionar un nodo en el canvas.
6. Mover el nodo, crear o eliminar una conexión y cambiar la selección.
7. Recargar la pestaña.

Referencias:

- entidades `BorradorWorkflowCanvas`, `NodoWorkflow`, `ConexionWorkflow`: `data-model.md`
- contrato de workspace: `contracts/ui-navigation.md`

Resultado esperado:

- se renderizan sidebar, tabs superiores, canvas y panel derecho
- el inspector refleja el nodo seleccionado
- los cambios de posición/selección se mantienen dentro de la sesión
- el workspace sigue presentándose en español

### Scenario E - Distinción entre backend real y prototipo local

1. Desde el workspace, revisar una vista basada en workflow o perfiles que use datos backend reales.
2. Revisar una vista `channels` o `testing` que aún sea prototipo local.
3. Intentar cerrar sesión y volver a entrar.

Referencias:

- contrato de integración: `contracts/api-integration.md`

Resultado esperado:

- los datos backend reales vuelven a consultarse al abrir la sesión
- los prototipos de sesión no se presentan como configuraciones aprobadas persistidas
- al cerrar sesión se limpia el estado local sensible

## Validation Commands

### Frontend

Desde `frontend/`:

```bash
npm run test
npm run build
```

Cobertura mínima esperada:

- login y restauración de sesión
- guardas de ruta por autenticación
- visibilidad de servicios por rol
- navegación `productos -> servicios -> workspace`
- selección y persistencia de sesión del canvas

### Backend smoke checks

Desde la raíz:

```bash
.venv\Scripts\python -m unittest backend.tests.test_auth backend.tests.test_rbac backend.tests.contract.test_engine_admin_api
```

Resultado esperado:

- autenticación y RBAC siguen consistentes con la UI planeada

## Expected Evidence

- login obligatorio antes de la plataforma
- productos semilla visibles y navegables
- servicios visibles según rol autenticado
- workspace visual funcional para `Motor de decisiones`
- separación explícita entre contratos backend reales y prototipos locales de sesión
