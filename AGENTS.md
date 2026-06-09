# AGENTS.md

## Leer primero

1. `README.md`
2. `docs/SPEC.md`
3. `docs/project/BACKLOG.md`
4. `docs/project/ISSUES.md`
5. `docs/project/SPRINTS.md`
6. `docs/analysis/README.md`
7. `backend/README.md`
8. `frontend/README.md`
9. `old-version/README.md`
10. `old-version/api-build.R`

## Fuentes de verdad

- Para comandos y toolchain, manda el archivo ejecutable sobre el texto: `pyproject.toml`, `frontend/package.json`, `backend/app/main.py`, `frontend/src/App.tsx`.
- Si docs y config chocan, confia en la config o en el codigo ejecutable.

## Forma del repo

- El MVP nuevo cubre `PLD` (`Prestamo de Libre Disponibilidad`) y `solicitudes de credito`.
- `backend/` y `frontend/` ya son la implementacion nueva; `old-version/` es solo referencia funcional y de reglas.
- No reintroduzcas autenticacion por IP, HTML generado por backend, ni reglas de negocio acopladas a tablas/UI.
- `Cobranzas` existe solo en el legado y queda fuera de alcance salvo pedido explicito.
- La nueva plataforma debe seguir preparada para otros productos de prestamo; no modeles todo como si PLD fuera el unico.

## Entry points y comandos

- Backend: `python -m uvicorn backend.app.main:app --reload`.
- Backend tests: `python -m unittest backend.tests.test_settings backend.tests.test_health backend.tests.test_models backend.tests.test_migrations backend.tests.test_auth backend.tests.test_seed`.
- Alembic: `python -m alembic -c backend/alembic.ini upgrade head`.
- Seed local: `python -m backend.app.infrastructure.db.seed`.
- Frontend: en `frontend/`, `npm install`, `npm run dev`, `npm run build`, `npm run test`.
- Python debe ejecutarse con `.venv\\Scripts\\python` cuando aplique.

## Legacy

- El backend legacy funcional principal es `old-version/api-build.R`; los otros `api-build-*` no son la referencia primaria.
- El legado sirve como guía de comportamiento, datos y reglas, no como plantilla de arquitectura.
- `ParametrosPLD-v3.xlsx` es fuente de migracion de parametros, no dependencia runtime por defecto.

## Trabajo diario

- Revisa `git status --short` antes de editar.
- No toques cambios ajenos sin necesidad.
- Si detectas discrepancia entre docs y legacy, prioriza `docs/SPEC.md` para el sistema nuevo y `old-version/api-build.R` para el sistema viejo.
