--1. backend/ base con FastAPI, health y config por entorno.
--2. frontend/ base y decisión de despliegue ya fijada.
--3. Modelo de datos inicial y migraciones Alembic.
--4. Autenticación base y RBAC.
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

Lo que no implementé todavía
- motor de decisiones
- tablas AI
- endpoints PLD


Ajustar .gitignore para evitar la carga de archivos tipo build, cache, temp files, logs

