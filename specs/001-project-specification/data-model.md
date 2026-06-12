# Data Model - Decision Engine MVP

## Overview

El modelo se organiza en tres grupos: seguridad y actores, runtime operacional del MVP y administracion versionada del motor. El objetivo es reutilizar tablas base ya existentes cuando sea posible y extenderlas con nuevas entidades para eliminar configuracion hardcodeada del runtime.

## Existing Core Entities To Preserve

### User

- Purpose: actor autenticado que ejecuta acciones operativas o administrativas.
- Key fields: `id`, `username`, `display_name`, `is_active`, `created_at`.
- Relationships: muchos a muchos con `Role` mediante `UserRole`; uno a muchos con eventos, evaluaciones, solicitudes y activaciones.

### Role

- Purpose: agrupar permisos RBAC.
- Key fields: `id`, `code`, `name`, `created_at`.
- Relationships: muchos a muchos con `User`.

### LoanProduct

- Purpose: registro persistido unico del producto administrable reutilizado por el runtime del motor y por las solicitudes de credito.
- Key fields actuales: `code`, `name`, `is_active`, `created_at`.
- Planned evolution:
  - incorporar `description`
  - reemplazar `is_active` por `status` (`draft`, `active`, `retired`)
  - agregar `created_by`, `activated_by`, `activated_at`, `retired_by`, `retired_at`
- Relationships:
  - uno a muchos con `LoanEvaluation`
  - uno a muchos con `CreditRequest`
  - uno a muchos con `ProductWorkflow`, `ProductVariable`, `RuleSet` y `PipelineStrategy`

### LoanEvaluation

- Purpose: ejecucion persistida de una evaluacion operacional.
- Key fields actuales: `id`, `loan_product_code`, `document_type`, `document_number`, `campaign_code`, `rule_set_version`, `parameter_version`, `pipeline_version`, `executed_by`, `executed_at`.
- Planned additions: `workflow_code`, `workflow_version_id`, `variable_catalog_version_id`, `decision_outcome`, `eligible`.
- Relationships: uno a muchos con `EvaluationInputSnapshot`; uno a uno con `DecisionTrace`; opcionalmente uno a uno o uno a muchos con `CreditRequest`.

### CreditRequest

- Purpose: solicitud registrada a partir de una evaluacion valida.
- Key fields actuales: `id`, `loan_product_code`, `document_type`, `document_number`, `campaign_code`, `requested_amount`, `comment`, `status`, `created_by`, `created_at`.
- Planned additions: `evaluation_id` obligatorio cuando derive de evaluacion, referencia explicita a `workflow_code` para auditoria.
- Relationships: uno a muchos con `CreditRequestStatusHistory`; uno a muchos con adjuntos ZIP; muchos a uno con `User` y `LoanProduct`.

### DecisionTrace

- Purpose: evidencia estructurada de una evaluacion.
- Key fields: `id`, `evaluation_id`, `pipeline_version`, `trace_payload`, `human_summary`, `created_at`.
- Relationships: uno a uno con `LoanEvaluation`.

## New Administrative Engine Entities

### Product Source Of Truth Decision

- Decision: `LoanProduct` evoluciona para convertirse en el producto administrable del motor.
- Consequence: no se introduce una segunda tabla paralela `EngineProduct`; el termino se mantiene solo como concepto de dominio, no como tabla adicional.

### ProductWorkflow

- Purpose: identidad estable de una modalidad de evaluacion dentro de un producto.
- Key fields:
  - `id`
  - `product_id`
  - `workflow_code`
  - `name`
  - `description`
  - `status` (`draft`, `active`, `retired`)
  - `created_by`, `created_at`, `activated_by`, `activated_at`, `retired_by`, `retired_at`
- Validation rules:
  - `workflow_code` unico dentro del producto
  - un workflow retirado no puede recibir nuevas versiones activables
- Relationships:
  - muchos a uno con `LoanProduct`
  - uno a muchos con `WorkflowVersion`

### WorkflowVersion

- Purpose: unidad publicable e inmutable del comportamiento operacional de un workflow.
- Key fields:
  - `id`
  - `workflow_id`
  - `version_number`
  - `status` (`draft`, `active`, `retired`)
  - `variable_catalog_version_id`
  - `pipeline_strategy_id`
  - `rule_bundle_reference`
  - `change_notes`
  - `created_by`, `created_at`, `activated_by`, `activated_at`, `retired_by`, `retired_at`
- Validation rules:
  - no se edita si esta `active`
  - solo una version `active` por workflow salvo futura politica explicita en contrario
- Relationships:
  - muchos a uno con `ProductWorkflow`
  - muchos a uno con `VariableCatalogVersion`
  - muchos a uno con `PipelineStrategy`
  - uno a muchos con `WorkflowRuleAssignment`
  - uno a muchos con `LoanEvaluation`

### ProductVariable

- Purpose: definicion administrable de una variable disponible para workflows del producto.
- Key fields:
  - `id`
  - `product_id`
  - `variable_key`
  - `name`
  - `description`
  - `data_type`
  - `required`
  - `allowed_sources` (`campaign_db`, `user_input`, `both`)
  - `status` (`draft`, `active`, `retired`)
  - `created_by`, `created_at`
- Validation rules:
  - `variable_key` unico dentro del producto
  - origen permitido obligatorio
- Relationships:
  - muchos a uno con `LoanProduct`
  - uno a muchos con `VariableCatalogItem`

### VariableCatalogVersion

- Purpose: snapshot publicable del conjunto de variables activas de un producto.
- Key fields:
  - `id`
  - `product_id`
  - `version_number`
  - `status` (`draft`, `active`, `retired`)
  - `created_by`, `created_at`, `activated_by`, `activated_at`
- Validation rules:
  - debe contener solo variables compatibles con el producto
  - se referencia desde `WorkflowVersion` y `LoanEvaluation`
- Relationships:
  - muchos a uno con `LoanProduct`
  - uno a muchos con `VariableCatalogItem`

### VariableCatalogItem

- Purpose: asociar una variable a una version de catalogo y fijar su configuracion publicada.
- Key fields:
  - `id`
  - `catalog_version_id`
  - `product_variable_id`
  - `is_required_in_runtime`
  - `default_value`
  - `source_policy_payload`
- Relationships:
  - muchos a uno con `VariableCatalogVersion`
  - muchos a uno con `ProductVariable`

### WorkflowRuleAssignment

- Purpose: asociar reglas publicadas a una version de workflow.
- Key fields:
  - `id`
  - `workflow_version_id`
  - `rule_version_id`
  - `execution_order`
  - `is_active`
- Relationships:
  - muchos a uno con `WorkflowVersion`
  - muchos a uno con `RuleVersion`

## Reused Versioned Rule And Pipeline Entities

### RuleSet / RuleVersion

- Purpose: mantener reglas declarativas y versionadas.
- Planned adaptation:
  - mover semantica de `is_active` / `approved_by` hacia `draft`, `active`, `retired`
  - vincular cada `RuleSet` a `LoanProduct` y cada `RuleVersion` a `WorkflowRuleAssignment`
- Validation rules:
  - una regla activa no se muta; se crea nueva version
  - expresiones deben validarse antes de activar

### PipelineStrategy / PipelineNode

- Purpose: representar el grafo ejecutable del motor.
- Planned adaptation:
  - mantener versionado por estrategia
  - asociar la estrategia publicada a `WorkflowVersion`
  - conservar validacion topologica y branching controlado

## Operational Support Entities To Add

### CreditRequestAttachment

- Purpose: metadata de archivos ZIP asociados a una solicitud.
- Key fields:
  - `id`
  - `request_id`
  - `storage_path`
  - `original_filename`
  - `mime_type`
  - `uploaded_by`
  - `uploaded_at`
  - `status`
- Relationships:
  - muchos a uno con `CreditRequest`

### AdministrativeAuditEvent

- Purpose: evento append-only para administracion del motor.
- Key fields:
  - `event_id`
  - `aggregate_type`
  - `aggregate_id`
  - `event_type`
  - `event_payload`
  - `created_by`
  - `created_at`
- Relationships:
  - muchos a uno con `User`
- Note: puede implementarse como especializacion de `DecisionEvent` si se decide reutilizar la tabla existente.

## State Transitions

### Product, Workflow, Rule, Variable Catalog

- `draft -> active`: requiere validacion y permisos autorizados
- `active -> retired`: deja de participar en nuevas evaluaciones, pero conserva referencias historicas
- `draft -> retired`: permitido para descarte administrativo antes de publicacion
- no se permite `active -> draft`

### Workflow Version

- `draft -> active`: requiere referencias validas a pipeline, reglas y catalogo de variables
- `active -> retired`: conserva evaluaciones historicas, pero deja de ser seleccionable
- cambios funcionales posteriores: crear nueva version `draft`

### Credit Request

- estado inicial: `registered` o equivalente definido por negocio
- transiciones posteriores: gobernadas por permiso y reglas operativas
- cancelacion: transicion terminal auditada

## Data Integrity And Reproducibility Rules

1. Toda evaluacion debe guardar `product_code`, `workflow_code`, `workflow_version_id`, `rule_set_version`, `pipeline_version` y `variable_catalog_version_id`.
2. Solo se persisten snapshots de campos efectivamente consumidos por el motor.
3. Los valores de variables deben respetar el origen permitido configurado en el catalogo publicado.
4. Una version activa de workflow no se edita; cualquier cambio crea una nueva version.
5. Las referencias historicas nunca se cascaden a borrado fisico.
