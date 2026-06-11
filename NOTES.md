Sprint 3




Falta un patrón de resolución de schemas que, dado product_code, seleccione el contrato REST correcto. Actualmente todo es estático: el endpoint declara PLDEvaluationRequest en firma.

build_default_decision_engine_registry() en bootstrap.py registra únicamente PLD. No hay un punto de extensión donde otros productos se auto-registren.

