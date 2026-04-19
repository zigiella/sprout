# reports/

Artefactos versionados del harness E2E cross-node.

Formato:

- `YYYY-MM-DD_<modelo>_<host>_cross-node-e2e.json`
- `YYYY-MM-DD_<modelo>_<host>_cross-node-e2e.md`

Cada corrida deja:

- contexto de host y modelo
- escenarios ejecutados
- latencia por etapa (`Rhizome`, `Pollen`, `Meristem`)
- latencia total
- delta emitido por Meristem o error de validacion

La idea es poder comparar rehearsal local, portatil de Bea y, mas adelante, los
ensayos que se hagan ya con el resto del stack maduro.
