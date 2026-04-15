# shared/

Schemas JSON y protocolos compartidos entre Rhizome, Pollen y Meristem.

Si un contrato de datos cruza de un nodo a otro, vive aqui. Unica fuente de verdad.

## Estructura

```
shared/
├── README.md
└── schemas/
    ├── weather_packet.json
    ├── policy_delta.json
    ├── policy_packet.json
    ├── contradiction_alert.json
    ├── rhizome_snapshot.json
    ├── decision_receipt.json
    └── README.md
```

## Convencion

- Cada schema en JSON Schema Draft 2020-12
- Cada schema tiene un `$id` estable: `https://sprout.network/schemas/v1/<nombre>.json`
- Versiones via subcarpeta (`v1/`, `v2/`) cuando haya cambios breaking
- Ejemplos minimos en `examples/` dentro de cada schema

## Validacion

### Python (Rhizome, Meristem)
```python
from pydantic import BaseModel
from pathlib import Path
import json

schema = json.loads(Path("shared/schemas/weather_packet.json").read_text())
# generar modelo con datamodel-code-generator o escribir pydantic model a mano
```

### Kotlin (Pollen)
```kotlin
// usar kotlinx.serialization con data classes que mapean 1:1
@Serializable data class WeatherPacket(
    val type: String,
    val id: String,
    // ...
)
```

## Cambios

Si cambias un schema, actualizar **los tres nodos en el mismo commit**. Nunca commits que dejen los schemas inconsistentes.

Si el cambio es breaking, bumpear version de carpeta y mantener la anterior para retrocompatibilidad temporal.
