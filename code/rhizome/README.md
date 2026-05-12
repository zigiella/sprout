# rhizome/

Nodo edge de parcela. Corre en Jetson Orin Nano Super con Gemma 4 E2B (fine-tuned cuando tengamos v1).

## Rol

- Lee sensores (humedad suelo x2, caudalimetro, nivel deposito)
- Captura imagen de camara periodicamente
- Toma decisiones locales con Gemma 4 E2B
- Ejecuta o bloquea accion con validacion dura del ESP32
- Persiste snapshots, eventos, recibos
- Sirve endpoint local para Pollen (sync via WiFi Direct)

## Stack

- Python 3.11
- Ollama (`gemma4:e2b` o `sprout-rhizome-e2b-v1` cuantizado)
- `pydantic` para schemas
- `smbus2` / `adafruit-circuitpython-ads1x15` para ADC I2C
- `opencv-python` + `picamera2` para camara
- Comunicacion con ESP32 via UART o I2C

## Estructura (a construir)

```
rhizome/
├── README.md
├── Makefile
├── bench/                  # harness benchmark reproducible
├── benchmarks/             # resultados versionados del harness
├── requirements.txt
├── src/
│   ├── main.py             # bucle principal
│   ├── sensors.py          # lectura humedad, caudal, nivel
│   ├── vision.py           # captura y preprocesado
│   ├── policy_engine.py    # aplica politica vigente con LLM
│   ├── safety.py           # handshake con ESP32
│   ├── llm_client.py       # cliente Ollama
│   ├── sync_server.py      # endpoint BLE/WiFi para Pollen
│   └── persistence.py      # SQLite local
├── policies/               # politicas vigentes (JSON con schema)
│   └── examples/
└── tests/
```

## Pendiente

Briefing completo en `docs/10_rhizome_spec.md` (a redactar por Cambium + especialista Jetson).

## Benchmark local

Mientras llega el Jetson, el benchmark de `#5` se prepara y valida desde portatil:

```bash
cd code/rhizome
make generate-prompts
make test
python -m bench.run_ollama_benchmark --model gemma4:e4b --hardware-label hp-probook-460-g11
```

El mismo harness se reutiliza luego en Jetson cambiando solo el target del modelo/runtime.

## API local para Pollen

La especificacion de Rhizome define una API de lectura para que Pollen pueda
visitar la parcela sin depender de mocks Android:

- `GET /status`
- `GET /snapshot/latest`
- `GET /receipts?since=...`
- `GET /explain/decision/{id}`
- `GET /summary/since?since=...&locale=es|en`
- `POST /policy`
- `GET /policy/active`

Como paso MVP, `src/rhizome_sync_facade.py` sirve esos endpoints desde
JSON locales con forma de contrato compartido (`code/shared/schemas/examples`).
Es una fachada de interoperabilidad: no toca ESP32, no abre actuadores, no llama
al LLM y no sustituye la persistencia real de Rhizome. Su valor es permitir que
Floema apunte `RhizomeNetworkClient` a una IP real de Jetson mientras el backend
definitivo de sensores/SQLite termina de cerrarse.

`/summary/since` es el endpoint para el boton principal de Pollen:
"Que ha pasado desde mi ausencia?". En el MVP de demo compone un resumen
determinista con:

- conteo de riegos, bloqueos y alertas;
- severidad `ok | attention | alert`;
- estado actual de deposito y sondas de suelo A/B;
- recomendacion breve;
- localizacion `es` o `en`.

No usa el LLM todavia. Es intencional: desbloquea la UX con una pieza
testeable y segura. La evolucion natural es que Gemma 4 E2B ayude a redactar
ese resumen sobre datos ya agregados, sin cambiar hechos ni decisiones.

`POST /policy` recibe la politica transitoria que Pollen genera durante una
visita, por ejemplo desde la beta voz -> politica. El endpoint:

- acepta solo `PolicyPacket` con `policy_origin="pollen-visit"`;
- normaliza `policy_scope` a `transient`;
- exige `target_node_id` igual al `node_id` de la fachada;
- exige `valid_until` con TTL maximo de 12h;
- persiste la politica como activa para la siguiente decision;
- no valida hard limits fisicos.

Esa ultima linea es intencional. La fachada es solo schema gate y persistencia
host-side; los hard limits viven en el Mini-Evaluator de Pollen antes de enviar
la politica y en el ESP32 cuando Rhizome intenta ejecutar una accion.

Arranque local/Jetson:

```bash
cd code/rhizome
python -m src.rhizome_sync_facade --host 0.0.0.0 --port 13010
```

Prueba minima:

```bash
curl http://127.0.0.1:13010/status
curl http://127.0.0.1:13010/snapshot/latest
curl http://127.0.0.1:13010/receipts
curl "http://127.0.0.1:13010/summary/since?locale=es"
```

Smoke de politica desde Jetson:

```bash
cd code/rhizome/jetson
./smoke_policy.sh
```

Base URL para Pollen en la red local del dia 19:

```text
http://192.168.1.60:13010/
```

Para video/demo se puede simular un segundo Rhizome en el mismo Jetson:

```bash
cd code/rhizome/jetson
./start_demo_two_rhizomes.sh
```

Esto levanta:

```text
rhizome_01 -> http://192.168.1.60:13010/
rhizome_02 -> http://192.168.1.60:13020/
```

`rhizome_02` usa `code/rhizome/demo_data/rhizome_02`. Debe documentarse como
simulacion de interoperabilidad multi-Rhizome, no como segundo nodo fisico.

## Rhizome Steward v0

`src/rhizome_steward.py` cierra el bucle autonomo minimo para piloto de
maceta supervisado:

```text
ESP32 TELEMETRY -> snapshot -> safety/need gate -> optional Gemma rationale
-> optional WATER -> DecisionReceipt -> logs rotados -> facade_data
```

Propiedades de seguridad:

- no envia `WATER` salvo que se pase `--execute-water`;
- nunca supera `30s` por evento (`FIRMWARE_MAX_WATER_SECONDS_MVP`);
- aplica cooldown local antes de volver a regar;
- limita eventos autonomos por dia;
- si no entiende la humedad, aplaza;
- si deposito baja de minimo, emite `ALERT`;
- si no hay sensor de deposito, por defecto aplaza salvo permiso explicito de
  perfil minimo;
- si una lectura falta, el snapshot conserva schema valido y marca
  `pending_contradictions`;
- el `ShadowSkeptic` es experimental y no afecta la decision.

Ejecucion sin hardware:

```bash
cd code/rhizome
python -m src.rhizome_steward run-once --esp32 fake
```

Ejecucion con ESP32 real, una sola pasada, aun sin abrir agua:

```bash
python -m src.rhizome_steward run-once \
  --esp32 serial \
  --serial-port /dev/ttyACM0
```

Ejecucion con permiso explicito para mandar `WATER A <seconds>` al ESP32:

```bash
python -m src.rhizome_steward run-once \
  --esp32 serial \
  --serial-port /dev/ttyACM0 \
  --execute-water \
  --water-seconds 8
```

Si la sonda de humedad aun no esta calibrada a porcentaje, usar umbrales raw:

```bash
python -m src.rhizome_steward run-once \
  --esp32 serial \
  --serial-port /dev/ttyACM0 \
  --soil-dry-below-raw 1500 \
  --soil-wet-above-raw 2600
```

Perfil hardware minimo de maceta:

```bash
python -m src.rhizome_steward run-once \
  --esp32 serial \
  --serial-port /dev/ttyACM0 \
  --allow-missing-tank-sensor \
  --soil-dry-below-raw 1500 \
  --soil-wet-above-raw 2600
```

Este perfil existe para una ESP32 minima con bomba y sensor de humedad, mientras
caudalimetro y nivel de deposito quedan previstos pero aun no instalados. Si se
permite riego con deposito no sensorizado, el receipt conserva
`tank_level_unavailable`; si falta caudalimetro, conserva
`flow_sensor_unavailable`. Cuando esos sensores existan, quitar el flag y usar
modo estricto.

Si la humedad llega como valor raw, la polaridad debe declararse. La sonda real
del handoff de Xilema reporta `soil_a_raw < 1300` como suelo muy humedo, por lo
que el primer observe mode usa `--soil-raw-polarity low_is_wet` y
`--soil-wet-below-raw 1300`. Xilema fija para el MVP:

```text
SOIL_RAW_POLARITY=low_is_wet
SOIL_WET_BELOW_RAW=1300
SOIL_DRY_ABOVE_RAW=2200
```

Interpretacion:

- `<1300`: muy humedo, `SKIP`;
- `1300..2199`: banda ambigua, `DEFER`;
- `>=2200`: seco para MVP, candidato a `WATER_A` si pasan las demas
  barandillas.

Si la firmware minima expone el pulso fisico seguro `PUMP_PULSE <ms>`, usar:

```bash
python -m src.rhizome_steward run-once \
  --esp32 serial \
  --serial-port /dev/ttyACM0 \
  --serial-water-command-mode pump-pulse
```

No usar `pump-toggle` con el firmware de dia 26: esta build no expone
`PUMP_ON`, y Xilema autoriza la ruta `PUMP_PULSE`. `water-duration` sigue siendo
valido para builds que ejecuten `WATER A <seconds>` fisicamente en la frontera
ESP32; en la build actual `WATER A 1` responde `execution=DRY_RUN`.

Si una build del ESP32 mueve fisicamente la bomba pero conserva
`execution=TEST_ONLY` en el ACK de `PUMP_PULSE`, Rhizome no lo cuenta como riego
real por defecto. Para el perfil supervisado validado en maceta por Bea, activar
explicitamente:

```bash
ACCEPT_ESP32_TEST_ONLY_PULSE_AS_EXECUTED=1
```

Esto mantiene las lineas raw del ESP32 en `execution_details`, pero evita que
Pollen muestre el evento como bloqueado por `ESP32_TEST_ONLY`.

Persistencia por defecto:

```text
~/.local/share/sprout/rhizome_steward/
├── telemetry_samples/YYYY-MM-DD.jsonl
├── decision_receipts/YYYY-MM-DD.jsonl
├── shadow_skeptic/YYYY-MM-DD.jsonl
├── current_snapshot.json
├── last_decision_receipt.json
└── facade_data/
```

El store aplica retencion por dias y presupuesto total de bytes
(`--retention-days`, `--max-total-bytes`) para poder correr semanas/meses sin
rebosar la microSD. Para que Pollen vea el bucle real, arranca la fachada con:

```bash
python -m src.rhizome_sync_facade \
  --host 0.0.0.0 \
  --port 13010 \
  --data-dir ~/.local/share/sprout/rhizome_steward/facade_data
```

Gemma 4 E2B puede entrar como redactor contractual de rationale con el adapter:

```bash
python -m src.rhizome_steward run-once \
  --esp32 serial \
  --serial-port /dev/ttyACM0 \
  --gemma-rationale-url http://127.0.0.1:12000
```

Gemma no cambia la accion ni autoriza agua; solo mejora la explicacion sobre
facts ya decididos.

### Datos devueltos a Pollen

Rhizome devuelve siempre JSON. Pollen puede elegir idioma con `?locale=en` o
`?locale=es`; si no se indica, el fallback es `es`.

Decision de arquitectura de idioma:

- El sistema razona en contratos, no en el idioma de la interfaz.
- Los campos operacionales (`action`, `executed`, `blocked_reason`, cantidades,
  timestamps, codigos de veto) no se traducen.
- Rhizome puede devolver narrativa localizada para el MVP, pero la fuente de
  verdad sigue siendo el `DecisionReceipt`.
- Pollen es la capa responsable de experiencia linguistica. Su Gemma 4 local
  puede traducir solo la narrativa que no llegue ya localizada, segun el idioma
  activo de la interfaz.
- Esta separacion permite que, en el futuro, Pollen pueda usar fine-tuning o
  adaptacion local para idiomas minoritarios (por ejemplo Pular, Swahili o
  Wolof) sin pedir a Rhizome que cambie su logica de riego ni sus contratos.

Endpoints principales:

```text
GET /snapshot/latest
GET /receipts?since=<UTC_ZULU>
GET /explain/decision/<decision_id>?locale=en|es
GET /summary/since?since=<UTC_ZULU>&locale=en|es
```

`/receipts` devuelve `DecisionReceipt` casi canonico: `action`, `executed`,
`blocked_reason`, `action_params`, `confidence`, `rationale_short`,
`rationale_full`, `backend_used`, `contradictions`. Pollen debe tratar
`executed=false` como propuesta no ejecutada, aunque `action` sea `WATER_A`.

`/explain/decision/<id>` devuelve una explicacion localizada construida desde el
receipt. Si Gemma 4 participo antes en el steward, esa explicacion incorpora el
`rationale_*` escrito por Gemma en el receipt. Si no, usa rationale
determinista.

`/summary/since` devuelve el payload del boton principal de ausencia:

```json
{
  "headline": "...",
  "summary": "...",
  "highlights": ["..."],
  "recommendation": "...",
  "counts": {
    "total": 2,
    "water": 1,
    "water_proposed": 2,
    "water_not_executed": 1,
    "block": 0,
    "alert": 0,
    "executed": 1
  },
  "source": "deterministic_visit_summary",
  "simulation": false
}
```

Gemma 4 no es fuente de verdad para estos campos. Su papel correcto es redactar
mejor `rationale_short`/`rationale_full` y, como siguiente paso, sintetizar una
narrativa de ausencia a partir de snapshots y receipts ya validados.

#### Narrador Gemma 4 opcional

La fachada puede usar Gemma 4 E2B local como narrador del boton de ausencia:

```bash
GEMMA_VISIT_NARRATOR_URL=http://127.0.0.1:12000 \
GEMMA_VISIT_NARRATOR_MODEL=gemma4:e2b \
./start_sync_facade.sh
```

Cuando esta activo, Gemma solo puede reescribir `headline`, `summary`,
`highlights` y `recommendation`. No puede cambiar `counts`, `severity`,
`source`, `simulation`, receipts ni snapshots. Si Gemma falla, tarda demasiado o
devuelve JSON invalido, la respuesta cae al resumen determinista.

Configuracion E2B: los usos Gemma de Rhizome usan `num_predict=1024` para evitar
fallbacks silenciosos por respuestas truncadas en E2B.

Campos de trazabilidad:

```json
{
  "source": "deterministic_visit_summary",
  "narrative_source": "gemma_visit_narrator",
  "gemma_narrator": {
    "enabled": true,
    "used": true,
    "model": "gemma4:e2b"
  }
}
```
