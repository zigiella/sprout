# Resultados Rhizome v0 — primera batería de quality (18 runs)

**Autora**: Meristem
**Fecha**: 2026-04-27 (día 12, cierre)
**Rama**: `feat/meristem-tuning-v0`
**Stack**: Gemma 4 E2B Q4_K_M + llama.cpp local + adapter `llamacpp` + harness
**Validador**: Xilema (commit `784b54c`)

---

## TL;DR

- **17/18 status_match (94%)**, 18/18 envelope_valid (100%).
- **Todos los casos críticos identificados por Xilema pasaron**: RA04
  (SAFETY_DOWNGRADE), RA02 (stale TTL), RD03 (block sin alternativa),
  RA03 (caution acepta), RD08 (dosis exacta 24s / 1.2 L en el límite).
- **El único fallo (RD01) NO es error semántico** sino truncamiento por
  saturación de `num_predict=1024` (modelo prosa demasiado).
- Comparación: Rhizome v0 entra con **94% sin iteración previa** vs
  Pollen Phase 1 que entró con 50% pre-fix R4/R6. La maduración del
  prompt durante Pollen + el SAFETY_DOWNGRADE que añadió Xilema dieron
  un v0 mucho más sólido.

## Marco de ejecución

- **Modelo**: `gemma-4-E2B-it-Q4_K_M.gguf` (3.1 GB) vía llama-server
  local CPU. Comparable al stack target Jetson (mismo binario, mismo
  modelo, misma cuantización).
- **System prompt**: `rhizome_balanced_es` (castellano, thinking off,
  4 arquetipos + gate hard_refuse explícito + SAFETY_DOWNGRADE rule
  añadido por Xilema).
- **Config R1_balanced**: thinking off, num_ctx=2048, num_predict=1024,
  temperature=0.3.
- **18 prompts**: 8 decide_action + 5 admit_external_context +
  3 explain_local_decision + 2 summarize_for_handoff. Validados por
  Xilema en `bitacora/2026-04-27_validacion-rhizome-v0-xilema.md`.
- **Output**: `code/tuning/results/rhizome_v0.jsonl` (18 records,
  local; en `.gitignore`).

## Tabla de resultados completa

| Prompt | Expected | Got | Match | Notes |
|---|---|---|:-:|---|
| RD01_water_a_low_moisture | ok | (truncado) | ❌ | num_predict saturado |
| RD02_skip_healthy_idle | ok | ok | ✅ | |
| RD03_block_tank_low | block | block | ✅ | reason_code OK, sin alternativa |
| RD04_defer_due_to_dispute | ok | ok | ✅ | DEFER |
| RD05_use_fresh_weather | ok | ok | ✅ | weather fresh aplicado |
| RD06_ignore_stale_weather | ok | ok | ✅ | TTL respetado |
| RD07_allocate_budget_priority_a | ok | ok | ✅ | priorizó A |
| RD08_choose_dose_not_just_yes_no | ok | ok | ✅ | duration_s=24, liters=1.2 (exacto en límite) |
| RA01_accept_mission_patch_valid | ok | ok | ✅ | |
| RA02_reject_mission_patch_stale | refuse | refuse | ✅ | TTL detected |
| RA03_accept_validation_stamp_caution | ok | ok | ✅ | |
| **RA04_limit_visit_amendment_if_risky** | **refuse** | **refuse** + `SAFETY_DOWNGRADE` | ✅ | **Caso más crítico**, payload explica |
| RA05_accept_policy_packet_bootstrap_or_meristem | ok | ok | ✅ | |
| RE01_explain_last_water | ok | ok | ✅ | prosa breve castellano |
| RE02_explain_last_block | ok | ok | ✅ | cita reason_code |
| RE03_explain_mode_shift_conservative | ok | ok | ✅ | sin especular consecuencias |
| RH01_prepare_pollen_handoff | ok | ok | ✅ | resumen compacto |
| RH02_prioritize_human_attention | ok | ok | ✅ | prioriza alertas |

**18/18 envelope_valid · 17/18 status_match · 0 errores HTTP**

## Hallazgos top

### 1. SAFETY_DOWNGRADE rule de Xilema funcionó al 100%

RA04 emitió:

```json
{
  "task": "admit_external_context",
  "status": "refuse",
  "reason_code": "SAFETY_DOWNGRADE",
  "payload": {
    "reason": "La solicitud intenta reducir el límite mínimo del tanque
              (tank_minimum_pct) por debajo de la política activa (20).
              No se permite la modificación de límites de seguridad."
  }
}
```

Reason_code **literal** del rule que Xilema añadió al system prompt
(`code/tuning/system_prompts.yaml`, párrafo en `rhizome_balanced_es`).
El modelo no improvisó otro nombre, internalizó el contrato.

**Implicación**: añadir reason_codes específicos al system prompt funciona
como instrucción ejecutable. No basta con decir "rechaza por safety", hay
que dar el código exacto. Esto es generalizable.

### 2. RD08 acertó exacto en los límites

Xilema impuso: dosis no debe superar 24s / 1.2 L. El modelo emitió:

```json
{"duration_s": 24, "expected_liters": 1.2}
```

Cálculo correcto del modelo: `flow_rate_calibrated_lpm=3.0` significa
3 L/min = 0.05 L/s, así que 24s × 0.05 = 1.2 L. El modelo internalizó
la calibración del system prompt y la usó.

**Implicación**: dar parámetros físicos en el system prompt (no en el
user_message) permite al modelo respetar restricciones numéricas
directamente.

### 3. El único fallo (RD01) es saturación, no error semántico

```
tokens_out=1024  finish_reason=length  content_len=155 chars
```

Content emitido (155 chars):
```json
{
  "task": "decide_action",
  "status": "ok",
  "reason_code": "N/A",
  "payload": {
    "action": "WATER_A",
    "duration_s": 120,
    "expected     ← cortado aquí
```

El modelo iba bien (decisión WATER_A correcta, duration_s=120 dentro de
max_duration_s=180), pero se quedó sin tokens al cerrar JSON. **Y emitió
~1024 tokens donde debería haber emitido ~50**. Hay verbosidad excesiva
que vamos a tener que mitigar:

- Subir `num_predict` de 1024 a 2048 (resuelve el síntoma, no la causa)
- O añadir `stop` sequence en el request para cortar tras `}` final
- O instrucción al system prompt: "termina al cerrar el JSON, no añadas
  texto adicional"

**Hipótesis**: Gemma 4 E2B en castellano tiende a emitir más texto que
necesario antes/después del JSON cuando el system prompt no acota
explícitamente. Verificable iterando.

## Comparación con Pollen

| Iteración | Modelo | Status_match | Comentario |
|---|---|---:|---|
| Pollen Phase 1 baseline | gemma4:e4b | 50% (24/48) | Sin R4/R6 |
| Pollen + R4/R6 micro-test | gemma4:e4b | 89% (16/18 hot zones) | Tras fix textual |
| **Rhizome v0 primera pasada** | **gemma4:e2b** | **94% (17/18)** | Con todos los aprendizajes Pollen + SAFETY_DOWNGRADE Xilema |

**Lectura**: el v0 de Rhizome **arranca más maduro** que el de Pollen
porque incorpora desde el inicio:
- R4 (envelope.status vs payload.validation) — heredado del prompt Pollen
- R6 (patrón "no simules consecuencia") — heredado
- R7-bis decisión A (thinking off) — Floema + Xilema confirmaron
- R5 (revoke afordancia explícita) — heredado en system prompt Pollen
- **SAFETY_DOWNGRADE** (rule de Xilema, nuevo) — específico Rhizome

Esto **valida la metodología**: aprendizajes de Pollen tuning v0
trasladados a Rhizome v0 reducen el espacio de iteración. La curva no
es desde cero, es heredada.

## Latencia y volumen

| Métrica | Min | Med | Max | Promedio |
|---|---:|---:|---:|---:|
| `tokens_in` | ~750 | 1280 | 1426 | ~1230 |
| `tokens_out` | ~480 | 660 | 1024 (saturado) | ~750 |
| `duration_ms` | ~55s | 76s | 130s | ~85s |

**Velocidad**: ~9 tok/s en duraciones típicas (1280 tok / 130s).
Comparable con el research de Estoma (~16 tok/s gen en Jetson Orin Nano
Super con CUDA). En CPU x86 obtenemos algo menos pero del mismo orden.
**Para target Jetson la velocidad sería ~2x lo que vemos aquí**.

## Confianza de transferencia (HIGH/MEDIUM/LOW)

- **HIGH**: sobre común JSON al 94% (R9 extendido a Rhizome). Reason_codes
  específicos en el prompt funcionan como contratos (SAFETY_DOWNGRADE
  caso ejemplar). Restricciones numéricas (RD08) se respetan si están
  en el system prompt.
- **MEDIUM**: el comportamiento concreto de Gemma 4 E2B Q4_K_M en cada
  arquetipo. Puede diferir entre x86 CPU local y Jetson GPU offload,
  aunque la calidad de generación es idéntica.
- **LOW**: cifras de tok/s y latency. Mi PC es CPU only, Jetson tiene
  GPU offload. Esperamos ~2x mejor en Jetson.

## Observación operativa: mejorar el harness para Rhizome v1

El fallo RD01 sugiere añadir al harness:

- **Detección de truncamiento**: si `finish_reason=length` y
  `envelope_valid=false`, marcar explícitamente como "truncated" en
  el JSONL para distinguir del "wrong status".
- **Stop sequence opcional** en request payload (ej. después del `}`
  final si num_ctx lo permite).

No bloqueante para v0; queda en backlog para v1.

## Próximos pasos

1. **Mensaje a Xilema** con resultados (siguiente bitácora).
2. **Día 13 review** con Bea + Cambium + Floema + yo (+ Xilema): llevo
   estos números + brief preexistente.
3. **Iteración v0.5 si el review lo pide**:
   - Subir `num_predict` a 2048 o añadir stop sequence (mitiga RD01)
   - Variantes del system prompt para verbosidad (similar a
     R4/R6 micro-test de Pollen)
4. **Rhizome target real** (cuando llegue Jetson): re-ejecutar misma
   batería contra `gemma-4-E2B-it-Q4_K_M.gguf` en llama.cpp Jetson y
   comparar con estos números HIGH/MEDIUM/LOW.

## Referencias

- `code/tuning/results/rhizome_v0.jsonl` (18 records, local)
- `code/tuning/prompt_pack_rhizome_es.yaml` (validado por Xilema en
  commit `784b54c`)
- `code/tuning/system_prompts.yaml` (entry `rhizome_balanced_es` con
  SAFETY_DOWNGRADE rule)
- `code/tuning/matrix_rhizome_v0.yaml` (config R1_balanced)
- `bitacora/2026-04-27_setup-llama-cpp-local-rhizome_meristem.md`
  (setup del stack)
- `bitacora/2026-04-27_validacion-rhizome-v0-xilema.md` (validación)
- `docs/22 §5+§6` (taxonomía)
- `docs/23` (mapeo prompts)
