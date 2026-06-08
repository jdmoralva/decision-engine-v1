# ISSUE-033 - Definir politicas de seguridad y diseno de contratos AI

## 1. Objetivo

Definir que datos pueden procesarse, que politicas de privacidad aplican y como se diseña la persistencia auditable de interacciones AI.

## 2. Fuentes revisadas

- `SPEC.md`
- `README.md`
- `docs/project/ISSUES.md`
- `docs/project/BACKLOG.md`
- `old-version/api-build.R`
- `old-version/README.md`

## 3. Contexto

- La capa AI es asistiva, no decisora.
- El motor determinista debe seguir funcionando si la AI falla.
- La AI debe consumir `DecisionTrace`.
- El MVP incluye AI asistiva, pero con grounding estricto y trazabilidad.
- El snapshot y la persistencia deben limitarse a campos efectivamente consumidos.

## 4. Principios de diseno AI

- No autonomia: la IA recomienda y explica, no decide.
- Grounding estricto: el prompt usa solo datos explicitamente permitidos.
- Explicabilidad auditable: toda salida debe poder rastrearse.
- Aislamiento: el flujo principal no depende de la AI.

## 5. Datos que puede consumir la AI

- Ficha del cliente.
- Reglas aplicadas.
- Resultado del motor.
- `DecisionTrace`.
- Contexto operativo minimo necesario para explicacion o resumen.

## 6. Datos que deben omitirse o minimizarse

- Datos innecesarios para la explicacion.
- Datos sensibles no requeridos para el caso.
- Campos de UI o presentacion sin valor de negocio.
- Cualquier informacion que no haya sido usada por el motor.

## 7. Politica de minimizacion

- En prompts y respuestas solo incluir campos relevantes.
- No enviar campos completos por conveniencia.
- Si un dato no aporta a la explicacion, no viaja al modelo.
- Si un dato puede anonimizarse o redondearse sin perder valor, se minimiza.

## 8. Persistencia AI propuesta

### 8.1 `ai_interactions`

- usuario
- evaluacion o solicitud asociada
- tipo de contexto
- version de plantilla
- payload de entrada
- modelo usado
- texto generado
- fecha

### 8.2 `ai_prompt_templates`

- clave de plantilla
- texto del prompt
- producto
- version
- estado activo
- auditoria de creacion

## 9. Contratos AI a formalizar

- contrato de explicacion de evaluacion.
- contrato de resumen de caso.
- contrato de sugerencias de accion.
- contrato de chequeo asistivo de registro.
- contrato de error o degradacion del servicio AI.

## 10. Riesgos

- Fugas de datos sensibles en prompts.
- Dependencia excesiva de texto libre sin trazabilidad.
- Mezclar salida AI con calculo determinista.
- Guardar mas informacion de la necesaria.
- Rehacer la persistencia si no se define ahora el contrato.

## 11. Criterio de aceptacion

- Queda explicito que datos del cliente se omiten o anonimizan antes de enviar al modelo.
- Queda aprobado el diseño de persistencia AI para implementarlo junto al ORM y las migraciones.
- El motor determinista sigue operando aunque la AI falle o se desactive.
- La salida AI queda auditable y ligada a `DecisionTrace`.

## 12. Notas de referencia

- Este documento fija politicas de seguridad y contratos AI para el MVP.
- No define implementacion.
- La base del diseno debe seguir `SPEC.md` y las decisiones ya cerradas del proyecto.

## 13. Cierre formal

`ISSUE-033` queda cerrado como definicion de politicas de seguridad y contratos AI.

Queda consolidado:

- el principio de No autonomia de la IA.
- la regla de grounding estricto para prompts y respuestas.
- la politica de minimizacion y omision de datos no necesarios.
- el diseno logico de persistencia para `ai_interactions` y `ai_prompt_templates`.
- la separacion entre salida AI y calculo determinista.

Con este cierre, el equipo puede avanzar a la implementacion de la capa AI y su persistencia sin reabrir las decisiones base de seguridad y privacidad.
