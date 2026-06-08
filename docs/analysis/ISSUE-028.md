# ISSUE-028 - Formalizar fuente oficial de reglas y tratamiento de discrepancias

## 1. Objetivo

Definir la precedencia entre `SPEC.md`, el legacy, el Excel de parametros y las decisiones funcionales cerradas.

## 2. Fuentes revisadas

- `SPEC.md`
- `README.md`
- `docs/project/ISSUES.md`
- `docs/project/BACKLOG.md`
- `old-version/api-build.R`
- `old-version/ParametrosPLD-v3.xlsx`
- `old-version/API_DB.db`

## 3. Contexto

El proyecto ya fija que:

- el MVP inicia con base limpia
- ZIP esta dentro del alcance
- las capacidades AI asistivas forman parte del MVP
- el snapshot debe persistir solo campos consumidos por el motor
- el legacy es referencia funcional, no arquitectura objetivo

## 4. Problema a resolver

Conviven varias fuentes con distinto nivel de autoridad:

- `SPEC.md`
- decisiones funcionales cerradas del proyecto
- comportamiento observado en `old-version/api-build.R`
- parametros historicos en `old-version/ParametrosPLD-v3.xlsx`

Sin una precedencia explicita, cualquier discrepancia puede bloquear analisis, contratos, modelo de datos y motor.

## 5. Precedencia propuesta

Orden de autoridad para el nuevo sistema:

1. Decisiones funcionales cerradas del proyecto.
2. `SPEC.md`.
3. Comportamiento observado en `old-version/api-build.R` y `old-version/API_DB.db`.
4. `old-version/ParametrosPLD-v3.xlsx` como referencia de parametrizacion legacy.

## 6. Regla de uso por fuente

- Decisiones cerradas: mandan cuando existen y estan documentadas.
- `SPEC.md`: define el comportamiento objetivo del nuevo sistema.
- Legacy: sirve para levantar reglas, flujos y casos reales cuando `SPEC.md` o las decisiones cerradas no detallan el punto.
- Excel: solo referencia de parametros y formula historica; no define por si solo el comportamiento del nuevo sistema.

## 7. Tratamiento de discrepancias

- Si una discrepancia existe entre `SPEC.md` y el legacy, prevalece `SPEC.md` salvo que una decision funcional cerrada diga lo contrario.
- Si una discrepancia existe entre legacy y Excel, prevalece el comportamiento confirmado por `SPEC.md` o por decisiones cerradas.
- Si el legacy y el Excel discrepan y no hay cobertura en `SPEC.md`, el caso debe escalarse como decision funcional pendiente.
- Ninguna discrepancia debe resolverse reintroduciendo acoplamientos legacy en el nuevo diseno.

## 8. Ruta de aprobacion

- Relevamiento tecnico o funcional.
- Registro de discrepancia con evidencia.
- Validacion por responsable funcional.
- Cierre en documento del proyecto.
- Uso de la decision cerrada como nueva referencia.

## 9. Criterio de aceptacion

- Existe un orden de precedencia claro entre fuentes.
- El equipo puede resolver discrepancias sin bloquear la implementacion del motor.
- La fuente oficial de reglas queda explicita para consulta, evaluacion, persistencia y auditoria.

## 10. Notas de referencia

- Este documento no redefine reglas de negocio.
- Este documento fija gobernanza documental y tecnica.
- El legacy y el Excel quedan como referencia de migracion, no como autoridad runtime.

## 11. Cierre formal

`ISSUE-028` queda cerrado como definicion de la fuente oficial de reglas y del tratamiento de discrepancias.

Queda consolidado:

- el orden de precedencia entre `SPEC.md`, legacy, Excel y decisiones funcionales cerradas.
- la regla de uso por fuente en el nuevo sistema.
- la politica de tratamiento de discrepancias sin reintroducir acoplamientos legacy.
- la ruta de aprobacion para cambios funcionales y casos ambiguos.
- el criterio para tratar el legacy y el Excel como referencia de migracion, no como autoridad runtime.

Con este cierre, el equipo puede avanzar con contratos, modelo de datos y motor sin depender de resolver de nuevo la gobernanza de fuentes.
