# ISSUE-006 - Diseñar modelo de datos inicial

## 1. Objetivo

Definir el esquema base de persistencia del MVP, incluyendo parametros del motor, configuracion de pipeline, `DecisionTrace` y snapshot minimo de inputs externos.

## 2. Fuentes revisadas

- `ISSUES.md`
- `docs/SPEC.md`
- `README.md`
- `docs/analysis/ISSUE-002.md`

## 3. Contexto

- El modelo debe quedar listo antes de implementar ORM y migraciones.
- El MVP inicia con base limpia, sin migracion historica.
- El esquema debe ser compatible con SQLite y evolucionar hacia SQL Server.
- La persistencia debe soportar trazabilidad, versionado y multiproducto.

## 4. Alcance del modelo

Debe separar:

- catalogo de productos de prestamo
- datos maestros
- parametros del motor
- eventos operativos
- trazas AI
- solicitudes
- historial de estados
- trazabilidad

## 5. Entidades principales sugeridas

- `users`
- `roles`
- `user_roles`
- `loan_products`
- `clients`
- `pld_campaigns`
- `pld_rule_sets`
- `pld_rule_parameters`
- `pld_evaluations`
- `pld_evaluation_inputs`
- `pld_evaluation_results`
- `evaluation_input_snapshots`
- `credit_requests`
- `credit_request_status_history`
- `audit_logs`
- `ai_interactions`
- `ai_prompt_templates`
- `decision_events`
- `decision_traces`
- `rule_sets`
- `rule_versions`
- `pipeline_strategies`
- `pipeline_nodes`

## 6. Tablas criticas para este issue

- `credit_requests`
- `pld_evaluations`
- `decision_traces`
- `evaluation_input_snapshots`
- `decision_events`
- `pipeline_strategies`
- `pipeline_nodes`
- `rule_sets`
- `rule_versions`

## 7. Campos clave esperados

### `credit_requests`

- `id`
- `loan_product_code`
- `document_type`
- `document_number`
- `campaign_code`
- `requested_amount`
- `comment`
- `customer_type`
- `profile_code`
- `segment_code`
- `employment_status`
- `validated_income`
- `rci`
- `offered_amount`
- `installment_amount`
- `term_months`
- `rate`
- `status`
- `created_by`
- `created_at`
- `cancelled_at`

### `pld_evaluations`

- `id`
- `loan_product_code`
- `document_type`
- `document_number`
- `campaign_code`
- `rule_set_version`
- `parameter_version`
- `pipeline_version`
- `executed_by`
- `executed_at`

### `decision_traces`

- `id`
- `evaluation_id`
- `pipeline_version`
- `trace_payload`
- `human_summary`
- `created_at`

### `evaluation_input_snapshots`

- `id`
- `evaluation_id`
- `source_type`
- `source_key`
- `field_name`
- `field_value`
- `created_at`

## 8. Versionado requerido

- Versionado de parametros.
- Versionado de pipeline.
- Versionado de reglas.
- Trazabilidad por evaluacion.
- Relacion entre version aplicada y resultado persistido.

## 9. Mapeo del Excel

`ParametrosPLD-v3.xlsx` debe mapearse a estructuras persistentes sin depender del archivo en runtime.
El modelo debe permitir cargar sus datos a:

- reglas
- parametros numericos/tabulares
- definiciones de flujo
- topologia permitida

## 10. Soporte multiproducto

El esquema debe incluir `loan_product_code` o equivalente en las entidades relevantes para evitar reestructuras futuras.
PLD es el primer producto, no el unico supuesto del modelo.

## 11. Restricciones de diseno

- Evitar dependencias innecesarias del motor de base de datos.
- Evitar tipos no portables.
- Evitar acoplar el modelo a la UI legacy.
- Persistir solo el snapshot minimo de los inputs realmente usados.
- Mantener separacion entre reglas de negocio, parametros y pipeline.

## 12. Criterio de aceptacion

- Existe documento o diagrama de tablas y relaciones.
- Existe mapeo de `ParametrosPLD-v3.xlsx` a tablas nuevas.
- El modelo deja trazabilidad de los inputs externos efectivamente utilizados.
- El esquema contempla `pipeline_strategies`, `pipeline_nodes` y `decision_traces`.
- El modelo es portable entre SQLite y SQL Server.

## 13. Riesgos

- Sobre-modelar demasiado pronto.
- Mezclar campos de UI con datos de dominio.
- Perder trazabilidad por no versionar parametros o pipeline.
- Diseñar tablas especificas de PLD que dificulten el segundo producto.

## 14. Notas de referencia

- Este documento define el modelo logico inicial, no la implementacion ORM.
- Debe servir como base para `ISSUE-007`.
- Las discrepancias con el legacy deben resolverse segun `docs/SPEC.md` y las decisiones funcionales cerradas.

## 15. Cierre formal

`ISSUE-006` queda cerrado como definicion del modelo de datos inicial del MVP.

Queda consolidado:

- el esquema logico base de persistencia.
- la separacion entre datos maestros, parametros, solicitudes, trazas y auditoria.
- el inventario de entidades criticas para el MVP.
- el mapeo de `ParametrosPLD-v3.xlsx` a estructuras persistentes.
- el soporte base para multiproducto mediante `loan_product_code`.

Con este cierre, el equipo puede avanzar a `ISSUE-007` sin depender de redefinir el modelo logico base.
