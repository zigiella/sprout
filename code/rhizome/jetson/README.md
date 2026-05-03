# Rhizome Jetson Runtime

Scripts operativos para arrancar Gemma 4 E2B en Jetson Orin Nano Super con
`llama.cpp` sin depender de Ollama ni de hardware ESP32.

Estos scripts no tocan firmware, sensores, actuadores ni reglas fisicas. Solo
gestionan el runtime local de inferencia y el adapter Ollama-compatible.

## Perfiles

| Perfil | Uso | Estado dia 18 |
|---|---|---|
| `safe-cpu` | Demo contractual y bateria Rhizome v0.5 | Quality pass 18/18, lento |
| `gpu-experimental` | Diagnostico/rendimiento | Runtime pass, no quality pass aun |

### `safe-cpu`

Arranca `llama-server` en `:8080` con:

```bash
-ngl 0 --device none --no-op-offload --reasoning off
```

Es el perfil seguro documentado por Endodermis el dia 17:

- mini-test critico frio 6/6;
- mini-test critico caliente 6/6;
- bateria Rhizome v0.5 combinada 18/18;
- sin OOM, sin truncamiento, sin Markdown fences.

### `gpu-experimental`

Arranca `llama-server` en `:8080` con:

```bash
-ngl 99 --fit off --no-op-offload --reasoning off
```

El flag clave es `--no-op-offload`; sin el, el build de `llama.cpp` en Jetson
puede abortar con:

```text
GGML_ASSERT(n_inputs < GGML_SCHED_MAX_SPLIT_INPUTS)
```

Estado dia 18:

- carga 36/36 capas en GPU;
- acelera mucho las respuestas;
- aun no es quality pass para Rhizome v0.5 porque RD04 muestra deriva
  semantica segura (`need_clarification` en lugar de `ok`).

## Requisitos

- Jetson Orin Nano Super con JetPack 6.x.
- Docker instalado.
- runtime NVIDIA disponible.
- usuario con permiso para ejecutar `docker`.
- modelo descargado en:

```bash
$HOME/sprout_models/gemma-4-E2B-it-Q4_K_S.gguf
```

## Arranque

Desde la Jetson:

```bash
cd ~/sprout/code/rhizome/jetson

./run_runtime.sh safe-cpu
./start_adapter.sh
./smoke_adapter.sh
./run_battery.sh critical
```

Para probar GPU:

```bash
./run_runtime.sh gpu-experimental
./start_adapter.sh
./smoke_adapter.sh
./run_battery.sh critical
```

## Variables utiles

```bash
MODEL_PATH=$HOME/sprout_models/gemma-4-E2B-it-Q4_K_S.gguf
LLAMA_IMAGE=ghcr.io/nvidia-ai-iot/llama_cpp:latest-jetson-orin
LLAMA_PORT=8080
ADAPTER_PORT=12000
CTX_SIZE=2048
N_GPU_LAYERS=99
```

Ejemplo:

```bash
CTX_SIZE=1024 ./run_runtime.sh gpu-experimental
```

## Verificacion

Health directo de `llama-server`:

```bash
curl -s http://127.0.0.1:8080/health
```

Health del adapter:

```bash
curl -s http://127.0.0.1:12000/health
```

Smoke:

```bash
./smoke_adapter.sh
```

Baseline operativo:

```bash
./collect_baseline.sh | tee jetson_baseline_$(date -u +%Y%m%dT%H%M%SZ).log
```

Bateria Rhizome v0.5:

```bash
./run_battery.sh critical          # 6 prompts criticos
./run_battery.sh remaining         # 12 prompts restantes
./run_battery.sh full              # critical + remaining
./run_battery.sh critical --dry-run
```

Los resultados se escriben en `code/tuning/results/` dentro del repo montado
en el contenedor del adapter, con un sufijo UTC para no pisar los JSONL
canonicos.

## Interpretacion

Para demo y pruebas contractuales, usar `safe-cpu` hasta que Cambium/Xilema
acepten formalmente un perfil GPU.

Para experimentos de rendimiento, usar `gpu-experimental` y ejecutar al menos:

```bash
cd ~/sprout/code/tuning
python harness.py --matrix matrix_rhizome_v05.yaml \
  --adapter-url http://127.0.0.1:12000 \
  --out results/rhizome_v05_gpu_probe.jsonl
```

No promover GPU a perfil demo hasta que la bateria critica sea estable y RD04
quede alineado con el contrato.
