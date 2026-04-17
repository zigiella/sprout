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
    └── tests/
```

## Convencion

- Version actual del contrato: `docs/20_data_contracts.md` v1.0
- `pydantic` es la implementacion canonica
- Los parsers ignoran campos desconocidos para forward compatibility
- Todos los timestamps viajan como ISO-8601 UTC con sufijo `Z`
- Los ejemplos canonicos y round-trips viven en `schemas/tests/`

## Validacion

### Python (Rhizome, Meristem)
```bash
cd code/shared
make test-schemas
# o, si no hay make disponible:
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
