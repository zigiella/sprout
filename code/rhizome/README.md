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
make generate-images
make generate-prompts
make test
python -m bench.run_ollama_benchmark --model gemma4:e4b --hardware-label hp-probook-460-g11
python -m bench.run_ollama_benchmark --model gemma4:e4b --hardware-label hp-probook-460-g11 --phases cold,warm,repeat --repeat 3
```

El mismo harness se reutiliza luego en Jetson cambiando solo el target del modelo/runtime.
