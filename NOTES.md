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

specs/001-project-specification/sessions/session-007.md

## Updates

Debe existir un módulo de administración de productos al que podrán acceder los roles de Administrador, Administrador de Negocio y Administrador de Riesgos. En este módulo se puede observar los productos activos y el detalle de cada producto, como la fecha de creación, última modificación, usuario creador, usuario aprobador y workflows activos. Tambien se debe poder ingresar al detalle de cada workflow para observar sus datos de creación, aprobación, pipeline, variables, parámetros y reglas. Debe existir una opción para cambiar la vista a los productos, workflows y demás configuraciones en estado draft. Los productos, workflows y demás configuraciones eliminadas o retiradas no deben ser visubles, pero deben persistir en base de datos para auditoria. 





