# UI Navigation Contract

## Scope

Contrato de interacción visible para la plataforma visual en frontend.

## Route Contract

| Route | Auth Required | Purpose |
|---|---|---|
| `#/login` | No | Mostrar inicio de sesión obligatorio |
| `#/productos` | Sí | Mostrar catálogo de productos visibles |
| `#/productos/:productCode/servicios` | Sí | Mostrar servicios visibles del producto |
| `#/productos/:productCode/servicios/:serviceKey` | Sí | Abrir espacio principal del servicio |
| `#/productos/:productCode/servicios/decision-engine/:section/:item?` | Sí | Abrir un submódulo del workspace de Motor de decisiones |

## Product Contract

- La vista `Productos` muestra el título `Productos` y la acción principal `Crear producto`.
- La grilla inicial contiene `PLD` y `Hipotecario`.
- Cada tarjeta expone:
  - nombre del producto
  - indicador visual de entorno
  - accesos rápidos a servicios, configuración, validación y despliegue
  - menú contextual con `Renombrar`, `Duplicar`, `Exportar` y `Eliminar` (placeholders in this phase)

## Service Visibility Contract

| Roles | Servicios visibles |
|---|---|
| `analista`, `evaluador` | `Bandeja de solicitudes` |
| `admin`, `admin_negocio`, `admin_riesgos` | `Bandeja de solicitudes`, `Motor de decisiones`, `Modelo de datos` |

Reglas:

- la visibilidad es global por rol y no varía por producto
- la UI siempre muestra nombres en español
- la vista de servicios es de consulta y apertura, no de creación

## Decision Workspace Contract

Al abrir `Motor de decisiones`, la pantalla debe renderizar:

- breadcrumb del producto/servicio
- sidebar principal con `Reglas de Negocio`, `Parámetros` y `Data`
- explorador/listado contextual según sección
- tabs superiores del workspace
- canvas central
- panel derecho de configuración
- controles flotantes de zoom, paneo y reencuadre
- acceso al perfil de usuario en la parte inferior del sidebar

### Sidebar Detail

`Reglas de Negocio`:

- `channels`
- `workflows`
- `testing`
- `events`

`channels`:

- `create channel`
- `active channels`
- `draft channels`

`workflows`:

- `create workflow`
- `approved workflows` (workflows con estado backend `active`, visibles en UI como `Aprobado`)
- `draft workflows`

`testing`:

- `create test`
- `stored tests`

`Parámetros`:

- `límites internos`
- `límites globales`
- `niveles de autonomía`

`Data`:

- `Importar dataset`
- `Configurar relaciones`
- `Administrar medidas`
- `Administrar catálogos`

## Canvas Contract

- El canvas carga un flujo de ejemplo de originación de crédito.
- El flujo incluye nodos de:
  - inicio
  - obtención de datos del cliente
  - validación de identidad
  - verificación de score
  - revisión de deuda
  - cálculo de ratio deuda-ingreso
  - evaluación de riesgo
  - aplicación de política
  - cálculo de oferta
  - aprobación
  - rechazo
  - revisión manual
  - fin
- Las conexiones soportan etiquetas `continuar`, `aprobado`, `rechazado`, `revisión manual`, `sí`, `no` y `error`.
- El usuario puede:
  - seleccionar un nodo
  - mover un nodo
  - agregar un nodo
  - eliminar un nodo
  - crear conexiones compatibles
  - acercar, alejar, desplazar y reencuadrar la vista

## Inspector Contract

Cuando hay nodo seleccionado, el panel derecho muestra:

- nombre
- tipo
- descripción
- variables de entrada
- variables de salida
- lógica de decisión
- manejo de errores
- modo de ejecución

Para nodos de decisión o regla también muestra:

- expresión o condición
- ruta verdadera
- ruta falsa
- ruta alternativa

Cuando no hay selección, el panel muestra un estado vacío coherente.

## Session Contract

- la sesión autenticada se restaura al recargar si el token sigue siendo válido
- el borrador visual del workflow se conserva solo durante la sesión del navegador
- el borrador visual de sesión no reemplaza el versionado gobernado del backend
- las acciones de perfil `cambiar contraseña` y `consultar permisos aprobados` funcionan como interacciones locales o mock en esta fase
- cerrar sesión limpia el token y el estado local sensible
