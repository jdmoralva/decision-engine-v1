# Notas

Este archivo sirve como ayuda memoria para el desarrollador.
Ignorar su contenido.

spec-kit
[https://github.github.com/spec-kit/quickstart.html]


## Conf

Si quieres volver a registrar PLD por configuración
En .env podrías poner:
DECISION_ENGINE_RUNTIME_BUILDERS=backend.app.products.pld.runtime:compile_pld_runtime

## Last Session

specs/002-credit-decision-workspace/sessions/session-010.md

## Updates

Debe existir un módulo de administración de productos al que podrán acceder los roles de Administrador, Administrador de Negocio y Administrador de Riesgos. En este módulo se puede observar los productos activos y el detalle de cada producto, como la fecha de creación, última modificación, usuario creador, usuario aprobador y workflows activos. Tambien se debe poder ingresar al detalle de cada workflow para observar sus datos de creación, aprobación, pipeline, variables, parámetros y reglas. Debe existir una opción para cambiar la vista a los productos, workflows y demás configuraciones en estado draft. Los productos, workflows y demás configuraciones eliminadas o retiradas no deben ser visubles, pero deben persistir en base de datos para auditoria. 

Precisiones para las FR-012 y FR-013:

Al ingresar al servicio de "Motor de Decisiones" debe mostrarse en el sidebar las siguientes opciones: Reglas de Negocio, Parámetros, Data. 

La sección Reglas de negocio debe mostrar los elementos: channels, workflows, testing, events.

La sección parámetros debe mostrar los elementos: límites internos, límites gobales, niveles de autonomía.

La sección Data debe mostrar los elementos: Importar dataset, Configurar relaciones, Crear catálogo, Administrar catálogos.

Precisiones para FR-014:

La parte inferior del sidebar debe mostrar el botón de acceso a los datos del perfil del usuario, donde podrá realizar acciones básicas de configuración como cambiar contraseña, consultar permisos aprobados y cerrar sesión.


Precisiones sobre la sección Reglas de negocio:

El elemento "channels" debe mostrar como opciones: create channel, active channels, draft channels. Los channels corresponden a distintos modos de evalaución creados para el producto (por ejemplo "Evaluación Regular", "Fast Track", etc). Su función es configurar el workflow correspondiente al modo de evaluación elegido (channel).

El elemento "workflows" debe mostrar como opciones: create workflow, active workflows y draft workflows. Al hacer click en active workflows se mostrarán los objetos creados bajo esta clase que se encuentran activos (similar para draft workflows), y al hacer click en uno de estos objetos, debe mostrarse el diagrama del workflow en el canva central y permitir su edición. Un workflow puede utilizar un sub-workflow como nodo dentro de su proceso de ejecución.

El elemento "testing" debe mostrar como opciones: create test, stored tests. Su función es realizar análisis AB testing para evaluar el impacto de un cambio en la configuración del workflow (challeger) vs el workflow activo (champion). El impacto se mide en la cantidad de clientes que superan las reglas del workflow. Para esto se debe seleccionar un periodo de consultas realizadas al motor (events).

El elemento "events" debe mostrar una tabla con las últimas 50 consultas al motor de decisiones, inclyendo los campos configurados para la vista. Debe permitir también el filtrado de periodos de consulta y cliente.

Saneamiento:

La implementación actual de algunas características utilizan la nomenclatura "pipeline", debe cambiarse esto por "channel" para guardar consistencia con estas especificaciones.

Creación/edición de workflows:

La edición del workflow se realiza mediante "drag and drop" de nodos y la creación de conexiones (edges) entre nodos en el Canvas o lienzo de edición central. 

El Canvas Visual debe permitir:

- crear workflows simples
- agregar nodos desde un panel lateral derecho (drag and drop)
- nodos disponibles ingesta, analisis, decision y salida
- configurar parametros de ingreso y salida de datos por nodo
- configurar reglas de negocio por nodo
- conectar nodos compatibles
- manejo de errores por nodo
- ejecutar el workflow
- visualizar estado por nodo
- registrar ejecuciones y resultados
- guardar el workflow
- mantener versionado del workflow 

Aprobación de workflows y creación de channels

La creación de un channel debe considerar el nombre del tipo de evaluación, ("Evaluación Regular", "Fast Track"), un paquete de parámetros o límites aprobados (ratio cuota ingreso, ratio deuda ingreso, plazo y monto a financiar máximos, etc.) y el workflow (ID) que se utilizará en la evaluación. Solo podrán usarse workflows aprobados y cada channel deberá tener solo un workflow posible.

Todo workflow nuevo se guarda con estado draft hasta que el usuario Administrador de Riesgos lo apruebe y cambie su estado a aprobado. Debe mantenerse la matriz RBAC configurada en la implementación actual.

Precisiones para FR-013A

La sección `Parámetros` debe mostrar los elementos `límites internos`, `límites globales` y `niveles de autonomía`. La creación y edición de estos parámetros solo podrán realizarse por el Administrador de Riesgos. Cada uno de estos elementos podrá crear reglas en base a las variables y medidas disponibles, incluyendo: ratio cuota ingreso interno, ratio deuda ingreso, plazo máximo, monto a financiar.

Precisiones para FR-013B

La sección `Data` debe mostrar los elementos `Importar dataset`, `Configurar relaciones`, `Administrar medidas` y `Administrar catálogos`. Las opciones de `Administrar medidas` y `Administrar catálogos` permiten la creación/eliminación de objetos (medida y catálogo). La opción de `Administrar medidas` permite la creación de nuevas variables a partir de los datasets importados y las variables que el usuario digita en la plataforma.



