# Analisis

Esta carpeta esta reservada para el levantamiento funcional y tecnico del flujo `PLD / solicitudes de credito` del sistema legacy.

`PLD` significa `Prestamo de Libre Disponibilidad` y es el primer producto que se migrara al nuevo sistema.

Aunque el analisis inmediato se concentra en PLD, conviene distinguir desde aqui:

- reglas y datos especificos de PLD
- patrones que podrian reutilizarse para otros tipos de prestamo en el futuro

Documentos esperados aqui:

- mapa del flujo PLD legacy
- catalogo de reglas de negocio
- mapeo de parametros desde `ParametrosPLD-v3.xlsx`
- notas sobre modelo de datos legacy
- decisiones funcionales cerradas durante `ISSUE-001`
- separacion entre capacidades compartidas de plataforma y capacidades exclusivas de PLD

Fuente principal para este analisis:

- `old-version/api-build.R`
- `old-version/script.js`
- `old-version/index.html`
- `old-version/bandeja.html`
- `old-version/API_DB.db`
- `old-version/ParametrosPLD-v3.xlsx`

Mientras estos documentos no existan, usa `SPEC.md` y `docs/project/ISSUES.md` como referencia para el trabajo del nuevo sistema.
