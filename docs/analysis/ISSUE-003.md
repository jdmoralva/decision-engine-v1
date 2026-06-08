# ISSUE-003 - Bootstrap del repositorio y estructura base

## 1. Objetivo

Crear la estructura base del proyecto nuevo separando backend, frontend y documentacion.

## 2. Fuentes revisadas

- `ISSUES.md`
- `SPEC.md`
- `README.md`

## 3. Contexto

- La raiz del repo todavia no contiene la implementacion nueva.
- `old-version/` es solo referencia funcional y tecnica.
- `SPEC.md` define la estructura objetivo del nuevo sistema.
- Sprint 1 exige dejar el esqueleto listo antes de avanzar a backend y frontend reales.

## 4. Estructura objetivo

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

## 5. Entregables

- Carpetas `backend/`, `frontend/`, `docs/`.
- Estructura base de `backend/app/...`.
- Estructura base de `frontend/src/...`.
- Archivos base del repositorio.
- Convenciones minimas documentadas.

## 6. Criterios de diseno

- Separacion explicita entre nuevo sistema y `old-version/`.
- La estructura debe seguir `SPEC.md` sin asumir acoplamientos legacy.
- No mezclar la futura UI con la logica de dominio.
- No introducir herramientas ni stack no decididos todavia.

## 7. Riesgos

- Crear una estructura demasiado rigida para un MVP multiproducto.
- Introducir nombres o carpetas que supongan PLD como unico producto.
- Adelantar decisiones de toolchain antes de cerrar `ISSUE-005`.

## 8. Criterio de aceptacion

- La estructura en `backend/` y `frontend/` sigue el arbol definido en `SPEC.md`.
- La separacion entre nuevo sistema y `old-version/` es explicita.
- La base del repo queda lista para iniciar `ISSUE-004` y `ISSUE-005`.

## 9. Notas de referencia

- Este issue define solo esqueleto y organizacion inicial.
- No define implementacion funcional.
- La prioridad es habilitar desarrollo paralelo sin contaminar el dominio con detalles de infraestructura.

## 10. Cierre formal

`ISSUE-003` queda cerrado como definicion de la estructura base del repositorio nuevo.

Queda consolidado:

- el arbol objetivo para backend, frontend y documentacion.
- la separacion explicita entre nuevo sistema y `old-version/`.
- las convenciones minimas para iniciar desarrollo paralelo.
- la base necesaria para avanzar a `ISSUE-004` y `ISSUE-005`.

Con este cierre, el equipo puede continuar con el bootstrap tecnico sin reabrir la organizacion estructural del repo.
