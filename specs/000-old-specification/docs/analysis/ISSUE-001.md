# ISSUE-001 - Cerrar alcance funcional del MVP

## 1. Objetivo

Cerrar el alcance real del MVP PLD, consolidando el flujo actual, las reglas observadas, las decisiones abiertas, el gobierno del flujo configurable y la separacion entre capacidades propias de PLD y capacidades compartidas de plataforma.

## 2. Fuentes revisadas

- `old-version/api-build.R`
- `old-version/script.js`
- `old-version/index.html`
- `old-version/bandeja.html`
- `old-version/README.md`
- `docs/SPEC.md`
- `docs/project/BACKLOG.md`
- `docs/project/ISSUES.md`
- `docs/project/SPRINTS.md`

## 3. Flujo AS-IS del legacy

### 3.1 Acceso inicial

- `GET /PLD` sirve `index.html`.
- El frontend llama a `/User` para identificar al usuario autenticado por IP.

### 3.2 Consulta de cliente

- El usuario ingresa tipo y numero de documento.
- El frontend envia `POST /get_tn`.
- El backend consulta `CampaniaPLD` y devuelve datos del cliente y campañas PLD.
- La consulta queda guardada en `BaseConsultasTN`.

### 3.3 Validacion inicial

- El usuario selecciona una campaña y ejecuta la primera validacion.
- El frontend envia `POST /validate1`.
- El backend recupera datos complementarios desde `CampaniaPLD` y devuelve campos para completar la evaluacion.

### 3.4 Recalculo y evaluacion

- El usuario completa situacion laboral, deuda e ingreso.
- El frontend envia `POST /validate2`.
- El backend recalcula oferta, cuota, tasa, plazo y RCI usando `CampaniaPLD` y `ParametrosPLD-v3.xlsx`.
- La evaluacion se persiste en `BaseValidacion`.

### 3.5 Registro de solicitud

- El usuario ingresa monto solicitado y comentario.
- El frontend envia `POST /grabasol`.
- El backend valida reglas de negocio y persiste en `BaseSolicitudesTN`.

### 3.6 Bandeja de solicitudes

- El usuario consulta por periodo.
- El frontend envia `POST /bandejasol`.
- El backend devuelve la lista operativa del periodo con acciones de anular y cambiar estado.

### 3.7 Anulacion y cambio de estado

- Anulacion: `POST /anulasol`.
- Cambio de estado: `POST /updatesol`.

### 3.8 Adjuntos ZIP

- Carga: `POST /upload_file`.
- Descarga: `GET /download_file`.

## 4. Reglas de negocio observadas

### 4.1 Consulta

- El documento se considera valido para consulta cuando, al limpiar caracteres no numericos, tiene 8 digitos.
- `TIPODOC` se traduce a entero para la consulta a base de datos.

### 4.2 Recalculo

- `FLG_SUNEDU` se deriva por prefijo de `AGR_SITLAB_SUN`.
- `tea_pld_48` depende del perfil: 1 -> 30%, 2 -> 35%, otro -> 40%.
- `rng_ingreso` se calcula por bandas de ingreso.
- `marca_cliente_cm` distingue cliente y no cliente.
- `pef_pld` usa deuda si existe, o gasto si no, dividido entre ingreso.
- `oferta_pld` se calcula combinando ofertas parciales y tope de garita, con redondeo y piso en cero.

### 4.3 Registro

- Solo una solicitud por mes y documento.
- Rechazo si la fuente de ingresos es `INFORMAL`.
- Rechazo si `Ingreso < 2000`.
- Rechazo si `RCI > 50%`.
- Rechazo si la oferta es menor a `3000`.
- Rechazo si el monto solicitado supera la oferta.
- Rechazo si el comentario está vacío.

### 4.4 Bandeja y estado

- La bandeja filtra por periodo y `Registro = 1`.
- La anulación actúa sobre solicitudes activas del periodo.
- El cambio de estado expone `Enviada`, `Aprobada`, `Observada` y `Rechazada`.

## 5. Roles observados

- `analista`: consulta, evaluación y registro.
- `evaluador`: cambio de estado en bandeja.
- `admin`: pendiente de formalización en el nuevo sistema.

## 6. Inputs externos y dependencias

- `old-version/API_DB.db`.
- `old-version/ParametrosPLD-v3.xlsx`.
- `ip_authorized.txt`.
- `ip_evaluator.txt`.
- `ip_logs.txt`.
- `data/zip/`.

## 7. Problemas de acoplamiento UI-backend

- El backend devuelve HTML dentro de respuestas JSON.
- El frontend depende de posiciones fijas de columnas para reconstruir payloads.
- La lógica de acciones depende de IDs dinámicos y del momento de inyeccion del DOM.
- La estructura de la UI condiciona los contratos de negocio.

## 8. Decisiones abiertas

- Stack final de frontend según despliegue.
- Mecanismo de autenticacion inicial.
- Fuente oficial de reglas ante discrepancias.
- Gobierno del flujo configurable.
- Snapshot mínimo por evaluacion.
- Politica de datos AI.
- Alcance exacto de ZIP dentro del MVP.

## 9. Separacion de plataforma

### 9.1 Exclusivo PLD

- Consulta.
- Evaluacion.
- Registro de solicitud.
- Bandeja.
- Anulacion.
- Cambio de estado.

### 9.2 Compartido de plataforma

- Autenticacion.
- Auditoria.
- Trazabilidad.
- Motor de decisiones.
- Pipeline.
- Persistencia versionada.
- AI asistiva.

## 10. Criterio de cierre

Se considera cerrado `ISSUE-001` cuando exista:

- mapa completo del flujo PLD.
- catalogo de reglas con condicion, entrada, salida y efecto.
- definicion de roles operativos y reglas de aprobacion/rechazo.
- decision de fuente oficial de reglas.
- definicion clara de capacidades exclusivas de PLD y capacidades compartidas.
- criterio operativo para continuar con contratos y bootstrap sin depender de mas exploracion del legacy.

## 11. Notas de referencia

- Este documento describe el comportamiento observado del legacy y las decisiones necesarias para el nuevo sistema.
- No define implementacion nueva.
- Las discrepancias entre fuentes deben resolverse segun `docs/SPEC.md` y las decisiones funcionales cerradas del proyecto.

## 12. Cierre formal

`ISSUE-001` queda cerrado como analisis funcional del legacy y base de alcance del MVP.

Queda consolidado:

- el flujo PLD extremo a extremo.
- el catalogo de reglas observadas.
- la separacion entre capacidades exclusivas de PLD y capacidades compartidas de plataforma.
- el inventario de inputs externos y dependencias.
- el inventario de acoplamientos UI-backend que deben eliminarse en la nueva implementacion.

Con este cierre, el equipo puede avanzar a `ISSUE-002`, `ISSUE-005`, `ISSUE-004` y `ISSUE-006` sin depender de mas exploracion del flujo general del legacy.
