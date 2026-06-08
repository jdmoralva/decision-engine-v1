1. backend/ base con FastAPI, health y config por entorno.
2. frontend/ base y decisión de despliegue ya fijada.
3. Modelo de datos inicial y migraciones Alembic.
4. Autenticación base y RBAC.
5. Motor de decisiones como módulo aislado.
6. DecisionTrace y versionado de reglas/pipeline.
7. Persistencia de inputs externos y snapshot mínimo.
8. Base AI: políticas, tablas ai_interactions y ai_prompt_templates.
9. Endpoints base del MVP PLD:

- consulta
- evaluación
- trace
- registro
- cambio de estado
- bandeja
- exportación
- ZIP

1. Bootstrap real (Recomendado)
   Descripción: backend + frontend + config + health + esqueleto de proyecto
2. Base de datos primero
   Descripción: modelo de datos, SQLAlchemy, Alembic y entidades iniciales
3. Autenticación y seguridad primero
   Descripción: login base, RBAC y estructura de seguridad antes del resto


Lo que no implementé todavía
- ORM / modelos SQLAlchemy
- migraciones Alembic reales
- autenticación / RBAC
- motor de decisiones
- tablas AI
- endpoints PLD


Para este bootstrap en Vite + React + TypeScript, ¿quieres que deje solo una pantalla inicial montada en React, o que además deje React Router configurado desde ahora?
1. Solo pantalla inicial (Recomendado)
Descripción: menos dependencias, arranque más limpio, suficiente para bootstrap
2. Pantalla inicial + Router
Descripción: deja la base lista para crecer a pantallas PLD enseguida

FRONTEND
1. cd frontend
2. npm install
3. npm run dev

