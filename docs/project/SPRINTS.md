# SPRINTS - Decision Engine

## Proposito

Este archivo organiza `ISSUES.md` en una secuencia de sprints sugerida para ejecutar el MVP del nuevo sistema, cuyo primer producto soportado es `PLD`, sobre una base tecnica ya orientada a multiples productos.

## Supuestos

- duracion sugerida por sprint: 2 semanas
- equipo tecnico minimo: 1 backend, 1 frontend, 1 apoyo funcional/QA compartido
- algunos issues pueden ejecutarse en paralelo si sus dependencias lo permiten

## Estado sugerido de cada sprint

- `planned`
- `active`
- `done`

---

## Sprint 1 - Descubrimiento y cierre de contratos base

- Estado: `done`
- Objetivo: cerrar alcance, contratos base, gobierno del flujo configurable, decision de frontend por despliegue y politicas de datos AI

### Issues comprometidos

- `ISSUE-001` Cerrar alcance funcional del MVP
- `ISSUE-002` Definir contratos iniciales del dominio y API
- `ISSUE-003` Bootstrap del repositorio y estructura base
- `ISSUE-004` Inicializar backend con FastAPI
- `ISSUE-005` Seleccionar e inicializar frontend web segun estrategia de despliegue
- `ISSUE-006` Diseñar modelo de datos inicial
- `ISSUE-027` Definir contratos de inputs externos y snapshot minimo
- `ISSUE-028` Formalizar fuente oficial de reglas y tratamiento de discrepancias
- `ISSUE-033` Definir politicas de seguridad y diseno de contratos AI

### Resultado esperado

- alcance del MVP aclarado
- contratos base definidos
- contrato de `DecisionTrace` y restricciones del pipeline configurable definidos
- estructura nueva del proyecto creada
- backend levantando localmente
- frontend elegido y justificado segun despliegue
- modelo de datos inicial definido
- contratos de inputs externos y snapshot minimo aprobados
- fuente oficial de reglas documentada
- politicas de datos AI aprobadas y diseno de persistencia AI definido

### Riesgos del sprint

- demoras en decisiones de autenticacion o frontend
- falta de cierre funcional de reglas
- ambiguedades del Excel de parametros

### Criterio de cierre

- el equipo ya puede iniciar implementacion real sin depender de mas exploracion del legacy para la estructura general

### Cierre documental

- Sprint 1 queda cerrado como fase de descubrimiento, contratos base y bootstrap inicial.
- Quedan consolidados el alcance del MVP, los contratos iniciales, la estructura base, el backend inicial, el frontend inicial, el modelo de datos inicial y las politicas base de AI.
- El equipo puede continuar con Sprint 2 sin reabrir decisiones estructurales del MVP.
- Nota de rebaseline: este cierre corresponde a las especificaciones originales vigentes al momento del sprint. Las nuevas especificaciones administrativas del motor no reabren Sprint 1 y se canalizan a un sprint posterior de saneamiento.

---

## Sprint 2 - Persistencia, seguridad base y fundaciones AI

- Estado: `done`
- Objetivo: dejar lista la persistencia inicial, autenticacion base, armazon del motor configurable y cliente LLM

### Issues comprometidos

- `ISSUE-007` Implementar ORM y migracion inicial
- `ISSUE-008` Definir e implementar autenticacion base
- `ISSUE-009` Definir permisos e implementar RBAC
- `ISSUE-010` Crear modulo aislado del motor de decisiones
- `ISSUE-034` Implementar servicio base de conexion a LLM

### Resultado esperado

- base SQLite inicial operativa
- migraciones funcionando
- autenticacion y autorizacion base implementadas
- motor desacoplado creado como modulo reusable con contratos base de nodos y estrategia
- servicio cliente LLM integrado y testeado en backend

### Riesgos del sprint

- definicion incompleta del proveedor de identidad
- cambios tardios en el modelo de datos

### Criterio de cierre

- el backend ya soporta usuarios autenticados y tiene una base tecnica estable para construir casos de uso PLD

### Cierre documental

- Sprint 2 queda cerrado como fase tecnica de persistencia inicial, seguridad base, motor aislado y fundaciones AI.
- Quedan consolidados `ISSUE-007`, `ISSUE-008`, `ISSUE-009`, `ISSUE-010` y `ISSUE-034`.
- El backend ya cuenta con ORM y migraciones, autenticacion temporal, RBAC base, core aislado del motor de decisiones y servicio base de conexion a LLM con proveedor activo configurable.
- La documentacion de cierre tecnico relevante queda en `docs/analysis/ISSUE-007.md`, `docs/analysis/ISSUE-008.md`, `docs/analysis/ISSUE-009.md`, `docs/analysis/ISSUE-010.md` y `docs/analysis/ISSUE-034.md`.
- El equipo puede avanzar a `Sprint 3` sin reabrir decisiones estructurales de seguridad, motor o integracion base con LLM.
- Nota de rebaseline: este cierre corresponde a las especificaciones originales vigentes al momento del sprint. Las nuevas especificaciones administrativas del motor no reabren Sprint 2 y se canalizan a un sprint posterior de saneamiento.

---

## Sprint 3 - Saneamiento del motor frente a las nuevas especificaciones

- Estado: `planned`
- Objetivo: sanear las brechas entre la implementacion actual del motor y las nuevas especificaciones administrativas, sin reabrir los sprints ya cerrados

### Issues comprometidos

- `ISSUE-032` Definir y validar base multiproducto de la plataforma
- `ISSUE-041` Alinear modelo de datos y contratos base del motor con nuevas especificaciones administrativas
- `ISSUE-042` Alinear runtime base del motor con productos, workflows, variables y fuentes declarativas

### Resultado esperado

- baseline tecnico actualizado para productos y workflows en `draft -> active`
- catalogo de variables por producto definido y alineado con persistencia y contratos
- estrategia clara para herencia de variables y reglas entre producto y workflow
- resolucion declarativa de inputs desde `campaign_db`, `user_input`, `derived` y `constant`
- brechas criticas saneadas antes de continuar con funcionalidades PLD sobre supuestos desactualizados

### Riesgos del sprint

- subestimar el impacto del nuevo modelo administrativo sobre contratos y persistencia
- introducir deuda adicional si se continua con features PLD sin sanear primero las brechas base

### Criterio de cierre

- las nuevas especificaciones del motor quedan aterrizadas en un baseline tecnico coherente y trazable para continuar la implementacion sin contradicciones mayores

---

## Sprint 4 - Runtime PLD y APIs nucleares

- Estado: `active`
- Objetivo: completar las reglas centrales del negocio sobre el core multiproducto y exponer evaluacion, traza y explicacion AI, partiendo de la consulta por producto ya implementada

### Issues comprometidos

- `ISSUE-011` Implementar reglas y formulas PLD sobre motor multiproducto
- `ISSUE-012` Crear suite de regresion del motor
- `ISSUE-013` Implementar API de consulta PLD
- `ISSUE-014` Implementar API de evaluacion PLD
- `ISSUE-035` Desarrollar el servicio de explicacion de evaluacion PLD

### Resultado esperado

- runtime PLD funcional y probado sobre core generico
- consulta PLD disponible por API
- evaluacion PLD disponible por API
- `DecisionTrace` consultable por API
- explicador de evaluaciones AI operativo por API

### Riesgos del sprint

- diferencias entre resultados del legacy y el nuevo motor
- riesgo de mantener contratos HTTP o documentacion mas PLD-centricos que la base tecnica real
- reglas de negocio implicitas no detectadas a tiempo

### Criterio de cierre

- existe paridad funcional suficiente para consulta y evaluacion sobre casos representativos

---

## Sprint 5 - Solicitudes, UI operativa y ZIP backend

- Estado: `planned`
- Objetivo: completar registro de solicitud, bandeja base, experiencia frontend principal y adjuntos ZIP por backend

### Issues comprometidos

- `ISSUE-015` Implementar API de registro de solicitud
- `ISSUE-016` Implementar bandeja y mantenimiento de solicitudes
- `ISSUE-017` Construir base del frontend y manejo de sesion
- `ISSUE-018` Implementar UI de consulta y evaluacion PLD
- `ISSUE-023` Implementar backend de adjuntos ZIP

### Resultado esperado

- registro de solicitud funcional
- bandeja operativa base disponible por API
- frontend permite consultar y evaluar
- base frontend operativa para continuar registro, bandeja y capacidades AI
- adjuntos ZIP disponibles por backend

### Riesgos del sprint

- complejidad de estados operativos
- ajustes de UX por hallazgos del flujo real

### Criterio de cierre

- el usuario puede recorrer de extremo a extremo consulta, evaluacion y pre-registro desde UI

---

## Sprint 6 - Flujo operativo ampliado, AI completa y salida controlada

- Estado: `planned`
- Objetivo: cerrar el flujo operativo del MVP, completar AI asistiva, trazabilidad estructurada y dejar lista la salida controlada

### Issues comprometidos

- `ISSUE-019` Implementar UI de registro y bandeja
- `ISSUE-020` Implementar auditoria, logs y endurecimiento basico
- `ISSUE-021` Implementar pruebas de integracion y E2E del MVP
- `ISSUE-022` Preparar despliegue inicial y CI
- `ISSUE-024` Implementar UI de adjuntos ZIP
- `ISSUE-025` Implementar asistencia AI al registro
- `ISSUE-026` Implementar briefing AI de bandeja
- `ISSUE-029` Exportacion de bandeja
- `ISSUE-036` Implementar integracion frontend de capacidades AI del MVP
- `ISSUE-037` Implementar event store de decisiones

### Resultado esperado

- flujo operativo principal disponible desde UI
- auditoria y logs basicos activos
- pruebas de integracion y al menos un E2E estable
- pipeline y despliegue base definidos
- event store de decisiones operativo con eventos inmutables y `DecisionTrace` persistido por evaluacion
- AI MVP completa operativa: explicacion, asistencia al registro y briefing de bandeja
- ZIP operativo de punta a punta

### Riesgos del sprint

- deuda tecnica acumulada en sprints previos
- tiempo insuficiente para estabilizar pruebas E2E

### Criterio de cierre

- el sistema queda listo para completar BRMS y pipeline configurable sin deuda critica en los flujos operativos del MVP

---

## Sprint 7 - BRMS y consolidacion de extensibilidad

- Estado: `planned`
- Objetivo: consolidar versionado de reglas y flujo, alta administrable de productos y workflows, catalogo de variables por producto e importacion de parametros sobre una base multiproducto ya iniciada

### Issues comprometidos

- `ISSUE-030` Importador de parametros desde Excel
- `ISSUE-031` Documentar estrategia de base limpia y referencia legacy
- `ISSUE-038` Implementar BRMS: productos, workflows, variables, reglas y configuracion de flujo

### Resultado esperado

- importador versionado de parametros
- base limpia documentada y legacy acotado a uso referencial
- lineamientos tecnicos para incorporar futuros productos de prestamo sobre la base ya construida
- productos y workflows administrables en `draft` con activacion posterior por negocio o riesgos
- catalogo de variables por producto y fuentes declarativas de input
- reglas de negocio y flujo almacenados en BD con versionado completo
- validacion tecnica de onboarding de un segundo producto sobre la misma base

### Riesgos del sprint

- complejidad del modelo de reglas y vigencias
- complejidad del modelo de herencia entre producto y workflow
- ambiguedades al migrar reglas PLD al BRMS

### Criterio de cierre

- el sistema ya soporta reglas versionadas administradas por backend, productos y workflows activables por negocio o riesgos, y queda consolidada la extension multiproducto sin reabrir fundaciones ya resueltas en dominio

---

## Sprint 8 - Convergencia administrable del pipeline y cierre del MVP

- Estado: `planned`
- Objetivo: cerrar el MVP con pipeline configurable por nodos ya convergido con persistencia y UI administrativa de productos, workflows, variables, reglas y flujo

### Issues comprometidos

- `ISSUE-039` Refactorizar motor a pipeline configurable por nodos
- `ISSUE-040` UI Administrativa de Productos, Workflows, Variables, Reglas y Flujo

### Resultado esperado

- pipeline configurable por producto funcionando con branching controlado y administracion persistida
- administradores pueden gestionar productos, workflows, variables, reglas y flujo desde interfaz web
- sandbox de pruebas de reglas funcional
- flujo de aprobacion de cambios de reglas y flujo operativo

### Riesgos del sprint

- complejidad de la convergencia final entre fundaciones ya implementadas, persistencia y capa administrativa
- complejidad de UX al exponer herencia, fuentes de input y ciclo `draft -> active`
- ajustes de UX en la administracion de reglas

### Criterio de cierre

- el MVP queda cerrado con BRMS, pipeline configurable por nodos y UI administrativa de productos, workflows, variables, reglas y flujo operativos

---

## Dependencias entre sprints

- Sprint 2 depende del cierre material de Sprint 1
- Sprint 3 depende de la persistencia y seguridad base de Sprint 2
- Sprint 4 depende del saneamiento de Sprint 3
- Sprint 5 depende del motor y APIs nucleares de Sprint 4
- Sprint 6 depende del flujo funcional ya implementado en Sprint 5
- Sprint 7 depende del flujo operativo estable y de la persistencia madura de Sprint 6
- Sprint 8 depende del BRMS backend de Sprint 7

---

## Camino critico del MVP

El camino critico recomendado es:

1. `ISSUE-001`
2. `ISSUE-027` (Inputs externos y snapshot)
3. `ISSUE-028` (Fuente oficial de reglas)
4. `ISSUE-002`
5. `ISSUE-003`
6. `ISSUE-004`
7. `ISSUE-005`
8. `ISSUE-006`
9. `ISSUE-033` (Politica AI)
10. `ISSUE-007`
11. `ISSUE-008`
12. `ISSUE-009`
13. `ISSUE-010`
14. `ISSUE-034` (Cliente LLM)
15. `ISSUE-032`
16. `ISSUE-041`
17. `ISSUE-042`
18. `ISSUE-011`
19. `ISSUE-012`
20. `ISSUE-013`
21. `ISSUE-014`
22. `ISSUE-035` (Explicador AI por API)
23. `ISSUE-015`
24. `ISSUE-016`
25. `ISSUE-017`
26. `ISSUE-018`
27. `ISSUE-023` (ZIP backend)
28. `ISSUE-019`
29. `ISSUE-024` (ZIP frontend)
30. `ISSUE-025` (Assist AI)
31. `ISSUE-026` (Bandeja AI)
32. `ISSUE-029` (Exportacion)
33. `ISSUE-036` (UI AI)
34. `ISSUE-020`
35. `ISSUE-021`
36. `ISSUE-022`
37. `ISSUE-037`
38. `ISSUE-030`
39. `ISSUE-031`
40. `ISSUE-038`
41. `ISSUE-039`
42. `ISSUE-040`

---

## Recomendacion operativa

Antes de iniciar Sprint 1 conviene tomar decisiones explicitas sobre:

- mecanismo definitivo de autenticacion
- decision de frontend segun facilidades reales de despliegue
- contratos de inputs externos y snapshot minimo
- fuente oficial de reglas cuando haya discrepancias con el legacy
- lineamientos corporativos de seguridad, logs y despliegue

Sin esas definiciones, `ISSUE-001`, `ISSUE-027`, `ISSUE-028` y `ISSUE-033` pueden bloquear el resto del camino critico.

Aunque `PLD` sigue siendo el producto funcional del MVP, el diseno de sprints 1 a 8 debe dejar validado el onboarding tecnico de un segundo producto sin acoplar estructuralmente la plataforma a PLD, permitiendo que negocio y riesgos registren productos y workflows en `draft` y los activen sin intervencion de TI en el flujo normal.
