# Endodermis — Rhizome Steward v0

**Fecha:** 2026-05-10 (dia 24)
**Rama:** `feat/endodermis/rhizome-steward-v0`
**Frente:** Rhizome Jetson / autonomia minima de maceta

---

## Pregunta de Bea

Necesitamos pasar de fachada + demo a autonomia minima verdadera:

- que Rhizome pueda controlar una maceta;
- que recoja datos;
- que rote logs para semanas/meses sin rebosar microSD;
- que use mejor Gemma 4;
- que explore doble agente sin afectar aun al resultado.

## Decision

Implemento `Rhizome Steward v0`, un bucle host-side pequeno y testeable:

```text
ESP32 heartbeat -> ESP32 telemetry -> snapshot -> deterministic gate
-> optional Gemma rationale -> optional WATER -> DecisionReceipt
-> bounded JSONL store -> facade_data para Pollen
```

## Alcance

El steward:

- lee telemetria de ESP32 real por serie o de `FakeESP32Client`;
- envia heartbeat antes de decidir y antes de `WATER`;
- decide con gates deterministas;
- por defecto no manda agua salvo `--execute-water`;
- respeta maximo firmware MVP `30s`;
- aplica cooldown;
- limita riegos autonomos por dia;
- aplaza si no entiende humedad;
- escribe `DecisionReceipt`;
- escribe `telemetry_samples/YYYY-MM-DD.jsonl`;
- escribe `shadow_skeptic/YYYY-MM-DD.jsonl`;
- escribe `current_snapshot.json`;
- escribe `facade_data/` compatible con `rhizome_sync_facade`;
- aplica retencion por dias y presupuesto total de bytes.
- mantiene `RhizomeSnapshot` compatible con schema compartido incluso cuando
  una lectura falta: no inventa riego, marca `pending_contradictions` y aplaza.
- soporta perfil hardware minimo de maceta: ESP32 con bomba + humedad, mientras
  deposito y caudalimetro quedan previstos como sensores futuros.

## Persistencia

Default:

```text
~/.local/share/sprout/rhizome_steward/
```

Default de retencion:

- `retention_days=120`
- `max_total_bytes=64 MiB`

Esto no sustituye al SSD, pero permite correr dias/semanas/meses de piloto de
maceta sin escribir sin control sobre microSD.

## Gemma 4

Gemma 4 E2B puede entrar por `--gemma-rationale-url`, apuntando al adapter
Ollama-compatible/llama.cpp:

```bash
--gemma-rationale-url http://127.0.0.1:12000
```

Regla de seguridad:

- Gemma no cambia la accion;
- Gemma no autoriza agua;
- Gemma no inventa facts;
- Gemma solo mejora `rationale_short` sobre decision ya cerrada.

Esto hace a Gemma mas visible y util sin romper la arquitectura: inteligencia
local para explicacion contractual, no actuacion fisica.

## Doble agente experimental

Activo por defecto:

```text
ShadowSkeptic deterministic_shadow_skeptic_v0
```

Registra:

- accion revisada;
- si objetaria;
- concerns;
- accion recomendada;
- `affects_decision=false`.

No puede cambiar el resultado. Sirve para recoger datos y decidir despues si
un `ShadowSkeptic` LLM merece pasar a produccion.

## Comandos

Sin hardware:

```bash
cd code/rhizome
python -m src.rhizome_steward run-once --esp32 fake
```

ESP32 real sin agua:

```bash
python -m src.rhizome_steward run-once \
  --esp32 serial \
  --serial-port /dev/ttyACM0
```

ESP32 real con permiso explicito de agua:

```bash
python -m src.rhizome_steward run-once \
  --esp32 serial \
  --serial-port /dev/ttyACM0 \
  --execute-water \
  --water-seconds 8
```

Wrappers Jetson:

```bash
cd ~/sprout/code/rhizome/jetson
./run_steward_once.sh
ESP32_MODE=serial ESP32_PORT=/dev/ttyACM0 ./run_steward_once.sh
ESP32_MODE=serial ESP32_PORT=/dev/ttyACM0 ./start_steward_loop.sh
```

Perfil minimo sin sensor de deposito instalado:

```bash
ESP32_MODE=serial ESP32_PORT=/dev/ttyACM0 \
  ALLOW_MISSING_TANK_SENSOR=1 \
  ./run_steward_once.sh
```

Si la firmware inicial solo expone encender/apagar bomba:

```bash
ESP32_MODE=serial ESP32_PORT=/dev/ttyACM0 \
  SERIAL_WATER_COMMAND_MODE=pump-toggle \
  ./run_steward_once.sh
```

Decision: por defecto falta de deposito aplaza. El perfil minimo exige flag
explicito y deja `tank_level_unavailable`/`flow_sensor_unavailable` en trazas.

## Validacion

Comandos:

```bash
python -m unittest tests.test_rhizome_steward tests.test_sync_facade
python -m py_compile code/rhizome/src/rhizome_steward.py
bash -n code/rhizome/jetson/run_steward_once.sh
bash -n code/rhizome/jetson/start_steward_loop.sh
```

Resultado:

- 21 tests OK.
- Compilacion OK.
- Sintaxis shell OK.
- `RhizomeSnapshot` y `DecisionReceipt` emitidos por el caso de sensor
  desconocido validan contra `code/shared/schemas`.
- CLI directo `run-once --esp32 fake` escribe estado, receipts, shadow y
  `facade_data`.

## Limites honestos

- No he cambiado firmware ESP32.
- No he tocado actuadores.
- El riego real requiere `--execute-water`.
- Si la humedad llega como raw sin calibrar, hay que pasar umbrales raw.
- El SSD sigue recomendado para operacion larga y modelo, pero no bloquea un
  piloto de maceta con logs rotados.

## Veredicto

Esta pieza convierte Rhizome de "fachada de demo + runtime de inferencia" en
"steward minimo de parcela". Sigue siendo prudente, pero ya tiene ciclo,
memoria, receipts y experimento de doble agente no vinculante.
