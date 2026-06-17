# Feature Specification: Plataforma Visual de Decisión de Crédito

**Feature Branch**: `[002-credit-decision-workspace]`

**Created**: 2026-06-15

**Status**: Draft

**Input**: User description: "Build the frontend of a web platform for a credit decision engine. The application should be inspired by enterprise decisioning platforms, with a clean, modern, professional UI similar to the provided screenshots. The platform will allow users to manage environments, services, business logic, decision workflows, connections, rules and deployment flows for credit origination decisions. specs and frontend should be in spanish"

## Clarifications

### Session 2026-06-15

- Q: ¿Debe la interfaz visible estar en español o conservar algunos textos del brief en inglés? → A: Toda la interfaz visible debe estar en español.
- Q: ¿La visibilidad de servicios depende solo del rol o también del producto? → A: La visibilidad de servicios es global por rol y se aplica igual en todos los productos.
- Q: ¿La vista inicial debe mostrar productos semilla fijos? → A: Sí, debe mostrar `PLD` y `Hipotecario` como productos semilla visibles.
- Q: ¿La primera pantalla de la plataforma debe ser login obligatorio? → A: Sí, la primera pantalla debe ser inicio de sesión obligatorio y luego se muestra la vista de productos.
- Q: ¿Qué nombres deben verse para los servicios disponibles por rol? → A: `Bandeja de solicitudes (CreditApplications)`, `Motor de decisiones (DecisionEngine)` y `Modelo de datos (DataModel)`.
- Q: ¿La vista de servicios permite crear nuevos servicios? → A: No, la vista es solo de consulta y apertura de servicios existentes.
- Q: ¿Cómo debe manejarse la nomenclatura de servicios entre UI e interno? → A: La UI debe mostrar `Bandeja de solicitudes`, `Motor de decisiones` y `Modelo de datos`; internamente pueden seguir como `CreditApplications`, `DecisionEngine` y `DataModel`.
- Q: ¿Qué precisiones aplican para FR-012 y FR-013? → A: Al ingresar a `Motor de decisiones`, el sidebar muestra `Reglas de Negocio`, `Parámetros` y `Data`; `Reglas de Negocio` incluye `evaluation`, `workflows`, `testing` y `events`; `Parámetros` incluye `límites internos`, `límites globales` y `niveles de autonomía`; `Data` incluye `Importar dataset`, `Configurar relaciones`, `Crear catálogo` y `Administrar catálogos`.

### Session 2026-06-16

- Q: ¿Qué debe mostrar la parte inferior del sidebar para FR-014? → A: Un botón de acceso a los datos del perfil del usuario con acciones básicas para cambiar contraseña, consultar permisos aprobados y cerrar sesión.
- Q: ¿Qué precisiones aplican a la sección Reglas de negocio? → A: `channels` muestra `create channel`, `active channels` y `draft channels`; `workflows` muestra `create workflow`, `approved workflows` y `draft workflows`; `testing` muestra `create test` y `stored tests`; `events` muestra una tabla con las últimas 50 consultas al motor y filtros por periodo y cliente.
- Q: ¿Cómo debe tratarse la nomenclatura `pipeline`? → A: Debe reemplazarse por `channel` para mantener consistencia; `pipeline` queda como término no canónico y no visible en la UI.
- Q: ¿Cómo debe editarse y operarse un workflow en el canvas? → A: La edición se realiza con drag and drop de nodos y conexiones en el canvas central; se pueden crear workflows simples, agregar nodos desde el panel lateral derecho, configurar entradas, salidas, reglas y errores por nodo, conectar nodos compatibles, ejecutar el workflow, visualizar estado por nodo, registrar ejecuciones y resultados, guardar el workflow y mantener su versionado.
- Q: ¿Cómo deben aprobarse los workflows y crearse los channels? → A: Todo workflow nuevo se guarda en `draft` hasta que el rol `Administrador de Riesgos` lo aprueba y lo cambia a `approved`; solo los workflows `approved` pueden asociarse a channels; cada channel admite un solo workflow posible y debe incluir nombre del tipo de evaluación y un paquete de parámetros aprobados; se mantiene la matriz RBAC actual.
- Q: ¿Cómo debe interpretarse el paquete de parámetros en la creación de channels? → A: Es una selección múltiple de parámetros aprobados disponibles; antes de guardar o finalizar la edición del channel el sistema debe validar que las reglas del workflow seleccionado no rompan los parámetros seleccionados.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Iniciar sesion y explorar productos (Priority: P1)

Como usuario autorizado, quiero iniciar sesion y ver los productos disponibles para ubicar rapidamente el entorno de trabajo correcto.

**Why this priority**: Es el punto de entrada principal y permite acceder al resto de la plataforma.

**Independent Test**: Se puede verificar abriendo la pantalla inicial, completando el inicio de sesion y confirmando que se muestran los productos y servicios permitidos.

**Acceptance Scenarios**:

1. **Given** que el usuario entra a la plataforma, **When** se carga la vista inicial, **Then** ve la pantalla de inicio de sesion.
2. **Given** que el usuario inicia sesion correctamente, **When** el sistema valida sus credenciales, **Then** ve los productos `PLD` y `Hipotecario` en tarjetas diferenciadas.
3. **Given** que el usuario abre el menú de un producto, **When** selecciona una acción del menú de tres puntos, **Then** ve opciones para renombrar, duplicar, exportar o eliminar.
4. **Given** que el usuario hace clic en un producto, **When** el sistema cambia de vista, **Then** se muestra la pantalla de servicios de ese producto.
5. **Given** que el usuario tiene un rol autorizado, **When** entra a un producto, **Then** solo ve los servicios permitidos por su rol en todos los productos.

---

### User Story 2 - Ver y abrir servicios (Priority: P2)

Como usuario autorizado, quiero ver los servicios de un producto y abrirlos para organizar el trabajo de decisión.

**Why this priority**: Los servicios son la unidad operativa que conecta el catálogo de productos con el diseño del flujo.

**Independent Test**: Se puede verificar entrando a un producto, revisando la grilla de servicios y abriendo uno existente.

**Acceptance Scenarios**:

1. **Given** que el usuario está dentro de un producto, **When** ve la pantalla de servicios, **Then** observa la ruta de navegación, el título `Servicios` y la grilla de servicios disponibles para su rol.
2. **Given** que el usuario hace clic en una tarjeta de servicio, **When** la selección se completa, **Then** se abre el espacio de diseño de ese servicio.

---

### User Story 3 - Diseñar flujos de decisión (Priority: P3)

Como usuario de negocio o configuración, quiero editar visualmente un flujo de decisión para construir y revisar la lógica de una solicitud de crédito.

**Why this priority**: Es el núcleo funcional del producto y concentra el mayor valor de negocio.

**Independent Test**: Se puede verificar abriendo un servicio, moviendo nodos, cambiando su selección, editando sus propiedades y comprobando que el estado del lienzo se actualiza en pantalla.

**Acceptance Scenarios**:

1. **Given** que el usuario abre el espacio de diseño, **When** se carga la vista, **Then** ve una barra lateral principal, un explorador de objetos, pestañas superiores, un lienzo central y un panel de configuración a la derecha.
2. **Given** que el usuario selecciona un nodo del flujo, **When** cambia la selección, **Then** el panel derecho muestra propiedades acordes al tipo de nodo.
3. **Given** que el usuario usa las herramientas del lienzo, **When** agrega, mueve, elimina o reencuadra nodos mediante drag and drop o conexiones entre nodos, **Then** el workflow visual refleja el cambio sin salir de la pantalla.
4. **Given** que el usuario cambia entre `Diseño`, `Pruebas`, `Despliegue` y `Ejecución`, **When** selecciona una pestaña, **Then** la interfaz muestra el contexto correspondiente del servicio.
5. **Given** que el usuario visualiza el sidebar, **When** llega a la parte inferior, **Then** encuentra el acceso a su perfil con opciones para cambiar contraseña, consultar permisos aprobados y cerrar sesión.

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
- **FR-006**: El sistema debe mostrar una vista de servicios con ruta de navegación, título `Servicios` y grilla de servicios disponibles para el rol autenticado.
- **FR-007**: El sistema debe mostrar los servicios en una grilla adaptable al ancho disponible.
- **FR-008**: Cada tarjeta de servicio debe mostrar nombre, estado, icono, acción de eliminación y menú de tres puntos.
- **FR-009**: Al seleccionar un servicio, el sistema debe abrir el espacio de diseño de ese servicio.
- **FR-010**: La vista de servicios debe ser solo de consulta y apertura de servicios existentes, sin incluir alta de servicios en esta fase.
- **FR-010A**: La visibilidad de servicios debe depender del rol autenticado y no variar por producto: los roles `Analista` y `Evaluador` solo ven `Bandeja de solicitudes`, mientras que `Administrador`, `Administrador de negocio` y `Administrador de riesgos` ven `Motor de decisiones`, `Modelo de datos` y `Bandeja de solicitudes`.
- **FR-010C**: La UI debe mostrar los nombres de servicios en español y puede conservar identificadores internos en inglés para consistencia con el brief o con el backend.
- **FR-010B**: La primera pantalla visible debe ser inicio de sesion y la vista de productos solo debe mostrarse tras autenticacion exitosa.
- **FR-011**: El espacio de diseño debe mostrar navegación lateral principal, explorador de objetos, lienzo de trabajo, pestañas superiores, panel derecho de configuración y controles flotantes del lienzo.
- **FR-012**: Al ingresar al servicio `Motor de decisiones`, el sidebar debe mostrar las opciones `Reglas de Negocio`, `Parámetros` y `Data`.
- **FR-013**: La sección `Reglas de Negocio` debe mostrar los elementos `channels`, `workflows`, `testing` y `events`.
- **FR-013C**: El elemento `channels` debe mostrar las opciones `create channel`, `active channels` y `draft channels`.
- **FR-013D**: Los `channels` corresponden a distintos modos de evaluación creados para el producto y configuran el workflow correspondiente al modo de evaluación elegido.
- **FR-013E**: El elemento `workflows` debe mostrar las opciones `create workflow`, `approved workflows` y `draft workflows`; al abrir `approved workflows` o `draft workflows` se deben listar los objetos correspondientes y al seleccionar uno se debe mostrar su diagrama en el canvas central para permitir su edición.
- **FR-013F**: Un workflow debe poder utilizar un sub-workflow como nodo dentro de su proceso de ejecución.
- **FR-013G**: El elemento `testing` debe mostrar las opciones `create test` y `stored tests` y debe permitir análisis AB testing para evaluar el impacto entre un workflow challenger y el workflow champion aprobado.
- **FR-013H**: El análisis AB testing debe medir el impacto por la cantidad de clientes que superan las reglas del workflow y debe permitir seleccionar un periodo de consultas realizadas al motor a partir de los `events`.
- **FR-013I**: El elemento `events` debe mostrar una tabla con las últimas 50 consultas al motor de decisiones, incluyendo los campos configurados para la vista, y debe permitir filtrado por periodo de consulta y cliente.
- **FR-013J**: La edición de un workflow debe realizarse mediante drag and drop de nodos y la creación de conexiones entre nodos en el canvas central.
- **FR-013K**: El canvas debe permitir crear workflows simples, agregar nodos desde el panel lateral derecho, conectar nodos compatibles y mostrar el estado por nodo durante la edición y la ejecución.
- **FR-013L**: Cada nodo debe permitir configurar sus parámetros de ingreso y salida de datos, sus reglas de negocio y su manejo de errores.
- **FR-013M**: El workflow debe poder ejecutarse desde el canvas, registrar sus ejecuciones y resultados, guardarse y mantener versionado de forma persistente dentro de la sesión de diseño.
- **FR-013N**: Todo workflow nuevo debe guardarse en estado `draft` hasta que el rol `Administrador de Riesgos` lo apruebe y lo cambie a `approved`; solo los workflows `approved` pueden asociarse a channels.
- **FR-013O**: La creación de un channel debe incluir el nombre del tipo de evaluación, un paquete de parámetros aprobados y un único workflow `approved`; cada channel debe asociar exactamente un workflow posible.
- **FR-013P**: El paquete de parámetros de un channel debe construirse mediante selección múltiple de parámetros aprobados disponibles en la creación de channels.
- **FR-013Q**: Antes de guardar o finalizar la edición de un channel, el sistema debe validar que las reglas del workflow asociado no rompan los parámetros seleccionados; si la validación falla, el channel no puede persistirse como finalizado.
- **FR-013A**: La sección `Parámetros` debe mostrar los elementos `límites internos`, `límites globales` y `niveles de autonomía`. La creación y edición de estos parámetros solo podrán realizarse por el Administrador de Riesgos. Cada uno de estos elementos podrá crear reglas en base a las variables y medidas disponibles, incluyendo: ratio cuota ingreso interno, ratio deuda ingreso, plazo máximo, monto a financiar.
- **FR-013B**: La sección `Data` debe mostrar los elementos `Importar dataset`, `Configurar relaciones`, `Administrar medidas` y `Administrar catálogos`. Las opciones de `Administrar medidas` y `Administrar catálogos` permiten la creación y eliminación de objetos (medida y catálogo). La opción de `Administrar medidas` permite la creación de nuevas variables a partir de los datasets importados y las variables que el usuario digita en la plataforma. Las nuevas medidas pasan por el proceso de creación -> draft -> aprobación por el Administrador de Riesgos.
- **FR-014**: La parte inferior del sidebar debe mostrar un botón de acceso a los datos del perfil del usuario con acciones básicas para cambiar contraseña, consultar permisos aprobados y cerrar sesión.
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
- **Channel**: Modo de evaluación configurado para un producto; identifica un tipo de evaluación, asocia un único workflow aprobado y un paquete de parámetros aprobado, y puede representar variantes como evaluación regular o fast track.
- **Paquete de parámetros aprobado**: Selección múltiple de parámetros aprobados disponibles que un channel puede usar para su configuración, sujeta a validación de compatibilidad con el workflow antes de guardar o finalizar.
- **Workflow**: Diagrama editable de ejecución que define la lógica operativa de un channel, puede incluir sub-workflows como nodos y se mantiene en `draft` hasta su aprobación por el rol autorizado.
- **Ejecución de workflow**: Instancia registrada de la ejecución de un workflow con su estado, resultado y trazabilidad asociada.
- **Test**: Configuración de análisis AB testing para comparar un workflow challenger contra el workflow champion aprobado usando eventos seleccionados.
- **Event**: Consulta registrada al motor de decisiones con campos configurables para auditoría, filtrado y análisis de periodos.
- **Flujo de decisión**: Estructura visual compuesta por nodos y conexiones que representa la lógica de originación de crédito.
- **Nodo**: Paso individual del flujo con nombre, tipo, propiedades y relaciones con otros nodos.
- **Conexión**: Relación entre nodos con una etiqueta semántica que expresa la transición.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un usuario puede localizar y abrir cualquiera de los dos productos semilla en menos de 30 segundos en una prueba guiada.
- **SC-002**: Al menos 4 de 5 personas en una prueba de usabilidad pueden abrir un servicio disponible y acceder al espacio de diseño sin ayuda.
- **SC-003**: Al menos 4 de 5 personas en una prueba de usabilidad pueden seleccionar un nodo y ver sus propiedades correctas en menos de 5 segundos.
- **SC-004**: Al menos 4 de 5 personas en una prueba de usabilidad pueden agregar, mover y eliminar un nodo sin perder el contexto del flujo.
- **SC-005**: La navegación entre productos, servicios y diseño mantiene visibles las acciones principales sin necesidad de desplazamiento horizontal en resoluciones de escritorio comunes.

## Assumptions

- La interfaz es de escritorio primero y prioriza uso en pantallas amplias.
- El contenido visible de la interfaz debe estar completamente en español.
- La gestión de productos, servicios y flujos inicia con datos semilla y estado local de interfaz.
- Las acciones de menú que no tengan backend asociado funcionan como marcadores de posición de la experiencia.
- La persistencia de cambios queda limitada a la sesión de frontend para este prototipo inicial.
