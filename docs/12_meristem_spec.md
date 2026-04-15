# Meristem — Spec tecnica del MVP

> Meristem es el nodo estrategico. No ejecuta, no transporta. Consolida, revisa politicas, detecta patrones entre parcelas y emite criterio mas duradero. **Vive local.**

---

## 1. Rol en el sistema

- Consolida snapshots y contradiction_alerts recibidos via Pollen
- Revisa si las politicas vigentes estan funcionando
- Detecta patrones entre parcelas (ej. "todos los Rhizome de la zona norte estan ajustando ventana de riego a la baja")
- Genera nuevos policy_packets o valida policy_deltas propuestos por Pollen
- Mantiene el marco estrategico del sistema (politicas con horizontes de dias a semanas)

Lo que **NO** hace:
- No riega en tiempo real
- No envia microordenes directas al actuador
- No es un punto unico de fallo del sistema (si Meristem cae, Rhizome sigue operando y Pollen sigue llevando deltas temporales)

---

## 2. Arquitectura de dos capas: **Meristem Local** y **Meristem Sombra**

Esta es la decision estructural del MVP y del writeup.

### 2.1 Meristem Local (produccion, demo, entrega)
- **Hardware:** portatil de Bea (16 GB RAM, sin GPU dedicada asumida)
- **Modelo:** `gemma4:e4b` via Ollama (~8 GB Q4_K_M, deja 8 GB para OS + contexto + herramientas)
- **Interfaz:** HTTP local en `http://localhost:11434/v1` (OpenAI-compatible)
- **Estado:** **lo que corre en el demo grabado**
- **Upgrade path:** si se adquiere Mac mini M4 24 GB antes del deadline, upgrade a `gemma-4-26b-a4b` via Ollama (~17 GB Q4_K_M, gana en razonamiento estrategico)

### 2.2 Meristem Sombra (solo tiempo de test, desarrollo, validacion)
- **Hardware:** cloud, Google AI Studio API
- **Modelo:** `gemma-4-31b-it` (el mas capaz de la familia)
- **Proposito:** **oraculo de validacion** durante desarrollo. No corre en produccion ni en demo.
- **Como se usa:** un `compare_harness` envia cada prompt en paralelo al local y al sombra, registra diffs, mide latencia.

### 2.3 Por que esta separacion

Tres razones:

1. **Narrativa local-first intacta.** El demo grabado y el sistema desplegado son 100% local. El jurado no ve nube.
2. **Datos de calidad para el writeup.** Podemos decir algo cuantitativo: *"Validamos 500 decisiones locales contra Gemma 4 31B como referencia cloud. El E4B local coincidio en X% de los casos y en los desacuerdos fue mas conservador en Y%."*
3. **Material para tracks tecnologicos.** Este patron de "routing entre modelos segun contexto" abre la puerta al **Cactus Special Track** si lo enmarcamos en la arquitectura de Pollen tambien.

### 2.4 Reglas duras del sombra (no negociables)

- Vive detras de un flag: `SHADOW_ENABLED=false` por defecto en cualquier rama
- Requiere variable de entorno `GEMINI_API_KEY` para activarse — si no esta, el sistema no intenta llamar al sombra
- El codigo de sombra vive en `code/meristem/shadow/` claramente separado
- **El demo grabado se rueda con el flag apagado y la credencial no cargada**
- El writeup menciona el sombra explicitamente y explica que no corre en produccion

---

## 3. Que viaja hacia y desde Meristem

### Entrada (desde Pollen)
- Snapshots de Rhizome recolectados
- `contradiction_alert`s
- `weather_packet`s observados por Pollen (voz, camara, sensores del telefono)
- `policy_delta`s propuestos por Pollen que requieren validacion

### Salida (hacia Pollen, para entrega a Rhizome)
- `policy_packet`s nuevos (politicas completas, raramente)
- `policy_delta`s validados o reajustados
- `policy_revocation`s cuando una politica deja de tener sentido (ej. fin de ola de calor)

Schemas completos en `code/shared/schemas/`.

---

## 4. Stack de software

### Lenguaje
- Python 3.11+

### Dependencias principales
- `ollama` (cliente oficial) para comunicacion con el modelo local
- `google-genai` (solo si `SHADOW_ENABLED`)
- `pydantic` para validacion de schemas
- `fastapi` + `uvicorn` si queremos una API HTTP local para que Pollen empuje y consulte
- `pandas` para el harness de comparacion
- `pytest` para tests

### Estructura
```
code/meristem/
├── README.md
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── main.py              # entrypoint / API HTTP
│   ├── consolidator.py      # consume snapshots y alerts
│   ├── policy_engine.py     # genera policies/deltas usando LLM
│   ├── validator.py         # valida deltas propuestos por Pollen
│   ├── llm_client.py        # cliente Ollama para E4B
│   ├── shadow/
│   │   ├── __init__.py
│   │   ├── shadow_client.py # cliente google-genai para 31B
│   │   └── compare.py       # harness de comparacion
│   └── prompts/             # prompts versionados
└── tests/
```

---

## 5. Prompt engineering para E4B

Gemma 4 E4B con 4B params activos puede parecer limitado para razonamiento estrategico. Compensamos con:

1. **Thinking mode habilitado** (`enable_thinking=True` en el chat template) para decisiones criticas
2. **Structured output** con schema JSON validado post-hoc via pydantic
3. **Few-shot prompting** con 3-5 ejemplos embedidos en el system prompt
4. **Fine-tuning del modelo de Rhizome (E2B)** ayuda indirectamente a Meristem porque reduce la entropia de las decisiones que Meristem tiene que consolidar

### System prompt base (draft)

```
Eres Meristem, el nodo estrategico de Sprout, una red agricola local-first.
Tu rol es consolidar evidencia de multiples parcelas, revisar politicas vigentes,
y emitir nuevas politicas o deltas cuando el contexto lo exige.

Principios duros:
- Nunca ordenes acciones inmediatas. Emites politicas.
- Toda politica tiene TTL.
- Cuando hay contradicciones entre parcelas, prefiere la prudencia.
- Cuando los datos tienen mas de 48h, marca menor confianza.
- Produces SOLO JSON valido conforme al schema provisto.
```

Los prompts completos viven versionados en `src/prompts/`.

---

## 6. Ciclo de consolidacion

Meristem no corre en tiempo real. Corre cuando Pollen llega con evidencia nueva:

1. Pollen hace push (WiFi local) → endpoint `/ingest` de Meristem
2. Meristem valida y persiste la evidencia
3. Dispara un job de consolidacion si hay >=N evidencias nuevas desde el ultimo ciclo
4. El job:
   - Construye contexto (snapshots + alerts + deltas pendientes)
   - Llama al LLM local (E4B) con prompt de revision de politica
   - Si `SHADOW_ENABLED`, llama tambien al sombra y registra diff
   - Valida el output contra schema
   - Persiste policy_packet o policy_delta validado
   - Lo deja en cola para que el proximo Pollen lo recoja

Latencia objetivo: <60s desde push de Pollen a disponibilidad del delta de retorno.

---

## 7. Persistencia

- **SQLite** local (sin servidor externo)
- Tablas:
  - `evidence`: snapshots, alerts, packets recibidos
  - `policies`: policy_packets emitidos (con version)
  - `deltas`: policy_deltas (propuestos + validados + revocados)
  - `decisions_log`: decisiones locales de Rhizome importadas via Pollen (para auditoria)
  - `shadow_comparisons`: si sombra esta on, diffs entre local y 31B cloud

---

## 8. Que demostrar en video (aparte de lo que hace Pollen)

- Un plano donde se ve al portatil de Bea corriendo Meristem (terminal o UI minimal)
- El output de un policy_delta generado localmente
- Indicador visible de "local only" (ej. sin icono de red o con overlay "sin conexion externa")
- **Opcional en writeup, NO en video:** grafico que muestra el % de acuerdo local vs sombra

---

## 9. Fuera de alcance del MVP

- Memoria estacional profunda (solo memoria corta operativa)
- RAG visible sobre base de conocimiento agricola (roadmap v2)
- UI rica con dashboards (solo terminal/CLI)
- Despliegue multi-Meristem (solo uno en el MVP)

---

## 10. Referencias

- [GEMMA4-SKILL.md](../GEMMA4-SKILL.md) seccion 4.3 (Ollama) y 5.1 (Google AI Studio)
- [Ollama library gemma4](https://ollama.com/library/gemma4)
