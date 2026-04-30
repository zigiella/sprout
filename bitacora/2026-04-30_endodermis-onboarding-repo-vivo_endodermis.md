# Onboarding repo vivo - Endodermis

**Autora:** Endodermis  
**Fecha:** 2026-04-30  
**Dia de proyecto:** 15  
**Rama:** `feat/endodermis/jetson-llamacpp-bringup`  
**Base actualizada:** `main` hasta `20951a5`  

## 1. Estado de arranque

Empiezo dia 15 desde repo vivo actualizado:

- `main` actualizado por fast-forward desde `e483cf8` hasta `20951a5`.
- mi rama `feat/endodermis/jetson-llamacpp-bringup` rebasada correctamente sobre ese `main`.
- arbol limpio antes de escribir esta bitacora.
- commits propios previos conservados encima de `main` actualizado:
  - `docs(endodermis): document onboarding`
  - `docs(endodermis): close day 14`

## 2. Documentos releidos o incorporados hoy

Releidos del repo vivo:

- `README.md`
- `docs/00_brief.md`
- `docs/01_architecture.md`
- `docs/10_rhizome_spec.md`
- `docs/13_esp32_spec.md`
- `docs/20_data_contracts.md`
- `docs/30_safety_rules.md`
- `docs/40_pitch_video.md`
- `docs/51_rhizome_gemma4_e2b_jetson_guide.md`
- `docs/23_rhizome_prompt_mapping_v0.md`
- `bitacora/2026-04-22_pivote-v2-constitucion-sprout_bea.md`
- `bitacora/2026-04-28_review-meeting-tuning_cambium.md`

Nuevos o relevantes tras actualizar `main`:

- `bitacora/2026-04-27_bme280-i2c-primer-sensor_xilema.md`
- `bitacora/2026-04-27_rhizome-explain-json-contract_xilema.md`
- `bitacora/2026-04-29_firmware-veto-codes-english_xilema.md`
- `hardware/host_tools/scenarios/guardian_demo.json`
- `hardware/host_tools/scenarios/bme280_disconnected_baseline.json`
- `hardware/host_tools/scenarios/bme280_connected_smoke.json`

Siguen ausentes en `main` los tres documentos de Meristem citados en el mensaje de Cambium:

- `bitacora/2026-04-29_mensaje-cambium-cierre-dia_meristem.md`
- `bitacora/2026-04-29_tabla-tres-agentes-writeup_meristem.md`
- `bitacora/2026-04-29_directrices-estrategicas-hackathon_meristem.md`

Tambien sigue ausente `code/tuning/`, aunque el plan operativo lo trata como fuente de `system_prompts.yaml` y `prompt_pack_rhizome_es.yaml`.

## 3. Cambios importantes respecto a mi lectura de dia 14

### 3.1 Codigos de veto ESP32 ya alineados en ingles

Mi principal gap de ayer queda resuelto por Xilema en `bitacora/2026-04-29_firmware-veto-codes-english_xilema.md`.

Cambios aplicados:

- `HEARTBEAT_PERDIDO` -> `JETSON_HEARTBEAT_LOST`
- `DEPOSITO_BAJO` -> `TANK_LOW`
- `FUERA_DE_RANGO` -> `EVENT_DURATION_OUT_OF_RANGE`
- `SIN_CAUDAL` -> `NO_FLOW_DETECTED`
- `ALERTA_LATCHED` -> `ALERT_LATCHED`

`guardian_demo.json` ya espera `JETSON_HEARTBEAT_LOST`, `TANK_LOW` y `ALERT_LATCHED`. Xilema deja evidencia fisica de `guardian_demo` y `telemetry_stub_roundtrip` en `COM5` con `success=True`.

### 3.2 Primer sensor real: BME280 por I2C

Xilema integro BME280 como primer periferico real no critico:

- `GPIO8` como SDA
- `GPIO9` como SCL
- `I2C port = 0`
- `100 kHz`
- comandos `I2C_SCAN`, `BME280_PROBE`, `BME280_READ`
- telemetria enriquecida con `bme280_valid`, temperatura, humedad y presion

La estrategia me parece buena: validar I2C con un sensor de bajo riesgo antes de entrar en entradas criticas como ADS1115/humedad/nivel.

### 3.3 Contrato JSON para explicaciones a Pollen

`GET /explain/decision/{id}` queda fijado como JSON object:

```json
{
  "explanation": "..."
}
```

No debe devolver texto plano ni texto crudo del modelo. Es una decision pequena pero muy sana: protege a Pollen/Retrofit de errores de serializacion en demo.

### 3.4 Meristem/Pollen avanzan fuera de esta rama

El mensaje de Cambium informa que Floema cerro el compromiso del bloque 3: `MeristemNetworkClient`, `VisitarMeristemScreen`, `FieldVisit.kt` y `PolicyPacket.kt`. En este checkout yo todavia no he revisado ese codigo porque no aparece como cambio de `main` en el pull de esta manana.

## 4. Verificacion Safety & Trust

Resultado: **lo considero verificado a nivel operativo, con una cautela de trazabilidad**.

Evidencia:

- Bea pego el contenido de la pagina oficial de Kaggle con `Safety & Trust` como Impact Track.
- La URL oficial de Kaggle responde: `https://www.kaggle.com/competitions/gemma-4-good-hackathon/overview`, aunque desde herramienta automatica no expone texto plano util por ser pagina dinamica.
- Busqueda web externa devuelve copias/publicaciones indexadas que listan `Safety & Trust` como area del hackathon, en linea con el material aportado por Bea.

Conclusion para estrategia:

- Sprout puede contar **Safety & Trust** como cuarta apuesta plausible junto a Main Track, Impact Global Resilience y Special Tech `llama.cpp`.
- Para writeup o claim formal, recomiendo que Cambium/Bea guarden captura o cita manual de la pagina Kaggle visible en navegador, porque la extraccion automatica no deja cita oficial limpia.

## 5. Estado tecnico real por frente

### Rhizome Jetson

La especificacion fija Gemma 4 E2B via `llama.cpp`, no Ollama, por limite real de Jetson Orin Nano Super. `docs/51` usa `llama-server` con `unsloth/gemma-4-E2B-it-GGUF:Q4_K_S`.

Gap operativo:

- `code/rhizome/bench/run_ollama_benchmark.py` sigue hablando API Ollama `/api/generate`.
- Para `llama-server` hace falta confirmar adapter compatible o runner OpenAI-compatible.
- El mensaje operativo menciona `Q4_K_M`; `docs/51` fija `Q4_K_S`. Hay que cerrar una cuantizacion antes de medir.

### Rhizome v0.5 quality harness

El review dia 13 aprueba `rhizome_balanced_es_v05` como base v1 hasta validacion Jetson. Smoke cases obligatorios: `RA04`, `RD03`, `RD08`, `RD01`.

Gap operativo:

- `code/tuning/` no esta en `main`.
- sin `system_prompts.yaml` ni `prompt_pack_rhizome_es.yaml`, no puedo ejecutar la bateria v0.5 real.

### ESP32 / frontera fisica

Mucho mas solido que ayer:

- codigos de veto en ingles ya aplicados;
- `guardian_demo` actualizado;
- BME280 como primera ruta I2C;
- harness host-side mejora errores de puerto serie fantasma;
- DRY_RUN sigue siendo el carril seguro para integracion.

### Contratos compartidos

`docs/20_data_contracts.md` describe contratos v2, incluyendo `MissionPatch`, `WeatherDigest`, `ValidationStamp`, `VisitAmendment`, `FieldVisit`, `SyncBundle` y `DecisionExplanationResponse`.

Gap:

- `code/shared/schemas/` sigue exportando v1 (`PolicyDelta`, `WeatherPacket`, `ContradictionAlert`) y no veo aun los modelos Pydantic v2 completos.

## 6. Verificacion local intentada

Intente ejecutar:

```powershell
python -m pytest hardware\host_tools\tests
```

Resultado:

- no se ejecuto la suite porque `C:\Python312\python.exe` no tiene `pytest` instalado.
- no lo considero fallo de codigo ni del harness.
- no instalo dependencias hasta que Cambium/Xilema confirmen entorno recomendado para repo vivo/Jetson.

## 7. Plan operativo concreto

### Dia 15

- Completar lectura de los tres documentos de Meristem cuando Bea/Cambium los pase por mensaje o entren al repo.
- Conversacion con Xilema + Cambium:
  - frontera fisica y propiedad del ESP32;
  - `guardian_demo` y `telemetry_stub_roundtrip`;
  - evidencia de codigos de veto en ingles;
  - ruta BME280 y limites de lo que no debo tocar;
  - bundle minimo Rhizome que Meristem necesita;
  - ruta de benchmark Jetson contra `llama-server`.
- Confirmar entorno Python/pytest recomendado para validaciones sin hardware.
- Cerrar decision `Q4_K_S` vs `Q4_K_M`.

### Dia 16

- Bring-up Jetson real:
  - JetPack 6.x;
  - modo MAXN SUPER;
  - Docker/runtime NVIDIA;
  - NVMe/cache si aplica;
  - `llama-server` con Gemma 4 E2B GGUF;
  - smoke request y evidencia de endpoint.

### Dia 17

- Ejecutar RA04, RD03, RD08, RD01 cuando `code/tuning/` este disponible.
- Comparar con baseline x86 de Meristem: tok/s, latencia, estabilidad de JSON/envelope.
- Acompanamiento a Xilema en USB-CDC nativo y DRY_RUN si ella lo pide.

### Dia 18

- Dejar Rhizome Jetson demo-ready o, si aparece regresion, dejarla reproducible con transcript y propuesta de fix minimo.

## 8. Preguntas abiertas

1. ¿Me pasais por mensaje los tres documentos de Meristem y/o la rama donde viven? Siguen sin aparecer en `main`.
2. ¿Donde esta `code/tuning/` con `system_prompts.yaml` y `prompt_pack_rhizome_es.yaml`? Sin eso no puedo ejecutar v0.5 real.
3. ¿La ruta aprobada para benchmark Jetson es adaptar el runner Ollama a `llama-server`, usar un adapter Ollama-compatible intermedio, o crear runner OpenAI-compatible separado?
4. ¿Fijamos `Q4_K_S` por coherencia con `docs/51` o `Q4_K_M` por indicacion operativa de Cambium?

## 9. Cierre de lectura

La foto del repo vivo es mejor que la de ayer: Xilema ya cerro el gap de codigos de veto, el ESP32 tiene mas evidencia real y el contrato de explicacion para Pollen esta mas fino.

La pieza critica que aun no puedo tocar es Rhizome v0.5 en Jetson, porque falta el harness de calidad real (`code/tuning/`). En cuanto aparezca, mi siguiente trabajo natural es convertir la lectura de hoy en ejecucion medible sobre hardware.
