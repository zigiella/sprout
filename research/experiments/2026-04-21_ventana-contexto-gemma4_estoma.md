# Ventana de contexto de Gemma 4 en Ollama

**Fecha bitacora:** 2026-04-21
**Autora del formato (celula):** Estoma
**Rescate de:** `bitacora/2026-04-20_research-ventana-contexto-gemma4-ollama_meristem.md` (untracked en main al cierre del dia 6)

> Esta es la primera bitacora de la celula Estoma+Peri y es un **rescate**, no un experimento original. La investigacion la hizo Bea el dia 6; Meristem la apunto para el equipo en bitacora untracked y ahi se quedo. La traemos al canal formal de la celula para probar el circuito completo en un caso real.

---

## 1. Ficha tecnica del experimento original

- **Naturaleza:** cotejo directo de **documentacion oficial**, no experimento publico de terceros. Por eso no hay repo ni paper que destripar; la fuente son las paginas canonicas del vendor.
- **Autoria de la investigacion:** **Bea**, cierre del dia 6 (2026-04-20), trabajo personal al hilo de preparar el harness.
- **Autoria de los apuntes de aplicacion a Sprout:** **Meristem**, mismo dia, bitacora untracked.
- **Fecha de consulta de fuentes:** 2026-04-20 (docs vivas; re-verificable bajo cambio).
- **Fuentes primarias:**
  - [Gemma model card (Google AI for Developers)](https://ai.google.dev/gemma/docs/core/model_card_4)
  - [Ollama — context length](https://docs.ollama.com/context-length)
  - [Ollama — Modelfile](https://docs.ollama.com/modelfile)
  - [Gemma + Ollama (integrations)](https://ai.google.dev/gemma/docs/integrations/ollama?hl=es-419)
- **Claim central en una linea:** el contexto efectivo de un modelo Gemma 4 servido por Ollama **no lo fija la model card, lo fija `min(techo_modelo, asignacion_Ollama_por_VRAM)`**, y por defecto en maquinas con <24 GiB de VRAM esa asignacion es **4K** — muy por debajo del techo nominal del modelo.

---

## 2. Metodo y resultados en nuestras palabras

### 2.1 Techos segun la model card de Google

| Modelo Ollama | Familia | Contexto max | Sliding window | Parametros |
|---|---|---|---|---|
| `gemma4:e2b` | denso | 128K | 512 | 2B |
| `gemma4:e4b` | denso | 128K | 512 | 4B |
| `gemma4:26b` | MoE | 256K | 1024 | 25.2B totales / 3.8B activos |

El 26B MoE se posiciona como **mas rapido de lo que su tamano bruto sugiere** (porque solo 3.8B se activan por token), pero su KV cache sigue siendo la de un modelo 25.2B — la ventana alta no es gratis.

### 2.2 Lo que pone Ollama por defecto

Aunque el modelo soporte 128K o 256K, Ollama **no concede esa ventana automaticamente**. La asigna segun VRAM detectada:

| VRAM detectada | Contexto que Ollama asigna |
|---|---|
| < 24 GiB | **4K** |
| 24–48 GiB | 32K |
| ≥ 48 GiB | 256K |

Ademas, su propia documentacion recomienda **al menos 64K** para tareas de agentes, web search o coding tools.

**Consecuencia operativa:** el contexto efectivo sera el minimo entre el techo del modelo y lo que Ollama haya reservado. Si nadie lo verifica, las alucinaciones que salen de un contexto apretado se confunden con "razonamiento pobre del modelo".

### 2.3 Recomendacion practica por modelo (criterio de Bea)

No tabla oficial; **criterio operativo de Bea apoyado en los limites documentados**. Lo dejamos como guia, no como contrato.

**`gemma4:e2b` — latencia, pruebas rapidas, clasificacion, extraccion, routing, preprocesado:**
- 8K — chat simple o prompts cortos.
- 16K–32K — uso general.
- 64K — coding ligero, asistentes con historial largo, RAG con bastante contexto.
- 128K — solo si la maquina aguanta y el caso lo justifica.

**`gemma4:e4b` — punto medio razonable, si hay un unico local "todoterreno":**
- 16K — base seria.
- 32K — casi todo.
- 64K — coding, agentes, RAG, analisis de documentos.
- 96K–128K — solo con razon clara y memoria suficiente.

**`gemma4:26b` — analisis largos, coding serio, agentes con mucha memoria, RAG extenso:**
- 32K — si la maquina va justa.
- 64K — configuracion util de verdad.
- 128K — cuando el caso lo pida y la VRAM no se hunda.
- 256K — solo si sabes lo que haces y puedes pagarlo en memoria y latencia.

### 2.4 Como fijar en practica

**Por llamada (Python + cliente Ollama):**

```python
from ollama import chat

DEFAULT_CTX = {
    "gemma4:e2b": 16384,
    "gemma4:e4b": 32768,
    "gemma4:26b": 65536,
}

def ask(model: str, prompt: str, think: bool = True):
    return chat(
        model=model,
        messages=[
            {"role": "system", "content": "Se preciso y no repitas contexto innecesario."},
            {"role": "user", "content": prompt},
        ],
        think=think,
        stream=False,
        options={
            "num_ctx": DEFAULT_CTX[model],
            "temperature": 0.2,
            "num_predict": 512,
        },
    )
```

**En Modelfile** (si se fija por modelo y no por llamada):

```
PARAMETER num_ctx 32768
```

**Global al demonio** (util cuando no se controla al caller):

```bash
OLLAMA_CONTEXT_LENGTH=64000 ollama serve
```

### 2.5 Como comprobar que no te estas enganando

Auditoria rapida de lo que *realmente* esta cargado:

```bash
ollama ps
```

La columna `CONTEXT` muestra la ventana real concedida al modelo cargado. La columna `PROCESSOR` dice si el modelo se ha offloadeado a CPU (lo que suele pasar cuando no cabe en VRAM). Es el check mas barato y casi nadie lo hace.

### 2.6 Perfiles por tipo de tarea (consolidado)

| Tarea | E2B | E4B | 26B |
|---|---|---|---|
| Chat / prompts cortos | 8K | 16K | 32K |
| RAG razonable | 16K–32K | 32K–64K | 64K–128K |
| Agentes / coding (recomendacion Ollama ≥64K) | 32K (si no queda otra) | 64K | 64K–128K |

---

## 3. Reproduccion propia

**No hay experimento nuevo en este rescate.** La evidencia aplicable la aporta indirectamente la medicion existente del harness de Xilema en `code/rhizome/benchmarks/2026-04-18_gemma4-e4b_hp-probook-460-g11_smoke.json` (y la version extendida del dia 5 citada por Meristem, `docs/benchmarks/2026-04-19_gemma4-e4b_hp-probook-460-g11.md`):

- Host: HP ProBook 460 G11, Windows 11, 16 GB RAM, sin GPU dedicada, Ollama 0.21.0.
- Baseline E4B E2E: 123.7s total, 6.17 t/s, first-token ≈100s, RAM peak 15.46 GiB.

**Relectura a la luz del default <24 GiB → 4K:** el E4B de Bea probablemente corrio con **ventana efectiva 4K**, no con los 8–16K que implicitamente asumiamos al diseñar prompts de Meristem. Eso convierte el baseline de "latencia pura de CPU" en "latencia de CPU con ventana cerca del tope" — explica mejor el `prompt_eval` alto y el first-token lento.

**Verificacion pendiente, barata:** antes de arrancar [#42](https://github.com/zigiella/sprout/issues/42), cargar el E4B en ese mismo host y correr `ollama ps` para anotar `CONTEXT` real y `PROCESSOR`. Sin ese check, "corrio a 4K" es **inferencia razonable desde documentacion**, no hecho medido. Queda como tarea ligada al primer PR que toque esa ruta.

Otras reproducciones utiles que la celula puede hacer en proximos experimentos (no hechas aqui):

- Medir `first_token` y `tokens/s` para E4B con `num_ctx ∈ {4K, 8K, 16K, 32K}` en el portatil real, sin otras variables.
- Medir lo mismo para 26B MoE via Gemini API (proxy cloud) con `num_ctx` equivalente conceptual.
- Confirmar que `ollama ps` reporta el CONTEXT esperado tras forzar `num_ctx` por llamada (sanity del path de config).

---

## 4. Transferibles a Sprout

Cinco impactos directos — cada uno menciona explicitamente a la miembra impactada y, cuando aplica, al issue abierto.

### 4.1 Relectura del baseline E4B — @meristem, @xilema

**Que cambia:** la latencia medida del harness no es techo puro de inferencia CPU; es techo con ventana apretada (probablemente 4K). La optimizacion de [#42](https://github.com/zigiella/sprout/issues/42) (migrar a `/api/chat` + quitar schema duplicado del user prompt) gana peso — el `prompt_eval_count` estaba mucho mas cerca del tope real de lo que pensabamos.

**Accion recomendada:** antes de arrancar [#42](https://github.com/zigiella/sprout/issues/42), ejecutar `ollama ps` con el E4B cargado, anotar `CONTEXT` real y `PROCESSOR` en el PR, y considerar fijar `num_ctx=16384` como default explicito al llamar a `chat(...)`.

**Dueña natural:** Meristem (ruta del adapter / policy_engine). Impacto secundario en el harness de **Xilema** si quiere anotar `CONTEXT` en los reports JSON junto a latencia, t/s y RAM peak.

### 4.2 Adapter Ollama-compatible a Gemini — @meristem, @cambium

**Que cambia:** el adapter `meristem_inference_adapter` de [#46](https://github.com/zigiella/sprout/issues/46) debe tratar `num_ctx` como opcion de primera clase y propagarla correctamente en los dos modos.

- **Modo `local`** (reverse-proxy a Ollama real): pasar `num_ctx` tal cual en `options`. Ollama lo respeta por llamada.
- **Modo `cloud`** (Gemini API): `num_ctx` no existe como parametro directo. Su equivalente conceptual es `hard_limit_modelo − thinking_budget − output_budget`. El adapter debe:
  - exponerlo como referencia,
  - validar con `count_tokens` antes de llamar,
  - devolver 400 si el prompt excede.
- **Defaults si el caller no envia `num_ctx`:** 16K (E2B), 32K (E4B), 64K (26B MoE) — tabla de Bea.

### 4.3 Grid del sweep de ventana — @meristem, @xilema

Refinamiento del grid propuesto por Meristem para [#47](https://github.com/zigiella/sprout/issues/47):

- **26B MoE (modelo primario del sweep, cloud):** `{16K, 32K, 64K, 128K}`. Cubre "base seria", "util de verdad", "cuando el caso lo pida", "techo con riesgo". Descartamos 8K (cae por debajo de la base seria para ese modelo).
- **E4B local (sanity del andamio):** `{8K, 16K}`. Valida que podemos subir desde el 4K efectivo actual.
- **Protocolo de cada punto:** arrancar con `ollama ps` (local) o log del `num_ctx` enviado (cloud) *antes* de la primera llamada, para auditar que la ventana real coincide con la nominal del punto. Sin ese check, el sweep mide otra cosa.

### 4.4 Configuracion fija del A/B de thinking — @meristem

Para el A/B de thinking mode ([#44](https://github.com/zigiella/sprout/issues/44), posiblemente absorbido por [#47](https://github.com/zigiella/sprout/issues/47)):

- **26B MoE:** `num_ctx = 32K` ("base seria", no inflar).
- **Sanity E4B:** `num_ctx = 16K`.

Se rechaza 64K para 26B porque entonces la varianza observable puede venir de mayor contexto disponible y no del thinking. Esta anotacion debe entrar en el protocolo del experimento.

### 4.5 Narrativa del video — @corola

**Impacto bajo, informativo.** La cartela "E4B MVP / 26B objetivo" del plano 10 gana solidez cuantitativa: la diferencia entre andamio y objetivo no es solo "4B vs 25.2B parametros" — es tambien ventana operativa util (128K vs 256K) y como Ollama la expone segun VRAM. No cambia el guion ni el rodaje; es municion para el writeup si aparece espacio.

---

## 5. No-transferibles

Tres cosas del material que **no** se aplican a Sprout tal cual, y conviene dejarlas escritas para no aplicar el consejo generico donde no toca.

### 5.1 La recomendacion "≥64K para agentes, web search, coding tools"

Viene de casos de uso generalistas de Ollama. **Sprout no hace web search ni coding tools en los nodos.** Meristem opera sobre snapshots estructurados + schemas + policy activa; aunque las operaciones E (meteo consolidada) y F (bucle hipotesis-aprendizaje) añadan +3–9k tokens sobre el bundle base, el ciclo realista cabe holgadamente por debajo de 64K. No convertimos "64K" en minimo universal del proyecto — se aplica donde tenga sentido (Meristem en ciclos context-heavy) y no, por ejemplo, en el E2B del Rhizome.

### 5.2 Los techos altos del 26B MoE (128K–256K)

Estan documentados como posibles pero **pagan caro en KV cache**. Sprout no los usa ni en MVP ni en arquitectura objetivo. Son referencia de que "el modelo soporta", no objetivo de configuracion. Importante no arrastrarlos al sweep como si fueran escalones naturales — lo son para casos de analisis muy largo, no para consolidacion agricola.

### 5.3 `PARAMETER num_ctx` fijo en Modelfile como patron default

Tentador para simplificar despliegue, pero en Sprout el mismo engine debe poder correr prompts de distinto tamano (snapshot simple vs. consolidacion con meteo+learnings). Fijar `num_ctx` en Modelfile rigidiza. El adapter lo expone por llamada y ese es el camino correcto. Esto va contra una lectura ingenua de la doc de Ollama (que presenta el Modelfile como la forma "natural" de fijar parametros) — conviene tenerlo escrito para no regresar a Modelfiles rigidos en refactors futuros.

---

## Referencias

- Model card Gemma 4 — https://ai.google.dev/gemma/docs/core/model_card_4
- Ollama context length — https://docs.ollama.com/context-length
- Ollama Modelfile — https://docs.ollama.com/modelfile
- Gemma + Ollama (integraciones) — https://ai.google.dev/gemma/docs/integrations/ollama?hl=es-419
- Borrador original rescatado: `bitacora/2026-04-20_research-ventana-contexto-gemma4-ollama_meristem.md` (untracked en main; queda como registro historico de la conversacion Bea↔Meristem)
- Medicion asociada del harness: `code/rhizome/benchmarks/2026-04-18_gemma4-e4b_hp-probook-460-g11_smoke.json` + la version extendida `docs/benchmarks/2026-04-19_gemma4-e4b_hp-probook-460-g11.md`
- Issues afectados: [#42](https://github.com/zigiella/sprout/issues/42) (migrar a `/api/chat`), [#44](https://github.com/zigiella/sprout/issues/44) (A/B thinking), [#46](https://github.com/zigiella/sprout/issues/46) (adapter Ollama→Gemini), [#47](https://github.com/zigiella/sprout/issues/47) (sweep de ventana)

---

**Siguiente paso (Peri):** al mergear esta bitacora a main, abrir issue `research-digest` con:
- Label: `research-digest`
- Titulo: `[digest] ventana de contexto Gemma 4 + Ollama`
- Resumen ejecutivo: §2.1, §2.2, los cinco transferibles de §4 y los tres no-transferibles de §5.
- Tags: `@meristem` (refuerzo — impacto en #42/#44/#46/#47), `@floema` (quien mas lo necesita para E4B en Pixel 10 Pro), `@xilema` (impacto en harness Rhizome), `@cambium` (revisa adapter y decide defaults), `@corola` (informativo para writeup).

— Estoma
