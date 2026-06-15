# Feature Specification: Project Specification Consolidation

**Status**: Refined

**Refined**: 2026-06-14 — Se definieron explicitamente las diferencias entre `delete` y `retire`, y como deben representarse los metadatos de aprobacion en artefactos `draft`.

**Refined**: 2026-06-14 — Se agregó el módulo de administración para consulta de productos y workflows activos/draft, con detalle auditable y ocultamiento de configuraciones retiradas o eliminadas del runtime/UI.

**Refined**: 2026-06-13 — Se explicitó que los cambios en perfiles y permisos entran en vigencia inmediata dentro del módulo de administración.

## Summary

Esta especificacion consolida el alcance funcional y operativo del MVP de `Decision Engine` a partir de `specs/000-old-specification/docs/SPEC.md` y `specs/000-old-specification/docs/DDR.md`. El proyecto debe entregar una plataforma de evaluacion y gestion de solicitudes de credito que cubra el flujo `PLD` de punta a punta, mantenga trazabilidad completa, incorpore asistencia AI no decisoria y deje validada una base reutilizable para otros productos de prestamo.

## Clarifications

### Session 2026-06-11

- Q: Que ciclo de vida deben tener los productos y workflows administrables del motor? → A: `draft -> active -> retired`
- Q: Donde deben definirse las variables del motor? → A: Las variables se definen por producto y cada workflow reutiliza o selecciona las que necesita.
- Q: Como debe definirse el origen de una variable? → A: Cada variable define su origen permitido: campaña, interfaz o ambos.
- Q: Que ciclo de vida deben tener las reglas del motor? → A: `draft -> active -> retired`
- Q: Como deben modificarse los workflows activos? → A: Un workflow `active` no se edita; cualquier cambio crea una nueva version.

### Session 2026-06-12

- Q: Que enfoque de desarrollo debe priorizar la implementacion de funcionalidades? → A: TDD con ciclo `Red -> Green -> Refactor`.
- Q: Cuales son los campos minimos que debe mostrar la bandeja operativa? → A: `request_id`, documento y nombre del solicitante, producto/workflow, estado actual, fecha de creacion, fecha de ultima actualizacion, `evaluation_id` vinculado y acciones disponibles segun rol.

### Session 2026-06-13

- Q: Cuando deben definirse y ejecutarse obligatoriamente las pruebas unitarias de nuevas funcionalidades? → A: Deben definirse antes o durante la implementacion y ejecutarse obligatoriamente cuando la funcionalidad quede lista para revision o cuando se complete una unidad funcional verificable.
- Q: Que estados operativos minimos debe tener una solicitud de credito en el MVP? → A: `registrada -> en_revision -> aprobada/rechazada`, con `anulada` como estado terminal alternativo permitido.
- Q: Como debe administrarse la matriz de perfiles y permisos? → A: Debe existir un modulo de administracion de perfiles que permita al administrador agregar o retirar permisos por perfil sin depender de valores hardcodeados como mecanismo operativo habitual.
- Q: Cuando entran en vigencia los cambios del modulo de administracion de perfiles? → A: Los cambios de permisos y perfiles entran en vigencia de manera inmediata una vez aplicados y auditados.

### Session 2026-06-14

- Q: Que roles pueden acceder al modulo de administracion de productos? → A: Solo `Administrador`, `Administrador de negocio` y `Administrador de riesgos`.
- Q: Que estados debe poder visualizar el modulo de administracion de productos? → A: Por defecto muestra productos, workflows y configuraciones `active`, y debe permitir cambiar la vista para consultar tambien elementos `draft`.
- Q: Como deben tratarse los productos, workflows y configuraciones eliminadas o retiradas? → A: No deben ser visibles en la UI administrativa operativa, pero deben persistir en base de datos para auditoria y reconstruccion historica.
- Q: Cual es la diferencia entre `delete` y `retire` en configuraciones administrables? → A: `retire` es una transicion gobernada del ciclo de vida que conserva el artefacto como historico retirado; `delete` es una baja administrativa logica permitida solo bajo la politica RBAC/estado, tambien persistida para auditoria, y no reemplaza las obligaciones de retiro o versionado sobre artefactos que ya estuvieron `active`.
- Q: Como deben verse los metadatos de aprobacion en productos o workflows `draft`? → A: Mientras el artefacto permanezca en `draft`, los campos de aprobacion deben mostrarse sin valor efectivo (`null`, vacio o estado `pendiente`) y solo completarse cuando exista una aprobacion/activacion real auditada.

## User Scenarios & Testing

**Nota de dependencia del MVP**: Aunque las historias se presentan por capacidad funcional, `User Story 4` habilita la base administrable del motor que consumen `User Story 1`, `User Story 2` y `User Story 3`. En la implementacion del MVP, `US4` debe completarse antes de ejecutar evaluaciones operativas sobre configuraciones persistidas.

**Nota de desarrollo**: La implementacion de funcionalidades debe priorizar `TDD`, siguiendo el ciclo `Red -> Green -> Refactor`; los cambios de comportamiento deben nacer con una prueba automatizada en falla, pasar a verde con la implementacion minima y luego refactorizar sin perder cobertura. Las pruebas unitarias de nuevas funcionalidades deben definirse antes o durante la implementacion y ejecutarse obligatoriamente cuando la funcionalidad quede lista para revision o cuando se cierre una unidad funcional verificable.

### User Story 1 - Consultar y evaluar una oferta de credito

Como analista, quiero consultar un cliente, revisar sus ofertas disponibles y ejecutar una evaluacion deterministica para entender si una oferta puede continuar a registro.

#### Acceptance Scenario

1. Dado un cliente identificado por tipo y numero de documento, cuando el analista realiza una consulta, entonces el sistema muestra sus datos relevantes y las ofertas disponibles del producto aplicable.
2. Dado que el analista selecciona una oferta y completa los datos complementarios requeridos, cuando solicita la evaluacion, entonces el sistema recalcula la oferta y devuelve un resultado estructurado con bloqueos, alertas y observaciones.
3. Dado un resultado de evaluacion disponible, cuando el analista solicita soporte interpretativo, entonces el sistema muestra una explicacion en lenguaje claro, un resumen del caso y sugerencias de siguiente paso sin alterar el resultado deterministico, dejando traza auditable del modelo, template, payload permitido y versiones del motor usadas para generar la asistencia.

### User Story 2 - Registrar y gestionar una solicitud

Como analista o evaluador, quiero registrar una solicitud de credito y gestionarla en una bandeja operativa para dar seguimiento a su ciclo de vida.

#### Acceptance Scenario

1. Dado un resultado de evaluacion habilitante, cuando el usuario registra la solicitud, entonces el sistema guarda la solicitud con su estado inicial y la asocia a la traza de evaluacion correspondiente.
2. Dado un rango de fechas o periodo operativo, cuando el usuario consulta la bandeja, entonces el sistema devuelve las solicitudes encontradas mostrando como minimo `request_id`, documento y nombre del solicitante, producto/workflow, estado actual, fecha de creacion, fecha de ultima actualizacion, `evaluation_id` vinculado y acciones permitidas segun rol.
3. Dado una solicitud existente, cuando un usuario autorizado consulta su detalle, entonces el sistema muestra sus datos operativos, la evaluacion vinculada, el historial de estados y los adjuntos disponibles segun rol.
4. Dado una solicitud existente, cuando un usuario autorizado la anula o cambia de estado dentro del flujo `registrada -> en_revision -> aprobada/rechazada` o hacia `anulada` como estado terminal alternativo permitido, entonces el sistema registra el cambio, conserva la trazabilidad historica y refleja el nuevo estado en la bandeja.

### User Story 3 - Administrar adjuntos y auditoria

Como usuario operativo o auditor, quiero acceder a los adjuntos y a la trazabilidad de cada solicitud para validar evidencia y reconstruir decisiones.

#### Acceptance Scenario

1. Dado una solicitud existente, cuando un usuario autorizado carga un archivo ZIP valido, entonces el sistema lo asocia a la solicitud y registra la accion en la traza operativa.
2. Dado una solicitud con adjuntos, cuando un usuario autorizado consulta el detalle, entonces puede visualizar la lista de archivos disponibles, sus metadatos y el contenido listado del ZIP correspondiente antes de descargarlo.
3. Dado una evaluacion o una accion operativa completada, cuando un auditor consulta la traza, entonces puede reconstruir entradas relevantes, resultado, eventos y acciones ejecutadas mediante una linea de tiempo paginada filtrable por evaluacion o solicitud.

### User Story 4 - Administrar productos, workflows, variables, parametros, pipeline y reglas del motor

Como usuario de negocio, riesgos o administracion autorizado, quiero consultar, registrar y gobernar productos, workflows, variables, parametros, pipeline y reglas del motor para habilitar cambios operativos sin depender de cambios de codigo como practica habitual.

Alcance operativo de esta historia: las altas, ediciones sobre borradores, versionados, activaciones, retiros y reemplazos de configuracion forman parte de la operacion administrable normal del MVP. Los cambios de codigo quedan reservados para nuevas capacidades compartidas de plataforma, cambios estructurales del motor o integraciones fuera del modelo administrable previsto.

#### Acceptance Scenario

1. Dado un producto nuevo, cuando un usuario autorizado lo registra, entonces el sistema lo guarda en estado `draft` con trazabilidad de quien lo creo.
2. Dado un producto existente, cuando el usuario autorizado crea variables, catalogos, parametros, workflows, pipeline y reglas asociados, entonces el sistema valida sus referencias y conserva el estado gobernado de cada configuracion.
3. Dado un workflow activo, cuando se requiere un cambio funcional, entonces el sistema obliga a crear una nueva version en lugar de editar la version activa y deja evidencia auditable de la activacion posterior.
4. Dado un producto o workflow en estado distinto de `active`, cuando una evaluacion operacional intenta usarlo, entonces el sistema rechaza esa ejecucion.
5. Dado un producto existente, cuando un usuario autorizado agrega un nuevo workflow a ese producto, entonces el sistema permite administrarlo y activarlo sin alterar los workflows activos ya publicados para el mismo producto.
6. Dado una configuracion incompleta o inconsistente, cuando un usuario intenta activarla, entonces el sistema bloquea la activacion, informa el motivo y mantiene sin cambios la configuracion `active` previamente valida.
7. Dado una version activa publicada por error, cuando un usuario autorizado necesita reemplazarla, entonces el sistema crea una nueva version `draft`, conserva auditablemente la version anterior y permite retirar la version incorrecta solo despues de activar la version de reemplazo o de retirar el workflow afectado.
8. Dado un administrador autorizado, cuando accede al modulo de administracion de perfiles, entonces puede agregar o retirar permisos de un perfil existente y el sistema conserva trazabilidad auditable de esos cambios.
9. Dado un cambio en los permisos de un perfil, cuando el administrador confirma la modificacion, entonces los usuarios asociados a ese perfil quedan gobernados de manera inmediata por la nueva asignacion sin requerir cambios de codigo ni despliegues para la sola modificacion de permisos.
10. Dado un usuario con rol `Administrador`, `Administrador de negocio` o `Administrador de riesgos`, cuando accede al modulo de administracion de productos, entonces el sistema muestra por defecto solo productos `active` y permite ingresar al detalle de cada producto con fecha de creacion, ultima modificacion, usuario creador, usuario aprobador y workflows activos asociados.
11. Dado un producto visible en el modulo administrativo, cuando el usuario autorizado ingresa al detalle de uno de sus workflows, entonces el sistema muestra sus datos de creacion, aprobacion, pipeline, variables, parametros y reglas vigentes para esa configuracion.
12. Dado un usuario autorizado dentro del modulo de administracion de productos, cuando cambia la vista a borradores, entonces el sistema muestra productos, workflows y demas configuraciones en estado `draft` sin mezclar en la vista operativa por defecto las configuraciones retiradas o eliminadas.
13. Dado un producto, workflow o configuracion retirada o eliminada, cuando un usuario consulta las vistas operativas del modulo administrativo, entonces el sistema no la muestra, pero mantiene sus registros persistidos y auditables en base de datos.
14. Dado un producto o workflow en estado `draft`, cuando un usuario autorizado consulta su detalle administrativo, entonces el sistema muestra sus metadatos de aprobacion como pendientes o sin valor efectivo hasta que exista una aprobacion real registrada.

## Edge Cases

- El sistema debe manejar clientes sin ofertas disponibles sin permitir que el flujo avance a evaluacion o registro.
- El sistema debe rechazar intentos de registrar solicitudes sin una evaluacion valida y trazable.
- El sistema debe impedir anulaciones o cambios de estado no permitidos para el estado actual o para el rol del usuario, incluyendo transiciones fuera del flujo `registrada -> en_revision -> aprobada/rechazada` y usos invalidos de `anulada` como estado terminal alternativo.
- El sistema debe manejar fallas de la asistencia AI sin bloquear la consulta, evaluacion, registro o consulta de bandeja.
- El sistema debe rechazar adjuntos que no correspondan al formato ZIP esperado o que no puedan asociarse de forma valida a una solicitud existente.
- El sistema debe manejar ZIP validos pero vacios, corruptos o con manifiesto ilegible sin perder la auditoria del intento realizado.
- El sistema debe preservar la reproducibilidad de una evaluacion aunque reglas o parametros hayan cambiado posteriormente.
- El sistema debe impedir la edicion directa de workflows en estado `active` y exigir una nueva version para cualquier cambio posterior.
- El sistema debe impedir activar productos, workflows, catalogos o reglas con referencias incompletas o inconsistentes.
- El sistema debe manejar intentos de usar una variable desde un origen no permitido rechazando la evaluacion antes de ejecutar el motor.
- El sistema debe impedir que un producto sin workflows `active` quede disponible para evaluaciones operativas.
- El sistema debe impedir variables duplicadas dentro del mismo producto cuando compartan la misma identidad de negocio o `variable_key`.
- El sistema debe impedir que una regla o workflow nuevo quede `active` si referencia variables retiradas, ausentes o con una politica de origen incompatible.
- El retiro de un producto no debe dejar workflows o reglas `active` utilizables bajo ese producto; la gobernanza debe forzar retiro o reemplazo coherente de sus artefactos activos antes del cierre final.
- El sistema debe impedir que la vista administrativa por defecto mezcle configuraciones `draft` con configuraciones `active` o exponga artefactos `retired` o eliminados como si siguieran operativos.
- El sistema debe manejar productos `active` sin metadata administrativa completa bloqueando su publicacion o marcandolos como inconsistentes hasta completar creador, aprobador y timestamps requeridos.
- El sistema debe impedir usar `delete` como atajo para borrar logicamente un artefacto `active` sin cumplir antes las reglas de reemplazo, retiro y trazabilidad exigidas por la gobernanza.
- El detalle administrativo de artefactos `draft` no debe mostrar usuarios o timestamps de aprobacion ficticios, heredados o inferidos si la aprobacion aun no ocurrio.

## Functional Requirements

### Core Flow

- FR-001: El sistema debe permitir consultar clientes por tipo y numero de documento y mostrar los datos relevantes necesarios para iniciar una evaluacion.
- FR-002: El sistema debe mostrar las campanas u ofertas disponibles asociadas al cliente y permitir seleccionar una oferta para evaluacion.
- FR-003: El sistema debe permitir capturar datos complementarios requeridos para la evaluacion de una oferta.
- FR-004: El sistema debe ejecutar una evaluacion deterministica de la oferta seleccionada y devolver un resultado estructurado que incluya al menos resultado de evaluacion, alertas, observaciones y motivos de bloqueo cuando existan.
- FR-005: El sistema debe permitir registrar una solicitud de credito solo cuando exista una evaluacion valida asociada al caso.
- FR-006: El sistema debe permitir consultar una bandeja de solicitudes por periodo mostrando como minimo `request_id`, documento y nombre del solicitante, producto/workflow, estado actual, fecha de creacion, fecha de ultima actualizacion, `evaluation_id` vinculado y acciones disponibles segun rol.
- FR-006A: El sistema debe permitir consultar el detalle de una solicitud mostrando sus datos operativos, la evaluacion vinculada, el historial de estados y los adjuntos disponibles segun rol.
- FR-007: El sistema debe permitir anular solicitudes y actualizar su estado solo a usuarios autorizados y bajo el flujo minimo `registrada -> en_revision -> aprobada/rechazada`, con `anulada` como estado terminal alternativo permitido.
- FR-008: El sistema debe permitir exportar los resultados de la bandeja en formato `CSV UTF-8`, incluyendo los filtros aplicados, para uso operativo y seguimiento.

### Traceability and Audit

- FR-009: El sistema debe registrar eventos auditables de cada evaluacion y de cada accion operativa relevante sobre una solicitud, incluyendo actor, rol, accion, entidad afectada, resultado y timestamp.
- FR-010: El sistema debe conservar la relacion entre consulta, evaluacion, solicitud, cambios de estado y adjuntos para permitir reconstruccion historica del caso de punta a punta.
- FR-011: El sistema debe preservar versiones suficientes de reglas, parametros y contexto para reproducir el resultado de una evaluacion realizada.

### Attachments

- FR-012: El sistema debe permitir cargar, listar, visualizar metadatos y contenido listado, y descargar adjuntos ZIP asociados a una solicitud.
- FR-013: El sistema debe registrar auditoria de las operaciones de carga y descarga de adjuntos.
- FR-013A: El sistema debe exponer una consulta paginada de auditoria y trazabilidad por `evaluation_id` o `request_id`, incluyendo actor, rol, accion, entidad afectada, resultado, timestamp y referencia AI cuando aplique.

### Assisted AI

- FR-014: El sistema debe ofrecer una explicacion asistida del resultado de evaluacion en lenguaje claro basada en la salida estructurada del motor.
- FR-015: El sistema debe ofrecer un resumen del caso y sugerencias de siguientes pasos como apoyo al usuario operativo.
- FR-016: El sistema debe garantizar que la asistencia AI sea opcional y que su indisponibilidad no impida continuar el flujo principal.
- FR-017: El sistema no debe permitir que la asistencia AI tome la decision final de aprobacion o rechazo de una solicitud.

### Multi-Product Foundation

- FR-018: El sistema debe tratar `PLD` como el primer producto operativo del MVP sin asumir que sera el unico producto soportado por la plataforma.
- FR-019: El sistema debe separar capacidades compartidas de plataforma de reglas, datos y variaciones exclusivas de un producto especifico.
- FR-020: El sistema debe permitir definir y ejecutar flujos de evaluacion diferenciados por producto y por contexto operativo sin redisenar las capacidades compartidas.
- FR-021: El sistema debe contemplar administracion gobernada y auditable de reglas, parametros y secuencia del flujo para habilitar evolucion posterior sin perder control operativo.
- FR-022: El sistema debe permitir registrar nuevos productos del motor sin requerir cambios de codigo como mecanismo normal de operacion.
- FR-022A: La definicion minima de un producto administrable debe incluir `product_code` unico, nombre, descripcion operativa, estado gobernado, responsables de creacion/activacion/retiro y trazabilidad temporal de esos cambios.
- FR-023: El sistema debe permitir crear multiples workflows por producto para soportar distintos modos de evaluacion o politicas.
- FR-023A: La definicion minima de un workflow debe incluir `workflow_code` unico dentro del producto, nombre, descripcion operativa, estado gobernado, version publicada vigente y trazabilidad de quien lo crea, activa, retira o reemplaza.
- FR-023B: El modulo de administracion de productos debe estar disponible solo para los roles `Administrador`, `Administrador de negocio` y `Administrador de riesgos`.
- FR-024: Cada producto y workflow administrable debe seguir un ciclo de vida `draft -> active -> retired`.
- FR-024A: La transicion `draft -> active` requiere validacion satisfactoria de referencias, permisos autorizados y evidencia auditable; la transicion `active -> retired` impide nuevas evaluaciones con ese artefacto pero conserva referencias historicas; `draft -> retired` se permite como descarte administrativo antes de publicacion; `active -> draft` no esta permitido.
- FR-024B: `Retire` y `delete` no son equivalentes. `Retire` es una transicion gobernada del ciclo de vida que conserva el artefacto como retirado historico; `delete` es una baja administrativa logica permitida solo para los estados y roles autorizados por la politica vigente, debe persistir con actor, motivo y timestamp, y no puede utilizarse para eludir obligaciones de versionado, reemplazo o retiro sobre artefactos que ya estuvieron `active`.
- FR-025: El sistema debe impedir que productos o workflows en estado distinto de `active` sean usados para evaluaciones operativas.
- FR-025A: Un producto solo puede quedar disponible para runtime si tiene al menos un workflow `active`; si no tiene ninguno, debe considerarse no operativo aunque el producto exista.
- FR-025B: Un mismo producto puede tener multiples workflows `active` en paralelo siempre que cada uno tenga `workflow_code` distinto y una politica operativa diferenciada; el runtime debe resolverlos explicitamente por `workflow_code`.
- FR-026: El sistema debe conservar trazabilidad de quien creo, activo, retiro o modifico productos y workflows.
- FR-026A: El modulo de administracion debe mostrar por defecto solo productos `active`, con opcion explicita para cambiar a una vista de productos, workflows y demas configuraciones `draft`.
- FR-026B: El detalle administrativo de un producto debe mostrar como minimo fecha de creacion, fecha de ultima modificacion, usuario creador, usuario aprobador y workflows `active` asociados.
- FR-026C: El detalle administrativo de un workflow debe mostrar como minimo sus datos de creacion, aprobacion, pipeline, variables, parametros y reglas asociadas a la version consultada.
- FR-026D: Los productos, workflows y demas configuraciones `retired` o eliminadas no deben ser visibles en las vistas operativas del modulo administrativo, pero deben persistir en base de datos con suficiente trazabilidad para auditoria y reconstruccion historica.
- FR-026E: Cuando un producto, workflow o configuracion permanezca en estado `draft`, sus metadatos de aprobacion deben mantenerse sin valor efectivo (`null`, vacio o equivalente a `pendiente`) y solo completarse cuando exista una aprobacion o activacion real auditada.
- FR-027: El sistema debe permitir definir variables a nivel de producto para que puedan ser reutilizadas por multiples workflows del mismo producto.
- FR-027A: Cada variable administrable debe incluir como minimo `variable_key` unico dentro del producto, nombre, significado de negocio, tipo de dato, obligatoriedad, estado gobernado y responsables de creacion/activacion/retiro.
- FR-027B: Las variables administrables deben seguir un ciclo de vida `draft -> active -> retired` coherente con el resto de configuraciones gobernadas.
- FR-028: Cada workflow debe poder seleccionar cuales variables de su producto utiliza en sus reglas y evaluaciones.
- FR-028A: La seleccion de variables de un workflow significa inclusion explicita en su catalogo publicado, definicion de obligatoriedad en runtime y disponibilidad para reglas/evaluacion; no implica editar una variable activa ni redefinir su identidad base dentro del workflow.
- FR-029: Cada variable de producto debe definir su origen permitido de datos entre base de campana, captura por interfaz o ambas opciones.
- FR-029A: El origen permitido de una variable es una politica de configuracion definida en tiempo de dise\u00f1o administrativo y validada en cada evaluacion; no se resuelve libremente caso por caso fuera de esa politica publicada.
- FR-030: El sistema debe validar que una evaluacion solo use valores de variables provenientes de los origenes permitidos para cada variable.
- FR-031: El sistema debe permitir crear multiples reglas dentro de cada workflow para expresar politicas y logica de decision.
- FR-031A: La definicion minima de una regla debe incluir `rule_key` o identificador versionable, nombre, descripcion, condicion o expresion declarativa, efecto esperado sobre la decision y estado gobernado auditable.
- FR-032: Cada regla administrable debe seguir un ciclo de vida `draft -> active -> retired`.
- FR-032A: La activacion de una regla requiere validacion sintactica, referencias vigentes a variables permitidas y aprobacion por un rol autorizado distinto o equivalente al que corresponda segun la politica de segregacion vigente.
- FR-033: El sistema debe impedir que reglas en estado distinto de `active` participen en evaluaciones operativas.
- FR-034: El sistema debe conservar trazabilidad de quien creo, activo, retiro o modifico reglas dentro de cada workflow.
- FR-035: El sistema no debe permitir la edicion directa de un workflow en estado `active`; cualquier cambio debe generar una nueva version gobernada y auditable.
- FR-035A: Una nueva version significa una nueva revision `draft` con identidad versionada propia, trazabilidad independiente y referencias publicables a catalogo, pipeline, parametros y reglas; puede originarse a partir de una configuracion previa, pero no reemplaza en sitio la version ya `active`.
- FR-035B: Si se detecta una configuracion activa incorrecta, el sistema debe permitir crear una version de reemplazo y bloquear que el retiro final de la version anterior deje al producto sin una opcion operativa coherente salvo retiro explicito del workflow o del producto.
- FR-036: El sistema debe permitir publicar catalogos versionados de variables por producto y asignarlos a versiones de workflow.
- FR-036A: Las acciones de crear/editar borradores pueden ser realizadas por usuarios administrativos autorizados; las acciones de activar, retirar y versionar artefactos criticos del motor deben respetar segregacion de funciones entre negocio, riesgos y administracion privilegiada segun la matriz RBAC vigente.
- FR-037: El sistema debe validar, antes de activar una configuracion del motor, que sus referencias a variables, reglas, pipeline y workflow sean consistentes y completas.
- FR-037A: El sistema debe permitir administrar parametros versionados por producto y workflow bajo un ciclo de vida gobernado y auditable.
- FR-037B: El sistema debe persistir en cada evaluacion las versiones efectivas de workflow, catalogo de variables, reglas, parametros y pipeline realmente aplicadas.
- FR-037C: El sistema debe permitir administrar estrategias de pipeline y sus nodos bajo versionado, validacion topologica y activacion gobernada.
- FR-037D: La validacion de activacion debe bloquear, como minimo, referencias inexistentes, variables duplicadas o retiradas, fuentes de variable incompatibles, ausencia de pipeline o reglas requeridas, y conflictos de estado entre producto, workflow y artefactos dependientes.

### Security and Operations

- FR-038: El sistema debe aplicar autenticacion y autorizacion basadas en roles para proteger consultas, evaluaciones, solicitudes, adjuntos y funciones administrativas.
- FR-038A: El sistema debe incluir un modulo de administracion de perfiles que permita a un administrador autorizado agregar y retirar permisos por perfil dentro de un modelo auditable y gobernado.
- FR-038B: La asignacion operativa de permisos a perfiles no debe quedar hardcodeada como mecanismo normal de operacion; los cambios rutinarios sobre permisos deben resolverse desde la administracion de perfiles persistida.
- FR-038C: Cada cambio sobre un perfil o sus permisos debe registrar actor, perfil afectado, permisos agregados o retirados, resultado y timestamp para trazabilidad administrativa.
- FR-038D: Los cambios confirmados sobre perfiles y permisos deben entrar en vigencia de manera inmediata para las evaluaciones de autorizacion subsiguientes, sin requerir publicacion separada, despliegues ni reinicio operativo como mecanismo normal.
- FR-039: El sistema debe ofrecer autenticacion operativa de frontend, restauracion de sesion y acceso por rol suficientes para ejecutar los flujos del MVP, sin impedir una futura integracion con un proveedor corporativo.
- FR-040: El sistema debe desacoplar el control de acceso de restricciones basadas unicamente en IP o de acoplamientos con la interfaz.
- FR-041: El sistema debe iniciar con base limpia, sin depender de migracion historica desde el sistema legado para operar el MVP.
- FR-042: El sistema debe registrar cada interaccion AI asociada al caso con modelo, version de template, payload permitido (subconjunto de datos anonimizados o no sensibles de la evaluacion o solicitud conforme a la politica de seguridad de datos), respuesta, estado de fallback y referencias a las versiones del motor utilizadas.

### Minimum RBAC Matrix

- Analista: puede autenticarse, restaurar sesion, consultar clientes, ejecutar evaluaciones, ver trazas del caso, registrar solicitudes, consultar bandeja y detalle de solicitudes, cargar adjuntos ZIP y mover solicitudes solo de `registrada` a `en_revision`.
- Evaluador: hereda permisos de analista y ademas puede aprobar, rechazar, anular solicitudes, exportar bandeja y consultar auditoria operacional.
- Administrador de negocio: puede acceder al modulo de administracion de productos para consultar productos `active`, cambiar a vista `draft`, revisar detalle de productos y workflows, crear y editar productos, workflows y reglas de negocio en estado `draft`, solicitar versionados y consultar bloqueos de activacion, pero no debe aprobar por si solo la activacion final de reglas o configuraciones que requieran control de riesgos. Mientras el estado de la modificacion sea `draft`, tambien podra eliminar dicha configuracion.
- Administrador de riesgos: puede acceder al modulo de administracion de productos para consultar productos `active`, cambiar a vista `draft`, revisar detalle de productos y workflows, crear y editar reglas, parametros, politicas de origen y criterios de activacion en estado, y puede aprobar o rechazar activaciones de configuraciones criticas segun la segregacion vigente. Tambien podra eliminar productos y workflows.
- Administrador: puede acceder al modulo de administracion de productos para consultar productos `active`, cambiar a vista `draft`, revisar detalle de productos y workflows, y gestionar productos, workflows, catalogos de variables, parametros, perfiles, permisos y usuarios; puede agregar o retirar permisos a un perfil desde el modulo de administracion correspondiente, pero no debe saltarse la segregacion de negocio/riesgos para publicar configuraciones del motor como operacion normal. Tambien puede consultar trazabilidad administrativa y operacional.
- Auditor: acceso de solo lectura a trazas, auditoria, detalle de solicitudes, historial de estados y metadatos de adjuntos, sin permiso para evaluar, registrar, transicionar ni administrar configuraciones.

## Key Entities

- Cliente: persona consultada para iniciar una evaluacion y recuperar datos relevantes de contexto.
- Oferta: propuesta disponible para un cliente que puede ser seleccionada y recalculada durante la evaluacion.
- Evaluacion: resultado deterministico generado para una oferta a partir de datos del cliente y datos complementarios capturados.
- Traza de decision: registro estructurado de entradas relevantes, reglas aplicadas, eventos, alertas, bloqueos y salida final de una evaluacion.
- Solicitud de credito: caso operativo registrado a partir de una evaluacion valida, con estado y seguimiento propio.
- Estado de solicitud: etapa operativa vigente de una solicitud junto con su historial de cambios dentro del flujo minimo `registrada`, `en_revision`, `aprobada`, `rechazada` o `anulada`.
- Adjunto ZIP: archivo asociado a una solicitud como evidencia operativa.
- Usuario operativo: actor con permisos segun rol para consultar, evaluar, registrar y administrar solicitudes.
- Regla o parametro versionado: definicion gobernada que influye en la evaluacion o en el comportamiento del flujo y cuya version debe poder auditarse.
- Producto de prestamo: configuracion de negocio que agrupa reglas, variaciones de flujo y datos propios de un tipo de prestamo; su definicion minima incluye `product_code` unico, nombre, descripcion operativa, estado gobernado y trazabilidad de creacion, activacion y retiro.
- Workflow de producto: modalidad de evaluacion asociada a un producto que define reglas activas y comportamiento operativo dentro de un ciclo de vida administrable; su definicion minima incluye `workflow_code` unico dentro del producto, nombre, descripcion y estado.
- Aprobacion administrativa: evidencia de quien aprobo una publicacion o activacion de producto, workflow o configuracion gobernada, con usuario, timestamp y resultado auditable.
- Eliminacion administrativa: baja logica gobernada de un producto, workflow o configuracion permitida solo para roles/estados autorizados, persistida con actor, motivo y timestamp, y distinta del estado `retired` del ciclo de vida.
- Version de workflow: revision gobernada de un workflow que permite introducir cambios sin alterar una configuracion ya activa; una nueva version es una revision `draft` con identidad versionada propia y referencias publicables a catalogo, reglas, parametros y pipeline, y puede derivarse de una version previa sin editarla en sitio.
- Variable de producto: dimension administrable definida para un producto y reutilizable por uno o varios workflows para construir reglas y evaluaciones; su definicion minima incluye `variable_key` unico, nombre, significado de negocio, tipo de dato, obligatoriedad, origen permitido y estado.
- Catalogo de variables: version publicable del conjunto de variables activas de un producto consumible por una version de workflow.
- Origen de variable: restriccion declarada de dise\u00f1o administrativo que define si una variable puede recibir datos desde base de campana, captura por interfaz o ambas fuentes; el runtime solo valida contra esa politica publicada.
- Regla de workflow: condicion o logica de decision administrable asociada a un workflow y gobernada por un ciclo de vida auditable; su definicion minima incluye identificador versionable, nombre, descripcion, condicion declarativa y efecto esperado sobre la decision.
- Parametro versionado: conjunto administrable de constantes o umbrales usados por el motor y publicado bajo una version auditable.
- Estrategia de pipeline: definicion administrable y versionada de la secuencia de nodos y branching permitido para un workflow.
- Nodo de pipeline: etapa versionada del flujo de evaluacion con referencias validadas dentro de una estrategia gobernada.
- Interaccion AI: registro auditable de una asistencia AI emitida para una evaluacion o solicitud con referencias de modelo, template, payload permitido (subconjunto filtrado de datos no identificables) y fallback.
- Perfil administrativo: agrupacion gobernada de permisos asignables a usuarios operativos o administrativos, editable desde un modulo de administracion con trazabilidad auditable y cambios de vigencia inmediata una vez confirmados.
- Permiso administrable: capacidad operativa o administrativa asignable a un perfil desde configuracion persistida, no solo desde constantes hardcodeadas en codigo.

## Assumptions

- El MVP funcional inicial cubre el flujo `PLD / solicitudes de credito` completo, mientras la base del sistema queda preparada para un segundo producto en una fase cercana.
- Las nuevas funcionalidades se desarrollan bajo prioridad `TDD`; sus pruebas unitarias se definen antes o durante la implementacion y deben ejecutarse antes de revision cuando el cambio ya constituye una funcionalidad o unidad funcional verificable.
- Los roles operativos principales incluyen al menos perfiles equivalentes a analista, evaluador, administrador y auditor con permisos diferenciados.
- La plataforma debe permitir administrar perfiles y permisos desde un modulo persistido; los valores hardcodeados solo pueden servir como bootstrap tecnico transitorio y no como mecanismo operativo rutinario.
- Los cambios sobre perfiles y permisos se aplican de manera inmediata una vez confirmados; no requieren una etapa separada de publicacion para entrar en vigencia operativa.
- La autenticacion del MVP usa el mecanismo operativo disponible en la plataforma actual y cubre login, restauracion de sesion y autorizacion por rol para los flujos definidos, sin bloquear una futura migracion a un proveedor corporativo.
- Los equipos de negocio y riesgos administran productos y workflows dentro de un esquema gobernado, sin depender de TI para el alta, activacion o retiro como operacion habitual.
- El modulo de administracion de productos expone por defecto solo configuraciones `active` y requiere una accion explicita para cambiar a la vista `draft`.
- Los equipos de negocio y riesgos operan bajo segregacion de funciones para configuraciones criticas: la creacion/edicion de borradores y la aprobacion/activacion final no deben depender de una misma accion no controlada como mecanismo normal.
- `Delete` se interpreta como baja logica persistida para auditoria y distinta de `retire`; no elimina fisicamente la evidencia ni reemplaza las transiciones de ciclo de vida exigidas para artefactos ya publicados.
- Las variables del motor se administran en el nivel de producto y cada workflow reutiliza solo las variables que requiere.
- Cada variable declara de forma explicita si sus datos pueden provenir de base de campana, de captura por interfaz o de ambas fuentes.
- Las reglas del motor se administran dentro de cada workflow y solo las reglas activas participan en evaluaciones operativas.
- Un workflow activo se considera inmutable para fines operativos; cualquier ajuste posterior se publica como una nueva version.
- La seleccion de variables de un workflow se resuelve mediante inclusion en catalogos versionados y definicion de obligatoriedad de runtime, no mediante duplicacion libre de variables dentro del workflow.
- Un producto retirado no mantiene artefactos `active` utilizables en runtime; sus workflows y reglas activas deben retirarse o reemplazarse de forma coherente antes de completar el retiro.
- La fuente de verdad del producto en el MVP es un unico registro persistido de producto administrable reutilizado tanto por runtime como por solicitudes de credito.
- La bandeja operativa se consulta por periodos y expone como minimo `request_id`, documento y nombre del solicitante, producto/workflow, estado actual, fecha de creacion, fecha de ultima actualizacion, `evaluation_id` vinculado y las acciones permitidas para el rol y estado vigentes.
- El ciclo de vida operativo minimo de una solicitud en el MVP es `registrada -> en_revision -> aprobada/rechazada`, con `anulada` como estado terminal alternativo permitido bajo autorizacion.
- Los adjuntos admitidos para el MVP se limitan a archivos ZIP asociados a una solicitud.
- Los productos, workflows y configuraciones eliminadas o retiradas persisten en base de datos para auditoria, pero quedan ocultos de las vistas operativas del modulo administrativo.
- Los metadatos de aprobacion de artefactos `draft` permanecen sin valor efectivo hasta que ocurra una aprobacion real; la UI administrativa puede representarlos como vacios o `pendiente`, pero no como aprobados.
- La asistencia AI consume solo informacion permitida del caso y se utiliza como apoyo explicativo, no como autoridad de decision.
- El legado sirve como referencia funcional, pero no impone dependencias de interfaz, autenticacion por IP ni estructura interna del nuevo sistema.
- La suite operativa base para validar `SC-012` ejecuta AI deshabilitada, datos semilla locales, base SQLite local, 5 iteraciones de calentamiento por endpoint y luego 30 consultas validas + 30 evaluaciones validas por producto/workflow activo con concurrencia 1 y payloads deterministas.
- La evidencia minima para cumplir `SC-013` consiste en pruebas automatizadas definidas antes o durante la implementacion, una ejecucion en verde sobre el cambio funcional y registro de esa ejecucion en la revision o en el corte de la unidad funcional verificable.

## Success Criteria

- SC-001: En la suite de validacion operativa del MVP, un usuario autorizado puede completar consulta, evaluacion y registro de una solicitud en una sola sesion de trabajo sin recurrir al sistema legacy.
- SC-002: El 100% de las evaluaciones registradas conserva una traza suficiente para que un auditor reconstruya entradas relevantes, resultado y acciones posteriores del caso.
- SC-003: El 100% de los cambios de estado y anulaciones realizados por usuarios autorizados queda reflejado en la bandeja con su historial asociado.
- SC-004: Ante indisponibilidad de la asistencia AI, al menos el 95% de los casos de la suite de validacion del MVP que cumplen reglas de negocio puede completar consulta, evaluacion, registro y bandeja sin bloqueo del flujo principal.
- SC-005: El 100% de las solicitudes con adjuntos validos permite a usuarios autorizados cargar, listar metadatos, visualizar el contenido listado del ZIP y descargarlo dentro del flujo operativo del caso.
- SC-006: La especificacion funcional del MVP deja identificadas y separadas las capacidades compartidas de plataforma y las capacidades exclusivas de `PLD`, de modo que el alcance base pueda extenderse a un segundo producto sin redefinir el flujo comun del sistema.
- SC-007: El 100% de los productos y workflows usados en evaluaciones operativas se encuentra en estado `active`, con historial auditable de creacion, activacion y retiro.
- SC-008: El 100% de las reglas aplicadas en evaluaciones operativas se encuentra en estado `active`, con historial auditable de creacion, activacion y retiro.
- SC-009: El 100% de los cambios sobre workflows que ya estuvieron `active` queda registrado como una nueva version auditable, sin edicion directa de la version usada en evaluaciones previas.
- SC-010: Los usuarios autorizados pueden autenticar, restaurar sesion y acceder solo a las acciones permitidas por su rol en los flujos del MVP.
- SC-011: El sistema permite registrar y activar al menos un producto adicional al flujo `PLD` sin requerir cambios de codigo en las capas compartidas del motor.
- SC-012: En la validacion de endurecimiento del MVP, `POST /consultas` y `POST /evaluaciones` cumplen `p95 <= 2s` y `p95 <= 4s` respectivamente con AI deshabilitada sobre la suite operativa base definida para el proyecto.
- SC-013: El 100% de las nuevas funcionalidades o unidades funcionales verificables incorporadas al MVP llega a revision con pruebas unitarias definidas antes o durante la implementacion, ejecutadas satisfactoriamente sobre el comportamiento cambiado y con evidencia de esa ejecucion adjunta a la revision o al corte funcional correspondiente.
- SC-014: En la suite administrativa del MVP, usuarios autorizados de negocio y riesgos pueden crear, versionar, activar y retirar configuraciones del motor sin cambios de codigo en el 100% de los escenarios administrativos definidos para el producto y sus workflows.
- SC-015: El 100% de los intentos de activar configuraciones incompletas o inconsistentes es rechazado con motivo auditable antes de que la configuracion quede disponible para runtime.
- SC-016: El 100% de las evaluaciones operativas rechaza antes de ejecutar el motor cualquier variable cuyo origen de datos no coincida con la politica publicada para esa variable.
- SC-017: El 100% de los cambios de version de workflow conserva la version previa auditable e inmutable y permite agregar un nuevo workflow a un producto existente sin alterar workflows activos no relacionados.
- SC-018: El 100% de los productos retirados y de los productos sin workflows `active` queda fuera del runtime operativo sin perder la reproducibilidad historica de evaluaciones previas.
- SC-019: En la suite administrativa del MVP, el 100% de las consultas al modulo de administracion de productos realizadas por `Administrador`, `Administrador de negocio` y `Administrador de riesgos` muestra por defecto solo configuraciones `active`, permite cambiar a vista `draft` y expone el detalle auditable requerido de productos y workflows.
- SC-020: El 100% de los productos, workflows y configuraciones retiradas o eliminadas permanece persistido para auditoria y no aparece en las vistas operativas del modulo administrativo.
