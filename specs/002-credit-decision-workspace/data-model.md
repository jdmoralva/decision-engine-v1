# Data Model - Plataforma Visual de Decisión de Crédito

## Overview

La feature introduce un modelo principalmente frontend que organiza la experiencia en cuatro capas: sesión autenticada, catálogo de plataforma, workspace de diseño y artefactos gobernados/integrados. El objetivo es poder navegar y editar visualmente sin romper la frontera entre prototipo de sesión y entidades reales del motor.

## Core Session And Navigation Entities

### Sesión de usuario

- Purpose: representar al usuario autenticado que accede a la plataforma.
- Key fields:
  - `accessToken`
  - `me.id`
  - `me.username`
  - `me.displayName`
  - `me.roles[]`
- Relationships:
  - habilita la visibilidad de `Servicio`
  - controla acceso a `ProductoWorkspace`
  - referencia acciones de perfil visibles en el sidebar
- Validation rules:
  - solo existe tras `login` exitoso y validación posterior con `GET /me`
  - si la restauración falla, la sesión local se invalida

### Ruta de aplicación

- Purpose: ubicar al usuario en `login`, `productos`, `servicios` o `workspace`.
- Key fields:
  - `routeName`
  - `productCode?`
  - `serviceKey?`
  - `workspaceSection?`
  - `workspaceItem?`
- Validation rules:
  - `productos`, `servicios` y `workspace` requieren sesión activa
  - `workspace` requiere `productCode` y `serviceKey`

## Platform Catalog Entities

### Producto

- Purpose: contenedor visual de servicios y accesos rápidos.
- Key fields:
  - `productCode`
  - `name`
  - `environmentLabel`
  - `environmentTone`
  - `quickActions[]`
  - `menuActions[]`
  - `source` (`seed`, `backend`)
- Relationships:
  - uno a muchos con `Servicio`
  - uno a uno lógico con `ProductoWorkspace`
- Validation rules:
  - `PLD` y `Hipotecario` deben estar visibles por defecto en esta fase
  - las acciones de menú pueden ser placeholder, pero no deben romper la navegación principal

### Servicio

- Purpose: unidad operativa visible dentro de un producto.
- Key fields:
  - `serviceKey` (`CreditApplications`, `DecisionEngine`, `DataModel`)
  - `displayName`
  - `statusLabel`
  - `iconKey`
  - `isVisible`
  - `visibilityRoles[]`
  - `supportsOpen`
- Relationships:
  - pertenece a un `Producto`
  - puede abrir un `ProductoWorkspace`
- Validation rules:
  - visibilidad global por rol, nunca por producto
  - la UI debe mostrar nombres en español
  - esta fase no permite alta de servicios

## Workspace Entities

### ProductoWorkspace

- Purpose: estado general del espacio de trabajo abierto para un producto y servicio.
- Key fields:
  - `productCode`
  - `serviceKey`
  - `title`
  - `activeSidebarGroup`
  - `activeSidebarItem`
  - `activeTopTab`
  - `profileMenuOpen`
- Relationships:
  - uno a uno con `BorradorWorkflowCanvas` cuando el servicio es `DecisionEngine`
  - uno a muchos con `WorkspaceListItem`

### WorkspaceListItem

- Purpose: elemento navegable del sidebar o explorador interno.
- Key fields:
  - `groupKey`
  - `itemKey`
  - `label`
  - `status?`
  - `source` (`backend`, `session`)
- Relationships:
  - pertenece a `ProductoWorkspace`
  - puede abrir tablas, formularios o `BorradorWorkflowCanvas`

### BorradorWorkflowCanvas

- Purpose: snapshot editable de sesión para el diagrama del workflow.
- Key fields:
  - `draftKey`
  - `productCode`
  - `workflowId?`
  - `workflowCode?`
  - `sourceState` (`seed`, `backend-detail`, `session`)
  - `dirty`
  - `lastSavedAt`
  - `selectedNodeId?`
  - `viewport`
  - `executionHistory[]`
  - `validationMessages[]`
- Relationships:
  - uno a muchos con `NodoWorkflow`
  - uno a muchos con `ConexionWorkflow`
  - uno a uno con `InspectorNodo`
- Validation rules:
  - se persiste solo en `sessionStorage`
  - no se presenta como workflow aprobado/publicado por sí mismo

### NodoWorkflow

- Purpose: paso individual del flujo visual.
- Key fields:
  - `nodeId`
  - `type` (`inicio`, `decision`, `regla`, `score`, `politica`, `accion`, `fin`, `subworkflow`)
  - `name`
  - `description`
  - `position.x`
  - `position.y`
  - `inputVariables[]`
  - `outputVariables[]`
  - `decisionLogic`
  - `errorHandling`
  - `executionMode`
  - `status` (`idle`, `selected`, `running`, `success`, `error`)
- Relationships:
  - pertenece a `BorradorWorkflowCanvas`
  - uno a muchos con `ConexionWorkflow` salientes y entrantes
- Validation rules:
  - `type` define el set mínimo de propiedades visibles en inspector
  - un nodo `subworkflow` debe referenciar un workflow reutilizable, aunque en esta fase pueda ser mock

### ConexionWorkflow

- Purpose: transición visual entre nodos.
- Key fields:
  - `edgeId`
  - `sourceNodeId`
  - `targetNodeId`
  - `label`
  - `semanticKey` (`continue`, `approved`, `rejected`, `manual_review`, `yes`, `no`, `error`)
- Validation rules:
  - debe unir nodos compatibles
  - su etiqueta visible debe mantenerse coherente con el tipo de ramificación

### InspectorNodo

- Purpose: vista lateral de propiedades del nodo seleccionado.
- Key fields:
  - `selectedNodeId?`
  - `name`
  - `type`
  - `description`
  - `inputVariables[]`
  - `outputVariables[]`
  - `decisionLogic`
  - `errorHandling`
  - `executionMode`
  - `condition?`
  - `trueRoute?`
  - `falseRoute?`
  - `alternativeRoute?`
- Validation rules:
  - si no hay nodo seleccionado, debe mostrar un estado vacío coherente

## Governed And Integrated Entities

### Workflow gobernado

- Purpose: artefacto real del backend que puede listarse o detallarse desde la UI.
- Key fields:
  - `id`
  - `productCode`
  - `workflowCode`
  - `name`
  - `description`
  - `status` (`draft`, `active`, `retired`)
  - `approval`
  - `retirement`
  - `deletion`
- Relationships:
  - puede originar un `BorradorWorkflowCanvas`
  - puede asociarse a un `Channel` futuro
- State transitions:
  - `draft -> active`
  - `active -> retired`
  - no se modela edición directa de `active`

### Paquete de parámetros aprobado

- Purpose: conjunto gobernado de parámetros seleccionables por un `Channel`.
- Key fields:
  - `id`
  - `productCode`
  - `workflowCode`
  - `versionNumber`
  - `status`
  - `payload`
- Relationships:
  - muchos a muchos lógicos futuros con `Channel`

### Channel

- Purpose: modo de evaluación visible para negocio dentro del workspace.
- Key fields:
  - `channelId`
  - `name`
  - `status` (`draft`, `active`)
  - `evaluationTypeName`
  - `workflowId`
  - `approvedParameterSetIds[]`
  - `compatibilityValidation`
  - `source` (`session`, `backend`)
- Relationships:
  - referencia un único `Workflow gobernado`
  - referencia múltiples `Paquete de parámetros aprobado`
- Validation rules:
  - un channel solo puede asociar un workflow aprobado
  - no puede finalizar si falla la validación de compatibilidad workflow/parámetros
- Note:
  - en esta fase se asume principalmente `source=session` por ausencia de contrato backend específico

### Test AB

- Purpose: comparación entre workflow champion y challenger.
- Key fields:
  - `testId`
  - `name`
  - `championWorkflowId`
  - `challengerWorkflowId`
  - `selectedPeriod`
  - `selectedClientFilter?`
  - `impactMetrics`
  - `source` (`session`, `backend`)
- Note:
  - se documenta para diseño, pero su soporte real queda pendiente de endpoint específico

### Evento de motor

- Purpose: fila consultable de las últimas consultas al motor en la vista `events`.
- Key fields:
  - `eventId`
  - `occurredAt`
  - `clientReference`
  - `productCode`
  - `workflowCode`
  - `resultSummary`
  - `displayFields`
- Relationships:
  - se usa como fuente para filtros de periodo/cliente y para pruebas AB
- Note:
  - en esta fase puede ser mock o adaptado de auditoría, pero no debe confundirse con una API persistida inexistente

## Integrity Rules

1. La visibilidad de servicios depende del rol autenticado, nunca del producto.
2. Todo texto visible de `Producto`, `Servicio`, sidebar, tabs y canvas debe estar en español.
3. El borrador editable del canvas dura solo la sesión del navegador.
4. Los estados `draft`, `active` y `retired` de artefactos reales se respetan tal como los define el backend.
5. `PLD` e `Hipotecario` son semillas de presentación, no un límite estructural del modelo.
