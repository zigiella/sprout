# Gemma 4 -- Skill de Referencia Completa para Desarrollo de Aplicaciones

> **Modelo:** Google Gemma 4 | **Release:** 2 de abril de 2026 | **Licencia:** Apache 2.0
> **Basado en:** Investigacion Gemini 3 | **Training data cutoff:** Enero 2025

---

## 1. FAMILIA DE MODELOS

| Modelo | Params Totales | Params Activos | Capas | Contexto | Modalidades | Arquitectura |
|--------|---------------|----------------|-------|----------|-------------|--------------|
| **Gemma 4 E2B** | 5.1B | 2.3B | 35 | 128K | Texto, Imagen, Audio, Video | Dense + PLE |
| **Gemma 4 E4B** | 8B | 4.5B | 42 | 128K | Texto, Imagen, Audio, Video | Dense + PLE |
| **Gemma 4 26B-A4B** | 25.2B | 3.8B/token | 30 | 256K | Texto, Imagen, Video | Mixture-of-Experts |
| **Gemma 4 31B** | 30.7B | 30.7B | 60 | 256K | Texto, Imagen, Video | Dense |

### Convencion de nombres
- **"E"** = Effective parameters (E2B, E4B usan Per-Layer Embeddings reduciendo computacion activa)
- **"A"** = Active parameters (26B-A4B es MoE, solo 3.8B activos por token de 25.2B totales)
- Sufijo **`-it`** = Instruction-tuned (ej: `gemma-4-31B-it`)
- Cada variante tiene checkpoints **base** e **IT**

### HuggingFace Model IDs
```
google/gemma-4-E2B          google/gemma-4-E2B-it
google/gemma-4-E4B          google/gemma-4-E4B-it
google/gemma-4-26B-A4B      google/gemma-4-26B-A4B-it
google/gemma-4-31B          google/gemma-4-31B-it
```

### Requerimientos de VRAM

| Modelo | FP16 | 8-bit | 4-bit |
|--------|------|-------|-------|
| E2B | ~15 GB | ~8 GB | ~5 GB |
| E4B | ~20 GB | ~12 GB | ~8 GB |
| 26B MoE | ~52 GB | ~28 GB | ~18 GB |
| 31B Dense | ~62 GB | ~35 GB | ~20 GB |

> **Sweet spot:** El 26B MoE cabe en 12-14 GB VRAM (cuantizado, contexto corto) y rinde como un modelo denso de ~26B.

---

## 2. ARQUITECTURA TECNICA

### 2.1 Compartido entre todos los modelos
- **model_type:** `gemma4` / `Gemma4ForConditionalGeneration`
- **vocab_size:** 262,144 tokens
- **Activacion:** `gelu_pytorch_tanh`
- **Normalizacion:** RMSNorm (eps=1e-6)
- **Atencion:** Hibrida -- alternando sliding-window local con full global attention. Ultima capa siempre global.
- **RoPE:**
  - Capas sliding-window: RoPE estandar, theta=10,000
  - Capas globales: p-RoPE (Proportional), theta=1,000,000, partial_rotary_factor=0.25
- **Final logit softcapping:** 30.0
- **dtype:** bfloat16

### 2.2 Configuraciones por modelo

#### Gemma 4 E2B
```json
{
  "hidden_size": 1536,
  "num_hidden_layers": 35,
  "num_attention_heads": 8,
  "num_key_value_heads": 1,
  "head_dim": 256,
  "global_head_dim": 512,
  "intermediate_size": 6144,
  "max_position_embeddings": 131072,
  "sliding_window": 512,
  "hidden_size_per_layer_input": 256,
  "num_kv_shared_layers": 20,
  "tie_word_embeddings": true,
  "use_double_wide_mlp": true
}
```
- Patron de capas: 28 sliding + 7 full attention
- Vision encoder: ~150M params
- Audio encoder: ~300M params

#### Gemma 4 E4B
```json
{
  "hidden_size": 2560,
  "num_hidden_layers": 42,
  "num_attention_heads": 8,
  "num_key_value_heads": 2,
  "head_dim": 256,
  "global_head_dim": 512,
  "intermediate_size": 10240,
  "max_position_embeddings": 131072,
  "sliding_window": 512,
  "hidden_size_per_layer_input": 256,
  "num_kv_shared_layers": 18,
  "tie_word_embeddings": true
}
```
- Vision encoder: ~150M params
- Audio encoder: ~300M params

#### Gemma 4 26B-A4B (MoE)
```json
{
  "hidden_size": 2816,
  "num_hidden_layers": 30,
  "num_attention_heads": 16,
  "num_key_value_heads": 8,
  "num_global_key_value_heads": 2,
  "head_dim": 256,
  "global_head_dim": 512,
  "intermediate_size": 2112,
  "max_position_embeddings": 262144,
  "sliding_window": 1024,
  "enable_moe_block": true,
  "num_experts": 128,
  "top_k_experts": 8,
  "moe_intermediate_size": 704
}
```
- Patron: 24 sliding + 4 full attention (posiciones 5, 11, 17, 23) + shared expert
- 128 expertos fine-grained, top-8 routing, 1 shared expert
- Vision encoder: ~550M params

#### Gemma 4 31B Dense
```json
{
  "hidden_size": 5376,
  "num_hidden_layers": 60,
  "num_attention_heads": 32,
  "num_key_value_heads": 16,
  "num_global_key_value_heads": 4,
  "head_dim": 256,
  "global_head_dim": 512,
  "intermediate_size": 21504,
  "max_position_embeddings": 262144,
  "sliding_window": 1024
}
```
- Patron: 50 sliding + 10 full attention (cada 6ta capa)
- Vision encoder: ~550M params

### 2.3 Vision Encoder

**E2B/E4B:** hidden_size=768, layers=16, heads=12, patch_size=16
**26B/31B:** hidden_size=1152, layers=27, heads=16, head_dim=72, patch_size=16, intermediate_size=4304

Todos: position_embedding_size=10240, default_output_length=280, pooling_kernel_size=3
Token budgets configurables: 70, 140, 280, 560, 1120 tokens por imagen.

### 2.4 Audio Encoder (solo E2B/E4B)

USM-style conformer: hidden_size=1024, layers=12, heads=8, conv_kernel_size=5
Max 30 segundos de audio. output_proj_dims=1536.

### 2.5 Per-Layer Embeddings (PLE) -- solo E2B/E4B

Tabla de embeddings secundaria que alimenta una senal residual en cada capa decoder.
E2B: `embed_tokens_per_layer.weight` shape [262144, 8960] (= 35 capas x 256 dim).
Escalado por sqrt(hidden_size_per_layer_input) = sqrt(256) = 16.0.

### 2.6 Special Token IDs

| Token | ID |
|-------|-----|
| pad_token | 0 |
| eos_token | 1 |
| bos_token | 2 |
| boi_token | 255999 |
| boa_token | 256000 |
| image_token | 258880 |
| audio_token | 258881 |
| eoi_token | 258882 |
| eoa_token | 258883 |
| video_token | 258884 |

---

## 3. CAPACIDADES

- **Texto:** Generacion, resumen, traduccion, Q&A, razonamiento, codigo
- **Imagen:** Input en todos los modelos. Token budgets configurables (70-1120)
- **Video:** Input hasta 60s a 1fps
- **Audio:** Solo E2B/E4B, hasta 30s
- **Thinking mode:** Chain-of-thought via token `<|think|>`. Output: `<|channel>thought\n[razonamiento]<channel|>`
- **Function calling nativo:** 6 tokens especiales (`<|tool>`, `<|tool_call>`, `<|tool_result>` + pares de cierre)
- **System prompt:** Primera familia Gemma con soporte nativo de system role
- **GUI detection:** Deteccion de elementos con bounding box JSON
- **OCR / Document parsing**
- **Multilingue:** 140+ idiomas (35+ pre-entrenados nativamente)
- **Sampling recomendado:** temperature=1.0, top_p=0.95, top_k=64

---

## 4. INFERENCIA

### 4.1 HuggingFace Transformers

```bash
pip install -U transformers torch torchvision torchcodec librosa accelerate
```

**Pipeline multimodal (any-to-any):**
```python
from transformers import pipeline

pipe = pipeline("any-to-any", model="google/gemma-4-E2B-it", device_map="auto", dtype="auto")
messages = [{"role": "user", "content": [
    {"type": "image", "image": "https://example.com/photo.jpg"},
    {"type": "text", "text": "Describe esta imagen."}
]}]
output = pipe(messages, max_new_tokens=100, return_full_text=False)
```

**Multimodal avanzado:**
```python
from transformers import AutoModelForMultimodalLM, AutoProcessor

model = AutoModelForMultimodalLM.from_pretrained("google/gemma-4-31B-it", dtype="auto", device_map="auto")
processor = AutoProcessor.from_pretrained("google/gemma-4-31B-it")
```

**Solo texto (Causal LM):**
```python
from transformers import AutoModelForCausalLM, AutoProcessor

model = AutoModelForCausalLM.from_pretrained("google/gemma-4-31B-it", dtype="auto", device_map="auto")
processor = AutoProcessor.from_pretrained("google/gemma-4-31B-it")
```

**Thinking mode:**
```python
text = processor.apply_chat_template(
    messages, tokenize=False,
    add_generation_prompt=True,
    enable_thinking=True
)
```

**Notas:**
- `transformers_version` requerida: 5.5.0.dev0+
- Clase para texto: `AutoModelForCausalLM`; para multimodal: `AutoModelForMultimodalLM`
- Processor: `AutoProcessor` (unificado para texto, imagen, audio, video)

### 4.2 vLLM

```bash
uv pip install -U vllm --pre \
  --extra-index-url https://wheels.vllm.ai/nightly/cu129 \
  --extra-index-url https://download.pytorch.org/whl/cu129
```

**Single GPU:**
```bash
vllm serve google/gemma-4-E4B-it --max-model-len 32768
```

**Multi-GPU (31B):**
```bash
vllm serve google/gemma-4-31B-it \
  --tensor-parallel-size 2 \
  --max-model-len 32768 \
  --gpu-memory-utilization 0.90
```

**Docker images:**
- `vllm/vllm-openai:gemma4` (CUDA 12.9)
- `vllm/vllm-openai:gemma4-cu130` (CUDA 13.0)
- `vllm/vllm-openai-rocm:gemma4` (AMD)
- `vllm/vllm-tpu:gemma4` (TPU)

Expone API compatible con OpenAI en `http://localhost:8000/v1`.

### 4.3 Ollama

```bash
ollama pull gemma4:e2b    # 7.2GB
ollama pull gemma4:e4b    # 9.6GB (default)
ollama pull gemma4:26b    # 18GB
ollama pull gemma4:31b    # 20GB
ollama run gemma4
```

API REST compatible con OpenAI en `http://localhost:11434/v1/chat/completions`.

### 4.4 llama.cpp

```bash
llama-server -hf ggml-org/gemma-4-E2B-it-GGUF
llama-server -hf ggml-org/gemma-4-26b-a4b-it-GGUF:Q4_K_M
```

### 4.5 MLX (Apple Silicon)

```bash
pip install -U mlx-vlm
mlx_vlm.generate --model google/gemma-4-E4B-it --image https://... --prompt "Describe"
mlx_vlm.generate --model "mlx-community/gemma-4-26b-a4b-it-4bit" --prompt "..." \
  --kv-bits 3.5 --kv-quant-scheme turboquant
```

### 4.6 Otros frameworks con soporte dia-1
LiteRT-LM, Transformers.js (ONNX/browser), Candle, SGLang, NVIDIA NIM/NeMo, LM Studio, Unsloth, Cactus, Baseten, Docker, MaxText, Tunix, Keras, mistral.rs (UQFF).

---

## 5. API ACCESS

### 5.1 Google AI Studio (Gratis)

```bash
pip install google-genai
export GEMINI_API_KEY="your-api-key"  # de aistudio.google.com/apikey
```

**Modelos disponibles via API:** `gemma-4-26b-a4b-it`, `gemma-4-31b-it`

```python
from google import genai

client = genai.Client()
response = client.models.generate_content(
    model="gemma-4-26b-a4b-it",
    contents="Tu prompt aqui"
)
print(response.text)
```

**Con system instructions:**
```python
from google.genai import types

response = client.models.generate_content(
    model="gemma-4-31b-it",
    config=types.GenerateContentConfig(
        system_instruction="Eres un asistente util."
    ),
    contents="Tu prompt"
)
```

**Thinking mode via API:**
```python
config = types.GenerateContentConfig(
    thinking=types.ThinkingConfig(thinking_level="high")
)
```

**Input de imagen:**
```python
response = client.models.generate_content(
    model="gemma-4-26b-a4b-it",
    contents=[
        types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
        "Describe esta imagen."
    ]
)
```

**Function calling:**
```python
tools = types.Tool(function_declarations=[{
    "name": "get_weather",
    "description": "Obtener clima de una ubicacion.",
    "parameters": {
        "type": "object",
        "properties": {"location": {"type": "string"}},
        "required": ["location"]
    }
}])
config = types.GenerateContentConfig(tools=[tools])
```

**Google Search grounding:**
```python
config = types.GenerateContentConfig(tools=[{"google_search": {}}])
```

### 5.2 Vertex AI (Enterprise)
Mismo SDK `google-genai`, inicializacion diferente. Soporta: endpoints auto-desplegados via Model Garden, GKE, GCE, Cloud Run (con GPUs NVIDIA RTX PRO 6000 Blackwell, 96GB vGPU), y TPUs.

---

## 6. CUANTIZACION

### Formatos disponibles

**GGUF (formato principal):**
```
unsloth/gemma-4-31B-it-GGUF
unsloth/gemma-4-26B-A4B-it-GGUF
unsloth/gemma-4-E4B-it-GGUF
unsloth/gemma-4-E2B-it-GGUF
ggml-org/gemma-4-E2B-it-GGUF
bartowski/google_gemma-4-E4B-it-GGUF
```

**NVIDIA NVFP4:** `nvidia/Gemma-4-31B-IT-NVFP4` (32.7 GB)
**MLX TurboQuant:** `mlx-community/gemma-4-26b-a4b-it-4bit`
**UQFF:** Disponible via mistral.rs

**Recomendado:** Q4_K_M (mejor balance calidad/tamano para la mayoria de usuarios).

### Estimaciones de memoria

**31B:** BF16 ~61GB | NVFP4 32.7GB | AWQ 4-bit ~20.5GB | KV cache 262K: ~20.78 GiB
**26B MoE:** BF16 ~50GB | AWQ 4-bit ~17.2GB | KV cache 262K: ~5.20 GiB

---

## 7. FINE-TUNING

### 7.1 LoRA / QLoRA con HuggingFace (PEFT + TRL)

**Hiperparametros recomendados:**
```yaml
learning_rate: 2e-4
lora_rank: 16
lora_alpha: 32          # heuristica: r x 2
lora_dropout: 0.05
target_modules: [attn, ffn]
epochs: 1-3
batch_size: 4/device
gradient_accumulation_steps: 4
warmup_ratio: 0.1
lr_scheduler: cosine
```

**Dataset sizes:**
- Task-specific: 500-5,000 ejemplos
- Domain knowledge: 10,000-50,000 ejemplos

**LoRA vs QLoRA:** LoRA (16-bit) mas rapido y ligeramente mas preciso pero 4x mas VRAM. QLoRA (4-bit) mas eficiente en memoria. Si training loss < 0.2, probable overfitting.

### 7.2 Vision Fine-tuning con QLoRA
Guia oficial: `ai.google.dev/gemma/docs/core/huggingface_vision_finetune_qlora`

### 7.3 Unsloth (Optimizado)
```bash
curl -fsSL https://unsloth.ai/install.sh | sh
unsloth studio -H 0.0.0.0 -p 8888
```
Docs: `unsloth.ai/docs/models/gemma-4/train`

### 7.4 Keras LoRA
Guia oficial: `ai.google.dev/gemma/docs/core/lora_tuning`

### 7.5 Vertex AI Fine-tuning
Deploy jobs con `aiplatform.CustomContainerTrainingJob` y H100 GPUs.

---

## 8. BENCHMARKS

### Instruction-Tuned (con thinking habilitado)

| Benchmark | 31B | 26B-A4B | E4B | E2B | Gemma 3 27B |
|-----------|-----|---------|-----|-----|-------------|
| MMLU Pro | 85.2% | 82.6% | 69.4% | 60.0% | 67.6% |
| AIME 2026 | 89.2% | 88.3% | 42.5% | 37.5% | 20.8% |
| GPQA Diamond | 84.3% | 82.3% | 58.6% | 43.4% | 42.4% |
| BBH Extra Hard | 74.4% | 64.8% | 33.1% | 21.9% | 19.3% |
| MMMLU | 88.4% | 86.3% | 76.6% | 67.4% | 70.7% |
| LiveCodeBench v6 | 80.0% | 77.1% | 52.0% | 44.0% | 29.1% |
| Codeforces ELO | 2150 | 1718 | 940 | 633 | 110 |
| MMMU Pro (Vision) | 76.9% | 73.8% | 52.6% | 44.2% | 49.7% |
| MATH-Vision | 85.6% | 82.4% | 59.5% | 52.4% | 46.0% |
| MRCR v2 128k | 66.4% | 44.1% | 25.4% | 19.1% | 13.5% |

**Audio (solo E2B/E4B):**
| Benchmark | E4B | E2B |
|-----------|-----|-----|
| CoVoST | 35.54 | 33.47 |
| FLEURS (menor=mejor) | 0.08 | 0.09 |

**Arena AI:** 31B = Rank #3, 26B-A4B = Rank #6. Ambos superan modelos de 20x mas parametros.

### vs Competidores (~27-31B)
- **vs Qwen 3.5 27B:** Dentro de 1-2% en la mayoria; Qwen ligeramente arriba en MMLU Pro (86.1 vs 85.2). Gemma arriba en math (AIME 89.2%) y coding (Codeforces 2150).
- **vs Llama 4 Scout:** Gemma significativamente arriba en GPQA Diamond (84.3 vs 74.3). Llama 4 requiere 109B total params (17B activos) -- solo servidores.

---

## 9. LICENCIA (Apache 2.0)

Primera familia Gemma bajo Apache 2.0 (OSI-approved). Versiones anteriores usaban licencia custom restrictiva de Google.

**Permisos:**
- Uso comercial sin restricciones
- Fine-tuning con datos propietarios
- Redistribucion (incluyendo versiones fine-tuned) comercialmente
- Sin limites de revenue o usuarios
- Self-host en cualquier cloud/on-prem/edge

**Requisitos:**
- Incluir texto de licencia Apache 2.0 en distribuciones
- Preservar avisos de atribucion

---

## 10. ECOSISTEMA GEMMA COMPLETO

```
Gemma Family
|
+-- Gemma 1 (Feb 2024) -- 2B, 7B -- Solo texto, 8K ctx
+-- Gemma 2 (Jun 2024) -- 2B, 9B, 27B -- Solo texto, 8K ctx
+-- Gemma 3 (Mar 2025) -- 1B, 4B, 12B, 27B -- Texto+Imagen, 128K ctx
+-- Gemma 4 (Abr 2026) -- E2B, E4B, 26B MoE, 31B -- Texto+Imagen+Audio+Video, 256K, Apache 2.0
|
+-- CodeGemma (Abr 2024) -- 2B, 7B, 7B-it -- Especialista codigo (base Gemma 1)
+-- RecurrentGemma (Abr 2024) -- 2B, 9B -- Arquitectura Griffin, recurrencia lineal
+-- PaliGemma 1 (2024) -- 3B -- Vision-Language (SigLIP + Gemma 1)
+-- PaliGemma 2 (Dic 2024) -- 3B, 10B, 28B -- Vision-Language (SigLIP + Gemma 2)
+-- ShieldGemma 1 (2024) -- 2B, 9B, 27B -- Safety classifier texto (base Gemma 2)
+-- ShieldGemma 2 (2025) -- 4B -- Safety classifier texto+imagen (base Gemma 3)
```

> **Nota:** No existe PaliGemma 4 ni CodeGemma 4 dedicados. Gemma 4 absorbe esas capacidades nativamente.

---

## 11. GUIA RAPIDA DE SELECCION

| Caso de uso | Modelo recomendado |
|-------------|-------------------|
| Mobile / Browser / Edge | E2B (5GB 4-bit) |
| Laptop / Desktop | E4B (8GB 4-bit) |
| Workstation GPU consumer (24GB) | 26B-A4B MoE Q4_K_M |
| Servidor / Multi-GPU | 31B Dense |
| Maximo rendimiento API sin infra | 31B via Google AI Studio API |
| Audio processing | E2B o E4B (unicos con audio) |
| Contexto largo (256K) | 26B-A4B o 31B |
| Fine-tuning con GPU limitada | E2B o E4B con QLoRA |
| Produccion enterprise | 31B via Vertex AI |
