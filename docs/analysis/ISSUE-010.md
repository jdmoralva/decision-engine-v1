# ISSUE-010 - Crear modulo aislado del motor de decisiones

## 1. Objetivo

Crear el modulo base del motor de decisiones desacoplado de FastAPI y de la UI, preparado para pipeline configurable por nodos.

## 2. Fuentes revisadas

- `docs/project/ISSUES.md`
- `docs/project/BACKLOG.md`
- `docs/SPEC.md`
- `backend/app/domain/decision_engine/__init__.py`
- `backend/app/domain/decision_engine/contracts.py`
- `backend/app/domain/decision_engine/exceptions.py`
- `backend/app/domain/decision_engine/normalization.py`
- `backend/app/domain/decision_engine/nodes.py`
- `backend/app/domain/decision_engine/pipeline.py`
- `backend/app/domain/decision_engine/registry.py`
- `backend/app/api/mappers/evaluations.py`
- `backend/tests/test_decision_engine_contracts.py`
- `backend/tests/test_decision_engine_normalization.py`
- `backend/tests/test_decision_engine_pipeline.py`
- `backend/tests/test_decision_engine_registry.py`
- `backend/tests/test_evaluation_contract_mappers.py`

## 3. Contexto

- El backend ya contaba con contratos HTTP preliminares, ORM base, autenticacion y RBAC.
- `ISSUE-010` debia introducir el modulo de dominio del motor sin acoplarlo a FastAPI.
- La solucion debia evitar que la plataforma quedara centrada en `PLD`, dejando a `PLD` como producto y no como forma base del motor.

## 4. Implementacion consolidada

Se implemento un nuevo paquete de dominio `decision_engine` en `backend/app/domain/decision_engine/` como nucleo aislado del motor.

La implementacion incluye:

- contratos internos del motor con `Pydantic`
- traza estructurada de decision
- normalizacion base compartida
- abstraccion de nodos
- contexto de ejecucion
- estrategia de pipeline
- orquestador `async`
- validacion topologica con deteccion de referencias invalidas, nodos inalcanzables y ciclos
- registry multiproducto por `product_code`

## 5. Entregables implementados

- `backend/app/domain/decision_engine/contracts.py`
- `backend/app/domain/decision_engine/exceptions.py`
- `backend/app/domain/decision_engine/normalization.py`
- `backend/app/domain/decision_engine/nodes.py`
- `backend/app/domain/decision_engine/pipeline.py`
- `backend/app/domain/decision_engine/registry.py`
- `backend/app/domain/decision_engine/__init__.py`

Adicionalmente se implementaron adaptadores HTTP finos en:

- `backend/app/api/mappers/evaluations.py`

## 6. Cobertura funcional del modulo

El modulo cubre:

- request interno generico por producto
- resultado interno generico por producto
- `AppliedVersions`
- `DecisionTrace` estructurado
- ejecucion por `DecisionNode`
- branching controlado por outcome
- seleccion de runtime por producto
- soporte base para futuros productos distintos de `PLD`

## 7. Criterios de diseno consolidados

- El core del motor no depende de FastAPI ni de schemas HTTP.
- La estructura base no asume que `PLD` sera el unico producto soportado.
- La API REST actua como adaptador de borde, no como contrato canonico del motor.
- El contrato interno del motor permanece en dominio.
- El pipeline se valida antes de ejecutar.

## 8. Validacion automatizada

La implementacion queda respaldada por pruebas que verifican:

- importacion del modulo sin dependencias web
- contratos internos validos
- normalizacion base
- orquestacion `async`
- branching controlado
- rechazo de topologias invalidas
- rechazo de ciclos
- registry multiproducto
- adaptacion entre contratos REST y contratos internos

Suite relevante:

- `backend/tests/test_decision_engine_contracts.py`
- `backend/tests/test_decision_engine_normalization.py`
- `backend/tests/test_decision_engine_pipeline.py`
- `backend/tests/test_decision_engine_registry.py`
- `backend/tests/test_evaluation_contract_mappers.py`

## 9. Criterio de aceptacion

- El modulo puede importarse sin dependencias web.
- El contrato del motor es estable y testeable.
- El motor expone funciones `async`.
- La estructura no asume que `PLD` sera el unico producto soportado.
- Existe soporte base para `DecisionNode`, `pipeline_strategy` y branching controlado.

## 10. Riesgos y notas abiertas

- El core ya es multiproducto, pero la API HTTP actual de evaluaciones sigue modelada alrededor de `PLD`.
- El adaptador inverso hacia `EvaluationRequest` debe tratarse como compatibilidad temporal mientras el contrato REST siga siendo PLD-especifico.
- La integracion real del endpoint con reglas de `PLD` queda para `ISSUE-011`.

## 11. Cierre formal

`ISSUE-010` queda cerrado como implementacion del modulo aislado base del motor de decisiones.

Queda consolidado:

- el paquete `decision_engine`
- el contrato interno canonico del motor
- la traza estructurada de decision
- la validacion base del pipeline
- el registry multiproducto
- el desacople entre dominio del motor y capa HTTP
