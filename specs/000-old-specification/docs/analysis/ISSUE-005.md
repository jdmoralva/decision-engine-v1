# ISSUE-005 - Seleccionar e inicializar frontend web segun estrategia de despliegue

## 1. Objetivo

Comparar opciones tecnicas de frontend segun despliegue y dejar inicializado el stack elegido para el MVP.

## 2. Fuentes revisadas

- `ISSUES.md`
- `docs/SPEC.md`
- `README.md`

## 3. Contexto

- `docs/SPEC.md` deja el stack frontend abierto segun facilidades tecnicas de despliegue.
- El despliegue inicial recomendado es frontend estatico servido por Nginx o equivalente.
- Sprint 1 exige cerrar esta decision antes de avanzar a funcionalidad.

## 4. Decision cerrada

- Stack elegido: `Vite + React + TypeScript`.
- Forma de despliegue: build estatico servido por Nginx o un reverse proxy equivalente.
- Alcance del frontend: base desacoplada, sin reglas de negocio criticas en la UI.

## 5. Justificacion

- `Vite` permite un bootstrap rapido y un build estatico simple para el entorno objetivo.
- `React` encaja con formularios complejos, tablas, estado de UI y pantallas operativas del MVP.
- `TypeScript` reduce errores en contratos y mejora la evolucion de pantallas y servicios.
- El resultado compilado como assets estaticos simplifica el despliegue y mantiene la separacion con la API FastAPI.
- El stack no impone una dependencia PLD-centrica; solo proporciona la base de presentacion para el MVP y futuras extensiones.

## 6. Restricciones de diseno

- Debe desacoplar UI, backend y motor.
- Debe soportar consulta, evaluacion, bandeja, exportacion, ZIP y paneles AI.
- Debe funcionar como frontend desplegable de forma simple.
- No debe asumir PLD como unico producto de largo plazo.

## 7. Criterios para comparar opciones

- facilidad de despliegue como estatico
- costo de inicializacion
- soporte para formularios complejos y tablas
- manejo de rutas y estados
- integracion con backend FastAPI
- soporte para carga/descarga de archivos
- mantenibilidad para futuras extensiones

## 8. Resultados esperados del analisis

- comparativa tecnica de opciones de frontend y despliegue
- decision documentada del stack elegido
- app frontend inicial
- pagina base funcional
- configuracion de arranque local

## 9. Despliegue objetivo

- frontend estatico servido por Nginx o equivalente
- backend FastAPI detras de reverse proxy
- stack frontend compatible con build estatico
- separacion clara entre assets compilados y API

## 10. Criterio de seleccion

El stack elegido debe:

- ser facil de desplegar en el entorno objetivo
- permitir una base ejecutable rapida
- no complicar la separacion entre UI, backend y motor
- soportar el flujo PLD y extensiones futuras

## 11. Riesgos

- Elegir un stack pesado para un MVP que necesita rapidez de bootstrap.
- Acoplar la UI al legacy o a la forma actual de los datos.
- Postergar demasiado la decision y bloquear el resto de Sprint 1.
- Escoger una tecnologia dificil de servir estaticamente en el entorno objetivo.

## 12. Criterio de aceptacion

- El stack elegido queda justificado segun despliegue previsto.
- Existe una base ejecutable del frontend seleccionado.
- El stack no compromete la separacion entre UI, backend y motor.

## 13. Nota importante

`docs/SPEC.md` no fija un stack concreto; solo exige que la decision se tome segun facilidad de despliegue.
Por eso este issue debe cerrar con una comparativa corta y una decision explicita, no con una preferencia asumida.

## 14. Cierre formal

`ISSUE-005` queda cerrado como seleccion e inicializacion del frontend web segun estrategia de despliegue.

Queda consolidado:

- el criterio de seleccion del stack frontend.
- el despliegue objetivo como frontend estatico servido por Nginx o equivalente.
- la base ejecutable inicial del frontend.
- la separacion entre UI, backend y motor.
- la base para continuar con los flujos funcionales del MVP sin reabrir la decision de stack.

Con este cierre, el equipo puede avanzar a la construccion de la experiencia funcional sin depender de volver a decidir la tecnologia base del frontend.
