# AGENTS.md

## Leer primero

1. `README.md`
2. `specs/001-project-specification/spec.md`
3. `specs/001-project-specification/plan.md`
4. `specs/001-project-specification/tasks.md`
5. `specs/001-project-specification/data-model.md`
6. `specs/001-project-specification/quickstart.md`
7. `specs/001-project-specification/research.md`
8. `backend/README.md`
9. `frontend/README.md`
10. `old-version/README.md`
11. `old-version/api-build.R`

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
- Si detectas discrepancia entre docs y legacy, prioriza `specs/001-project-specification/spec.md` para el sistema nuevo y `old-version/api-build.R` para el sistema viejo.
- El archivo `NOTES.md` es un documento de ayuda memoria para el programador.

<!-- SPECKIT START -->
For constitution file, `glob` may return “No files found”, read file from `C:/Users/User/Documents/1. Projects/23. Decision Engine 1/.specify/memory/constitution.md`.
For additional context about technologies to be used, project structure, shell commands, and other important information, read `specs/001-project-specification/plan.md`.
Specification and code may be in English, but frontend and UI must be in Spanish.
<!-- SPECKIT END -->
