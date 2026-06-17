# Implementation Plan: Plataforma Visual de Decisión de Crédito

**Branch**: `[main]` | **Date**: 2026-06-17 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-credit-decision-workspace/spec.md`

## Summary

Construir una experiencia frontend de escritorio, en español, para una plataforma visual de decisión de crédito con login obligatorio, catálogo de productos, catálogo de servicios por rol y un workspace visual para `Motor de decisiones`. La implementación debe reutilizar la autenticación real (`/auth/login`, `/me`) y los contratos administrativos existentes donde encajan, pero mantener en estado local de sesión los flujos todavía no soportados por backend, como el canvas editable, `channels`, pruebas AB, vista de eventos de producto y parte del modelado de datos. La decisión central es separar claramente lo persistido y gobernado por el backend de lo que será prototipo frontend, sin introducir suposiciones `PLD` en capas compartidas ni presentar como persistido algo que hoy es solo local de sesión.

## Technical Context

**Language/Version**: Python 3.12+ backend, TypeScript 5.6+ frontend

**Primary Dependencies**: FastAPI, SQLAlchemy, Alembic, React 18, Vite 5, Vitest, jsdom

**Storage**: SQLite para backend existente; `localStorage` para sesión autenticada; `sessionStorage` para borradores del workspace visual

**Testing**: `unittest` en backend, `vitest run` en frontend, validación adicional con `npm run build`

**Target Platform**: Aplicación web de escritorio servida localmente con backend HTTP en `127.0.0.1:8000` y frontend Vite en `127.0.0.1:5173`

**Project Type**: Web application con backend API, SPA React y prototipo de editor visual frontend-first

**Performance Goals**: restaurar sesión y cargar la primera vista útil en menos de 2 segundos en entorno local típico; mantener interacciones del canvas suficientemente fluidas para arrastre, selección, zoom y paneo en pantallas de escritorio comunes; evitar scroll horizontal para acciones principales en resoluciones de escritorio comunes

**Constraints**: toda la UI visible en español; login obligatorio antes de productos; visibilidad de servicios global por rol y no por producto; `PLD` y `Hipotecario` visibles como semillas UI sin volverlos contratos universales; no reintroducir HTML backend ni dependencia del DOM legacy; no inventar persistencia backend para `channels`, canvas, AB testing o eventos si el contrato real no existe; cualquier gobierno real de workflows/versiones debe apoyarse en estados backend (`draft`, `active`, `retired`) y RBAC existente

**Scale/Scope**: una nueva superficie frontend con 3 niveles principales (login, productos/servicios, workspace visual), 3 servicios visibles, múltiples submódulos de `Motor de decisiones`, un canvas con nodos y conexiones de ejemplo, y estado editable acotado a sesión para esta fase

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Multiproduct boundaries: PASS. `PLD` y `Hipotecario` se modelan como semillas visibles de producto, mientras la navegación, el RBAC y el workspace permanecen genéricos por `productCode` y `serviceKey`.
- Deterministic engine isolation: PASS. El alcance es frontend y no modifica cálculos del motor ni mezcla lógica del motor con UI o AI.
- Versioning and governance: PASS. El plan distingue entre artefactos reales gobernados por backend (`draft`/`active`/`retired`) y borradores de sesión del canvas que no se presentan como configuraciones publicadas.
- Security and audit impacts: PASS. Se apoya en login real, restauración con `/me`, guardas por rol y uso conservador de endpoints admin ya protegidos; se identifican como faltantes los endpoints de autoservicio/perfil y los de catálogo público.
- AI optionality: PASS. La feature no agrega cambios AI ni coloca AI en el camino crítico.
- Persistence compatibility: PASS. No requiere cambios de persistencia obligatorios; cualquier integración futura seguirá usando los contratos SQLite-compatibles ya existentes.

## Project Structure

### Documentation (this feature)

```text
specs/002-credit-decision-workspace/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── api-integration.md
│   └── ui-navigation.md
└── tasks.md
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
backend/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   └── schemas/
│   ├── application/
│   ├── config/
│   ├── domain/
│   ├── infrastructure/
│   ├── security/
│   └── main.py
└── tests/
    ├── contract/
    ├── integration/
    └── *.py

frontend/
├── src/
│   ├── app/
│   ├── components/
│   ├── features/
│   │   ├── auth/
│   │   ├── platform/
│   │   ├── product-catalog/
│   │   ├── service-catalog/
│   │   ├── decision-workspace/
│   │   ├── credit-requests/
│   │   ├── engine-admin/
│   │   ├── evaluations/
│   │   └── loan-consultations/
│   ├── routes/
│   ├── services/
│   ├── App.tsx
│   └── main.tsx
└── package.json
```

**Structure Decision**: Se mantiene la estructura web application ya presente. El trabajo se concentra en `frontend/src/` con organización por features y una nueva separación explícita entre shell de aplicación, rutas, `platform`, `product-catalog`, `service-catalog` y `decision-workspace`. El backend solo se consume mediante clientes en `frontend/src/services/` y no se amplía en esta fase salvo futura necesidad contractual.

## Implementation Phases

### Phase 0 - Research and alignment

1. Confirmar el encaje entre la spec visual y los contratos/backend reales ya disponibles.
2. Definir qué partes del workspace serán backend-backed y cuáles deben permanecer en sesión local.
3. Fijar el modelo de rutas, estado de sesión, RBAC visible y terminología UI (`channel` visible, `pipeline` interno solo donde aplique).

### Phase 1 - Design and contracts

1. Definir el modelo de entidades frontend y de integración para productos, servicios, workflows, `channels`, parámetros y eventos.
2. Documentar el contrato de navegación UI y el contrato de integración API/mock.
3. Especificar la guía de validación end-to-end para login, productos, servicios y workspace.

### Phase 2 - Implementation planning

1. Reestructurar `frontend/src/App.tsx` hacia shell + rutas + guards de sesión.
2. Implementar páginas de catálogo de productos y catálogo de servicios con seeds y gating por rol.
3. Implementar workspace visual para `Motor de decisiones` con sidebar, canvas, panel derecho y estado editable en `sessionStorage`.
4. Integrar lecturas reales de autenticación y, donde encaje, lecturas administrativas reales de productos/workflows/perfiles.
5. Cubrir con pruebas de sesión, RBAC, navegación y edición local del canvas.

## Architecture Decisions For This Plan

1. **Frontend-first workspace con integración selectiva**. Login, restauración de sesión y endpoints admin existentes se usan como contratos reales; canvas, `channels`, pruebas AB y eventos de producto quedan como prototipo de sesión hasta tener endpoints explícitos.
2. **Separar catálogo público de productos/servicios del módulo admin real**. La vista de productos/servicios no reutiliza directamente la semántica admin-only del backend; consume seeds UI y adapta luego a contratos públicos cuando existan.
3. **RBAC visible derivado de roles autenticados**. La UI calcula visibilidad de servicios desde `/me.roles`, manteniendo una matriz conservadora alineada con los permisos reales del backend.
4. **Borrador del workspace persistido solo por sesión**. El estado editable del canvas se guarda en `sessionStorage` por `productCode` y `workflowId` para cumplir la spec sin crear falsa persistencia backend.
5. **Terminología visible `channel`, integración interna desacoplada de `pipeline`**. La UI no expone `pipeline`; cualquier acoplamiento futuro con `pipeline-strategies` se resuelve mediante adaptadores, no filtrando el término al usuario.
6. **Estados gobernados mapeados en UI, no reinventados**. Donde el backend expone `draft`, `active` o `retired`, la UI presenta `Borrador`, `Aprobado` y `Retirado`; no se inventan estados alternativos en capas compartidas. Por ejemplo, el valor de backend `active` es renderizado como `Aprobado` en la UI.
7. **Desktop-first sin perder claridad estructural**. El layout prioriza pantallas amplias con jerarquía de paneles y navegación lateral, pero debe degradar sin ocultar acciones críticas en anchos de escritorio comunes.

## Post-Design Constitution Check

- Multiproduct boundaries: PASS. El diseño usa `productCode` como dimensión de navegación y evita acoplar estructuras compartidas a `PLD`.
- Deterministic engine isolation: PASS. El canvas y la navegación no mueven lógica determinística fuera del backend ni mezclan decisiones del motor en la UI.
- Versioning and governance: PASS. El diseño diferencia artefactos gobernados por backend de ediciones de sesión, y conserva el flujo `draft -> approved/active` para workflows reales.
- Security and audit impacts: PASS. La autenticación sigue siendo real; la autorización visible se acota a roles autenticados y no expone acciones fuera del backend disponible.
- AI optionality: PASS. No hay nuevas dependencias AI ni impacto en el camino crítico.
- Persistence compatibility: PASS. No se requieren tablas o migraciones nuevas para esta fase de planificación.

## Complexity Tracking

No constitution violations identified.
