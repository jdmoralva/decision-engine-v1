# AGENTS.md

## Estado real del repo

- La raiz todavia no contiene la implementacion nueva. Hoy este repo es principalmente documental mas el legado en `old-version/`.
- No hay manifests ni toolchain ejecutable en la raiz todavia: sin `package.json`, `pyproject.toml`, `requirements.txt`, workflows CI, `opencode.json` ni `AGENTS.md` previo.
- `README.md` en la raiz es un resumen ejecutivo del proyecto y su estado actual, no una especificacion tecnica completa.

## Fuentes de verdad

Lee en este orden antes de asumir nada:

1. `README.md`
2. `SPEC.md`
3. `docs/project/BACKLOG.md`
4. `docs/project/ISSUES.md`
5. `docs/project/SPRINTS.md`
6. `docs/analysis/README.md`
7. `old-version/README.md`
8. `old-version/api-build.R`

Usa los docs de la raiz y `docs/` para el sistema nuevo y `old-version/` solo como referencia funcional y de reglas.

## Alcance del proyecto nuevo

- El nuevo sistema cubre solo `PLD / solicitudes de credito`.
- `Cobranzas` aparece en `old-version/`, pero esta fuera de alcance salvo instruccion explicita del usuario.
- No reintroduzcas decisiones del legado que ya fueron descartadas en `SPEC.md`, especialmente:
  - autenticacion basada en IP
  - dependencia de HTML generado por backend
  - acoplamiento UI-tabla para reglas de negocio

## Como entender el legado

- El entrypoint principal del legado es `old-version/api-build.R`.
- La version funcional completa del backend legado esta en `old-version/api-build.R`; `api-build-v2.R`, `api-build-v3.R` y `api-debug.R` no son la referencia principal.
- `old-version/api-build.R` sirve HTML y API desde el mismo proceso Plumber y termina con `api$run(host = '0.0.0.0', port = 8080, swagger = F)`.
- La logica clave del flujo PLD legacy esta repartida entre:
  - `old-version/index.html`
  - `old-version/script.js`
  - `old-version/api-build.R`
  - `old-version/API_DB.db`
  - `old-version/ParametrosPLD-v3.xlsx`

## Que no asumir

- No inventes comandos de build, test, lint o typecheck para la raiz: hoy no existen en el repo.
- No asumas que la estructura `backend/` y `frontend/` ya existe; en este momento solo esta definida en `SPEC.md` y `docs/project/BACKLOG.md`.
- No tomes `old-version/` como plantilla de arquitectura; solo usalo para levantar comportamiento, datos y reglas.
- No uses `docs/sessions/SESSIONS.md` como fuente de verdad tecnica; solo guarda referencias de sesiones previas.

## Restricciones importantes para futuras sesiones

- Si vas a construir la nueva app, sigue la estructura objetivo definida en `SPEC.md` en lugar de extender el monolito legacy.
- Manten separado el motor de decisiones del framework web y de la UI; esta separacion es un objetivo central del repo.
- Trata `ParametrosPLD-v3.xlsx` como fuente legacy para migracion de parametros, no como dependencia runtime por defecto.
- Si detectas discrepancias entre documentacion y legado ejecutable, prioriza:
  - contratos y alcance en `SPEC.md` para el sistema nuevo
  - comportamiento de `old-version/api-build.R` para el sistema antiguo

## Git y worktree

- El worktree puede estar sucio desde el inicio. Revisa `git status --short` antes de editar.
- No limpies ni reestructures `old-version/` por defecto; es material de referencia para migracion.
