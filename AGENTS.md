# AGENTS.md

## Read First

- `README.md` for current repo scope and local URLs.
- `pyproject.toml` and `frontend/package.json` for real backend/frontend commands.
- `backend/app/main.py`, `backend/app/config/settings.py`, and `frontend/vite.config.ts` for actual wiring.
- `.specify/memory/constitution.md` for project constraints that override local habits.
- If legacy behavior matters, use `old-version/api-build.R` as the main runtime reference, not the other `api-build-*` files.

## Project specs 

- `specs/001-project-specification/spec.md`
- `specs/001-project-specification/plan.md`
- `specs/001-project-specification/tasks.md`

## Repo Shape

- `backend/` and `frontend/` are the new implementation. `old-version/` is behavior/rules reference only.
- Keep shared layers product-agnostic. `PLD` is the first product, not the universal model.
- `Cobranzas` is out of scope unless the user asks for it explicitly.
- Do not reintroduce IP-based auth, backend-rendered HTML, or runtime dependence on Excel/DOM structure.

## Verified Commands

- Backend dev server from repo root: `.venv\Scripts\python -m uvicorn backend.app.main:app --reload`
- Run migrations: `.venv\Scripts\python -m alembic -c backend/alembic.ini upgrade head`
- Seed local users/roles: `.venv\Scripts\python -m backend.app.infrastructure.db.seed`
- Run one backend test module: `.venv\Scripts\python -m unittest backend.tests.test_issue_013_consultations_api`
- Frontend dev server from `frontend/`: `npm install`, then `npm run dev`
- Frontend build from `frontend/`: `npm run build`
- Frontend tests from `frontend/`: `npm run test`
- Run one frontend test file from `frontend/`: `npm run test -- tests/session-storage.test.ts`

## Runtime And Test Gotchas

- Backend settings auto-load the repo-root `.env`; override with `DECISION_ENGINE_ENV_FILE` when needed. `.env` is gitignored and may contain real secrets, so never print or commit it.
- `get_settings()`, `get_engine()`, and `get_session_factory()` are cached. Tests that change env or DB settings must call `clear_settings_cache()` and `clear_database_caches()` first.
- `seed_identity_data_for_local_dev()` creates tables with `Base.metadata.create_all()`. Use Alembic when you need migration coverage; seed is only a local bootstrap shortcut.
- Frontend `/api/*` calls rely on the Vite proxy in `frontend/vite.config.ts` targeting `http://127.0.0.1:8000`; local UI work that hits the API needs both servers running.
- `frontend/vite.config.js` and `frontend/vite.config.d.ts` are tracked build artifacts for `vite.config.ts`; if you change the TS config, keep the generated siblings in sync.

## Current Real Entry Points

- FastAPI app entrypoint is `backend.app.main:app`; routers are mounted there.
- The decision engine bootstrap lives in `backend/app/domain/decision_engine/bootstrap.py` and currently registers `PLD` with workflow code `standard`.
- The only implemented business runtime endpoint today is `POST /api/v1/loans/{product_code}/consultas`.
- That consultation flow uses an in-memory local-dev provider in `backend/app/infrastructure/loan_consultations.py`; the built-in happy-path demo record is `PLD` + `DNI 12345678`.
- Evaluation and credit-request routes exist as contracts, but current handlers still return `501`.
- The frontend is still a thin bootstrap: `frontend/src/App.tsx` is the main screen and currently implements login/session restoration in Spanish.

## Working Conventions

- Prefer executable truth over prose when docs disagree.
- If you need behavior from the legacy system, port the behavior, not the legacy architecture.
- Frontend/UI copy should stay in Spanish.

<!-- SPECKIT START -->

For files located inside the `.specify` directory, `glob` may return “No files found”. Attempt to read it directly from the corresponding path under: `<PROJECT_ROOT>/.specify/`.
Examples:
- `constitution.md` → `<PROJECT_ROOT>/.specify/memory/constitution.md`
- `extensions.yml` → `<PROJECT_ROOT>/.specify/extensions.yml`

For additional context about technologies to be used, project structure, shell commands, and other important information, read `specs/001-project-specification/plan.md`.

Specification and code may be in English, but frontend and UI must be in Spanish.

<!-- SPECKIT END -->

