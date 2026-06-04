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

## Sprint 1 - Descubrimiento y bootstrap inicial

- Estado: `planned`
- Objetivo: cerrar alcance, contratos iniciales y esqueleto del proyecto

### Issues comprometidos

- `ISSUE-001` Cerrar alcance funcional del MVP
- `ISSUE-002` Definir contratos iniciales del dominio y API
- `ISSUE-003` Bootstrap del repositorio y estructura base
- `ISSUE-004` Inicializar backend con FastAPI
- `ISSUE-005` Inicializar frontend con React y TypeScript
- `ISSUE-006` Diseñar modelo de datos inicial
- `ISSUE-027` Definir politicas de seguridad y contratos AI

### Resultado esperado

- alcance del MVP aclarado
- contratos base definidos
- estructura nueva del proyecto creada
- backend y frontend levantando localmente
- modelo de datos inicial definido
- decision inicial sobre como mantener la plataforma extensible a otros tipos de prestamo
- politicas de datos AI aprobadas y base de base de datos AI diseñada

### Riesgos del sprint

- demoras en decisiones de autenticacion
- falta de cierre funcional de reglas
- ambiguedades del Excel de parametros

### Criterio de cierre

- el equipo ya puede iniciar implementacion real sin depender de mas exploracion del legado para la estructura general

---

## Sprint 2 - Persistencia y seguridad base

- Estado: `planned`
- Objetivo: dejar lista la persistencia inicial, autenticacion base y armazon del motor

### Issues comprometidos

- `ISSUE-007` Implementar ORM y migracion inicial
- `ISSUE-008` Definir e implementar autenticacion base
- `ISSUE-009` Definir permisos e implementar RBAC
- `ISSUE-010` Crear modulo aislado del motor de decisiones
- `ISSUE-028` Implementar servicio base de conexion a LLM

### Resultado esperado

- base SQLite inicial operativa
- migraciones funcionando
- autenticacion y autorizacion base implementadas
- motor desacoplado creado como modulo reusable
- base tecnica lista para soportar otros productos sin rehacer componentes compartidos
- servicio cliente LLM integrado y testeado en backend

### Riesgos del sprint

- definicion incompleta del proveedor de identidad
- cambios tardios en el modelo de datos

### Criterio de cierre

- el backend ya soporta usuarios autenticados y tiene una base tecnica estable para construir casos de uso PLD

---

## Sprint 3 - Motor PLD y APIs nucleares

- Estado: `planned`
- Objetivo: implementar las reglas centrales del negocio y exponer consulta y evaluacion

### Issues comprometidos

- `ISSUE-011` Implementar reglas y formulas del motor PLD
- `ISSUE-012` Crear suite de regresion del motor
- `ISSUE-013` Implementar API de consulta PLD
- `ISSUE-014` Implementar API de evaluacion PLD
- `ISSUE-029` Desarrollar el servicio de explicacion de evaluacion PLD

### Resultado esperado

- motor PLD funcional y probado
- consulta PLD disponible por API
- evaluacion PLD disponible por API
- explicador de evaluaciones AI operativo por API

### Riesgos del sprint

- diferencias entre resultados del legado y el nuevo motor
- reglas de negocio implicitas no detectadas a tiempo

### Criterio de cierre

- existe paridad funcional suficiente para consulta y evaluacion sobre casos representativos

---

## Sprint 4 - Solicitudes y primera UI operativa

- Estado: `planned`
- Objetivo: completar registro de solicitud, bandeja base y experiencia frontend principal

### Issues comprometidos

- `ISSUE-015` Implementar API de registro de solicitud
- `ISSUE-016` Implementar bandeja y mantenimiento de solicitudes
- `ISSUE-017` Construir base del frontend y manejo de sesion
- `ISSUE-018` Implementar UI de consulta y evaluacion PLD
- `ISSUE-030` Implementar panel de explicacion AI en frontend

### Resultado esperado

- registro de solicitud funcional
- bandeja operativa base disponible por API
- frontend permite consultar y evaluar
- panel de explicacion y sugerencias AI integrado en el flujo de evaluacion de la UI

### Riesgos del sprint

- complejidad de estados operativos
- ajustes de UX por hallazgos del flujo real

### Criterio de cierre

- el usuario puede recorrer de extremo a extremo consulta, evaluacion y pre-registro desde UI

---

## Sprint 5 - MVP completo, QA y despliegue base

- Estado: `planned`
- Objetivo: cerrar el MVP operable con trazabilidad, pruebas y salida controlada

### Issues comprometidos

- `ISSUE-019` Implementar UI de registro y bandeja
- `ISSUE-020` Implementar auditoria, logs y endurecimiento basico
- `ISSUE-021` Implementar pruebas de integracion y E2E del MVP
- `ISSUE-022` Preparar despliegue inicial y CI

### Resultado esperado

- flujo MVP completo disponible desde UI
- auditoria y logs basicos activos
- pruebas de integracion y al menos un E2E estable
- pipeline y despliegue base definidos

### Riesgos del sprint

- deuda tecnica acumulada en sprints previos
- tiempo insuficiente para estabilizar pruebas E2E

### Criterio de cierre

- el MVP puede demostrarse, validarse y desplegarse en un entorno controlado

---

## Sprint 6 - Mejoras post-MVP

- Estado: `planned`
- Objetivo: cerrar capacidades complementarias y de migracion

### Issues comprometidos

- `ISSUE-023` Exportacion de bandeja
- `ISSUE-024` Importador de parametros desde Excel
- `ISSUE-025` Migracion historica desde legacy
- `ISSUE-026` Definir base multiproducto de la plataforma

### Resultado esperado

- exportacion desacoplada del DOM
- importador versionado de parametros
- definicion y ejecucion de migracion historica si aplica
- lineamientos tecnicos para incorporar futuros productos de prestamo

### Criterio de cierre

- el sistema queda mejor preparado para operacion continua y administracion futura de reglas

---

## Dependencias entre sprints

- Sprint 2 depende del cierre material de Sprint 1
- Sprint 3 depende de la persistencia y seguridad base de Sprint 2
- Sprint 4 depende del motor y APIs nucleares de Sprint 3
- Sprint 5 depende del flujo funcional ya implementado en Sprint 4
- Sprint 6 es posterior al MVP y puede ajustarse segun prioridades reales

---

## Camino critico del MVP

El camino critico recomendado es:

1. `ISSUE-001`
1a. `ISSUE-027` (Politica AI)
2. `ISSUE-002`
3. `ISSUE-003`
4. `ISSUE-004`
4a. `ISSUE-028` (Cliente LLM)
5. `ISSUE-006`
6. `ISSUE-007`
7. `ISSUE-008`
8. `ISSUE-009`
9. `ISSUE-010`
10. `ISSUE-011`
11. `ISSUE-012`
12. `ISSUE-013`
13. `ISSUE-014`
13a. `ISSUE-029` (Explicador AI por API)
14. `ISSUE-015`
15. `ISSUE-016`
16. `ISSUE-017`
17. `ISSUE-018`
17a. `ISSUE-030` (UI de explicacion AI)
18. `ISSUE-019`
19. `ISSUE-020`
20. `ISSUE-021`
21. `ISSUE-022`

---

## Recomendacion operativa

Antes de iniciar Sprint 1 conviene tomar decisiones explicitas sobre:

- autenticacion definitiva o temporal
- continuidad o eliminacion del flujo ZIP
- politica de migracion historica
- fuente oficial de reglas cuando haya discrepancias con el legado

Sin esas definiciones, `ISSUE-001` y `ISSUE-008` pueden bloquear el resto del camino critico.

La extension a otros productos no forma parte del MVP, pero el diseno de sprints 1 y 2 debe evitar que la plataforma quede acoplada estructuralmente a PLD.
