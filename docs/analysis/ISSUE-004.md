# ISSUE-004 - Inicializar backend con FastAPI

## 1. Objetivo

Levantar el backend base con FastAPI, configuracion por entorno y endpoint de salud.

## 2. Fuentes revisadas

- `ISSUES.md`
- `SPEC.md`
- `README.md`

## 3. Contexto

- La raiz del repositorio aun no contiene la implementacion nueva.
- `ISSUE-003` debe cerrar antes la estructura base.
- El backend forma parte de la Fase 1 de bootstrap tecnico.
- El stack objetivo del backend ya esta definido en `SPEC.md`.

## 4. Stack base

- Python 3.12+
- FastAPI
- Pydantic
- SQLAlchemy 2.x
- Alembic

## 5. Responsabilidades del backend

- Exponer API REST.
- Autenticar y autorizar.
- Orquestar casos de uso.
- Persistir informacion.
- Invocar el motor de decisiones.
- Invocar asistencia con IA.
- Registrar auditoria.

## 6. Entregables

- Proyecto FastAPI funcional.
- Configuracion base por entorno.
- Endpoint `health`.
- Archivo `pyproject.toml` base.

## 7. Criterios de diseno

- El backend debe arrancar de forma local sin dependencias del legacy.
- La configuracion por entorno debe quedar desacoplada del codigo.
- La base debe dejar listo el camino para persistencia, autenticacion, auditoria y motor.
- El arranque inicial debe ser compatible con un backend multiproducto, no PLD-only.

## 8. Riesgos

- Iniciar el backend antes de tener la estructura base creada.
- Mezclar logica de dominio con el arranque web.
- Introducir una configuracion rigida que luego complique tests, entorno y despliegue.
- Atar el backend a decisiones de frontend todavia no cerradas.

## 9. Criterio de aceptacion

- El backend levanta localmente.
- El endpoint `health` responde correctamente.
- Existe estructura base para configuracion por entorno.
- `ruff` queda integrado desde la inicializacion.

## 10. Notas de referencia

- Este issue solo inicializa el backend.
- No define persistencia completa ni autenticacion final.
- Debe dejar la base lista para `ISSUE-007`, `ISSUE-008` y `ISSUE-010`.

## 11. Cierre formal

`ISSUE-004` queda cerrado como inicializacion del backend base con FastAPI.

Queda consolidado:

- el arranque local del backend.
- la configuracion base por entorno.
- el endpoint `health`.
- el `pyproject.toml` inicial y la base para `ruff`.
- la base tecnica necesaria para continuar con persistencia, autenticacion y motor.

Con este cierre, el equipo puede avanzar a `ISSUE-007`, `ISSUE-008` y `ISSUE-010` sin reabrir la inicializacion del backend.
