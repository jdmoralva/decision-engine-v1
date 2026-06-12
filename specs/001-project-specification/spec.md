# Feature Specification: Project Specification Consolidation

## Summary

Esta especificacion consolida el alcance funcional y operativo del MVP de `Decision Engine` a partir de `docs/SPEC.md` y `docs/DDR.md`. El proyecto debe entregar una plataforma de evaluacion y gestion de solicitudes de credito que cubra el flujo `PLD` de punta a punta, mantenga trazabilidad completa, incorpore asistencia AI no decisoria y deje validada una base reutilizable para otros productos de prestamo.

## Clarifications

### Session 2026-06-11

- Q: Que ciclo de vida deben tener los productos y workflows administrables del motor? → A: `draft -> active -> retired`
- Q: Donde deben definirse las variables del motor? → A: Las variables se definen por producto y cada workflow reutiliza o selecciona las que necesita.
- Q: Como debe definirse el origen de una variable? → A: Cada variable define su origen permitido: campaña, interfaz o ambos.
- Q: Que ciclo de vida deben tener las reglas del motor? → A: `draft -> active -> retired`
- Q: Como deben modificarse los workflows activos? → A: Un workflow `active` no se edita; cualquier cambio crea una nueva version.

## User Scenarios & Testing

**Nota de dependencia del MVP**: Aunque las historias se presentan por capacidad funcional, `User Story 4` habilita la base administrable del motor que consumen `User Story 1`, `User Story 2` y `User Story 3`. En la implementacion del MVP, `US4` debe completarse antes de ejecutar evaluaciones operativas sobre configuraciones persistidas.

### User Story 1 - Consultar y evaluar una oferta de credito

Como analista, quiero consultar un cliente, revisar sus ofertas disponibles y ejecutar una evaluacion deterministica para entender si una oferta puede continuar a registro.

#### Acceptance Scenario

1. Dado un cliente identificado por tipo y numero de documento, cuando el analista realiza una consulta, entonces el sistema muestra sus datos relevantes y las ofertas disponibles del producto aplicable.
2. Dado que el analista selecciona una oferta y completa los datos complementarios requeridos, cuando solicita la evaluacion, entonces el sistema recalcula la oferta y devuelve un resultado estructurado con bloqueos, alertas y observaciones.
3. Dado un resultado de evaluacion disponible, cuando el analista solicita soporte interpretativo, entonces el sistema muestra una explicacion en lenguaje claro, un resumen del caso y sugerencias de siguiente paso sin alterar el resultado deterministico, dejando traza auditable del modelo, template, payload permitido y versiones del motor usadas para generar la asistencia.

### User Story 2 - Registrar y gestionar una solicitud

Como analista o supervisor, quiero registrar una solicitud de credito y gestionarla en una bandeja operativa para dar seguimiento a su ciclo de vida.

#### Acceptance Scenario

1. Dado un resultado de evaluacion habilitante, cuando el usuario registra la solicitud, entonces el sistema guarda la solicitud con su estado inicial y la asocia a la traza de evaluacion correspondiente.
2. Dado un rango de fechas o periodo operativo, cuando el usuario consulta la bandeja, entonces el sistema devuelve las solicitudes encontradas con su estado, datos relevantes y acciones permitidas segun rol.
3. Dado una solicitud existente, cuando un usuario autorizado la anula o cambia de estado, entonces el sistema registra el cambio, conserva la trazabilidad historica y refleja el nuevo estado en la bandeja.

### User Story 3 - Administrar adjuntos y auditoria

Como usuario operativo o auditor, quiero acceder a los adjuntos y a la trazabilidad de cada solicitud para validar evidencia y reconstruir decisiones.

#### Acceptance Scenario

1. Dado una solicitud existente, cuando un usuario autorizado carga un archivo ZIP valido, entonces el sistema lo asocia a la solicitud y registra la accion en la traza operativa.
2. Dado una solicitud con adjuntos, cuando un usuario autorizado consulta el detalle, entonces puede visualizar la lista de archivos disponibles, sus metadatos y el contenido listado del ZIP correspondiente antes de descargarlo.
3. Dado una evaluacion o una accion operativa completada, cuando un auditor consulta la traza, entonces puede reconstruir entradas relevantes, resultado, eventos y acciones ejecutadas mediante una linea de tiempo paginada filtrable por evaluacion o solicitud.

### User Story 4 - Administrar productos, workflows, variables, parametros, pipeline y reglas del motor

Como usuario de negocio, riesgos o administracion autorizado, quiero registrar y gobernar productos, workflows, variables, parametros, pipeline y reglas del motor para habilitar cambios operativos sin depender de cambios de codigo como practica habitual.

#### Acceptance Scenario

1. Dado un producto nuevo, cuando un usuario autorizado lo registra, entonces el sistema lo guarda en estado `draft` con trazabilidad de quien lo creo.
2. Dado un producto existente, cuando el usuario autorizado crea variables, catalogos, parametros, workflows, pipeline y reglas asociados, entonces el sistema valida sus referencias y conserva el estado gobernado de cada configuracion.
3. Dado un workflow activo, cuando se requiere un cambio funcional, entonces el sistema obliga a crear una nueva version en lugar de editar la version activa y deja evidencia auditable de la activacion posterior.
4. Dado un producto o workflow en estado distinto de `active`, cuando una evaluacion operacional intenta usarlo, entonces el sistema rechaza esa ejecucion.

## Edge Cases

- El sistema debe manejar clientes sin ofertas disponibles sin permitir que el flujo avance a evaluacion o registro.
- El sistema debe rechazar intentos de registrar solicitudes sin una evaluacion valida y trazable.
- El sistema debe impedir anulaciones o cambios de estado no permitidos para el estado actual o para el rol del usuario.
- El sistema debe manejar fallas de la asistencia AI sin bloquear la consulta, evaluacion, registro o consulta de bandeja.
- El sistema debe rechazar adjuntos que no correspondan al formato ZIP esperado o que no puedan asociarse de forma valida a una solicitud existente.
- El sistema debe manejar ZIP validos pero vacios, corruptos o con manifiesto ilegible sin perder la auditoria del intento realizado.
- El sistema debe preservar la reproducibilidad de una evaluacion aunque reglas o parametros hayan cambiado posteriormente.
- El sistema debe impedir la edicion directa de workflows en estado `active` y exigir una nueva version para cualquier cambio posterior.
- El sistema debe impedir activar productos, workflows, catalogos o reglas con referencias incompletas o inconsistentes.
- El sistema debe manejar intentos de usar una variable desde un origen no permitido rechazando la evaluacion antes de ejecutar el motor.

## Functional Requirements

### Core Flow

- FR-001: El sistema debe permitir consultar clientes por tipo y numero de documento y mostrar los datos relevantes necesarios para iniciar una evaluacion.
- FR-002: El sistema debe mostrar las campanas u ofertas disponibles asociadas al cliente y permitir seleccionar una oferta para evaluacion.
- FR-003: El sistema debe permitir capturar datos complementarios requeridos para la evaluacion de una oferta.
- FR-004: El sistema debe ejecutar una evaluacion deterministica de la oferta seleccionada y devolver un resultado estructurado que incluya al menos resultado de evaluacion, alertas, observaciones y motivos de bloqueo cuando existan.
- FR-005: El sistema debe permitir registrar una solicitud de credito solo cuando exista una evaluacion valida asociada al caso.
- FR-006: El sistema debe permitir consultar una bandeja de solicitudes por periodo con informacion suficiente para seguimiento operativo.
- FR-007: El sistema debe permitir anular solicitudes y actualizar su estado solo a usuarios autorizados y bajo reglas de flujo definidas.
- FR-008: El sistema debe permitir exportar los resultados de la bandeja en formato `CSV UTF-8`, incluyendo los filtros aplicados, para uso operativo y seguimiento.

### Traceability and Audit

- FR-009: El sistema debe registrar trazabilidad completa de cada evaluacion y de cada accion operativa relevante sobre una solicitud.
- FR-010: El sistema debe conservar la relacion entre consulta, evaluacion, solicitud, cambios de estado y adjuntos para permitir reconstruccion historica del caso.
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
- FR-023: El sistema debe permitir crear multiples workflows por producto para soportar distintos modos de evaluacion o politicas.
- FR-024: Cada producto y workflow administrable debe seguir un ciclo de vida `draft -> active -> retired`.
- FR-025: El sistema debe impedir que productos o workflows en estado distinto de `active` sean usados para evaluaciones operativas.
- FR-026: El sistema debe conservar trazabilidad de quien creo, activo, retiro o modifico productos y workflows.
- FR-027: El sistema debe permitir definir variables a nivel de producto para que puedan ser reutilizadas por multiples workflows del mismo producto.
- FR-028: Cada workflow debe poder seleccionar cuales variables de su producto utiliza en sus reglas y evaluaciones.
- FR-029: Cada variable de producto debe definir su origen permitido de datos entre base de campana, captura por interfaz o ambas opciones.
- FR-030: El sistema debe validar que una evaluacion solo use valores de variables provenientes de los origenes permitidos para cada variable.
- FR-031: El sistema debe permitir crear multiples reglas dentro de cada workflow para expresar politicas y logica de decision.
- FR-032: Cada regla administrable debe seguir un ciclo de vida `draft -> active -> retired`.
- FR-033: El sistema debe impedir que reglas en estado distinto de `active` participen en evaluaciones operativas.
- FR-034: El sistema debe conservar trazabilidad de quien creo, activo, retiro o modifico reglas dentro de cada workflow.
- FR-035: El sistema no debe permitir la edicion directa de un workflow en estado `active`; cualquier cambio debe generar una nueva version gobernada y auditable.
- FR-036: El sistema debe permitir publicar catalogos versionados de variables por producto y asignarlos a versiones de workflow.
- FR-037: El sistema debe validar, antes de activar una configuracion del motor, que sus referencias a variables, reglas, pipeline y workflow sean consistentes y completas.
- FR-037A: El sistema debe permitir administrar parametros versionados por producto y workflow bajo un ciclo de vida gobernado y auditable.
- FR-037B: El sistema debe persistir en cada evaluacion las versiones efectivas de workflow, catalogo de variables, reglas, parametros y pipeline realmente aplicadas.
- FR-037C: El sistema debe permitir administrar estrategias de pipeline y sus nodos bajo versionado, validacion topologica y activacion gobernada.

### Security and Operations

- FR-038: El sistema debe aplicar autenticacion y autorizacion basadas en roles para proteger consultas, evaluaciones, solicitudes, adjuntos y funciones administrativas.
- FR-039: El sistema debe ofrecer autenticacion operativa de frontend, restauracion de sesion y acceso por rol suficientes para ejecutar los flujos del MVP, sin impedir una futura integracion con un proveedor corporativo.
- FR-040: El sistema debe desacoplar el control de acceso de restricciones basadas unicamente en IP o de acoplamientos con la interfaz.
- FR-041: El sistema debe iniciar con base limpia, sin depender de migracion historica desde el sistema legado para operar el MVP.
- FR-042: El sistema debe registrar cada interaccion AI asociada al caso con modelo, version de template, payload permitido (subconjunto de datos anonimizados o no sensibles de la evaluacion o solicitud conforme a la politica de seguridad de datos), respuesta, estado de fallback y referencias a las versiones del motor utilizadas.

## Key Entities

- Cliente: persona consultada para iniciar una evaluacion y recuperar datos relevantes de contexto.
- Oferta: propuesta disponible para un cliente que puede ser seleccionada y recalculada durante la evaluacion.
- Evaluacion: resultado deterministico generado para una oferta a partir de datos del cliente y datos complementarios capturados.
- Traza de decision: registro estructurado de entradas relevantes, reglas aplicadas, eventos, alertas, bloqueos y salida final de una evaluacion.
- Solicitud de credito: caso operativo registrado a partir de una evaluacion valida, con estado y seguimiento propio.
- Estado de solicitud: etapa operativa vigente de una solicitud junto con su historial de cambios.
- Adjunto ZIP: archivo asociado a una solicitud como evidencia operativa.
- Usuario operativo: actor con permisos segun rol para consultar, evaluar, registrar y administrar solicitudes.
- Regla o parametro versionado: definicion gobernada que influye en la evaluacion o en el comportamiento del flujo y cuya version debe poder auditarse.
- Producto de prestamo: configuracion de negocio que agrupa reglas, variaciones de flujo y datos propios de un tipo de prestamo.
- Workflow de producto: modalidad de evaluacion asociada a un producto que define reglas activas y comportamiento operativo dentro de un ciclo de vida administrable.
- Version de workflow: revision gobernada de un workflow que permite introducir cambios sin alterar una configuracion ya activa.
- Variable de producto: dimension administrable definida para un producto y reutilizable por uno o varios workflows para construir reglas y evaluaciones.
- Catalogo de variables: version publicable del conjunto de variables activas de un producto consumible por una version de workflow.
- Origen de variable: restriccion declarada que define si una variable puede recibir datos desde base de campana, captura por interfaz o ambas fuentes.
- Regla de workflow: condicion o logica de decision administrable asociada a un workflow y gobernada por un ciclo de vida auditable.
- Parametro versionado: conjunto administrable de constantes o umbrales usados por el motor y publicado bajo una version auditable.
- Estrategia de pipeline: definicion administrable y versionada de la secuencia de nodos y branching permitido para un workflow.
- Nodo de pipeline: etapa versionada del flujo de evaluacion con referencias validadas dentro de una estrategia gobernada.
- Interaccion AI: registro auditable de una asistencia AI emitida para una evaluacion o solicitud con referencias de modelo, template, payload permitido (subconjunto filtrado de datos no identificables) y fallback.

## Assumptions

- El MVP funcional inicial cubre el flujo `PLD / solicitudes de credito` completo, mientras la base del sistema queda preparada para un segundo producto en una fase cercana.
- Los roles operativos principales incluyen al menos perfiles equivalentes a analista, supervisor y administrador con permisos diferenciados.
- La autenticacion del MVP usa el mecanismo operativo disponible en la plataforma actual y cubre login, restauracion de sesion y autorizacion por rol para los flujos definidos, sin bloquear una futura migracion a un proveedor corporativo.
- Los equipos de negocio y riesgos administran productos y workflows dentro de un esquema gobernado, sin depender de TI para el alta, activacion o retiro como operacion habitual.
- Las variables del motor se administran en el nivel de producto y cada workflow reutiliza solo las variables que requiere.
- Cada variable declara de forma explicita si sus datos pueden provenir de base de campana, de captura por interfaz o de ambas fuentes.
- Las reglas del motor se administran dentro de cada workflow y solo las reglas activas participan en evaluaciones operativas.
- Un workflow activo se considera inmutable para fines operativos; cualquier ajuste posterior se publica como una nueva version.
- La fuente de verdad del producto en el MVP es un unico registro persistido de producto administrable reutilizado tanto por runtime como por solicitudes de credito.
- La bandeja operativa se consulta por periodos y expone solo las acciones permitidas para el rol y estado vigentes.
- Los adjuntos admitidos para el MVP se limitan a archivos ZIP asociados a una solicitud.
- La asistencia AI consume solo informacion permitida del caso y se utiliza como apoyo explicativo, no como autoridad de decision.
- El legado sirve como referencia funcional, pero no impone dependencias de interfaz, autenticacion por IP ni estructura interna del nuevo sistema.

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
