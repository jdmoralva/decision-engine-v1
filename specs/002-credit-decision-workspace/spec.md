# Feature Specification: Plataforma Visual de Decisión de Crédito

**Feature Branch**: `[002-credit-decision-workspace]`

**Created**: 2026-06-15

**Status**: Draft

**Input**: User description: "Build the frontend of a web platform for a credit decision engine. The application should be inspired by enterprise decisioning platforms, with a clean, modern, professional UI similar to the provided screenshots. The platform will allow users to manage environments, services, business logic, decision workflows, connections, rules and deployment flows for credit origination decisions. specs and frontend should be in spanish"

## Clarifications

### Session 2026-06-15

- Q: ¿Debe la interfaz visible estar en español o conservar algunos textos del brief en inglés? → A: Toda la interfaz visible debe estar en español.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Explorar productos y servicios (Priority: P1)

Como usuario autorizado, quiero ver los productos disponibles y entrar a sus servicios para ubicar rápidamente el entorno de trabajo correcto.

**Why this priority**: Es el punto de entrada principal y permite acceder al resto de la plataforma.

**Independent Test**: Se puede verificar abriendo la pantalla inicial, seleccionando un producto y confirmando que se muestran sus servicios y acciones disponibles.

**Acceptance Scenarios**:

1. **Given** que el usuario entra a la plataforma, **When** se carga la vista inicial, **Then** ve los productos `PLD` y `Hipotecario` en tarjetas diferenciadas.
2. **Given** que el usuario abre el menú de un producto, **When** selecciona una acción del menú de tres puntos, **Then** ve opciones para renombrar, duplicar, exportar o eliminar.
3. **Given** que el usuario hace clic en un producto, **When** el sistema cambia de vista, **Then** se muestra la pantalla de servicios de ese producto.

---

### User Story 2 - Crear y seleccionar servicios (Priority: P2)

Como usuario autorizado, quiero ver los servicios de un producto y crear nuevos servicios para organizar el trabajo de decisión.

**Why this priority**: Los servicios son la unidad operativa que conecta el catálogo de productos con el diseño del flujo.

**Independent Test**: Se puede verificar entrando a un producto, revisando la grilla de servicios, creando un servicio desde un modal y abriendo uno existente.

**Acceptance Scenarios**:

1. **Given** que el usuario está dentro de un producto, **When** ve la pantalla de servicios, **Then** observa la ruta de navegación, el título `Servicios` y el botón `Agregar nuevo servicio`.
2. **Given** que el usuario abre la acción de crear servicio, **When** completa el formulario y confirma, **Then** el nuevo servicio aparece en la grilla.
3. **Given** que el usuario hace clic en una tarjeta de servicio, **When** la selección se completa, **Then** se abre el espacio de diseño de ese servicio.

---

### User Story 3 - Diseñar flujos de decisión (Priority: P3)

Como usuario de negocio o configuración, quiero editar visualmente un flujo de decisión para construir y revisar la lógica de una solicitud de crédito.

**Why this priority**: Es el núcleo funcional del producto y concentra el mayor valor de negocio.

**Independent Test**: Se puede verificar abriendo un servicio, moviendo nodos, cambiando su selección, editando sus propiedades y comprobando que el estado del lienzo se actualiza en pantalla.

**Acceptance Scenarios**:

1. **Given** que el usuario abre el espacio de diseño, **When** se carga la vista, **Then** ve una barra lateral principal, un explorador de objetos, pestañas superiores, un lienzo central y un panel de configuración a la derecha.
2. **Given** que el usuario selecciona un nodo del flujo, **When** cambia la selección, **Then** el panel derecho muestra propiedades acordes al tipo de nodo.
3. **Given** que el usuario usa las herramientas del lienzo, **When** agrega, mueve, elimina o reencuadra nodos, **Then** el flujo visual refleja el cambio sin salir de la pantalla.
4. **Given** que el usuario cambia entre `Diseño`, `Pruebas`, `Despliegue` y `Ejecución`, **When** selecciona una pestaña, **Then** la interfaz muestra el contexto correspondiente del servicio.

---

### Edge Cases

- La pantalla debe mostrar estados vacíos claros si todavía no existen productos o servicios.
- El menú de acciones no debe interferir con la selección de una tarjeta cuando el usuario sólo quiere abrirla.
- El panel de propiedades debe conservar una vista coherente cuando no hay nodo seleccionado.
- Si el usuario elimina un nodo con dependencias visibles, el lienzo debe reflejar el cambio sin dejar referencias rotas en pantalla.
- La interfaz debe seguir siendo utilizable en anchos de escritorio comunes sin ocultar controles esenciales.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema debe mostrar una pantalla de productos con el título `Productos` y una acción principal `Crear producto`.
- **FR-002**: El sistema debe mostrar por defecto los productos `PLD` y `Hipotecario` como tarjetas diferenciadas.
- **FR-003**: Cada tarjeta de producto debe mostrar nombre, indicador visual de entorno y accesos rápidos para servicios, configuración, validación y despliegue.
- **FR-004**: Cada tarjeta de producto debe ofrecer un menú de tres puntos con acciones de marcador de posición para renombrar, duplicar, exportar y eliminar.
- **FR-005**: Al seleccionar un producto, el sistema debe llevar al usuario a la vista de servicios de ese producto.
- **FR-006**: El sistema debe mostrar una vista de servicios con ruta de navegación, título `Servicios` y acción principal `Agregar nuevo servicio`.
- **FR-007**: El sistema debe mostrar los servicios en una grilla adaptable al ancho disponible.
- **FR-008**: Cada tarjeta de servicio debe mostrar nombre, estado, icono, acción de eliminación y menú de tres puntos.
- **FR-009**: Al seleccionar un servicio, el sistema debe abrir el espacio de diseño de ese servicio.
- **FR-010**: La acción `Agregar nuevo servicio` debe abrir un modal para crear un servicio nuevo.
- **FR-011**: El espacio de diseño debe mostrar navegación lateral principal, explorador de objetos, lienzo de trabajo, pestañas superiores, panel derecho de configuración y controles flotantes del lienzo.
- **FR-012**: El explorador de objetos debe incluir un buscador y secciones expandibles para `Lógica de negocio`, `Conexiones`, `Modelos de datos`, `Plantillas de documentos` y `Eventos`.
- **FR-013**: La sección `Lógica de negocio` debe mostrar los elementos `Decisión`, `Flujo principal`, `Verificaciones de validación`, `Reglas de elegibilidad` y `Reglas de precios`.
- **FR-014**: El sistema debe permitir agregar objetos desde el espacio de diseño mediante una acción ubicada al pie del explorador.
- **FR-015**: El lienzo debe mostrar un flujo de ejemplo con nodos y conexiones para un proceso de originación de crédito.
- **FR-016**: El flujo de ejemplo debe incluir nodos para inicio, obtención de datos del cliente, validación de identidad, verificación de score, revisión de deuda, cálculo de ratio deuda-ingreso, evaluación de riesgo, aplicación de política, cálculo de oferta, aprobación, rechazo, revisión manual y fin.
- **FR-017**: El sistema debe distinguir visualmente al menos los tipos de nodo inicio, decisión, regla, score, política, acción y fin.
- **FR-018**: Las conexiones del flujo deben soportar etiquetas como `continue` (`continuar`), `approved` (`aprobado`), `rejected` (`rechazado`), `manual review` (`revisión manual`), `yes` (`sí`), `no` y `error`.
- **FR-019**: El usuario debe poder seleccionar un nodo y ver sus propiedades en el panel derecho.
- **FR-020**: El panel derecho debe mostrar nombre, tipo, descripción, variables de entrada, variables de salida, lógica de decisión, manejo de errores y modo de ejecución del nodo seleccionado.
- **FR-021**: Para nodos de decisión o regla, el panel derecho debe incluir campos de expresión, condición, ruta verdadera, ruta falsa y ruta alternativa.
- **FR-022**: El usuario debe poder mover nodos dentro del lienzo y ver la nueva posición reflejada de inmediato.
- **FR-023**: El usuario debe poder acercar, alejar, desplazar y reencuadrar la vista del lienzo.
- **FR-024**: El usuario debe poder agregar nuevos nodos desde una barra de herramientas del lienzo.
- **FR-025**: El usuario debe poder eliminar el nodo seleccionado desde el lienzo o sus controles asociados.
- **FR-026**: Los cambios de selección, posición, alta y baja de nodos deben mantenerse en el estado de la interfaz mientras dure la sesión.
- **FR-027**: La interfaz debe mostrarse en español en todos los textos visibles del producto, incluidos títulos, botones, pestañas, menús y etiquetas de contexto.
- **FR-028**: La experiencia debe priorizar una presentación de escritorio con jerarquía visual clara, tarjetas compactas y paneles bien delimitados.

### Constitution Alignment *(mandatory)*

- **Shared vs Product-Specific Boundary**: La estructura general de navegación, catálogo y editor visual es compartida por la plataforma; `PLD` e `Hipotecario` son productos semilla visibles en la interfaz, no el único modelo posible.
- **Deterministic Engine Impact**: Ninguno. Esta feature no cambia cálculos del motor; sólo permite explorar y editar visualmente definiciones de flujo en la interfaz.
- **Versioning and Evidence Impact**: La interfaz debe conservar el estado editable dentro de la sesión y mostrar cambios coherentes mientras el usuario trabaja; no introduce evidencia persistida nueva ni modifica versiones del motor.
- **Security and Traceability Impact**: La pantalla debe respetar el acceso del usuario autenticado y no exponer acciones fuera de sus permisos actuales; las acciones administrativas visibles son de navegación y edición visual.
- **AI Impact**: None.

### Key Entities *(include if feature involves data)*

- **Producto**: Contenedor de organización para servicios y flujos; incluye nombre, estado visual, acciones rápidas y menú contextual.
- **Servicio**: Unidad de trabajo dentro de un producto; incluye nombre, estado, icono y acceso al espacio de diseño.
- **Flujo de decisión**: Estructura visual compuesta por nodos y conexiones que representa la lógica de originación de crédito.
- **Nodo**: Paso individual del flujo con nombre, tipo, propiedades y relaciones con otros nodos.
- **Conexión**: Relación entre nodos con una etiqueta semántica que expresa la transición.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un usuario puede localizar y abrir cualquiera de los dos productos semilla en menos de 30 segundos en una prueba guiada.
- **SC-002**: Al menos 4 de 5 personas en una prueba de usabilidad pueden crear un servicio nuevo y abrirlo en el espacio de diseño sin ayuda.
- **SC-003**: Al menos 4 de 5 personas en una prueba de usabilidad pueden seleccionar un nodo y ver sus propiedades correctas en menos de 5 segundos.
- **SC-004**: Al menos 4 de 5 personas en una prueba de usabilidad pueden agregar, mover y eliminar un nodo sin perder el contexto del flujo.
- **SC-005**: La navegación entre productos, servicios y diseño mantiene visibles las acciones principales sin necesidad de desplazamiento horizontal en resoluciones de escritorio comunes.

## Assumptions

- La interfaz es de escritorio primero y prioriza uso en pantallas amplias.
- El contenido visible de la interfaz debe estar completamente en español.
- La gestión de productos, servicios y flujos inicia con datos semilla y estado local de interfaz.
- Las acciones de menú que no tengan backend asociado funcionan como marcadores de posición de la experiencia.
- La persistencia de cambios queda limitada a la sesión de frontend para este prototipo inicial.
