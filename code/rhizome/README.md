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

Como paso MVP, `src/rhizome_sync_facade.py` sirve esos cuatro endpoints desde
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
