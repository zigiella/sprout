# Gemma 4 en Jetson Orin Nano Super

**Fecha bitacora:** 2026-04-21
**Autora:** Estoma
**Dueña de hardware afectada:** Xilema (Rhizome)
**Hardware del equipo:** Jetson Orin Nano Super 8GB, ya comprado (kickoff 2026-04-15).

---

## 1. Ficha tecnica del experimento original

- **Naturaleza:** meta-investigacion sobre multiples fuentes publicas — no hay *un* experimento unico citable. Consolido documentacion oficial, tutoriales, benchmarks informales y foros.
- **Fecha de consulta:** 2026-04-21.
- **Autoria externa:** NVIDIA (docs oficiales + forum), Jetson AI Lab (tutoriales), Unsloth (GGUFs de Gemma 4), diversos autores en DEV.to y forum threads.
- **Claim central en una linea:** el Jetson Orin Nano Super (67 TOPS, 8 GB LPDDR5, $249) corre bien Gemma 4 **E2B Q4_K_M** via Ollama nativo o llama.cpp con CUDA; **E4B Q4_K_M cabe pero apretado y con reports de crash**; 26B/31B **no caben**. Los benchmarks especificos *Gemma 4 + Orin Nano Super* aun son escasos en fuentes primarias — usamos Gemma 3n e2b como proxy documentado.

---

## 2. Metodo y resultados en nuestras palabras

### 2.1 Hardware del Jetson Orin Nano Super

Lo importante para nosotros:

| Caracteristica | Valor |
|---|---|
| CPU | 6-core ARM Cortex-A78AE |
| GPU | NVIDIA Ampere, 1024 CUDA cores + 32 Tensor cores |
| Memoria | 8 GB LPDDR5 **unified** (compartida CPU+GPU) |
| Bandwidth memoria | 102 GB/s (subido de 68 GB/s) |
| AI perf | 67 TOPS INT8 (subido de 34 TOPS original) |
| Power modes | 7W / 15W / 25W / MAXN |
| Precio dev kit | $249 USD |

El "Super" es **upgrade de software** (JetPack 6.2) sobre el mismo hardware Orin Nano. Sin JetPack actualizado se queda en los 34 TOPS del Orin Nano original — verificar antes del primer bench.

**Consecuencia directa para Sprout:** los 8 GB son compartidos entre OS, GPU, KV cache, cualquier servicio adicional (cam capture, MQTT, ESP32 driver, voice). Fijar memoria para el modelo sin margen es error facil.

### 2.2 Compatibilidad Gemma 4 en la familia Jetson

Segun jetson-ai-lab, la segmentacion por device es:

| Jetson | Modelos Gemma 4 que caben |
|---|---|
| Orin Nano (8 GB) | **E2B** — fit natural; E4B solo al limite |
| Orin NX (16 GB) | E2B, E4B |
| AGX Orin (64 GB), Thor | familia completa (incl. 26B MoE, 31B) |

Para el Orin Nano Super 8 GB del equipo: **E2B es el fit natural**, E4B cabe "con calzador".

### 2.3 VRAM por modelo × cuantizacion

De la guia compute-market (verificable contra unsloth/GGUFs):

| Modelo | FP16 | Q8_0 | Q4_K_M |
|---|---|---|---|
| E2B (2B) | ~4 GB | ~2.2 GB | **~1.5 GB** |
| E4B (4B) | ~8 GB | ~4.5 GB | **~2.5 GB** |
| 26B MoE | ~52 GB | ~28 GB | ~15 GB |
| 31B dense | ~62 GB | ~33 GB | ~18 GB |

Nota importante sobre MoE: **todos los expertos deben cargarse en VRAM aunque solo 3.8B esten activos por token**. La eficiencia MoE es en compute, no en memoria. Ese 15 GB del 26B MoE es real y descarta el Orin Nano para este modelo.

Unsloth publica GGUFs oficiales:
- `unsloth/gemma-4-E2B-it-GGUF` — Q4_K_M ≈ 1.3 GB
- `unsloth/gemma-4-E4B-it-GGUF` — Q4_K_M ≈ 2.5 GB
- `unsloth/gemma-4-26B-A4B-it-GGUF` — fuera de scope para este nodo

### 2.4 Runtimes disponibles

| Runtime | Estado Jetson | Ergonomia | Throughput | Notas para Sprout |
|---|---|---|---|---|
| **Ollama nativo** | oficial soportado, script install | ⭐⭐⭐⭐⭐ | ~50% del peak | el camino natural para MVP |
| **Ollama en Docker** | **CPU fallback conocido** en Jetson (GPU no detectada) | — | — | **evitar**, ver §5.2 |
| **llama.cpp** | oficial, compilar con CUDA | ⭐⭐⭐⭐ | alto, GGUF path | path backup si Ollama falla |
| **vLLM** | contenedores oficiales para Orin y Thor | ⭐⭐⭐ | mejor en *serving* HTTP multicliente | over-engineer para Rhizome (ver §5.3) |
| **MLC LLM** | contenedor `dustynv/mlc` | ⭐⭐ | el mas alto en edge, pero setup y tuning (`prefill_chunk_size`) | considerar si Ollama queda corto |
| **TensorRT-LLM** | oficial NVIDIA, builds separados | ⭐ | el mas optimizado | demasiado complejo para MVP |

### 2.5 Numeros reales en Jetson Orin Nano Super

**Aqui esta el gap honesto:** las fuentes primarias consultadas (NVIDIA Technical Blog, jetson-ai-lab/gemma4-e2b, tutorials/gemma4-on-jetson) **no publican tok/s especificos para Gemma 4 + Orin Nano Super al dia de hoy**. Una sintesis de busqueda menciono "220 tok/s sustained en E2B" pero no se confirma en ningun fetch directo; lo descarto como dato hasta que haya cita solida o medicion propia (§5.1).

Lo que si tenemos son **proxies cercanos** en el mismo hardware:

**Gemma 3n e2b en Orin Nano Super con Ollama nativo** (forum NVIDIA):
- eval (generation): **16.55 tok/s**
- prompt eval: **135.68 tok/s**
- total: ~48 s para 787 tokens
- **degradacion conocida**: con contexto >1500 tokens el prompt_eval baja a ~15 tok/s

**Gemma 3 4B en Orin Nano Super** (mismo forum):
- eval: **10.11 tok/s**
- prompt eval: **471.53 tok/s**

**DeepSeek R1 1.5B en Orin Nano Super con Ollama nativo** (DEV.to):
- eval: **30.98 tok/s**
- prompt eval: **67.38 tok/s**
- JetPack 6.2

**DeepSeek R1 1.5B en Orin Nano Super por power mode** (DEV.to):
- 15W → 16.40 tok/s
- 25W → 24.20 tok/s
- MAXN → 27.47 tok/s

**Llama 3 8B en Orin Nano** (TikTok/Shawn Hymel): ~4.5 tok/s. Cabe pero incomodo.

**Gemma 4 E2B en Orin Nano Super con Ollama:** esperable en el rango ~15–25 tok/s gen por la familia de arquitectura y tamano; asumir ~16 tok/s como floor y ~25 tok/s como techo razonable. **Hay que medirlo.**

### 2.6 Features de Gemma 4 relevantes en Jetson

- **Contexto 128K** en E2B/E4B (126K en docs algunas veces — revisar). Sliding window 512 tokens. En Orin Nano Super con 8 GB, la ventana efectiva de Ollama sera 4K por defecto (cross-ref bitacora `2026-04-21_ventana-contexto-gemma4_estoma.md`); subir a 16K es seguro con E2B Q4_K_M, subir a 32K es posible pero empieza a comer al KV cache.
- **Thinking / reasoning**: en Jetson se activa con `"enable_thinking": true` en request (cita jetson-ai-lab/tutorials/gemma4-on-jetson). Concuerda con `think=True` en cliente Python Ollama.
- **Tool calling** nativo soportado.
- **Multimodal**: text + image + audio input (audio hasta 30 s). **Audio en E2B bajo llama.cpp tiene issues abiertos al dia de hoy** — ver §5.4. Image input funciona.

### 2.7 Instalacion rapida (commands canonicos)

Ollama nativo (camino recomendado para Rhizome):
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull gemma4:e2b       # si catalog tiene el tag
# o alternativa via GGUF de unsloth:
ollama create gemma4:e2b -f ./Modelfile   # Modelfile apunta a unsloth E2B Q4_K_M
```

Docker, solo como referencia, **no recomendado** para Rhizome:
- JetPack 6: `dustynv/ollama:r36.2.0`
- JetPack 7 (Thor): `ghcr.io/nvidia-ai-iot/ollama:r38.2.arm64-sbsa-cu130-24.04`

Auditoria de uso GPU tras primera carga:
```bash
ollama ps        # CONTEXT real + PROCESSOR (debe decir GPU, no CPU)
```

---

## 3. Reproduccion propia

**No tengo Jetson accesible desde la celula.** Reproducible concreto para que Xilema ejecute — protocolo corto, que cabe en un ciclo de trabajo:

1. **Baseline sanity.**
   - Actualizar JetPack ≥ 6.2; verificar `cat /etc/nv_tegra_release`.
   - Instalar Ollama nativo via script.
   - `ollama pull gemma4:e2b` (o via `Modelfile` apuntando a `unsloth/gemma-4-E2B-it-GGUF` Q4_K_M).
   - Cargar modelo una vez (`ollama run gemma4:e2b "hola"`), salir.
   - `ollama ps` → capturar `CONTEXT` y `PROCESSOR`. `PROCESSOR=GPU` es condicion de seguir; si dice `CPU`, parar y depurar.
2. **Bench del harness.**
   - Reutilizar `code/rhizome/bench/prompt_set.jsonl` (ya congelado por Xilema en #5).
   - Correr `run_ollama_benchmark.py` apuntando a `gemma4:e2b`.
   - `num_ctx=16384` explicito. Power mode MAXN.
   - Capturar: first_token_ms, eval tok/s, prompt_eval tok/s, RAM peak, CONTEXT efectivo.
3. **Barrido de contexto.** Repetir con `num_ctx ∈ {8K, 16K}` para sanity (grid de §4.3 de la bitacora de ventana de contexto).
4. **Barrido de power mode.** Repetir el bench completo en `15W`, `25W`, `MAXN`. Genera curva power-vs-throughput util para el writeup y para defender demo low-power.
5. **Prueba de degradacion con contexto largo.** Prompt con ~1500 tokens de evidencia + snapshot, ver si aparece el fenomeno observado en Gemma 3n (prompt_eval cayendo de 135 a 15 tok/s).
6. **Opcional — comparacion runtime.** llama.cpp con el mismo GGUF + `--gpu-layers -1`. Solo si Ollama queda corto en spec.

Output esperado, para calibrar expectativas (no compromiso): E2B Q4_K_M ronda ~1.5 GB; first_token con modelo frio ~10–30 s; eval tok/s probablemente entre 15 y 25 en MAXN.

---

## 4. Transferibles a Sprout

Siete impactos. @mencion a dueña impactada.

### 4.1 Rhizome = `gemma4:e2b` Q4_K_M — @xilema, @cambium

**Decision propuesta:** default para Rhizome es **E2B Q4_K_M** (~1.5 GB), dejando memoria para OS, camara, KV cache hasta 16K, y servicios auxiliares. E4B Q4_K_M (~2.5 GB) cabe pero:
- va apretado en 8 GB unified.
- tiene reports de crash (`signal: killed`) en drivers tempranos 2026.
- la relacion calidad/latencia en agro no esta demostrada justificar el salto sobre E2B en un nodo que hace decisiones locales acotadas por §30.

**Accion:** Xilema puede pullear `unsloth/gemma-4-E2B-it-GGUF` (Q4_K_M) en cuanto tenga el Jetson flasheado, sin esperar mas research.

### 4.2 Ollama **nativo**, no Docker — @xilema

Confirmado como issue recurrente: Ollama **dentro** de container en Jetson hace **CPU fallback** (no detecta GPU). El camino es `curl -fsSL https://ollama.com/install.sh | sh`. Si el stack general de Sprout es dockerizado, Rhizome debe documentar esta excepcion.

### 4.3 JetPack 6.2 minimo — @xilema

Sin JetPack 6.2 el Orin Nano Super corre como Orin Nano "normal" (34 TOPS, 68 GB/s bandwidth) — el "Super" es upgrade de software. Ademas, E4B crash en drivers viejos se resuelve con JetPack al dia. **Verificacion previa al primer bench** (`cat /etc/nv_tegra_release`).

### 4.4 Curva power vs throughput como material narrativo — @xilema, @cambium, @corola

Orin Nano Super expone 7W / 15W / 25W / MAXN. El proxy DeepSeek R1 1.5B muestra ×1.7 gap de tok/s entre 15W y MAXN. Esta curva es:
- **Tecnica:** ayuda a fijar power mode del despliegue en parcela (15W probablemente defendible; MAXN para demo).
- **Narrativa:** refuerza el mensaje offline-first + low-power. Dato del writeup aunque no aparezca en el video.

### 4.5 Eleccion de runtime — @xilema, @cambium

**Default Ollama nativo** (ergonomia + 50% del peak). Saltar a MLC o TensorRT-LLM **solo si** Ollama no llega a la spec de latencia de Rhizome. vLLM es para serving multi-cliente — **no** es el caso de Rhizome. Decision simple, recomendable fijarla por escrito antes de que alguien invierta 2 dias en TensorRT-LLM por inercia.

### 4.6 Thinking mode uniforme — @meristem, @xilema

En Jetson (Ollama, llama.cpp, vLLM) la flag para reasoning es `"enable_thinking": true` en request. Concuerda con el `think=True` del cliente Python. Meristem ya lo estudia en #44; **el patron se extiende a Rhizome**: misma flag, mismo mecanismo. Eso simplifica el A/B de #44 / #47 — las conclusiones sobre thinking en E4B/26B son trasladables conceptualmente a E2B en Rhizome.

### 4.7 Narrativa "Un modelo. Tres profundidades. Tres tiempos." — @corola

La frase espinal gana cuantificacion:
- **Rhizome:** Gemma 4 E2B via Ollama en Jetson Orin Nano Super (8 GB, 67 TOPS, 25W sostenible).
- **Pollen:** Gemma 4 E2B (o E4B post-upgrade) via LiteRT en Pixel 10 Pro.
- **Meristem:** Gemma 4 E4B/26B MoE via Ollama local o proxy Gemini (cartela "E4B MVP / 26B objetivo").

El **mismo modelo base** en dos runtimes distintos (Ollama en Jetson, LiteRT en Pixel) en E2B. Misma familia Gemma 4 escalando a E4B/26B MoE en Meristem. No es munición que cambie el guion; es argumento duro para el writeup.

---

## 5. No-transferibles

Cinco cosas que **no** aplican y conviene escribirlas.

### 5.1 "220 tok/s sustained E2B en Jetson"

Aparecio en una sintesis de busqueda, **no** confirmado en fuentes primarias directas. Probable que corresponda a MLC o TensorRT-LLM en condiciones ideales, o a otro modelo. No lo usamos hasta que Xilema lo mida o aparezca cita directa. Ante la duda, asumir rango 15–25 tok/s con Ollama (proxy Gemma 3n).

### 5.2 26B MoE y 31B en Orin Nano Super

**No caben.** 26B MoE Q4_K_M necesita ~15 GB (todos los expertos cargados); Orin Nano Super tiene 8 GB. Esos modelos corren en el nodo Meristem (portatil o cloud via adapter #46), no en Rhizome. Lo documento para que nadie intente "aprovechar el Jetson para el 26B" — no es posible.

### 5.3 vLLM para Rhizome

vLLM brilla en **serving HTTP multicliente**. Rhizome hace 1–2 inferencias por ciclo de consolidacion local — no es serving concurrente. La complejidad de setup de vLLM no se paga aqui. Uso natural de vLLM en Sprout seria si alguna vez expusieramos Meristem via HTTP a muchos Rhizome simultaneos — fuera de MVP.

### 5.4 Audio E2B via llama.cpp

Al dia de hoy **tiene issues abiertos** (jetson-ai-lab/tutorials/gemma4-on-jetson). Si alguien piensa "audio input en Rhizome via mic usando llama.cpp", **no funciona hoy**. Text + image si. Para MVP: no confiar en audio como input en Rhizome; si hace falta, canal audio vive en Pollen (Pixel) donde LiteRT lo soporta.

### 5.5 Trasladar numeros de DeepSeek R1 1.5B como proxy de Gemma 4 E2B

DeepSeek R1 1.5B hace texto; Gemma 4 E2B carga encoders multimodales (imagen, audio). Los ~30 tok/s de DeepSeek no son expectativa realista para E2B. El proxy justo es **Gemma 3n e2b (~16 tok/s)**, mismo perfil multimodal edge. Usar ese como floor de expectativa.

---

## Referencias

- NVIDIA Technical Blog — Bringing AI Closer to the Edge and On-Device with Gemma 4: https://developer.nvidia.com/blog/bringing-ai-closer-to-the-edge-and-on-device-with-gemma-4/
- NVIDIA Technical Blog — Jetson Orin Nano Developer Kit Gets a Super Boost: https://developer.nvidia.com/blog/nvidia-jetson-orin-nano-developer-kit-gets-a-super-boost/
- NVIDIA — Jetson Orin Nano Super Developer Kit: https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-orin/nano-super-developer-kit/
- Jetson AI Lab — Gemma 4 E2B: https://www.jetson-ai-lab.com/models/gemma4-e2b/
- Jetson AI Lab — Gemma 4 on Jetson tutorial: https://www.jetson-ai-lab.com/tutorials/gemma4-on-jetson
- Jetson AI Lab — Ollama on Jetson: https://www.jetson-ai-lab.com/tutorials/ollama/
- NVIDIA Developer Forums — Gemma 3 y 3n en Jetson Orin Nano Super: https://forums.developer.nvidia.com/t/gemma-3-and-gemma-3n-on-jetson-orin-nano-super/337513
- NVIDIA Developer Forums — Introducing Ollama Support for Jetson Devices: https://forums.developer.nvidia.com/t/introducing-ollama-support-for-jetson-devices/289333
- DEV.to — My Journey with DeepSeek R1 on NVIDIA Jetson Orin Nano Super (Docker + Ollama): https://dev.to/ajeetraina/my-journey-with-deepseek-r1-on-nvidia-jetson-orin-nano-super-using-docker-and-ollama-1k2m
- Cytron Tutorial — DeepSeek R1 on NVIDIA Jetson Orin Nano Super: https://www.cytron.io/tutorial/deepseek-r1-on-nvidia-jetson-orin-nano-super
- compute-market — Gemma 4 Hardware Guide 2026: https://www.compute-market.com/blog/gemma-4-local-hardware-guide-2026
- Hugging Face — unsloth/gemma-4-E2B-it-GGUF: https://huggingface.co/unsloth/gemma-4-E2B-it-GGUF
- Hugging Face — unsloth/gemma-4-E4B-it-GGUF: https://huggingface.co/unsloth/gemma-4-E4B-it-GGUF
- Hugging Face — unsloth/gemma-4-26B-A4B-it-GGUF: https://huggingface.co/unsloth/gemma-4-26B-A4B-it-GGUF

---

**Siguiente paso (Peri):** al mergear, abrir issue `research-digest` con:
- Label: `research-digest`
- Titulo: `[digest] Gemma 4 en Jetson Orin Nano Super`
- Resumen ejecutivo: §2.1, §2.3, §2.5 (proxies numericos honestos), cinco transferibles §4.1–§4.5 como accion concreta.
- Tags: `@xilema` (dueña principal, primer bench al tener hardware al dia), `@cambium` (decide runtime default + power mode), `@meristem` (thinking flag consistente entre nodos — §4.6), `@floema` (simetria Pollen/Rhizome — §4.7), `@corola` (frase espinal cuantificada — §4.7).

— Estoma
