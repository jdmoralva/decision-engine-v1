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

- `index.html`: punto de entrada HTML para Vite
- `src/main.tsx`: montaje de React
- `src/App.tsx`: pantalla inicial del frontend
- `src/styles.css`: estilos globales del bootstrap

## Alcance actual

Este frontend todavia es una base minima. Aun no incluye:

- router
- integracion con backend
- autenticacion
- flujos PLD
- componentes funcionales del MVP
