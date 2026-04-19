# reports/

Artefactos **generados localmente** por el harness E2E cross-node.

Formato esperado:

- `YYYY-MM-DD_<modelo>_<host>_cross-node-e2e.json`
- `YYYY-MM-DD_<modelo>_<host>_cross-node-e2e.md`

Cada corrida deja:

- contexto de host y modelo
- escenarios ejecutados
- latencia por etapa (`Rhizome`, `Pollen`, `Meristem`)
- latencia total
- delta emitido por Meristem o error de validacion

## Importante

- Los `*.json` y `*.md` de este directorio **no se versionan**.
- `.gitignore` conserva solo este `README.md`.
- Si una corrida produce un hallazgo que debe quedar en el repo, se resume en
  `docs/benchmarks/` como evidencia historica, separada de la herramienta.
