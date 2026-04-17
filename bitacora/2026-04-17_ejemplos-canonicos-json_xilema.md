# Xilema - issue #2 - ejemplos canonicos JSON

Fecha: 2026-04-17
Rama: `feat/rhizome-canonical-json-examples`
Issue: `#2`

## Objetivo

Sacar los ejemplos canonicos de `schemas/tests/factories.py` a una ubicacion propia, generar los `.json` desde Pydantic y usarlos como fixtures reales para round-trip Python <-> JSON <-> Python.

## Trabajo realizado

- Creo `code/shared/schemas/examples/` como espacio canonico de ejemplos.
- Muevo los builders de payload a `schemas/examples/builders.py`.
- Añado `schemas/examples/generate_examples.py` para serializar los ejemplos a JSON desde los modelos Pydantic.
- Genero 6 archivos core:
  - `rhizome_snapshot.json`
  - `policy_packet.json`
  - `policy_delta.json`
  - `weather_packet.json`
  - `contradiction_alert.json`
  - `decision_receipt.json`
- Añado un fixture suplementario `decision_receipt_blocked.json` para cubrir el caso `executed=false` con `blocked_reason`, pedido en la issue.
- Actualizo tests para validar los ficheros comprometidos y comprobar que el generador no se ha quedado desfasado.
- Mantengo `schemas/tests/factories.py` como wrapper de compatibilidad para no romper imports existentes mientras el repo converge.

## Validacion

En `code/shared/`:

```bash
python -m schemas.examples.generate_examples --check
python -m pytest schemas/tests
```

Resultado: `33 passed`.

## Nota de drift

He detectado un desacople menor entre issue y documento:

- La issue `#2` pide los archivos como `code/shared/schemas/examples/<schema>.json`.
- `docs/20_data_contracts.md` seccion 6 menciona nombres con sufijo `_01`.

He seguido la nomenclatura de la issue para no bloquear a Floema ni a los fixtures cruzados. Si quereis, esto se puede alinear luego en docs con un cambio pequeno y explicito.

## Contexto de rama

`main` no traia todavia el merge de `#13` cuando he arrancado `#2`, asi que he apoyado esta rama sobre `feat/rhizome-schemas-pydantic` para no duplicar ni reimplementar la base de schemas.
