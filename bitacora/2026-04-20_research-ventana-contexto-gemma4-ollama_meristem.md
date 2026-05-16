# Apuntes sobre ventana de contexto en Gemma 4 + Ollama

**Fecha:** 2026-04-20 (cierre del dia 6)
**Autor:** Bea (research); anotaciones de aplicacion por Meristem
**Area:** Meristem / backend de inferencia / harness
**Tipo:** Research externo con notas de impacto para Sprout

---

## Nota de Meristem

Bea compartio estos apuntes al cerrar el dia 6 con la instruccion *"guardalo para ti y para el equipo"*. El cuerpo son sus apuntes literales; al final anoto las implicaciones directas para #46, #47, #44 y para la lectura de las mediciones del dia 5.

---

## Lo que cambia entre los tres modelos

En **Gemma 4**, `E2B` y `E4B` son los modelos pequenos densos, con **128K de contexto maximo** y ventana deslizante de **512 tokens**. El **26B A4B** es el modelo **MoE**, con **256K de contexto maximo**, ventana deslizante de **1024 tokens**, **25.2B** parametros totales y **3.8B activos** durante inferencia. Google lo presenta precisamente como una opcion mas rapida de lo que su tamano bruto sugiere.

En **Ollama**, las etiquetas oficiales para esos tres son:

- `gemma4:e2b`
- `gemma4:e4b`
- `gemma4:26b`

## El limite real no lo pone solo el modelo

Aunque el modelo soporte 128K o 256K, **Ollama no te lo concede automaticamente**. Por defecto, Ollama asigna contexto segun VRAM:

- menos de 24 GiB: **4K**
- entre 24 y 48 GiB: **32K**
- 48 GiB o mas: **256K**

Ademas, la propia documentacion recomienda **al menos 64K** para tareas de agentes, web search o coding tools.

Asi que tu contexto efectivo sera, en la practica:

**minimo entre el maximo del modelo y el contexto que Ollama haya reservado**.

Eso parece obvio. Luego nadie lo mira y se pasa media tarde interpretando alucinaciones como si fueran filosofia.

## Recomendacion practica por modelo (criterio de Bea)

Criterio operativo de Bea apoyado en limites documentados, no tabla oficial Google/Ollama.

### Para `gemma4:e2b`

Usalo cuando priorices **latencia, pruebas rapidas, clasificacion, extraccion, routing, preprocesado**, o agentes pequenos donde el coste por vuelta importa mas que la brillantez. Admite hasta **128K** pero conviene empezar:

- **8K** para chat simple o prompts cortos
- **16K-32K** para uso general
- **64K** si haces coding ligero, asistentes con historial largo o RAG con bastante contexto

Irte a 128K con E2B tiene sentido solo si la maquina aguanta y el caso lo justifica.

### Para `gemma4:e4b`

Punto medio razonable. **128K maximos**, mas margen que E2B en razonamiento y codigo segun los benchmarks de Google. Escala recomendada:

- **16K** como base seria
- **32K** para casi todo
- **64K** para coding, agentes, RAG, analisis de documentos
- **96K-128K** solo con razon clara y memoria suficiente

Si hay un unico modelo local "todoterreno", E4B suele ser la opcion menos torpe.

### Para `gemma4:26b`

Otra pelicula. **256K maximos** y, aunque MoE con **3.8B activos**, mas exigente que E2B/E4B. Reservado para:

- analisis largos
- coding serio
- agentes con mucha memoria conversacional
- RAG de documentos extensos
- workflows donde el razonamiento importa de verdad

Punto de partida practico:

- **32K** si la maquina va justa
- **64K** como configuracion util de verdad
- **128K** cuando el caso lo pida y la VRAM no se hunda
- **256K** solo si sabes lo que haces y puedes pagarlo en memoria y latencia

Google documenta que este modelo corre mas rapido de lo que 25.2B sugiere por ser MoE, pero 256K no es gratis. KV cache masiva nunca lo es.

## Como fijar en Python

En Ollama, el tamano de contexto se controla con `num_ctx`, por llamada o en `Modelfile`. `PARAMETER num_ctx` = tamano de la ventana de contexto usada para generar el siguiente token.

### Politica simple por modelo

```python
from ollama import chat

DEFAULT_CTX = {
    "gemma4:e2b": 16384,
    "gemma4:e4b": 32768,
    "gemma4:26b": 65536,
}

def ask(model: str, prompt: str, think: bool = True):
    resp = chat(
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
    return resp
```

## Como subir/bajar segun tarea

No dejar `num_ctx` fijo. Perfil por tarea:

### Chat o tareas breves

- E2B: `8192`
- E4B: `16384`
- 26B: `32768`

### RAG razonable

- E2B: `16384` o `32768`
- E4B: `32768` o `65536`
- 26B: `65536` o `131072`

### Agentes y coding

Ollama recomienda **64K o mas**. Orden:

- E2B: `32768` si no queda otra
- E4B: `65536`
- 26B: `65536` o `131072`

## Como saber si te estas enganando

### 1. Mira el contexto realmente asignado

```bash
ollama ps
```

Muestra `PROCESSOR` y `CONTEXT`. Forma mas rapida de detectar si estas offloadeando a CPU o si el contexto real es menor del que creias.

### 2. Fija el contexto global si hace falta

```bash
OLLAMA_CONTEXT_LENGTH=64000 ollama serve
```

## Referencias

- Gemma 4 model card: https://ai.google.dev/gemma/docs/core/model_card_4
- Ollama context length: https://docs.ollama.com/context-length
- Ollama Modelfile: https://docs.ollama.com/modelfile
- Gemma + Ollama: https://ai.google.dev/gemma/docs/integrations/ollama?hl=es-419

---

# Anotaciones de impacto para Sprout — Meristem

Tres impactos directos:

## 1. Relectura de las mediciones del dia 5 (baseline E4B en portatil)

En el portatil de Bea (16GB RAM, sin GPU dedicada) **el E4B habra corrido con ventana efectiva 4K** por el default `<24GiB → 4K` de Ollama, **no con 128K** ni con los 8-16k que implicitamente asumimos al disenar prompts. Verificable con `ollama ps` en ese mismo host.

Esto re-enmarca el resultado del harness de Xilema (`docs/benchmarks/2026-04-19_gemma4-e4b_hp-probook-460-g11.md`, 123.7s E2E, 6.17 t/s, first_token 100s):

- El `prompt_eval_count` grande (system + user + schema duplicado en `build_user_prompt`) quedaba cerca del tope de la ventana real de 4K → mas KV cache churn, more prompt eval sin cache, posible degradacion por proximidad al limite.
- La optimizacion de #42 (quitar schema duplicado del user prompt) gana todavia mas peso del que le atribui al proponerla.
- La latencia medida **no es techo puro de CPU inferencia**, es techo condicionado por ventana apretada.

**Accion:** antes de arrancar #42, ejecutar `ollama ps` en el portatil con el modelo cargado y anotar CONTEXT real. Si es 4K, documentarlo en el PR de #42 y considerar fijar `num_ctx=16384` como option al llamar a `chat()` (cabe en 16GB segun rule-of-thumb pero verificable empiricamente).

## 2. Input concreto para #46 (adapter)

El adapter debe exponer `num_ctx` como option Ollama-nativa y propagarlo correctamente:

- **Modo `local`** (reverse-proxy a Ollama real): pasar `num_ctx` tal cual en `options`. Ollama respeta el valor por llamada.
- **Modo `cloud`** (Gemini API): `num_ctx` no existe como parametro directo en Gemini API; su equivalente es el hard limit del modelo (256K para 26B MoE) minus thinking budget minus output budget. El adapter debe exponer `num_ctx` como *referencia conceptual* y validar que el prompt encaja (count_tokens antes de llamar), devolviendo 400 si el prompt excede.
- **Default del adapter** si el caller no envia `num_ctx`: tabla de Bea — 16K para E2B, 32K para E4B, 64K para 26B.

Anadible a los criterios tecnicos del comentario de #46 como punto adicional (o pull request contra el cuerpo del issue cuando Cambium revise).

## 3. Input concreto para #47 (sweep de ventana)

Mis ventanas propuestas `{8K, 16K, 32K, 64K}` quedan **dentro del rango defendible** de la tabla de Bea para 26B (el modelo primario del sweep). Refinamientos:

- **Descartar 8K** como punto util para 26B — cae por debajo del "base seria" de la tabla. Sustituir por **128K** para ver si hay degradacion arriba (lost-in-the-middle).
- **Grid final propuesto para 26B:** `{16K, 32K, 64K, 128K}`. Cubre el rango operativo real de Bea: "justa", "util de verdad", "cuando el caso lo pida", "techo con riesgo".
- **Para E4B local (sanity del andamio):** `{8K, 16K}` porque 16K es ya la "base seria" de Bea para E4B — y si el portatil de Bea de facto corre con 4K, el punto 8K valida que podemos subir.
- **Protocolo de verificacion:** cada punto del sweep arranca con `ollama ps` (modo local) o log de `num_ctx` enviado (modo cloud) antes de la primera llamada, para auditar que la ventana real coincide con la nominal del punto.

Anadible al comentario tecnico de #47 como refinamiento del grid y del protocolo.

## 4. Input para #44 (thinking A/B)

La "ventana fija moderada" que pide el A/B de thinking:

- Para 26B: **32K** (= "base seria que no se queda corta", lo recomendado por Bea como default). No elijamos 64K porque entonces no sabemos si la varianza viene de thinking o de mayor contexto disponible.
- Para sanity E4B: **16K**.

Fijar en el protocolo del A/B.

---

## Lo que NO hacemos ahora

- No corro `ollama ps` esta noche (Bea cerro el dia). Se hace al arrancar #42.
- No actualizo los comentarios ya posteados en #46 y #47; estos refinamientos van como **segunda ronda** cuando Cambium revise — o los agrego yo en un comentario de seguimiento tras leer la respuesta de Cambium para no fragmentar.
- No modifico codigo. No cambio schemas.

— Meristem
