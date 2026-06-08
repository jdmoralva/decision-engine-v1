# ISSUE-027 - Definir contratos de inputs externos y snapshot minimo

## 1. Objetivo

Formalizar los inputs externos de cliente, campanas y deuda, y definir el snapshot minimo que se persiste por evaluacion.

## 2. Fuentes revisadas

- `old-version/api-build.R`
- `old-version/script.js`
- `SPEC.md`
- `docs/project/ISSUES.md`
- `docs/project/BACKLOG.md`

## 3. Inputs externos observados

### 3.1 Cliente

- `TIPODOC`
- `CODDOC`

### 3.2 Campana / oferta

- `Oferta`
- `TASA_PLD`
- `OFERTA_PLD_5_INICIAL`
- `SALDO_CONSUMO`

### 3.3 Deuda / capacidad

- `Deuda`
- `Ingreso`
- `Sueldo`

### 3.4 Datos complementarios usados por la evaluacion

- `Cliente`
- `Perfil`
- `Sunedu`

## 4. Flujo de consumo de inputs

### 4.1 Consulta y validacion inicial

- `POST /get_tn` obtiene datos del cliente y campañas desde `CampaniaPLD`.
- `POST /validate1` devuelve campos complementarios para completar la evaluacion.

### 4.2 Recalculo y evaluacion

- `POST /validate2` recibe datos desde la UI y los combina con `CampaniaPLD` y `ParametrosPLD-v3.xlsx`.
- El recalculo usa informacion de perfil, banda de ingreso, marca de cliente, situacion laboral, deuda o gasto, oferta y tasa.

## 5. Contratos a formalizar

- contrato de consulta de cliente.
- contrato de validacion inicial.
- contrato de recalculo / evaluacion.
- contrato de inputs externos para cliente, campanas y deuda.
- contrato de error estructurado.
- contrato de snapshot minimo por evaluacion.

## 6. Snapshot minimo propuesto

Persistir solo los campos realmente consumidos por el motor:

- tipo de documento
- numero de documento
- producto o campaña evaluada
- marca de cliente
- perfil
- bandera SUNEDU
- situacion laboral
- ingreso validado
- deuda reportada o gasto usado
- oferta base usada
- tasa aplicada
- plazo aplicado
- RCI calculado
- version de reglas
- version de parametros
- version de pipeline
- identificador de evaluacion

## 7. Reglas de persistencia

- No persistir campos solo visuales de UI.
- No persistir HTML ni estructuras derivadas de tabla.
- Persistir solo entradas reales del motor y evidencia de calculo.
- Separar origen externo, dato operativo, dato calculado y dato de trazabilidad.

## 8. Ambiguedades detectadas

- Si `Cliente` es un dato externo o una derivacion operativa.
- Si `Oferta` se guarda como input externo o solo como resultado recalculado.
- Si `Deuda` y `GASTO` conviven como fuentes alternativas o si una prevalece.
- Que campos quedan en el snapshot minimo y cuales solo en `DecisionTrace`.

## 9. Criterio de aceptacion

- Queda explicito que solo se persisten los campos consumidos por el motor.
- Los contratos diferencian origen externo, uso operativo y trazabilidad de evaluacion.
- El snapshot minimo queda cerrado sin depender de la UI legacy.

## 10. Notas de referencia

- Este documento describe el comportamiento observado del legacy y el criterio minimo necesario para el nuevo sistema.
- No define implementacion nueva.
- Las discrepancias entre fuentes deben resolverse segun `SPEC.md` y las decisiones funcionales cerradas del proyecto.

## 11. Cierre formal

`ISSUE-027` queda cerrado como definicion de contratos de inputs externos y snapshot minimo.

Queda consolidado:

- el inventario de inputs externos consumidos por la evaluacion.
- el criterio para persistir solo los campos efectivamente usados por el motor.
- la separacion entre dato externo, dato operativo, dato calculado y dato de trazabilidad.
- la lista minima de campos para el snapshot por evaluacion.
- las ambiguedades que deben resolverse al diseñar `DecisionTrace` y el modelo de datos.

Con este cierre, el equipo puede avanzar a la definicion final del modelo de datos y del `DecisionTrace` sin depender de seguir analizando inputs legacy.
