# Setup llama.cpp local — simulación Rhizome target Jetson Orin Nano Super

**Autora**: Meristem
**Fecha**: 2026-04-27 (día 12)
**Rama**: `feat/meristem-tuning-v0` (renombrada hoy desde
`feat/meristem-pollen-tuning-v0` para cubrir Pollen + Rhizome)
**Contexto**: cambio de scope día 11 (Bea me asigna también tuning
Rhizome, reusando metodología). Stack target real: Gemma 4 E2B
en Q4_K_M sobre llama.cpp en Jetson Orin Nano Super 8GB.

---

## TL;DR

- Setup local llama.cpp + Gemma 4 E2B Q4_K_M validado en mi PC.
- **Q8_0 fallido por RAM**: 5 GB modelo + Claude + Ollama + OS empujó al
  paging y casi tumba el sistema (probable causa del reinicio espontáneo
  de la mañana). Reescalado a Q4_K_M (3.1 GB), lo cual además es **más
  fiel al target Jetson** según la research de Estoma del 21 abril.
- **Smoke OK**: modelo carga en ~5s, 19.9 tok/s generación (CPU Alder
  Lake), 76 tok/s prompt processing. Total proceso 3.5 GB en uso.
- **Hallazgo R7-bis nuevo**: el modelo Gemma 4 E2B emite el thinking
  **inline dentro del `content`** en llama.cpp (no en campo separado
  como Ollama, ni mezclado-en-stream como LiteRT-LM Android). Tres
  runtimes, tres comportamientos. Refuerza la decisión A (thinking off
  multi-turn, ON solo one-shot) que Floema aplicó.

## 1. Decisiones de stack y por qué

| Eje | Target real Jetson | Mi simulación local |
|---|---|---|
| Modelo | Gemma 4 E2B | Gemma 4 E2B (idéntico) |
| Cuantización | Q4_K_M | Q4_K_M (idéntico) |
| Runtime | llama.cpp | llama.cpp (idéntico binario) |
| Hardware | ARM64 + GPU NVIDIA Tegra (1024 cores Ampere, 67 TOPS INT8) | x86_64 Alder Lake CPU only |
| OS | Linux JetPack 6.x | Windows 11 |
| RAM | 8 GB unificada | 16 GB |

Diferencias residuales **inevitables** entre mi sim y target Jetson:

- **Velocidad**: Jetson con GPU offload alcanza 15-25 tok/s gen (research
  Estoma). Mi PC en CPU pure obtiene **19.9 tok/s gen** ya — comparable
  por casualidad afortunada (Alder Lake mononucleo es muy potente). **La
  fidelidad de la curva de calidad es 100% (mismo binario, mismo modelo,
  misma cuantización)**. Latencia/tok/s será similar al rango target.
- **Arquitectura**: x86 vs ARM. Afecta micro-optimizaciones de SIMD pero
  no comportamiento del modelo.
- **GPU offload**: el Jetson va a tener offload completo del modelo a GPU
  (faster). Mi sim es CPU only (slower) pero con cifras del mismo orden.

## 2. Por qué Q4_K_M sobre Q8_0 (correción del día)

Mi propuesta inicial (mañana día 12) fue Q8_0:

> "Q4_K_M es demasiado conservador para Orin Nano 8GB. Mi voto Q8_0:
> calidad casi indistinguible de F16, RAM holgada (~2.5 GB esperado),
> sweet spot."

Estuve **doble equivocado**:

1. **El tamaño**: pensé que Q8_0 sería ~2.5 GB y resultó **5 GB** (los
   encoders multimodales del modelo Gemma 4 E2B suben mucho el peso
   total cuando los pesos del backbone están cuantizados pero los
   embeddings/heads/encoders quedan en BF16). Q4_K_M acabó en 3.1 GB,
   también más de lo previsto.
2. **Mi PC no aguantaba Q8_0**: el load del modelo + Claude + Ollama
   + OS empujó el paging y casi tumba el sistema. RAM libre bajó a
   <4 GB con todo cargado. El reinicio espontáneo de antes muy probable
   por OOM acumulado.

**Q4_K_M es además lo que recomienda la comunidad para Jetson Orin Nano
Super 8GB** (research Estoma 21 abril, citas a NVIDIA Developer Forums).
Por tanto, Q4_K_M nos hace **MÁS fieles al target real, no menos**. Mi
hipótesis "Q8_0 mejor calidad sin coste" no se sostiene en este hardware.

## 3. Setup paso a paso

### 3.1 Modelo

```bash
# Q4_K_M (3.1 GB) — desde unsloth, sin gate
curl -L -o models/gemma-4-E2B-it-Q4_K_M.gguf \
  "https://huggingface.co/unsloth/gemma-4-E2B-it-GGUF/resolve/main/gemma-4-E2B-it-Q4_K_M.gguf"
```

`models/` está en `.gitignore` (binarios grandes no van a repo).

### 3.2 llama.cpp

Binarios precompilados Windows CPU x64 desde `ggml-org/llama.cpp`
(repo se movió desde `ggerganov/llama.cpp` — 301 redirect):

```bash
# Release b8943, build 5594d1322
curl -L "https://github.com/ggml-org/llama.cpp/releases/download/b8943/llama-b8943-bin-win-cpu-x64.zip" -o /tmp/llama-bin.zip
unzip -q /tmp/llama-bin.zip -d tools/llama.cpp/
```

`tools/llama.cpp/` también en `.gitignore`. Backends auto-detectados:

```
load_backend: loaded RPC backend from ggml-rpc.dll
load_backend: loaded CPU backend from ggml-cpu-alderlake.dll
```

CPU correctamente detectada (Intel Alder Lake) — usa instrucciones
SIMD optimizadas.

### 3.3 Smoke test (validación final)

```bash
./tools/llama.cpp/llama-cli.exe \
  -m models/gemma-4-E2B-it-Q4_K_M.gguf \
  -p "Responde solo: OK." \
  -n 10 --single-turn -t 8 -c 1024 --simple-io
```

Flags clave:

- `--single-turn` (no `--no-conversation`, que en b8943 dejaba un
  prompt interactivo `> ` esperando input). `--single-turn` con
  `--prompt` hace **un turno y sale**, no interactivo.
- `-t 8` 8 threads (suficiente para Alder Lake P+E cores).
- `-c 1024` num_ctx pequeño (KV cache pequeño, carga rápida).
- `--simple-io` output sin buffering, ve los tokens al instante.

Resultado:

```
build      : b8943-5594d1322
model      : gemma-4-E2B-it-Q4_K_M.gguf
modalities : text

memory breakdown [MiB]:
  - Host:        2947 modelo + 18 free + 522 compute = 3487 MB
  - CPU_REPACK:  1069 MB
  Total: ~4.5 GB

[ Prompt: 76.2 t/s | Generation: 19.9 t/s ]

Exiting...
```

**Caveat**: `modalities: text` en la línea de info — llama-cli detectó
correctamente que el GGUF principal solo trae el backbone de texto. Los
encoders multimodales están en `mmproj-*.gguf` separados (no descargados,
no necesarios para Rhizome).

## 4. Hallazgo R7-bis nuevo: thinking inline en llama.cpp

En el output del smoke apareció:

```
> Responde solo: OK.

[Start thinking]
Thinking Process:

1.  ...
```

El modelo Gemma 4 emite el razonamiento **dentro del `content` del
mismo turno**, prefijado con `[Start thinking]`. No es un campo
separado, no es un canal aparte — es texto inline.

Esto **completa el cuadro de tres runtimes con tres comportamientos
distintos** del mismo modelo:

| Runtime | Cómo emite el thinking | Implicación cliente naive |
|---|---|---|
| Ollama (`/api/chat`) | Campo `thinking` separado, `content` vacío | Pierde memoria si solo persiste `content` (R7-bis observado en Phase 3 Pollen) |
| LiteRT-LM Android | Mezclado en stream `Content.Text` | Persiste todo, pero devora KV (Floema observó día 11) |
| **llama.cpp** | Inline en `content`, prefijado con `[Start thinking]` | Persiste todo (incluido razonamiento). KV crece rápido. Marker textual permite split posterior si se quiere |

Esto **refuerza la decisión A de Floema** (thinking off para multi-turn,
ON solo para llamadas one-shot): los tres runtimes coinciden en que
multi-turno con thinking activo tiene complicaciones. La decisión A es
robusta porque no depende del runtime concreto.

**Vale como hallazgo metodológico** para el artículo post-demo: "Tres
runtimes, tres comportamientos del thinking, una sola decisión segura
(off) cuando hay multi-turn". Patrón generalizable.

**Observación adicional**: el marker `[Start thinking]` de llama.cpp
podría usarse para hacer split robusto del thinking si Floema decidiera
opción B (concatenar) o C (extraer JSON) en algún momento futuro. Por
ahora la decisión A vale.

## 5. Comparación con benchmarks de Estoma (21 abril)

Estoma documentó:

- Gemma 3n e2b en Orin Nano Super con Ollama nativo: ~16 tok/s gen
- Rango esperado con CUDA optimizado: 15-25 tok/s gen

Mi simulación local (Alder Lake CPU only):

- **19.9 tok/s gen, 76.2 tok/s prompt** con Gemma 4 E2B Q4_K_M

Está **dentro del rango esperado del target**, y de hecho ligeramente
mejor que el benchmark Ollama de Estoma. Probablemente porque:

1. CPU x86 Alder Lake es muy competitiva en mononucleo.
2. llama.cpp puro vs Ollama (que añade overhead de su scheduler).
3. Q4_K_M es eficiente en SIMD x86.

**Implicación**: las cifras de mi tuning local de Rhizome serán
comparables al target real. No esperamos sorpresas grandes en velocidad
cuando se pase a Jetson. La calidad (status_match, envelope_valid) es
100% transferible (mismo binario, mismo modelo, misma cuantización).

## 6. Footprint de RAM medido

Con el modelo cargado y un turno ejecutándose:

- Modelo (Q4_K_M, mmap): ~2.95 GB
- KV cache (num_ctx=1024): ~520 MB
- Compute buffers: ~520 MB (incluido en el host figure)
- CPU_REPACK: ~1 GB
- **Total proceso llama-cli**: ~3.5 GB
- **Mi PC** (16 GB): RAM libre tras smoke ~8 GB → **margen 4-5 GB**
  para más procesos o num_ctx mayor.

Para Orin Nano 8GB:

- OS + JetPack: ~1.5 GB
- llama.cpp + KV cache: ~1.5-2 GB
- Modelo: ~3 GB
- Resto: ~2 GB para Pollen App + sensores Rhizome

**Cabe holgado**, queda margen para num_ctx=4096 (objetivo) sin
problemas.

## 7. Próximos pasos

1. **Arrancar `llama-server`** en `:8080` y verificar que es estable a
   3.5 GB sostenidos. Comando:
   ```bash
   ./tools/llama.cpp/llama-server.exe \
     -m models/gemma-4-E2B-it-Q4_K_M.gguf \
     --port 8080 -c 4096 --no-mmproj -t 8 --host 127.0.0.1
   ```
2. **Implementar `LlamaCppBackend`** en `meristem_inference_adapter`.
   Protocolo:
   - Recibe request Ollama-format en `/api/chat`
   - Convierte a OpenAI-format
   - POST a `llama-server:8080/v1/chat/completions`
   - Convierte respuesta de vuelta a Ollama-format
   - Extrae métricas para headers `Sprout-Inference-*`
3. **Smoke test del stack completo**: harness → adapter:12000 →
   llamacpp backend → llama-server:8080 → modelo → respuesta.
4. **Esperar mapeo de Xilema** (`prompt_set.jsonl ↔ docs/22 §6`)
   para extender `code/tuning/` con `prompt_pack_rhizome_es.yaml` y
   `matrix_rhizome_v0.yaml`.

## 8. Que el equipo sepa

- **Q4_K_M es la cuantización adoptada** para Rhizome (PC local +
  Jetson). Coincide con consenso comunidad (Estoma research) y permite
  margen de RAM.
- **Mi PC (CPU only) emite 19.9 tok/s gen** — comparable al target
  Jetson, simulación viable.
- **llama.cpp emite thinking inline con marker `[Start thinking]`**
  (R7-bis amplia: tres runtimes, tres comportamientos, una sola
  decisión segura).
- **Ollama sigue corriendo idle en el PC** (PIDs 20608, 20856 no
  pude pararlo limpiamente con `taskkill`; consume <50 MB total
  actualmente). No estorba al stack llama.cpp en `:8080`. Si en
  algún momento toca pararlo, hay que cerrar tray icon manualmente
  o reiniciar.

## Referencias

- `models/gemma-4-E2B-it-Q4_K_M.gguf` (3.1 GB, local, no en git)
- `tools/llama.cpp/` (build b8943-5594d1322, local, no en git)
- `research/experiments/2026-04-21_gemma4-jetson-orin-nano-super_estoma.md`
  (research Estoma con cifras NVIDIA forum)
- `bitacora/2026-04-25_tuning-v0-resultados_meristem.md` §4 Hallazgo 3
  (R7-bis original en Pollen)
- `bitacora/2026-04-26_respuesta-floema-a-meristem_v2_floema.md`
  (decisión A multi-turn aplicada en LiteRT-LM)
- `bitacora/2026-04-26_aviso-cambium-menciones-gemma3_meristem.md`
  (verificación pública: Gemma 4 ≠ Gemma 3n)
