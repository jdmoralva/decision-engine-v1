# Frontend

Bootstrap minimo del frontend de `Decision Engine` usando `Vite + React + TypeScript`.

## Requisitos

- Node.js 20+
- npm 10+

## Arranque local

```bash
npm install
npm run dev
```

Abrir `http://localhost:5173`.

## Build de produccion

```bash
npm run build
```

El resultado se genera en `frontend/dist/`.

## Estructura actual

- `index.html`: punto de entrada HTML para Vite.
- `src/main.tsx`: montaje de React.
- `src/App.tsx`: shell inicial de la aplicacion.
- `src/styles.css`: estilos globales del bootstrap.
- `src/app/`: composicion transversal del frontend.
- `src/routes/`: definicion de rutas y guardas de navegacion.
- `src/services/`: clientes HTTP y utilidades de integracion.
- `src/features/auth/`: login, sesion y contexto autenticado.
- `src/features/engine-admin/`: pantallas de administracion del motor.
- `src/features/loan-consultations/`: consulta de cliente/oferta por producto.
- `src/features/evaluations/`: evaluacion, resultado y trace.
- `src/features/credit-requests/`: registro, detalle y bandeja operativa.
- `src/features/attachments/`: adjuntos ZIP y timeline de auditoria.
- `src/components/`: componentes UI compartidos.

## Validacion local

Desde `frontend/`:

```bash
npm run dev
npm run build
npm run test
```

## Alcance actual

Este frontend todavia es una base minima. Aun no incluye:

- router
- integracion con backend
- autenticacion
- flujos PLD
- componentes funcionales del MVP
