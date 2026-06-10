# ISSUE-007 - Implementar ORM y migracion inicial

## 1. Objetivo

Implementar el modelo en SQLAlchemy y habilitar migraciones con Alembic.

## 2. Fuentes revisadas

- `docs/project/ISSUES.md`
- `docs/SPEC.md`
- `docs/analysis/ISSUE-006.md`
- `backend/app/infrastructure/db/base.py`
- `backend/app/infrastructure/db/models.py`
- `backend/alembic/env.py`
- `backend/alembic/versions/20260607_0001_initial_schema.py`
- `backend/tests/test_models.py`
- `backend/tests/test_migrations.py`

## 3. Contexto

- `ISSUE-006` ya definio el modelo logico inicial del MVP.
- Este issue debia materializar ese diseno en ORM y dejar habilitada la creacion reproducible de la base.
- La implementacion debia mantenerse compatible con SQLite y preparada para evolucionar hacia SQL Server.
- La persistencia del MVP debia incluir soporte base para multiproducto, trazabilidad, pipeline y AI.

## 4. Implementacion consolidada

Se implemento la base ORM del backend usando `SQLAlchemy 2.x` con una base declarativa comun y modelos iniciales para las entidades nucleares del MVP.

Tambien se habilito `Alembic` como mecanismo de migracion para crear el esquema desde cero sobre SQLite.

## 5. Entregables implementados

- Base declarativa en `backend/app/infrastructure/db/base.py`.
- Modelos SQLAlchemy iniciales en `backend/app/infrastructure/db/models.py`.
- Configuracion Alembic en `backend/alembic/env.py` y `backend/alembic.ini`.
- Migracion inicial funcional en `backend/alembic/versions/20260607_0001_initial_schema.py`.
- Pruebas automatizadas de metadata y migraciones en:
  - `backend/tests/test_models.py`
  - `backend/tests/test_migrations.py`

## 6. Cobertura del modelo inicial

El ORM inicial incluye tablas base para:

- usuarios, roles y asignacion de roles
- productos de prestamo
- solicitudes de credito e historial de estados
- evaluaciones de prestamo
- snapshots minimos de inputs externos
- `DecisionTrace`
- eventos de decision
- reglas versionadas
- estrategias y nodos de pipeline
- interacciones y plantillas AI

## 7. Criterios de diseno consolidados

- El modelo queda desacoplado de la UI legacy.
- Las entidades relevantes incluyen soporte base para multiproducto mediante `loan_product_code`.
- La persistencia contempla trazabilidad de evaluacion, versionado y evidencia consumida por el motor.
- La base inicial se mantiene portable para SQLite y futura evolucion a SQL Server.
- Alembic queda integrado como mecanismo reproducible de creacion del esquema.

## 8. Validacion automatizada

La implementacion queda respaldada por pruebas que verifican:

- presencia de tablas nucleares del MVP en metadata
- creacion del esquema en SQLite
- existencia de columnas criticas para solicitudes, evaluaciones y trazas
- ejecucion satisfactoria de `alembic upgrade head` sobre una base vacia

## 9. Criterio de aceptacion

- La base SQLite se crea desde cero con migraciones.
- Los modelos reflejan el diseno aprobado en `ISSUE-006`.

## 10. Notas de referencia

- La migracion inicial actual crea el esquema a partir de `Base.metadata`.
- Esto resuelve correctamente el bootstrap del esquema para el MVP inicial.
- Las futuras evoluciones del modelo deberan preferir migraciones explicitas por cambio para mantener trazabilidad fina del historial de schema.

## 11. Cierre formal

`ISSUE-007` queda cerrado como implementacion del ORM inicial y habilitacion de migraciones con Alembic.

Queda consolidado:

- el modelo SQLAlchemy inicial del MVP.
- la base declarativa comun del backend.
- la configuracion operativa de Alembic.
- la migracion inicial funcional para crear la base desde cero.
- la validacion automatizada de metadata y migraciones.

Con este cierre, el equipo puede avanzar a `ISSUE-008`, `ISSUE-009`, `ISSUE-010` y a los casos de uso de negocio sin reabrir la base ORM inicial.
