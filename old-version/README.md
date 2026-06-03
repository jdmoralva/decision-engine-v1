# Decision Engine

## Objetivo General

Desarrollar una aplicacion web interna para la gestion operativa de solicitudes de credito y campanas asociadas, usando una arquitectura ligera basada en frontend HTML/JavaScript y una capa de servicios REST implementada en R mediante Plumber.

La version levantada del sistema muestra que la solucion no solo cubre un flujo generico de consultas y registro, sino dos dominios funcionales claramente diferenciados:

- Tramite Normal / PLD
- Cobranzas / Aplicacion de campanas

La plataforma esta orientada a usuarios dentro de una red corporativa y permite consultar informacion de clientes, evaluar ofertas, registrar solicitudes, administrar bandejas operativas, cargar y descargar archivos, y mantener trazabilidad basica de uso.

---

## Arquitectura General

La solucion implementada en la carpeta `old-version` responde a una arquitectura monolitica ligera compuesta por tres capas principales.

## 1. Capa de Presentacion

### Tecnologias

- HTML5
- CSS3
- JavaScript
- jQuery

### Implementacion observada

El frontend esta compuesto por paginas HTML estaticas servidas por la propia API:

- `index.html`: consulta y evaluacion de Tramite Normal / PLD
- `bandeja.html`: bandeja de solicitudes TN
- `solicitud.html`: consulta de campanas de cobranzas
- `bandeja1.html`: bandeja de solicitudes de cobranzas
- `styles.css`: estilos globales
- `script.js`: logica completa de interaccion y consumo AJAX

### Caracteristicas principales

- Navegacion multipagina con menu lateral persistente
- Cabecera fija con branding institucional
- Formularios para consulta de clientes y captura de datos
- Tablas HTML generadas dinamicamente desde respuestas JSON
- Acciones embebidas en tablas como evaluar, enviar, anular y actualizar
- Exportacion de bandeja a CSV desde el navegador
- Carga y descarga de archivos ZIP
- Validaciones basicas en cliente

---

## 2. Capa de Servicios

### Tecnologias

- R
- Plumber

### Implementacion observada

La API principal identificada es `old-version/api-build.R`, que cumple doble funcion:

- Servir paginas HTML y recursos estaticos
- Exponer endpoints REST para consultas, validaciones, registro y mantenimiento operativo

Tambien existen archivos auxiliares o de prueba:

- `api-build-v2.R`
- `api-build-v3.R`
- `api-debug.R`

La implementacion funcional mas completa corresponde a `api-build.R`.

### Endpoints y recursos principales

#### Recursos frontend

- `GET /PLD`
- `GET /Campanias`
- `GET /Bandeja`
- `GET /Aplicacion`
- `GET /css`
- `GET /js`
- `GET /User`

#### Tramite Normal / PLD

- `POST /get_tn`
- `POST /validate1`
- `POST /validate2`
- `POST /grabasol`
- `POST /bandejasol`
- `POST /anulasol`
- `POST /updatesol`

#### Gestion documental

- `POST /upload_file`
- `GET /download_file`

#### Cobranzas

- `POST /get_data`
- `POST /envio_sol1`
- `POST /envio_sol2`
- `POST /envio_sol3`
- `POST /bandeja_sol1`
- `POST /bandeja_sol2`

---

## 3. Capa de Datos

La solucion usa una capa de datos hibrida basada en archivos locales y SQLite.

### Fuentes identificadas

- Base SQLite: `API_DB.db`
- Parametros de negocio en Excel: `ParametrosPLD-v3.xlsx`
- Archivos de control por IP:
  - `ip_authorized.txt`
  - `ip_evaluator.txt`
- Logs locales:
  - `ip_logs.txt`
- Repositorio de archivos ZIP:
  - `data/zip/`

### Tablas identificadas en SQLite

- `CampaniaPLD`
- `BaseValidacion`
- `BaseSolicitudesTN`
- `BaseConsultasTN`
- `BaseClientes`
- `BaseRCC`
- `BaseOferta`
- `BaseSolicitudes`
- `BaseConsultas`

---

## Modelo de Comunicacion

La comunicacion entre frontend y backend se realiza mediante llamadas AJAX sobre HTTP hacia la API Plumber.

### Consultas

#### HTTP GET

Utilizadas para:

- Servir paginas y recursos estaticos
- Recuperar datos del usuario autenticado por IP
- Descargar archivos

### Transacciones

#### HTTP POST

Utilizadas para:

- Consultar datos de clientes
- Recalcular oferta y validaciones
- Registrar solicitudes
- Consultar bandejas
- Actualizar estados
- Anular registros
- Cargar archivos
- Ejecutar procesos de campanas

### Formato de intercambio

#### JSON

Utilizado para:

- Parametros de entrada
- Respuestas de negocio
- Resultados tabulares
- Mensajes operativos y de error

#### Multipart form-data

Utilizado para:

- Carga de archivos ZIP

---

## Funcionalidades Implementadas

## 1. Tramite Normal / PLD

### Consulta de cliente y campanas

Permite:

- Consultar cliente por tipo y numero de documento
- Obtener datos generales del cliente
- Mostrar indicadores financieros relevantes
- Visualizar campanas y ofertas disponibles

### Validacion y recalculo de oferta

Permite:

- Capturar situacion laboral
- Registrar ingreso validado
- Registrar deuda o carga financiera
- Recalcular oferta
- Recalcular cuota, tasa, plazo y RCI
- Aplicar reglas de negocio apoyadas en tablas de parametros Excel
- Guardar la evaluacion en base de datos

### Registro de solicitud

Permite:

- Registrar solicitud a partir de la oferta evaluada
- Validar restricciones de negocio antes del grabado

Controles observados:

- Una solicitud por periodo
- Ingreso minimo
- RCI maximo
- Oferta minima
- Monto solicitado no mayor a la oferta
- Comentario obligatorio
- Restriccion por fuente de ingresos informal

### Bandeja de solicitudes TN

Permite:

- Consultar solicitudes por periodo
- Exportar resultados a CSV
- Anular solicitudes
- Actualizar estado de la solicitud

Estados observados:

- Enviada
- Aprobada
- Observada
- Rechazada

---

## 2. Cobranzas / Aplicacion de campanas

### Consulta de cliente

Permite:

- Consultar cliente por documento
- Recuperar datos de credito
- Recuperar datos RCC
- Mostrar campanas de cobranza disponibles

### Envio de solicitud de campana

Permite:

- Seleccionar campana
- Visualizar resumen de solicitud
- Registrar solicitud en base de datos
- Restringir una solicitud por periodo

### Bandeja de solicitudes de cobranzas

Permite:

- Consultar solicitudes por cliente
- Anular solicitudes activas

---

## 3. Gestion documental

Permite:

- Cargar archivos ZIP
- Descargar archivos almacenados
- Validar extension desde frontend
- Validar tamano maximo desde frontend
- Guardar fisicamente el archivo en el proyecto

---

## Seguridad y Control Operativo

## Implementado en la version levantada

### Autenticacion basada en IP

El acceso se valida contra una lista local de IPs autorizadas.

### Autorizacion operativa por IP

Existe una segunda lista de IPs evaluadoras con permisos para ciertas acciones, como actualizacion de estados.

### Trazabilidad basica

Cada solicitud registra actividad en archivo de log local y en tablas operativas de base de datos.

### Control de frecuencia

Se observa una limitacion rudimentaria por volumen de solicitudes recientes desde la misma IP.

### Validaciones de entrada

Se aplican validaciones sobre:

- Documento ingresado
- Formularios
- Reglas de negocio
- Archivos cargados

## Limitaciones observadas

- No se identifico autenticacion corporativa formal
- No se observo uso de HTTPS en la implementacion local
- Parte de la validacion esta distribuida entre frontend y backend
- El control de acceso depende de IP y archivos locales
- Existe fuerte acoplamiento entre tablas HTML, JavaScript y estructura de datos

---

## Despliegue

La implementacion observada se ejecuta como una aplicacion ligera servida directamente por Plumber.

### Caracteristicas

- Servidor R
- API Plumber
- Puerto `8080`
- Acceso via navegador
- Recursos estaticos servidos por la misma API
- Almacenamiento local de archivos y logs

---

## Estructura de la Version Antigua

La carpeta `old-version` contiene el prototipo funcional levantado:

- `api-build.R`: API principal
- `api-build-v2.R`, `api-build-v3.R`, `api-debug.R`: variantes o pruebas
- `index.html`, `solicitud.html`, `bandeja.html`, `bandeja1.html`: vistas
- `script.js`: logica frontend
- `styles.css`: estilos
- `API_DB.db`: base SQLite
- `ParametrosPLD-v3.xlsx`: parametros de negocio
- `data/`: archivos auxiliares y repositorio de carga
- `ip_authorized.txt`, `ip_evaluator.txt`, `ip_logs.txt`: control operativo

---

## Resultado del Levantamiento

La version antigua corresponde a un portal interno monolitico que centraliza:

- Consulta de clientes
- Evaluacion de oferta PLD
- Registro de solicitudes de credito
- Gestion de bandejas operativas
- Aplicacion de campanas de cobranzas
- Gestion documental basica
- Interaccion con datos locales y reglas de negocio parametrizadas

El sistema fue construido con una arquitectura pragmatica y ligera, adecuada para despliegue interno rapido, pero con alto acoplamiento entre interfaz, logica de negocio y almacenamiento.
