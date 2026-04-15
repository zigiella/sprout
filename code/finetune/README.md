# Sprout Policy Reasoning v1 — Fine-tuning con Unsloth

> Modelo derivado de Gemma 4 E2B, especializado en interpretar politicas agricolas locales bajo senales contradictorias y contexto incompleto. Publicado con pesos y benchmarks. Candidato al **Unsloth Special Track ($10K)**.

---

## 1. Objetivo

Entrenar un Gemma 4 E2B adaptado al dominio de Sprout para que:

1. Genere decisiones locales (decision + razonamiento + flags + confianza) con schema JSON consistente
2. Detecte contradicciones entre senales (sensor vs vision, vision vs politica, meteo vs estado)
3. Respete caducidades explicitamente (si weather_packet.ttl expirado -> no usar)
4. Funcione on-device en Jetson Orin Nano Super y en Pixel 10 Pro
5. Sea mejor que E2B base en este dominio especifico

---

## 2. Entregables

- **Pesos LoRA** publicados en HuggingFace: `sprout/sprout-rhizome-e2b-v1`
- **Version GGUF cuantizada** (Q4_K_M, Q5_K_M) para llama.cpp/Ollama
- **Model card** con proposito, limitaciones, licencia, benchmarks
- **Benchmarks reproducibles** en `code/finetune/notebooks/eval.ipynb`
- **Dataset sintetico** publicado (o resumen + generator script, segun licencia)

---

## 3. Stack

- **Base model:** `google/gemma-4-E2B-it`
- **Framework:** [Unsloth](https://unsloth.ai/docs/models/gemma-4/train)
- **Metodo:** QLoRA 4-bit
- **Compute:** Google Colab A100 (preferente) o T4 (fallback)
- **Tracking:** Weights & Biases (opcional) o CSV manual

---

## 4. Hiperparametros

```yaml
base_model: google/gemma-4-E2B-it
method: QLoRA
load_in_4bit: true
lora:
  r: 16
  alpha: 32
  dropout: 0.05
  target_modules: [q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj]
training:
  learning_rate: 2e-4
  epochs: 3
  per_device_batch_size: 4
  gradient_accumulation_steps: 4
  warmup_ratio: 0.1
  lr_scheduler: cosine
  max_seq_length: 4096
  weight_decay: 0.01
  bf16: true
```

Justificacion en [GEMMA4-SKILL.md seccion 7](../../GEMMA4-SKILL.md).

---

## 5. Dataset: "Sprout Policy Reasoning v1"

### 5.1 Tamanos por fase

| Fase | # ejemplos | Origen |
|------|-----------|--------|
| Seed | 50 | Escritura manual (Bea + Cambium) |
| Expansion | 1450 | Generacion con Claude/GPT-4, plantilla estructurada |
| Revision | 1500 | Revision humana del 100% |
| Split | train 1350 / val 75 / test 75 | Estratificado por tipo de escenario |

### 5.2 Formato de cada ejemplo

```json
{
  "input": {
    "rhizome_id": "rhizome_02",
    "timestamp": "2026-04-15T17:12:00Z",
    "sensors": {
      "soil_moisture": 0.23,
      "reservoir_level": 0.38,
      "flow_confirmed": null
    },
    "vision_summary": "hojas con curling leve en margen superior, tono amarillento incipiente",
    "context": {
      "policy_active": {"name": "conservador_v3", "ttl_remaining_h": 6},
      "hours_since_last_watering": 18,
      "weather_borrowed": null,
      "short_memory": ["bloqueo_riego_t-4h_por_deposito_bajo"]
    }
  },
  "output": {
    "decision": "riego_micro_ajuste",
    "duration_s": 45,
    "reasoning": "Suelo bajo y vision sugiere estres temprano. Deposito marginal y sin meteo prestada reciente. Micro-dosis con senal de revision.",
    "contradiction_flags": ["visual_stress_but_policy_conservative"],
    "requires_revision": true,
    "confidence": 0.72
  }
}
```

### 5.3 Categorias de escenarios (balanceadas)

| Categoria | % | Descripcion |
|-----------|---|-------------|
| normal | 20% | Sensores coherentes, politica vigente aplicable, decision directa |
| contradiccion_sensor_vision | 15% | Humedad OK pero planta mal, o al reves |
| meteo_fresca_cambia_coste | 15% | Weather packet fresco modifica el calculo esperado |
| meteo_caducada | 10% | Weather packet llega con TTL expirado, debe ignorarse |
| deposito_bajo | 10% | Deposito critico, prudencia obligatoria |
| falta_caudal | 5% | Bomba ordenada pero caudalimetro no confirma |
| politica_caducada | 10% | Politica activa cerca de expirar, pedir revision |
| parcela_sin_meteo | 10% | Sin estacion local ni weather packet reciente |
| modo_alerta | 5% | Riesgo fisico obvio, bloqueo total |

### 5.4 Proceso de generacion

1. **Seed (~50 ejemplos).** Bea + Cambium escriben a mano los casos duros. Cada categoria debe tener al menos 3 seeds.
2. **Plantillas.** De cada seed extraemos una plantilla con slots (sensores, meteo, vision, contexto).
3. **Expansion sintetica.** Usamos Claude/GPT-4 con prompt que genera variaciones respetando la plantilla y los principios del sistema (offline-first, prudencia, caducidad).
4. **Revision humana.** Cada ejemplo generado se revisa manualmente. Si no respeta los principios, se corrige o descarta.
5. **Dedup y split.** Eliminamos duplicados semanticos y hacemos split estratificado.

---

## 6. Prompt template (training)

```
<|system|>
Eres Rhizome, el nodo edge de Sprout. Decides acciones locales seguras para una parcela con agua limitada y conectividad incierta. Tu salida es SIEMPRE un JSON conforme al schema provisto. Principios: offline-first, la IA propone y la seguridad dispone, toda politica tiene caducidad, nunca uses contexto caducado.

Schema de salida:
{schema_json}

<|user|>
Estado actual:
{input_json}

<|assistant|>
{output_json}
```

Prompts versionados en `code/finetune/prompts/`.

---

## 7. Evaluacion

### 7.1 Metricas automaticas

- **JSON validity rate** (objetivo >=95%): ¿el output es JSON parseable y pasa schema?
- **Key field accuracy** (objetivo >=85%): ¿`decision`, `duration_s`, `requires_revision` estan en rangos validos?
- **Contradiction detection F1** (held-out test set): precision + recall de `contradiction_flags` vs ground truth
- **Expiration respect rate** (objetivo 100%): de los casos con weather caducada, ¿cuantos ignora correctamente?

### 7.2 Eval humana

50 casos lado-a-lado:
- Output de Gemma 4 E2B base
- Output de `sprout-rhizome-e2b-v1` (fine-tuned)

Bea y Cambium (ciegos a cual es cual) puntuan 0-5 en: coherencia, prudencia, utilidad del razonamiento.

### 7.3 Latencia

Benchmark en:
- Jetson Orin Nano Super (target produccion Rhizome)
- Pixel 10 Pro (target Pollen)
- Portatil CPU (baseline)

Objetivo: <3s per decision en Jetson, <5s en Pixel.

---

## 8. Estructura del subproyecto

```
code/finetune/
├── README.md                    # este archivo
├── requirements.txt
├── dataset/
│   ├── seed/                    # 50 ejemplos escritos a mano
│   │   ├── 001_normal.json
│   │   ├── 002_contradiccion_sensor_vision.json
│   │   └── ...
│   ├── templates/               # plantillas de expansion
│   ├── generator.py             # script de expansion sintetica
│   ├── review.py                # interfaz minima de revision humana
│   ├── schema.json              # schema de validacion
│   └── processed/
│       ├── train.jsonl
│       ├── val.jsonl
│       └── test.jsonl
├── notebooks/
│   ├── 01_generate_dataset.ipynb
│   ├── 02_train_unsloth.ipynb
│   ├── 03_eval.ipynb
│   └── 04_export_gguf.ipynb
├── prompts/
│   └── system_v1.txt
└── configs/
    └── train_v1.yaml
```

---

## 9. Timeline dentro del sprint

Semana 1: seed + plantillas (paralelo al resto del sprint)
Semana 2: generacion sintetica + revision + training
Semana 3: evaluacion + publicacion + integracion en Rhizome/Pollen
Semana 4: buffer por si algo falla

---

## 10. Riesgos

| Riesgo | Mitigacion |
|--------|-----------|
| Colab se queda sin compute en momento clave | Plan B: alquilar A100 2h en runpod.io (~$3) |
| E2B fine-tuned es peor que base en casos generales | Eval humana pesa mas que la automatica; si es peor, publicamos hallazgo en writeup como limitacion honesta |
| Dataset sintetico tiene sesgo | Revision humana 100% + seeds escritos por el equipo cubren casos reales de la terraza |
| GGUF tiene perdida de calidad no aceptable | Probamos Q5_K_M si Q4_K_M es insuficiente |

---

## 11. Cumplimiento de naming Gemma

Segun [guia de naming de Google](https://ai.google/documents/32/External_Gemma_Model_Variant_Guidelines.pdf):

- NO usamos "Gemma" en el nombre del modelo derivado
- Modelo publicado: `sprout/sprout-rhizome-e2b-v1` (no `sprout-gemma-...`)
- En la model card indicamos claramente: "Fine-tuned from Gemma 4 E2B. Not affiliated with Google DeepMind."
- Mantenemos la licencia Apache 2.0 heredada de Gemma 4

---

## 12. Referencias

- [Unsloth Gemma 4 training guide](https://unsloth.ai/docs/models/gemma-4/train)
- [GEMMA4-SKILL.md seccion 7](../../GEMMA4-SKILL.md)
- [HuggingFace PEFT docs](https://huggingface.co/docs/peft)
