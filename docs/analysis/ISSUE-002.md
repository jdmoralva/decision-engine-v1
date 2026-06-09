# ISSUE-002 - Definir contratos iniciales del dominio y API

## 1. Objetivo

Definir los contratos de consulta, evaluacion, traza de evaluacion, registro, cambio de estado, inputs externos y snapshot minimo desacoplados de la UI.

## 2. Fuentes revisadas

- `docs/SPEC.md`
- `docs/project/ISSUES.md`
- `docs/project/BACKLOG.md`
- `old-version/api-build.R`
- `old-version/script.js`
- `old-version/index.html`
- `old-version/bandeja.html`

## 3. Contexto

- El legacy devuelve HTML embebido dentro de respuestas JSON.
- El frontend depende de posiciones de tabla y IDs dinamicos.
- El nuevo sistema debe exponer contratos tipados, estables y documentados con OpenAPI.
- El motor debe quedar desacoplado de la UI y del framework web.

## 4. Contratos a definir

- consulta de cliente PLD
- evaluacion PLD
- `DecisionTrace`
- registro de solicitud
- cambio de estado
- inputs externos de cliente, campanas y deuda
- snapshot minimo por evaluacion
- errores estructurados

## 5. Contrato de entrada sugerido

```json
{
  "tipo_documento": "DNI",
  "numero_documento": "12345678",
  "producto": "PLD",
  "campana": "PLD_48M",
  "marca_cliente": "CLIENTE",
  "perfil": "PERFIL 2",
  "marca_sunedu": "CON SUNEDU",
  "situacion_laboral": "DEP",
  "ingreso_validado": 4500,
  "deuda_reportada": 1200,
  "usuario": "jmorales"
}
```

## 6. Contrato de salida sugerido

```json
{
  "elegible": true,
  "segmento": "CS_DEP",
  "ingreso_revisado": 4500,
  "rci": 0.32,
  "oferta_calculada": 12500,
  "cuota_calculada": 420,
  "tasa": 0.35,
  "plazo": 48,
  "alertas": [],
  "bloqueos": [],
  "version_reglas": "pld-v1",
  "version_parametros": "pld-params-v1",
  "version_pipeline": "pld-pipeline-v1",
  "decision_trace_id": "uuid"
}
```

## 7. `DecisionTrace` minimo

- identificador de evaluacion
- pipeline ejecutado
- nodos o etapas recorridas
- versiones aplicadas
- alertas
- bloqueos
- evidencia estructurada consumible por AI y auditoria humana

## 8. Inputs externos a formalizar

- cliente: tipo y numero de documento
- campanas: oferta, tasa, monto base, saldo y atributos de campana
- deuda: deuda reportada o gasto equivalente
- otros datos operativos usados por el motor: perfil, marca cliente, SUNEDU, situacion laboral e ingreso validado

## 9. Snapshot minimo por evaluacion

Persistir solo los campos efectivamente consumidos por el motor:

- tipo y numero de documento
- producto y campana
- marca de cliente
- perfil
- marca SUNEDU
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

## 10. Errores estructurados

```json
{
  "error": {
    "code": "REQUEST_VALIDATION_ERROR",
    "message": "El monto solicitado excede la oferta.",
    "details": []
  }
}
```

## 11. Criterios de diseno

- Los contratos no dependen de HTML ni de posiciones de tabla.
- Los nombres de campos deben ser estables y versionables.
- Los contratos deben documentarse en OpenAPI.
- El snapshot debe excluir campos solo visuales o derivados de UI.
- La traza debe ser consumible por auditoria humana y por AI.

## 12. Criterio de aceptacion

- Contratos documentados con campos, tipos, validaciones y errores esperados.
- Contratos consistentes con el modelo de datos objetivo.
- OpenAPI incluye los contratos principales.
- Se explicita que se persiste como snapshot y que no.
- El contrato de traza queda definido para AI y auditoria.

## 13. Notas de referencia

- Este documento describe el contrato base para el nuevo sistema.
- No define implementacion.
- Las discrepancias con el legacy deben resolverse segun `docs/SPEC.md` y las decisiones funcionales cerradas del proyecto.

## 14. Cierre formal

`ISSUE-002` queda cerrado como definicion de contratos iniciales del dominio y API.

Queda consolidado:

- el contrato de consulta PLD.
- el contrato de evaluacion y su salida estructurada.
- el contrato minimo de `DecisionTrace`.
- el contrato de registro de solicitud y cambio de estado.
- el contrato de inputs externos de cliente, campanas y deuda.
- el criterio de snapshot minimo por evaluacion.
- el formato estandar de errores.
- la base para documentar estos contratos en OpenAPI.

Con este cierre, el equipo puede avanzar a `ISSUE-006` y `ISSUE-007` sin depender de redefinir los contratos base del dominio.
