# Rhizome — Spec tecnica del MVP

> Rhizome es el nodo edge en parcela. Ejecuta decisiones locales seguras con Gemma 4 E2B sobre Jetson Orin Nano Super. Es el nodo mas critico del MVP: es lo que el jurado ve "hacer cosas" en el video.

Este documento es el **briefing de onboarding** para **Xilema**, dev Rhizome. Esta disenado para que pueda empezar el dia 1 sin dependencias externas.

---

## 1. Rol y responsabilidad

### 1.1 Que hace Rhizome
- Lee sensores (humedad suelo x2, caudalimetro, nivel deposito)
- Captura imagen de camara periodicamente y bajo demanda
- Interpreta la politica vigente con Gemma 4 E2B local
- Produce decisiones con razonamiento y banderas de contradiccion
- Emite comandos de riego hacia el ESP32 (nunca directamente al actuador)
- Persiste snapshots, eventos, receipts
- Sirve endpoint local para sync con Pollen
- Sigue operando sin red externa

### 1.2 Que NO hace
- No decide estrategia global (eso es Meristem)
- No sincroniza con otros Rhizome directamente (eso es Pollen)
- No tiene autoridad sobre la capa fisica (el ESP32 puede bloquear cualquier orden)
- No pide a la nube (ni API Gemini, ni Vertex, ni nada)

### 1.3 Resultado esperado
Al final del sprint, Rhizome debe poder ejecutar este flujo sin intervencion:
1. Cada 60s: lee sensores, actualiza memoria corta
2. Cada 5min: captura imagen y hace resumen visual con Gemma 4
3. Cada 15min o tras cambio significativo: evalua politica vigente con Gemma 4, decide accion
4. Cuando decide accion: envia comando al ESP32, espera ACK, registra receipt
5. Cuando Pollen se conecta: sirve snapshot completo, recibe policy deltas, acepta o rechaza segun TTL

---

## 2. Hardware objetivo

Resumen. BOM completo en [`02_bom.md`](02_bom.md).

### 2.1 Plataforma
- **Jetson Orin Nano Super Developer Kit** (8 GB RAM, 67 TOPS)
- JetPack 6.x (Ubuntu 22.04 base)
- Arranque desde microSD 256 GB (A2)
- Root filesystem en NVMe M.2 500 GB (Kingston NV3) tras setup inicial

### 2.2 Perifericos
| Componente | Modelo | Bus | Notas |
|-----------|--------|-----|-------|
| Camara | Arducam IMX219 Jetson-ready | CSI 22-pin | Kit debe incluir cable 15-22, verificar |
| Sensor humedad (x2) | DFRobot SEN0308 capacitivo | Analogico → ADS1115 | Uno por macetero |
| ADC | ADS1115 16-bit | I2C | Va dentro de caja IP65 |
| Sensor nivel deposito | DFRobot SEN0368 capacitivo sin contacto | Analogico → ADS1115 | Pegado al exterior del deposito |
| Caudalimetro | modelo por cerrar (depende de tubo) | GPIO digital (pulsos) | Decision en semana 1 |
| Meteo (solo parcela A) | Ecowitt GW3011 + WS90 868 MHz | WiFi/Ethernet del gateway | No conecta directo a Jetson; via HTTP del gateway |
| ESP32 | ESP32-S3-DevKitC-1-N8R8 | UART o I2C | Capa dura de seguridad fisica |

### 2.3 Actuacion
| Componente | Cantidad | Control |
|-----------|---------:|---------|
| Bomba (DFRobot FIT0563 o similar 12V) | 1 | Rele 1 |
| Electrovalvula 12V NC | 2 | Reles 2 y 3 |

**Decision fisica:** una bomba + dos electrovalvulas NC + tres reles = dos canales reales de riego. Una T sin valvulas NO es dos canales.

### 2.4 Arquitectura electrica
- **19 V DC** — Jetson (adaptador incluido con el Dev Kit)
- **12 V DC** — valvulas y bomba (fuente separada, ~2 A minimo)
- **5 V logico** — modulo de reles (derivado del Jetson via USB o 5V pin)
- **3.3 V logico** — GPIO Jetson

> ⚠️ **Punto critico a validar dia 1**: el modulo de reles de 4 canales que compramos debe activarse con **3.3 V logico** (los Jetson Orin Nano GPIO son 3.3V, NO 5V). Si el modulo comprado es "5V only", necesitamos level shifter o un board diferente. Verificar SKU antes de abrir caja.

---

## 3. Stack de software

### 3.1 Base del sistema
- Ubuntu 22.04 (viene con JetPack 6.x)
- Python 3.11 (instalar si JetPack trae solo 3.10)
- Docker (opcional, para correr Ollama si lo vemos limpio)

### 3.2 Runtime de inferencia

**Opcion A (preferida):** **Ollama ARM64**
- Instalacion: `curl -fsSL https://ollama.com/install.sh | sh`
- Model: `ollama pull gemma4:e2b` (~5 GB)
- API local: `http://localhost:11434/v1` (compatible OpenAI)

**Opcion B (si Ollama no rinde):** **llama.cpp compilado para Jetson con CUDA**
- Repo: https://github.com/ggerganov/llama.cpp
- Compilar con `CMAKE_ARGS="-DLLAMA_CUDA=ON"`
- Servir con `llama-server -hf ggml-org/gemma-4-E2B-it-GGUF -ngl 99`

**Opcion C (para despues del MVP):** **TensorRT-LLM**
- Maxima velocidad pero mayor complejidad de setup
- Solo si los benchmarks de A/B muestran que la inferencia es el cuello de botella

### 3.3 Dependencias Python principales
```
pydantic>=2.6
httpx>=0.27             # cliente HTTP async
fastapi>=0.110          # endpoint para Pollen
uvicorn>=0.29
smbus2>=0.4             # I2C
adafruit-circuitpython-ads1x15>=2.3
opencv-python>=4.9
# Para Jetson camera:
# picamera2 o GStreamer via nvarguscamerasrc
sqlalchemy>=2.0         # ORM sobre SQLite
pillow>=10.2
python-dotenv>=1.0
pytest>=8.0
ruff>=0.3
```

### 3.4 Dependencias del sistema
```bash
sudo apt install -y i2c-tools python3-smbus libopenjp2-7 libatlas-base-dev
sudo usermod -aG i2c $USER
# Habilitar I2C en JetPack via jetson-io si no esta ya
```

---

## 4. Arquitectura del software

### 4.1 Bucle principal (high level)
```
┌─────────────────────────────────────────────────┐
│                 main loop                        │
│  ┌──────────────┐  ┌──────────────┐             │
│  │  sensor loop │  │  vision loop │             │
│  │  (60s)       │  │  (300s)      │             │
│  └──────┬───────┘  └──────┬───────┘             │
│         │                  │                     │
│         ▼                  ▼                     │
│  ┌─────────────────────────────┐                │
│  │    state manager (SQLite)    │                │
│  └──────────┬──────────────────┘                │
│             │                                    │
│             ▼                                    │
│  ┌─────────────────────────────┐                │
│  │  policy engine (Gemma 4 E2B)│                │
│  └──────────┬──────────────────┘                │
│             │                                    │
│             ▼                                    │
│  ┌─────────────────────────────┐                │
│  │  safety gate (ESP32 talk)   │                │
│  └──────────┬──────────────────┘                │
│             │                                    │
│             ▼                                    │
│  ┌─────────────────────────────┐                │
│  │  actuation (via ESP32 ACK)  │                │
│  └─────────────────────────────┘                │
└─────────────────────────────────────────────────┘

+ sync_server FastAPI (lado)     ← Pollen conecta aqui
```

### 4.2 Layout de codigo

```
code/rhizome/
├── README.md
├── pyproject.toml
├── .env.example
├── Makefile                       # bootstrap, run, test
├── src/
│   ├── __init__.py
│   ├── main.py                    # entrypoint
│   ├── config.py                  # config via env + pydantic
│   ├── sensors/
│   │   ├── __init__.py
│   │   ├── ads1115.py             # driver ADS1115
│   │   ├── soil.py                # SEN0308 humedad
│   │   ├── reservoir.py           # SEN0368 nivel
│   │   └── flowmeter.py           # caudalimetro GPIO
│   ├── vision/
│   │   ├── __init__.py
│   │   ├── camera.py              # captura IMX219
│   │   └── summarizer.py          # Gemma 4 multimodal → texto
│   ├── policy/
│   │   ├── __init__.py
│   │   ├── engine.py              # aplica politica con LLM
│   │   ├── schemas.py             # pydantic models
│   │   └── prompts/
│   │       └── system_v1.txt
│   ├── safety/
│   │   ├── __init__.py
│   │   └── esp32_bridge.py        # UART/I2C con ESP32
│   ├── sync/
│   │   ├── __init__.py
│   │   ├── server.py              # FastAPI para Pollen
│   │   └── schemas.py             # weather_packet, policy_delta, etc
│   ├── persistence/
│   │   ├── __init__.py
│   │   ├── db.py                  # SQLite + SQLAlchemy
│   │   └── models.py              # tablas
│   └── llm_client.py              # cliente Ollama
├── policies/                      # politicas ejemplo (JSON)
│   ├── conservador_v1.json
│   ├── normal_v1.json
│   └── alerta_v1.json
└── tests/
    ├── test_sensors.py
    ├── test_policy.py
    └── test_safety.py
```

### 4.3 Contratos de datos
Schemas compartidos con Pollen y Meristem viven en `code/shared/schemas/`. Los importamos via submodule o copia manual durante el MVP.

Modelos clave (definir con pydantic):
- `RhizomeSnapshot` — estado completo en un instante
- `PolicyPacket` / `PolicyDelta` — politica vigente y cambios
- `WeatherPacket` — meteo observada (propia o prestada)
- `ContradictionAlert` — inconsistencia detectada
- `DecisionReceipt` — lo que se ejecuto (o no) y por que

---

## 5. Integraciones

### 5.1 Con ESP32 (capa dura de seguridad)
Protocolo simple sobre UART @ 115200 baud:

```
Rhizome → ESP32:
  CMD <id> <action> <params> <checksum>\n
  ej: CMD 42 WATER_A 30 7F\n      (regar parcela A, 30s max)

ESP32 → Rhizome:
  ACK <id> <status> <data>\n
  ej: ACK 42 OK flow=142ml\n
  ej: ACK 42 REJECTED reason=deposito_bajo\n

ESP32 → Rhizome (asincronos):
  EVT <event> <data>\n
  ej: EVT FLOW_INTERRUPTED cmd=42\n
  ej: EVT HEARTBEAT_LOST\n
```

Todas las comandas ejecutables:
- `WATER_A <seconds>` y `WATER_B <seconds>` (0-60s max hard-coded en firmware)
- `STOP` (para todo inmediato)
- `STATUS` (lee deposito, caudal, estado valvulas)
- `HEARTBEAT` (cada 5s, obligatorio)

Reglas duras **en el firmware** (no en Python):
- Bloquear si deposito <20%
- Bloquear si caudal no se confirma en 3s tras abrir valvula
- Bloquear si duracion >60s
- Bloquear si se pierde heartbeat >10s
- Bloquear si llega modo ALERTA

### 5.2 Con Pollen (nodo itinerante)
Rhizome expone FastAPI en `http://<rhizome-ip>:8080`:

- `GET /snapshot` — estado completo actual
- `GET /policy/active` — politica vigente
- `POST /delta/apply` — Pollen entrega policy delta, Rhizome valida y aplica o rechaza
- `POST /packet/weather` — Pollen entrega weather packet, Rhizome valida TTL y guarda
- `POST /alert/contradiction` — Pollen reporta contradiccion observada

Descubrimiento: Pollen usa mDNS (`sprout-rhizome-01.local`) o BLE advertisement con ID del nodo.

### 5.3 Con Meristem
Rhizome **no habla directamente con Meristem**. Todo pasa por Pollen. Este principio es duro.

---

## 6. Entregables del especialista

Los que la especialista Jetson debe dejar en el repo:

### 6.1 Semana 1 (dias 1-5)
- [ ] JetPack 6.x flasheado y NVMe montado como root
- [ ] Ollama funcionando con `gemma4:e2b`, benchmark documentado (tokens/s texto + tiempo multimodal)
- [ ] Camara IMX219 capturando a 1080p, confirmado via `gst-launch` o Python
- [ ] ADS1115 leyendo dos sensores de humedad via I2C
- [ ] Sensor de nivel leyendo deposito
- [ ] ESP32-S3 con firmware minimo: acepta CMD, emite ACK, hace blink (sin bomba todavia)
- [ ] UART Jetson↔ESP32 funcionando, echo test
- [ ] Entrada en `bitacora/` con benchmarks reales
- [ ] `Makefile` con `make bootstrap` funcional

### 6.2 Semana 2 (dias 6-10)
- [ ] Firmware ESP32 con reglas duras completas
- [ ] Bomba + 2 valvulas cableadas y controladas via ESP32
- [ ] Caudalimetro leyendo pulsos, calibracion documentada
- [ ] `policy_engine.py` produciendo JSON valido con Gemma 4 E2B base
- [ ] Primer test E2E: "lectura → decision → comando → ACK → receipt"
- [ ] Tests unitarios de sensors/ y safety/

### 6.3 Semana 3 (dias 11-15)
- [ ] Integracion del modelo fine-tuned `sprout-rhizome-e2b-v1`
- [ ] `sync_server.py` con endpoints FastAPI
- [ ] Integracion Pollen↔Rhizome probada (incluso mock de Pollen al principio)
- [ ] Vision loop con summarizer funcional
- [ ] Persistencia completa en SQLite

### 6.4 Semana 4 (dias 16-20)
- [ ] Demo completa E2E con los 3 nodos
- [ ] Documentacion de operacion (README exhaustivo en `code/rhizome/`)
- [ ] Caja IP65 montada y cableada
- [ ] Grabacion del B-roll tecnico para el video

---

## 7. Onboarding: primeros 3 dias

### Dia 1
1. Leer `README.md`, `CONTRIBUTING.md`, `docs/00_brief.md`, `docs/01_architecture.md`, este documento
2. Crear rama `feat/rhizome-bootstrap`
3. Flashear JetPack 6.x en microSD, arrancar Jetson
4. Correr `sudo apt update && sudo apt upgrade`
5. Instalar paquetes base del 3.3 del sistema
6. Instalar Ollama ARM64
7. `ollama pull gemma4:e2b`
8. Primer benchmark: `time ollama run gemma4:e2b "¿Que estado tiene esta planta?"` — registrar tokens/s
9. Primera entrada bitacora: `bitacora/YYYY-MM-DD_jetson-primer-arranque_<tu-nombre>.md`

### Dia 2
1. Setup NVMe como root filesystem (tutorial oficial NVIDIA)
2. Clonar repo localmente en el Jetson
3. Crear `code/rhizome/pyproject.toml` con dependencias
4. `make bootstrap` que hace pip install y validaciones iniciales
5. Test de camara via GStreamer
6. Test de I2C: `i2cdetect -y 7` (deberia ver ADS1115 en 0x48)

### Dia 3
1. Primer driver: `src/sensors/ads1115.py` leyendo canales
2. Conectar un SEN0308, validar lectura estable (test manual)
3. Primer commit real: driver + test unitario con mock
4. Abrir PR pequeno para que Cambium lo revise

---

## 8. Tests y validacion

### 8.1 Tests unitarios
- Cada driver tiene test con hardware mocked (nada de "esto solo corre con sensor conectado")
- Objetivo: >=70% cobertura en `src/`
- Correr con `make test`

### 8.2 Tests de integracion
- Test que usa el ADS1115 real, marcado como `@pytest.mark.hardware` (se salta en CI)
- Test E2E con mock de ESP32 (serial loopback)

### 8.3 Criterios de validacion del MVP
- [ ] Decision completa (lectura → politica → ACK) en <5s
- [ ] Inferencia de texto con E2B: >=5 tokens/s (no aceptable si baja)
- [ ] Inferencia multimodal (imagen + texto): <15s por decision visual
- [ ] Uptime: 24h continuas sin crash (test de estabilidad)
- [ ] Recuperacion tras corte de corriente: <60s para estado operativo

---

## 9. Benchmarks obligatorios (reportar en bitacora)

Al final de cada semana, la especialista reporta:

| Metrica | Objetivo | Como medir |
|---------|---------|-----------|
| Tokens/s texto (E2B) | >=5 | `time` sobre prompt de 200 tokens |
| Latencia decision completa | <5s | log timestamps del policy_engine |
| Latencia vision (captura + summarize) | <15s | log del vision_loop |
| RAM en uso idle | <5 GB | `free -m` con sistema corriendo |
| RAM en uso pico inferencia | <7 GB | idem durante decision |
| Consumo electrico idle | por medir | multimetro en DC in |
| Consumo electrico inferencia | por medir | multimetro |
| Temperatura pico Jetson | <70°C | `tegrastats` |

---

## 10. Workflow de colaboracion

### 10.1 Git flow
- Trabajo en ramas: `feat/rhizome-<tema-corto>` (ej. `feat/rhizome-ads1115-driver`)
- PR contra `main` cuando el feature esta listo
- Un PR = una funcionalidad coherente
- Cambium revisa arquitectura y consistencia
- PR no se mergea sin entrada en `bitacora/` correspondiente

### 10.2 Comunicacion
- Preguntas de arquitectura: entrada en bitacora con tag `pregunta-<tema>`
- Bloqueos: entrada en bitacora tipo `Bloqueo` con causa y lo que se necesita
- Decisiones tecnicas relevantes: entrada tipo `Decision`

### 10.3 Ritmo sugerido
- Daily: un commit minimo al dia (incluso si es WIP)
- Weekly: reporte en bitacora con benchmarks + blockers + proximos pasos

---

## 11. Riesgos conocidos y plan B

| Riesgo | Probabilidad | Impacto | Mitigacion |
|--------|:-----------:|:-------:|-----------|
| Ollama lento en Jetson Orin Nano | Media | Alto | Plan B: llama.cpp compilado con CUDA |
| Modulo de reles no trigger con 3.3V | Media | Alto | Verificar SKU el dia 1, plan B: level shifter o MOSFET board |
| Camara IMX219 no entrega cable 15-22 | Baja | Medio | Comprar cable por separado inmediatamente |
| Caudalimetro sin SKU coherente con tubo | Alta | Medio | Fijar bomba y diametro primero, luego cerrar caudalimetro |
| JetPack 6.x no juega bien con librerias Python especificas | Media | Medio | Docker con imagen nvcr.io/nvidia/l4t-* como fallback |
| Gemma 4 multimodal (vision) muy lento en Jetson | Media | Medio | Reducir token budget de imagen (70-140 tokens en vez de 280+) |
| ESP32-S3 no acepta firmware a la primera | Baja | Bajo | Tiene bootloader robusto, hay 1000 tutoriales |

---

## 12. Fuera de alcance para el MVP

- Multi-tenant Rhizome (multiples nodos en un repo)
- OTA firmware updates
- Battery + solar autonomo completo (se documenta, no se ejecuta)
- Dashboard web local
- TensorRT-LLM optimizacion extrema
- RAG con base de conocimiento agricola

---

## 13. Referencias

- [NVIDIA Jetson Orin Nano Super guide](https://developer.nvidia.com/embedded/learn/get-started-jetson-orin-nano-devkit)
- [JetPack 6 release notes](https://docs.nvidia.com/jetson/archives/r36.3/ReleaseNotes/index.html)
- [Ollama on ARM64](https://github.com/ollama/ollama/blob/main/docs/linux.md)
- [llama.cpp CUDA build](https://github.com/ggerganov/llama.cpp#cuda)
- [GEMMA4-SKILL.md](../GEMMA4-SKILL.md) secciones 2, 4.2, 4.4
- [docs/11_pollen_spec.md](11_pollen_spec.md) — protocolo de sync
- [docs/12_meristem_spec.md](12_meristem_spec.md) — schemas compartidos
- [docs/02_bom.md](02_bom.md) — BOM actualizado v4
