# SPRINTS - Decision Engine

## Proposito

Este archivo organiza `ISSUES.md` en una secuencia de sprints sugerida para ejecutar el MVP del nuevo sistema, cuyo primer producto soportado es `PLD`.

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

- Estado: `planned`
- Objetivo: cerrar alcance, contratos base, decision de frontend por despliegue y politicas de datos AI

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

---

## Sprint 2 - Persistencia, seguridad base y fundaciones AI

- Estado: `planned`
- Objetivo: dejar lista la persistencia inicial, autenticacion base, armazon del motor y cliente LLM

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
- motor desacoplado creado como modulo reusable
- servicio cliente LLM integrado y testeado en backend

### Riesgos del sprint

- definicion incompleta del proveedor de identidad
- cambios tardios en el modelo de datos

### Criterio de cierre

- el backend ya soporta usuarios autenticados y tiene una base tecnica estable para construir casos de uso PLD

---

## Sprint 3 - Motor PLD y APIs nucleares

- Estado: `planned`
- Objetivo: implementar las reglas centrales del negocio y exponer consulta, evaluacion y explicacion AI

### Issues comprometidos

- `ISSUE-011` Implementar reglas y formulas del motor PLD
- `ISSUE-012` Crear suite de regresion del motor
- `ISSUE-013` Implementar API de consulta PLD
- `ISSUE-014` Implementar API de evaluacion PLD
- `ISSUE-035` Desarrollar el servicio de explicacion de evaluacion PLD

### Resultado esperado

- motor PLD funcional y probado
- consulta PLD disponible por API
- evaluacion PLD disponible por API
- explicador de evaluaciones AI operativo por API

### Riesgos del sprint

- diferencias entre resultados del legacy y el nuevo motor
- reglas de negocio implicitas no detectadas a tiempo

### Criterio de cierre

- existe paridad funcional suficiente para consulta y evaluacion sobre casos representativos

---

## Sprint 4 - Solicitudes, UI operativa y ZIP backend

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

## Sprint 5 - Flujo operativo ampliado, AI completa y salida controlada

- Estado: `planned`
- Objetivo: cerrar el flujo operativo del MVP, completar AI asistiva y dejar lista la salida controlada

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
- event store de decisiones operativo con eventos inmutables
- AI MVP completa operativa: explicacion, asistencia al registro y briefing de bandeja
- ZIP operativo de punta a punta

### Riesgos del sprint

- deuda tecnica acumulada en sprints previos
- tiempo insuficiente para estabilizar pruebas E2E

### Criterio de cierre

- el sistema queda listo para completar BRMS y pipeline configurable sin deuda critica en los flujos operativos del MVP

---

## Sprint 6 - BRMS y extensibilidad de plataforma

- Estado: `planned`
- Objetivo: consolidar versionado de reglas, importacion de parametros y base multiproducto

### Issues comprometidos

- `ISSUE-030` Importador de parametros desde Excel
- `ISSUE-031` Documentar estrategia de base limpia y referencia legacy
- `ISSUE-032` Definir base multiproducto de la plataforma
- `ISSUE-038` Implementar BRMS: catalogacion de reglas

### Resultado esperado

- importador versionado de parametros
- base limpia documentada y legacy acotado a uso referencial
- lineamientos tecnicos para incorporar futuros productos de prestamo
- reglas de negocio almacenadas en BD con versionado completo

### Riesgos del sprint

- complejidad del modelo de reglas y vigencias
- ambiguedades al migrar reglas PLD al BRMS

### Criterio de cierre

- el sistema ya soporta reglas versionadas administradas por backend y queda preparada la extension multiproducto

---

## Sprint 7 - Pipeline configurable y cierre del MVP

- Estado: `planned`
- Objetivo: cerrar el MVP con pipeline configurable y UI administrativa de reglas

### Issues comprometidos

- `ISSUE-039` Refactorizar motor a pipeline de etapas
- `ISSUE-040` UI Administrativa de Reglas

### Resultado esperado

- pipeline configurable por producto funcionando
- administradores pueden gestionar reglas desde interfaz web
- sandbox de pruebas de reglas funcional
- flujo de aprobacion de cambios operativo

### Riesgos del sprint

- complejidad del refactor del motor
- ajustes de UX en la administracion de reglas

### Criterio de cierre

- el MVP queda cerrado con BRMS, pipeline configurable y UI administrativa de reglas operativos

---

## Dependencias entre sprints

- Sprint 2 depende del cierre material de Sprint 1
- Sprint 3 depende de la persistencia y seguridad base de Sprint 2
- Sprint 4 depende del motor y APIs nucleares de Sprint 3
- Sprint 5 depende del flujo funcional ya implementado en Sprint 4
- Sprint 6 depende del flujo operativo estable y de la persistencia madura de Sprint 5
- Sprint 7 depende del BRMS backend de Sprint 6

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
15. `ISSUE-011`
16. `ISSUE-012`
17. `ISSUE-013`
18. `ISSUE-014`
19. `ISSUE-035` (Explicador AI por API)
20. `ISSUE-015`
21. `ISSUE-016`
22. `ISSUE-017`
23. `ISSUE-018`
24. `ISSUE-023` (ZIP backend)
25. `ISSUE-019`
26. `ISSUE-024` (ZIP frontend)
27. `ISSUE-025` (Assist AI)
28. `ISSUE-026` (Bandeja AI)
29. `ISSUE-029` (Exportacion)
30. `ISSUE-036` (UI AI)
31. `ISSUE-020`
32. `ISSUE-021`
33. `ISSUE-022`
34. `ISSUE-037`
35. `ISSUE-030`
36. `ISSUE-031`
37. `ISSUE-032`
38. `ISSUE-038`
39. `ISSUE-039`
40. `ISSUE-040`

---

## Recomendacion operativa

Antes de iniciar Sprint 1 conviene tomar decisiones explicitas sobre:

- mecanismo definitivo de autenticacion
- decision de frontend segun facilidades reales de despliegue
- contratos de inputs externos y snapshot minimo
- fuente oficial de reglas cuando haya discrepancias con el legacy
- lineamientos corporativos de seguridad, logs y despliegue

Sin esas definiciones, `ISSUE-001`, `ISSUE-027`, `ISSUE-028` y `ISSUE-033` pueden bloquear el resto del camino critico.

La extension a otros productos no forma parte del MVP, pero el diseno de sprints 1 y 2 debe evitar que la plataforma quede acoplada estructuralmente a PLD.
