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

## Contrato Pollen bilingue

Ajuste posterior a conversacion con Bea: Pollen no debe leer una propuesta
`WATER_A` como riego real si `executed=false`.

Cambios:

- `/explain/decision/<id>?locale=en|es` distingue riego ejecutado de propuesta
  no ejecutada.
- `/summary/since?locale=en|es` cuenta `water` como riegos ejecutados, y anade
  `water_proposed` + `water_not_executed`.
- `simulation` ahora depende del origen de datos: demo/examples => `true`;
  `facade_data` real del steward => `false`.

Regla de producto:

> Pollen muestra narrativa bilingue; Rhizome conserva verdad operacional en
> `DecisionReceipt`. Gemma 4 puede mejorar el rationale, pero no convierte una
> propuesta no ejecutada en riego real.

Decision linguistica adicional:

- El sistema puede "pensar" internamente en el idioma que el equipo elija, pero
  su autoridad vive en contratos JSON, no en frases.
- Los codigos, acciones, cantidades, timestamps y flags de ejecucion permanecen
  estables y sin traducir.
- Pollen, con Gemma 4 local, es responsable de adaptar la experiencia al idioma
  de la interfaz y de traducir solo lo que no llegue ya localizado.
- Esto deja abierta una via fuerte de impacto: fine-tuning o adaptacion futura
  de Pollen para idiomas minoritarios africanos como Pular, sin sobrecargar a
  Rhizome ni tocar la frontera fisica.

## Narrador Gemma 4 para ausencia

Decision posterior: empezar a usar Gemma 4 de forma mas completa en Rhizome sin
cederle autoridad operacional.

Implementacion:

- `GET /summary/since` puede activar un narrador Gemma 4 mediante
  `--narrator-url` / `GEMMA_VISIT_NARRATOR_URL`.
- Gemma solo reescribe `headline`, `summary`, `highlights` y `recommendation`.
- La fuente de verdad permanece en `DecisionReceipt`, `RhizomeSnapshot`,
  `counts`, `severity`, `executed`, `blocked_reason`, `simulation` y codigos de
  seguridad.
- Si Gemma falla, devuelve texto fuera de schema o tarda demasiado, se conserva
  el resumen determinista.
- Trazabilidad nueva: `source="deterministic_visit_summary"`,
  `narrative_source="gemma_visit_narrator"` cuando se usa, y
  `gemma_narrator.used=true`.

Esta capa da mas valor demo a Gemma 4: no decide agua, pero convierte eventos
tecnicos auditables en una explicacion humana de ausencia.

## Handoff Xilema: sonda raw humeda

Xilema reporta ESP32 con bomba + humedad de suelo casi listo y lectura actual
`soil_a_raw=1263-1267`, interpretada como suelo muy humedo (`soil_a_raw < 1300`).

Ajuste de Rhizome:

- se anade polaridad raw explicita: `low_is_dry` o `low_is_wet`;
- el perfil `run_steward_serial_observe_minimal.sh` usa `low_is_wet` y
  `SOIL_WET_BELOW_RAW=1300`;
- sin `SOIL_DRY_ABOVE_RAW`, Rhizome puede hacer `SKIP` por suelo humedo, pero
  no autoriza `WATER` desde raw; fuera de la banda humeda, aplaza;
- esto evita interpretar `1265` como porcentaje o como seco por error.

## Validacion

Comandos:

```bash
python -m unittest tests.test_rhizome_steward tests.test_sync_facade
python -m py_compile code/rhizome/src/rhizome_steward.py
bash -n code/rhizome/jetson/run_steward_once.sh
bash -n code/rhizome/jetson/start_steward_loop.sh
```

Resultado:

- 29 tests OK.
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
