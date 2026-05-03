# Dia 18 - Frente GPU offload Jetson

**Autora:** Endodermis  
**Fecha:** 2026-05-03  
**Dia de proyecto:** 18  
**Rama:** `feat/endodermis/jetson-gpu-offload-day18`

## 1. Objetivo

Bea prioriza abrir primero el frente GPU.

Objetivo acotado:

- diagnosticar por que Gemma 4 E2B Q4_K_S no arranca con offload CUDA en
  Jetson Orin Nano Super;
- no tocar ESP32, firmware ni frontera fisica;
- no cambiar prompts ni contratos;
- mantener disponible el runtime estable CPU-only como fallback de demo.

## 2. Estado inicial

Main actualizado hasta `7ccf570`.

Jetson viva:

| Campo | Valor |
|---|---|
| hostname | `rhizome-01-node` |
| fecha Jetson | `2026-05-03T10:39:46+02:00` |
| contenedores | `sprout-llama-e2b` y `sprout-adapter-12000` vivos desde ~15 h |
| RAM | 7.4 GiB total, ~3.8 GiB available |
| swap | ~226 MiB usado |
| temperatura idle | ~40 C |

Dato importante:

```text
tegrastats: lfb 1x1MB
/proc/meminfo: CmaTotal 262144 kB, CmaFree 692 kB
```

Lectura inicial:

- hay memoria disponible agregada;
- pero la memoria fisica contigua disponible esta casi agotada;
- esto encaja con el fallo dia 17: `NvMapMemAllocInternalTagged ... error 12`
  y `cudaMalloc failed: out of memory`.

## 3. Imagen y binario

Imagen:

```text
ghcr.io/nvidia-ai-iot/llama_cpp:latest-jetson-orin
```

Detalles:

| Campo | Valor |
|---|---|
| image id | `sha256:fc4f7159df6b...` |
| digest | `sha256:ba196b9760fda683a84048916ec6666650cc4b05d3bfc05c02bf1917553e55f1` |
| created | `2026-04-30T00:26:27Z` |
| arch | `aarch64` |
| llama.cpp | `version: 8966 (7b8443ac7)` |
| CUDA arch | `8.7` |

Modelo:

```text
/home/rhizome_01/sprout_models/gemma-4-E2B-it-Q4_K_S.gguf
```

Estado: descargado dia 17, ~2.9 GiB.

## 4. Hipotesis de trabajo

H1. No es un fallo de contrato ni de prompt: la bateria Rhizome v0.5 ya paso
18/18 en Jetson.

H2. No es simplemente "RAM total insuficiente": hay ~3.8 GiB available.

H3. El fallo probable esta en buffers CUDA/NvMap que requieren memoria contigua
o una reserva que la Jetson no puede satisfacer tras el estado actual.

H4. Un reboot frio o un arranque sin servicios previos puede cambiar el
resultado de offload. Si es asi, la solucion operativa para demo puede ser:
boot limpio -> lanzar runtime GPU primero -> luego adapter.

---

## 5. Parada temporal de servicios Sprout

Para diagnostico GPU paro temporalmente:

```bash
docker stop sprout-adapter-12000 sprout-llama-e2b
```

No se toca ESP32 ni frontera fisica.

Resultado tras parar:

| Campo | Antes | Despues |
|---|---:|---:|
| MemAvailable | ~3.8 GiB | ~5.3 GiB |
| `tegrastats lfb` | `1x1MB` | `48x4MB` |
| `CmaFree` | ~692 KB | ~20 MB |

Lectura:

- parar servicios libera RAM agregada y mejora bloques libres;
- `CmaFree` sigue bajo;
- el estado de memoria contigua importa para CUDA/NvMap en Jetson.

## 6. Probe incremental `llama-cli`

Primer intento con `llama-cli` parecia timeout, pero era modo conversacion
esperando siguiente turno. Cambio a:

```bash
--single-turn --simple-io --no-display-prompt
```

Con `-c 512 -b 128 -ub 128`:

| `-ngl` | Resultado | Nota |
|---:|---|---|
| 1 | OK | GPU visible |
| 2 | OK | GPU visible |
| 4 | OK | GPU visible |
| 8 | OK | GPU visible |
| 16 | FAIL | `GGML_ASSERT(n_inputs < GGML_SCHED_MAX_SPLIT_INPUTS)` |

El fallo `-ngl 16` no es `cudaMalloc`; es un assert interno del scheduler.
Stack trace entra por `common_params_fit_impl` / `sched_reserve`.

## 7. Flags que desbloquean offload

Pruebo mitigaciones con `-ngl 16`:

| Flags | Resultado |
|---|---|
| `--no-op-offload` | OK |
| `--no-kv-offload` | FAIL |
| `--no-op-offload --no-kv-offload` | OK |
| `--flash-attn off` | OK |
| `--split-mode none` | FAIL |

Prueba alta con:

```bash
--fit off --no-op-offload
```

Resultado:

| `-ngl` | Resultado | Prompt tok/s aprox | Generation tok/s aprox |
|---:|---|---:|---:|
| 24 | OK | 23.0 | 9.5 |
| 32 | OK | 27.9 | 11.9 |
| 36 | OK | 23.9 | 24.2 |
| 99 | OK | 22.4 | 22.4 |

Conclusion tecnica:

- la GPU funciona;
- el comando de ayer fallaba por combinacion de offload automatico/scheduler,
  no porque el modelo sea imposible en Orin Nano;
- flags candidatos:

```bash
--fit off --no-op-offload
```

## 8. `llama-server` GPU full offload

Comando que arranca:

```bash
docker run -d --name sprout-llama-e2b \
  --runtime=nvidia \
  --network host \
  -v "$HOME/sprout_models:/models:ro" \
  ghcr.io/nvidia-ai-iot/llama_cpp:latest-jetson-orin \
  llama-server -m /models/gemma-4-E2B-it-Q4_K_S.gguf \
    -c 2048 -b 128 -ub 128 -ngl 99 \
    --fit off \
    --no-op-offload \
    --reasoning off \
    --host 0.0.0.0 --port 8080
```

Logs relevantes:

```text
load_tensors: offloaded 36/36 layers to GPU
CUDA0 model buffer size = 1347.84 MiB
CUDA0 KV buffer size = 12.00 MiB
CUDA0 KV buffer size = 24.00 MiB
CUDA0 compute buffer size = 140.75 MiB
graph splits = 2
main: server is listening on http://0.0.0.0:8080
```

Smoke adapter:

| Campo | CPU-only dia 17 | GPU full dia 18 |
|---|---:|---:|
| smoke minimo `/api/chat` | ~2277 ms | ~1152 ms |
| tokens out | 7 | 7 |
| JSON limpio | si | si |

## 9. Mini-bateria critica GPU full

Primera pasada GPU full:

| Prompt | envelope | status | duration_ms |
|---|---:|---:|---:|
| RD01 | OK | OK | 4447 |
| RD03 | OK | OK | 2544 |
| RD08 | OK | OK | 2662 |
| RA02 | OK | OK | 1648 |
| RA04 | OK | OK | 1685 |
| RH02 | FAIL | FAIL | 6655 |

Fallo RH02:

- JSON sin fence;
- `done_reason=stop`;
- falta una llave final de cierre;
- no es `length`, es desviacion de generacion.

Repeticion GPU full:

```text
6/6 envelope_valid
6/6 status_match
```

Duraciones repeticion:

| Prompt | duration_ms |
|---|---:|
| RD01 | 2681 |
| RD03 | 2448 |
| RD08 | 2640 |
| RA02 | 1643 |
| RA04 | 1635 |
| RH02 | 4379 |

Lectura:

- GPU full es mucho mas rapido;
- el fallo RH02 parece variabilidad, no bloqueo sistematico;
- aun asi no se puede declarar quality pass con una pasada fallida.

## 10. Bateria restante GPU full

Ejecuto los 12 restantes con GPU full.

Resultado:

```text
12/12 envelope_valid
11/12 status_match
```

Fallo:

| Prompt | Esperado | Obtenido |
|---|---|---|
| RD04_defer_due_to_dispute | `ok` | `need_clarification` |

Contenido resumido:

```json
{
  "task": "decide_action",
  "status": "need_clarification",
  "question_es": "La validación del sensor para parcela A está disputada. ¿Desea proceder con el riego o esperar una nueva validación?",
  "payload": null
}
```

Lectura:

- no es peligroso: ante disputa pide confirmacion humana;
- pero rompe contrato de bateria, porque el baseline espera `ok` con accion
  prudente/deferida;
- por tanto GPU full no es quality pass todavia.

## 11. Mitigaciones probadas para calidad

### `temperature=0`

Probe RD04 + RH02:

| Prompt | Resultado |
|---|---|
| RD04 | sigue `need_clarification` |
| RH02 | OK |

`temperature=0` reduce variabilidad de RH02, pero no corrige RD04.

### Offload parcial `-ngl 12`

Arranca, pero:

- mucho mas lento por muchos graph splits;
- RD04 sigue fallando;
- RH02 falla envelope en el probe temp0.

No sirve como punto medio.

### Full GPU sin prompt cache / slot unico

Comando con:

```bash
--parallel 1 --cache-ram 0 --no-cache-prompt --no-cache-idle-slots
```

RD04 repetido 5 veces:

```text
0/5 status_match
```

No mejora; empeora.

### RD04 repetido con full GPU normal

5 repeticiones, temperatura 0.3:

```text
5/5 envelope_valid
2/5 status_match
3/5 need_clarification
```

Lectura:

- hay deriva semantica real en RD04 bajo GPU full;
- la salida sigue siendo segura, pero no estable segun contrato.

## 12. Estado final dejado en Jetson

Restauro runtime estable CPU-only:

```bash
docker run -d --name sprout-llama-e2b \
  --runtime=nvidia \
  --network host \
  -v "$HOME/sprout_models:/models:ro" \
  ghcr.io/nvidia-ai-iot/llama_cpp:latest-jetson-orin \
  llama-server -m /models/gemma-4-E2B-it-Q4_K_S.gguf \
    -c 2048 -ngl 0 \
    --device none \
    --no-op-offload \
    --reasoning off \
    --host 0.0.0.0 --port 8080
```

Adapter sigue vivo en `:12000`.

Smoke final:

```text
status=200
content='Hola.'
backend=local-llamacpp
duration_ms=1406
smoke OK
```

## 13. Veredicto

**GPU runtime pass:** SI.

- La Jetson puede cargar Gemma 4 E2B Q4_K_S con `llama-server`;
- `36/36` capas pueden ir a GPU;
- comando clave: `--fit off --no-op-offload`;
- rendimiento de smoke y mini-bateria mejora claramente.

**GPU quality pass:** NO TODAVIA.

- GPU full produce 18/18 JSON valido en la bateria completa, pero 17/18
  `status_match` por RD04;
- RD04 es seguro pero fuera de contrato;
- RH02 mostro una vez JSON incompleto, aunque paso en repeticion.

**Demo recommendation hoy:** usar CPU-only estable para demostraciones
contractuales, o usar GPU solo si el flujo real tiene validador determinista
delante y no depende del LLM para decidir RD04.

**Siguiente PR recomendada:** wrapper de arranque documentado con dos perfiles:

1. `safe-cpu`: 18/18 quality pass, lento, default demo seguro;
2. `gpu-experimental`: `--fit off --no-op-offload`, rapido, marcado como
   experimental hasta cerrar RD04/RH02.

No he tocado firmware, ESP32 ni contratos.

---

## 14. Operacionalizacion sin depender de Xilema

Bea pregunta si puedo avanzar mientras ella y Xilema miran ESP32. Avanzo en
zona Jetson pura, sin tocar frontera fisica.

Creo:

```text
code/rhizome/jetson/README.md
code/rhizome/jetson/run_runtime.sh
code/rhizome/jetson/start_adapter.sh
code/rhizome/jetson/smoke_adapter.sh
code/rhizome/jetson/collect_baseline.sh
code/rhizome/jetson/run_battery.sh
```

Objetivo:

- convertir la bitacora GPU/CPU en comandos reproducibles;
- evitar que Cambium/Xilema tengan que copiar comandos largos;
- dejar claro que `safe-cpu` es el default contractual;
- dejar `gpu-experimental` disponible sin promoverlo a demo.

Perfiles:

| Script | Funcion |
|---|---|
| `run_runtime.sh safe-cpu` | arranca `llama-server` CPU-only estable |
| `run_runtime.sh gpu-experimental` | arranca `llama-server` con `--fit off --no-op-offload` |
| `start_adapter.sh` | arranca adapter `llamacpp` en `:12000` via contenedor Python |
| `smoke_adapter.sh` | POST minimo `/api/chat` y valida JSON en `message.content` |
| `collect_baseline.sh` | captura baseline Jetson sin `sudo` |
| `run_battery.sh` | ejecuta `critical`, `remaining` o `full` sin pisar JSONL canonicos |

Verificacion:

- `bash -n` local: OK;
- `bash -n` remoto en Jetson: OK;
- `run_runtime.sh safe-cpu` remoto: health OK;
- `start_adapter.sh` remoto: health OK;
- `smoke_adapter.sh` remoto: JSON OK;
- `run_runtime.sh gpu-experimental` remoto: health OK;
- `smoke_adapter.sh` con GPU experimental: JSON OK;
- restaurado `run_runtime.sh safe-cpu` al final;
- smoke final CPU-only: OK.
- `run_battery.sh critical --dry-run` en Jetson: OK.

Estado final dejado en Jetson:

```text
sprout-llama-e2b      Up, perfil safe-cpu
sprout-adapter-12000  Up, backend llamacpp
```

Decision:

- estos scripts son operativos, no cambian contratos;
- quedan listos para PR pequeno;
- no sustituyen una decision de Cambium/Xilema sobre perfil GPU demo.
