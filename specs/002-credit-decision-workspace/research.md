# Research - Plataforma Visual de Decisión de Crédito

## Decision 1: Mantener la feature como workspace frontend-first con integración backend selectiva

- Decision: Implementar la nueva plataforma visual principalmente en `frontend/`, reutilizando solo autenticación, restauración de sesión y lecturas administrativas del backend cuando ya existen contratos reales.
- Rationale: El repo ya tiene `POST /api/v1/auth/login`, `GET /api/v1/me` y varios endpoints admin protegidos, pero no tiene contratos públicos o persistidos para catálogo de servicios, `channels`, canvas, AB testing ni eventos de producto con la forma pedida por la spec.
- Alternatives considered:
  - Forzar toda la experiencia sobre endpoints admin existentes: descartado porque mezclaría módulo admin con catálogo visible general y expondría semánticas que no encajan con la UX solicitada.
  - Esperar a tener todo el backend antes de diseñar el frontend: descartado porque la spec pide una plataforma visual y el alcance actual admite prototipo de sesión.

## Decision 2: Modelar la navegación con rutas explícitas de login, productos, servicios y workspace

- Decision: Separar el frontend en un shell con rutas claras para `login`, `productos`, `servicios` y `workspace`, en lugar de seguir ampliando `App.tsx` como un flujo lineal hash-based manual.
- Rationale: La spec agrega múltiples superficies y estados de navegación. Mantener todo en un único componente principal escalaría mal y volvería más frágiles las guardas de sesión y RBAC.
- Alternatives considered:
  - Continuar con parsing manual del hash en `App.tsx`: descartado por baja mantenibilidad al crecer la navegación.
  - Introducir un router y un store global pesados desde el inicio: descartado por exceso de complejidad para el alcance actual.

## Decision 3: Derivar la visibilidad de servicios desde roles autenticados, no desde producto

- Decision: Construir una matriz de visibilidad por rol usando `/me.roles`, aplicada igual a todos los productos.
- Rationale: La spec aclara que la visibilidad es global por rol y coincide con la realidad del backend, donde el acceso a `/admin/engine/*` está limitado a `admin`, `admin_negocio` y `admin_riesgos`.
- Alternatives considered:
  - Visibilidad distinta por producto: descartado por contradecir una aclaración explícita.
  - Resolver permisos consultando perfiles desde frontend para todos los usuarios: descartado porque `GET /profiles/{roleCode}/permissions` es un endpoint privilegiado, no de autoservicio.

## Decision 4: Persistir el borrador editable del canvas en `sessionStorage`

- Decision: Guardar el estado del workspace visual por sesión y por `productCode`/`workflowId` en `sessionStorage`.
- Rationale: La spec exige mantener edición dentro de la sesión, pero no requiere persistencia backend real en esta fase. `sessionStorage` reduce pérdida accidental durante navegación o recarga sin simular publicación persistida.
- Alternatives considered:
  - Solo estado en memoria React: descartado porque se perdería al refrescar la pestaña.
  - `localStorage`: descartado porque extiende vida útil más allá de la sesión declarada.
  - Persistencia backend ad hoc: descartado por falta de contrato real y riesgo de falsear gobierno/versionado.

## Decision 5: Mantener `channel` como término visible y desacoplarlo de `pipeline`

- Decision: La UI mostrará exclusivamente `channel`; cualquier integración futura con `pipeline-strategies` debe pasar por adaptadores internos.
- Rationale: La spec aclara que `pipeline` es término no canónico y no debe quedar visible. El backend actual aún usa `pipeline`, por lo que el desacople debe ser explícito en la capa de UI.
- Alternatives considered:
  - Mostrar `pipeline` por consistencia con backend: descartado por contradecir la nomenclatura aprobada.
  - Renombrar backend existente durante esta fase: descartado porque la feature actual es principalmente frontend y de planificación.

## Decision 6: Distinguir artefactos gobernados reales de prototipos locales de sesión

- Decision: Workflows, productos, variables, parámetros y perfiles seguirán las fuentes reales del backend cuando se lean o administren; `channels`, pruebas AB, eventos del servicio y partes del modelado de datos se tratarán como prototipo local o mock hasta contar con endpoints específicos.
- Rationale: La constitución exige no inventar gobierno/versionado ni presentar como persistido algo que no tiene soporte contractual. Esta separación mantiene honestidad operativa.
- Alternatives considered:
  - Presentar todos los submódulos como persistidos: descartado por riesgo de regresión conceptual y de expectativas falsas.
  - Limitar la UI solo a lo ya soportado por backend: descartado porque dejaría fuera el objetivo principal del workspace visual.

## Decision 7: Validar la feature con pruebas de sesión, RBAC, rutas y edición local del canvas

- Decision: Cubrir la nueva experiencia con pruebas frontend en `Vitest` centradas en login/restauración, guardas de ruta, visibilidad por rol, selección de nodos y persistencia de sesión del canvas, más `npm run build` como verificación estructural.
- Rationale: La mayor parte del riesgo está en composición de UI y adaptación de contratos, no en lógica backend nueva. La toolchain actual ya soporta esa validación.
- Alternatives considered:
  - Depender solo de pruebas manuales: descartado por riesgo de regresiones en navegación y RBAC.
  - Añadir una infraestructura E2E pesada en esta fase: descartado porque la base actual ya tiene `vitest` y el alcance puede cubrirse con integración DOM + mocks.
