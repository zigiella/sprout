# shared/

Schemas JSON y protocolos compartidos entre Rhizome, Pollen y Meristem.

Si un contrato de datos cruza de un nodo a otro, vive aqui. La **fuente de verdad** es la implementacion en Python con `pydantic` v2; Kotlin la replica para Pollen.

## Estructura

```
shared/
├── README.md
├── Makefile
└── schemas/
    ├── __init__.py
    ├── base.py
    ├── enums.py
    ├── rhizome_snapshot.py
    ├── policy_packet.py
    ├── policy_delta.py
    ├── weather_packet.py
    ├── contradiction_alert.py
    ├── decision_receipt.py
    ├── examples/
    │   ├── builders.py
    │   ├── generate_examples.py
    │   └── *.json
    └── tests/
```

## Convencion

- Version actual del contrato: `docs/20_data_contracts.md` v1.0
- `pydantic` es la implementacion canonica
- Los parsers ignoran campos desconocidos para forward compatibility
- Todos los timestamps viajan como ISO-8601 UTC con sufijo `Z`
- Los payloads canonicos viven en `schemas/examples/`
- Los JSON canonicos se generan con `python schemas/examples/generate_examples.py`
- Los round-trips Python viven en `schemas/tests/`

### Naming de ejemplos

Convencion formalizada en [CONTRIBUTING §6](../../CONTRIBUTING.md#6-convenciones-de-naming):
- `<schema>.json` = canonico unico por schema
- `<schema>_<variante>.json` = variantes deliberadas (caso de bloqueo, contradiccion, etc.)

## Validacion

### Python (Rhizome, Meristem)
```bash
cd code/shared
make generate-examples
make test-schemas
# o, si no hay make disponible:
python -m schemas.examples.generate_examples
python -m pytest schemas/tests
```

### Kotlin (Pollen)
```kotlin
// usar kotlinx.serialization con data classes que mapean 1:1
// respecto a los modelos Pydantic
```

## Cambios

Si cambias un schema, sigue primero el proceso del contrato de datos:

1. entrada en `bitacora/`
2. actualizacion de `docs/20_data_contracts.md`
3. cambio en `code/shared/schemas/`
4. sincronizacion posterior con Kotlin

Si cambias un ejemplo canonico, no edites el JSON a mano: ajusta `schemas/examples/builders.py` y vuelve a generar los archivos.
