# ISSUE-034 - Implementar servicio base de conexion a LLM

## 1. Objetivo

Crear el cliente de integracion con el proveedor del modelo de lenguaje, aislando fallas y reintentos.

## 2. Fuentes revisadas

- `docs/project/ISSUES.md`
- `docs/project/SPRINTS.md`
- `docs/SPEC.md`
- `docs/analysis/ISSUE-033.md`
- `backend/app/config/settings.py`
- `backend/app/application/ai/__init__.py`
- `backend/app/application/ai/contracts.py`
- `backend/app/application/ai/exceptions.py`
- `backend/app/application/ai/client.py`
- `backend/app/application/ai/factory.py`
- `backend/app/application/ai/providers/openai_client.py`
- `backend/app/application/ai/providers/gemini_client.py`
- `backend/tests/test_ai_settings.py`
- `backend/tests/test_ai_client_factory.py`
- `backend/tests/test_ai_openai_client.py`
- `backend/tests/test_ai_gemini_client.py`

## 3. Contexto

- `ISSUE-033` ya habia cerrado las politicas de seguridad, minimizacion y aislamiento de la capa AI.
- `Sprint 2` exigia dejar listo un cliente base de LLM junto con el armazon del motor y la seguridad inicial.
- La implementacion debia contemplar mas de un proveedor y no volver dependiente al flujo determinista del estado del servicio AI.

## 4. Implementacion consolidada

Se implemento un nuevo modulo de aplicacion `backend/app/application/ai/` para encapsular la integracion con proveedores LLM.

La implementacion incluye:

- contrato interno `AIModelClient`
- contratos neutrales `AIModelRequest` y `AIModelResponse`
- manejo de errores de configuracion, timeout, error temporal y error del proveedor
- cliente base HTTP asincrono con reintentos
- implementacion concreta para `OpenAI`
- implementacion concreta para `Gemini`
- factory para seleccionar un proveedor activo fijo por configuracion
- carga de configuracion AI desde variables de entorno y desde `.env`

## 5. Entregables implementados

- `backend/app/application/ai/client.py`
- `backend/app/application/ai/contracts.py`
- `backend/app/application/ai/exceptions.py`
- `backend/app/application/ai/factory.py`
- `backend/app/application/ai/providers/openai_client.py`
- `backend/app/application/ai/providers/gemini_client.py`
- extension de `backend/app/config/settings.py` para configuracion AI

## 6. Configuracion y uso de API keys

La configuracion AI agregada en `Settings` incluye:

- `ai_enabled`
- `ai_provider`
- `ai_timeout_seconds`
- `ai_max_retries`
- `openai_api_key`
- `openai_model_name`
- `gemini_api_key`
- `gemini_model_name`

Variables esperadas:

- `AI_ENABLED`
- `AI_PROVIDER`
- `AI_TIMEOUT_SECONDS`
- `AI_MAX_RETRIES`
- `OPENAI_API_KEY`
- `OPENAI_MODEL_NAME`
- `GEMINI_API_KEY`
- `GEMINI_MODEL_NAME`

### 6.1 Como se cargan las claves

La funcion `get_settings()` ejecuta `_load_env_file()` antes de construir `Settings`.

El comportamiento es:

1. Se busca `DECISION_ENGINE_ENV_FILE`.
2. Si no existe, se usa `.env` en la raiz del repositorio.
3. El archivo se procesa linea por linea para cargar pares `KEY=VALUE`.
4. Cada valor se aplica con `os.environ.setdefault(...)`.
5. Luego `Settings` se construye con `os.getenv(...)`.

Esto implica el siguiente orden de precedencia:

1. Variables ya definidas en el entorno del proceso o del sistema.
2. Valores del archivo `.env`.
3. Defaults del codigo para campos no sensibles.

### 6.2 Como se usan las claves

- Si `AI_ENABLED=false`, el factory rechaza la construccion del cliente.
- Si `AI_PROVIDER=openai`, se exige `OPENAI_API_KEY`.
- Si `AI_PROVIDER=gemini`, se exige `GEMINI_API_KEY`.
- Solo se valida y utiliza la clave del proveedor activo.

### 6.3 Consideraciones de seguridad

- `.env` esta ignorado por Git y no debe versionarse.
- No se hardcodean claves reales en el codigo.
- No se imprimen ni se registran las API keys.
- La capa AI sigue separada del motor determinista y no queda en el camino critico del calculo.

## 7. Comportamiento del cliente base

El cliente base HTTP soporta:

- llamadas `async`
- timeout configurable
- reintentos frente a `timeout`
- reintentos frente a `429`, `500`, `502`, `503` y `504`
- rechazo inmediato de errores no transitorios `4xx`

La seleccion del proveedor se resuelve mediante `build_ai_model_client(settings)`.

En esta fase se adopto un proveedor activo fijo por configuracion. No se implemento fallback automatico entre proveedores.

## 8. Cobertura funcional del issue

`ISSUE-034` deja lista la base tecnica para:

- explicacion AI de evaluaciones
- resumen de casos
- sugerencias de accion
- futuras integraciones con `ai_prompt_templates` y `ai_interactions`

No incluye todavia:

- persistencia operativa de interacciones AI
- endpoints AI
- prompts versionados desde BD
- casos de uso funcionales de explicacion o resumen

## 9. Validacion automatizada

La implementacion queda respaldada por pruebas que verifican:

- carga de configuracion AI desde `.env`
- precedencia de variables de entorno sobre `.env`
- seleccion correcta del proveedor activo
- error si falta la clave del proveedor activo
- construccion de request para `OpenAI`
- construccion de request para `Gemini`
- parseo de respuestas exitosas
- reintentos ante errores temporales

Suite relevante:

- `backend/tests/test_ai_settings.py`
- `backend/tests/test_ai_client_factory.py`
- `backend/tests/test_ai_openai_client.py`
- `backend/tests/test_ai_gemini_client.py`

## 10. Evaluacion del resultado

La implementacion cumple correctamente el objetivo y los entregables de `ISSUE-034`.

Cumplimientos observados:

- existe la clase cliente `AIModelClient`
- existen variables de entorno configuradas y mapeadas a `Settings`
- existen pruebas unitarias de integracion del cliente y del factory
- el backend puede inicializar la configuracion AI mediante configuracion externa
- un fallo de red o timeout del LLM no bloquea el arranque del backend ni contamina el motor determinista

No se detecto un hallazgo bloqueante dentro del alcance de este issue.

## 11. Riesgos y notas abiertas

- La carga de `.env` es una implementacion simple propia; si en el futuro la configuracion crece, podria convenir migrar a una libreria especializada.
- El modulo aun no persiste interacciones AI en `ai_interactions`.
- No existe aun un endpoint funcional que consuma este cliente.
- No existe fallback automatico entre proveedores; esta decision fue intencional para mantener auditabilidad y predictibilidad.

## 12. Cierre formal

`ISSUE-034` queda cerrado como implementacion del servicio base de conexion a LLM para el backend.

Queda consolidado:

- el cliente AI base asincrono
- la seleccion por proveedor activo fijo
- el soporte para `OpenAI` y `Gemini`
- la carga de configuracion desde entorno y `.env`
- el manejo base de timeout y reintentos
- la base tecnica necesaria para las capacidades AI funcionales de sprints posteriores
