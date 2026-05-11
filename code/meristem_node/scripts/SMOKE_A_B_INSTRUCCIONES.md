# Smoke A+B día 26 — instrucciones para lanzar con Claude cerrado

Script auto-contenido. Hace todo el smoke E2E sin intervención humana.
Ideal para lanzarlo, cerrar Claude, esperar 5-10 min, y al volver
revisar resultados.

---

## Lanzar

### Opción 1 — con E4B (recomendado, modelo de producción Meristem)

```bash
cd C:\DATA\PETS\TEST\T6-GEMMA\code\meristem_node
python scripts/smoke_a_b_auto.py --model e4b > smoke_d26_e4b.log 2>&1
```

**Pre-requisito**: al menos **10 GB de RAM libre**. Si Claude está
cerrado + Bract + Floema parados, debería caber. Si OOM, el script
detecta el fallo y aborta limpio.

### Opción 2 — con E2B (fallback si OOM)

```bash
cd C:\DATA\PETS\TEST\T6-GEMMA\code\meristem_node
python scripts/smoke_a_b_auto.py --model e2b > smoke_d26_e2b.log 2>&1
```

**Pre-requisito**: ~3-4 GB RAM libre. Casi siempre cabe.

**Nota honesta**: con E2B, el smoke valida que el pipeline funciona,
pero **NO ejercita tool calling** (verificado día 26 mañana). Para
ver `compare_targets` invocado en directo necesitas E4B.

---

## Mientras corre

El script tarda **~5-10 minutos** total (con E4B puede subir a
~15 min). Salida en tiempo real al log file. Puedes mirar progreso con:

```bash
tail -f smoke_d26_e4b.log
```

Etapas:
1. Limpia procesos viejos en puertos 8080, 11435, 13000 (~3s)
2. Arranca llama-server con el modelo (~60-90s la primera vez)
3. Arranca adapter en :11435 (~5s)
4. Arranca meristem-node en :13000 (~5s)
5. Caso 1 — seed rhizome_02 (~60-180s)
6. Caso 2 — bundle M7 con compare_targets demo (~60-180s)
7. Caso 3 — POST /chat sobre alerta rhizome_01 (~60-180s)
8. Guarda `results_d26_smoke.json` + imprime resumen
9. Apaga todo limpio

---

## Al volver — qué revisar

### 1. El log completo

```bash
type smoke_d26_e4b.log
```

Al final verás un bloque grande:

```
==============================================================================
SMOKE A+B DIA 26 — RESUMEN
==============================================================================
Modelo:       e4b
num_predict:  256
Branch:       feat/meristem-d26-smoke-script

--- seed_rhizome_02 ---
  latency: ... ms
  http:    200
  status:  ok  reason: STABLE_BUNDLE
  mode:    llm  parsed_ok: True  finish: stop
  tokens_out: ...
  tools:   ninguna invocada en runtime
  rationale (240): Tu Rhizome sigue funcionando bien. ...

--- bundle_M7 ---
  latency: ... ms
  http:    200
  status:  ok  reason: PERSISTENT_EMERGENCY
  mode:    llm  parsed_ok: True  finish: stop
  tokens_out: ...
  TOOLS INVOKED (1):           ← LO QUE QUEREMOS VER
    - compare_targets({'target_a': 'rhizome_01', ...})
  rationale (240): Detectamos una emergencia persistente en rhizome_01;
                   comparándolo con rhizome_02 (estable), parece...

--- chat_alert ---
  latency: ... ms
  http:    200
  mode:    llm
  answer (300): Según la policy pkt_meristem_xxx la alerta...

==============================================================================
VEREDICTO: ...
==============================================================================
```

### 2. El JSON detallado

```bash
type results_d26_smoke.json
```

Contiene todo (llm_metrics completos, conversation_id, evidence_refs).

### 3. Logs del stack (si algo raro)

```bash
type scripts\_smoke_logs\llama-server.log
type scripts\_smoke_logs\adapter.log
type scripts\_smoke_logs\meristem.log
```

---

## Qué tiene que pasar (criterios de éxito)

### Mínimo (pipeline funcional)

- ✅ Los 3 casos terminan sin error
- ✅ `mode: llm` en los 3 (no `stub_fallback`)
- ✅ `parsed_ok: True` en los 2 visits
- ✅ `finish_reason: stop` (no `length` ni `timeout`)

### Ideal (lo que queremos validar con E4B)

- 🎯 **Bundle M7 invoca `compare_targets`** → `tool_calls_log` con
  al menos 1 entrada con `name: "compare_targets"`
- 🎯 **`/chat` cita policy_id real** en `evidence_refs` (no array vacío)
- 🎯 Rationale natural en castellano que cite "rhizome_01" y "rhizome_02"
  (no placeholders tipo `[Aquí iría...]`)

Si el mínimo se cumple pero el ideal no, **igualmente es válido para
demo**: el pipeline está, las capacidades funcionan, falta calidad
fina (que normalmente requiere ajuste de prompts en iteraciones
post-MVP).

---

## Si OOM o algo falla

El script imprime el veredicto y guarda JSON parcial incluso si algo
peta. Caminos posibles:

| Síntoma | Diagnóstico | Acción |
|---|---|---|
| `llama-server timeout` con E4B | OOM probable | Relanzar con `--model e2b` |
| `mode: stub_fallback` con E2B | num_predict insuficiente | Relanzar con `--num-predict 1536` |
| Adapter no arranca | Falta dep Python | `cd code/meristem_inference_adapter && pip install -e .` |
| Meristem no arranca | Falta dep | `cd code/meristem_node && pip install -r requirements.txt` |
| Ollama del usuario en :11434 | OK, no conflicto | El script usa :11435 deliberadamente |

---

## Cleanup garantizado

Aunque el script falle, hace cleanup en `finally`:
- Kill llama-server, adapter, meristem
- Borrar BBDD demo (`meristem_node.db`)

Si por alguna razón quedan procesos colgados:

```powershell
# PowerShell
Get-Process | Where-Object { $_.Name -in @('llama-server', 'python') -and $_.CommandLine -match 'meristem|llama' } | Stop-Process -Force
```

O más bruto (mata todo Python — cuidado):

```powershell
Stop-Process -Name python -Force
```

---

## Cuando termines

Pásame el contenido de `smoke_d26_*.log` cuando vuelva a estar
disponible y analizo. Si veo `TOOLS INVOKED` con `compare_targets`
en bundle M7, **es el material para video que necesitamos** y queda
zanjado el riesgo abierto del día 24.

---

— Meristem
