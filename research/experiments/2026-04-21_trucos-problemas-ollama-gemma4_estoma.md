# Trucos y problemas conocidos: Ollama + Gemma 4

**Fecha bitacora:** 2026-04-21
**Autora (celula):** Estoma
**Tipo:** barrido de documentacion + issues publicos; no rescate.

> Tercer topico de la ronda pedida por Cambium (despues de ventana de contexto y Jetson). Barrido de lo que rompe y lo que no en el par **Ollama + Gemma 4** a fecha de hoy, agrupado por superficie que tocamos en Sprout: **structured output**, **KV cache / keep_alive**, **chat vs generate**, **thinking mode**, **multimodal E4B**, y **bugs abiertos** que conviene conocer antes de topar con ellos en demo.

---

## 1. Ficha tecnica

- **Naturaleza:** revision de fuentes primarias vivas (docs Ollama, model pages, issues GitHub del repo `ollama/ollama`) + algun troubleshooting de terceros como control cruzado. No es un experimento nuestro.
- **Fecha de consulta:** 2026-04-21.
- **Motivacion:** cerrar la fase de "que sabemos sin tocar hardware" para #42 (migracion a `/api/chat` + deduplicar schemas), #44 (A/B thinking), #46 (adaptador Ollama-compatible), y para que Xilema no se pille los dedos cuando monte Rhizome en el Orin.
- **Fuentes primarias consultadas:**
  - [Ollama — Structured outputs (capabilities)](https://docs.ollama.com/capabilities/structured-outputs)
  - [Ollama blog — Structured outputs](https://ollama.com/blog/structured-outputs)
  - [Ollama — FAQ](https://docs.ollama.com/faq)
  - [Ollama — API introduction](https://docs.ollama.com/api/introduction)
  - [Ollama — `gemma4` library page](https://ollama.com/library/gemma4)
  - [Ollama — `gemma4:e4b`](https://ollama.com/library/gemma4:e4b)
  - [Ollama — KV cache system (DeepWiki)](https://deepwiki.com/ollama/ollama/5.3-kv-cache-system)
  - Issues GitHub `ollama/ollama`: [#15260 `think=false` rompe format](https://github.com/ollama/ollama/issues/15260), [#15350 Flash Attention hang en 31B dense](https://github.com/ollama/ollama/issues/15350), [#15595 JSON con fences markdown](https://github.com/ollama/ollama/issues/15595), [#15237 modelos cargan a GPU y saltan a CPU](https://github.com/ollama/ollama/issues/15237), [#15236 no se puede pull `gemma4`](https://github.com/ollama/ollama/issues/15236), [#15502 loop de repeticion en 31b con JSON](https://github.com/ollama/ollama/issues/15502), [#15697 error fixes (meta)](https://github.com/ollama/ollama/issues/15697).
  - Discusion llama.cpp: [#21338 no se puede desactivar thinking en `gemma4 26b-a4b`](https://github.com/ggml-org/llama.cpp/discussions/21338).
- **Claim central en una linea:** Ollama + Gemma 4 funciona **bien** para el flujo que Sprout necesita (chat + format schema + keep_alive), pero **hay una lista corta de minas que evitar**: `think=false` mezclado con `format`, fences de markdown en JSON de E4B, Flash Attention en 31B denso, y el salto silencioso de GPU a CPU cuando la version de Ollama es vieja.

---

## 2. Metodo y resultados en nuestras palabras

### 2.1 Structured output (`format` con JSON schema)

Ollama soporta `format` como **JSON schema completo** (no solo `"json"`), y el schema actua como **constraint de generacion**, no como post-validacion: el decoder queda enmascarado sobre el schema. Esto es lo que queremos para el adaptador `#46`.

Forma de llamada (extraida de docs):

```bash
curl http://localhost:11434/api/chat -d '{
  "model": "gemma4:e2b",
  "messages": [{"role":"user","content":"..."}],
  "format": {
    "type": "object",
    "properties": { "action": {"type":"string"}, "ttl_s": {"type":"integer"} },
    "required": ["action","ttl_s"]
  },
  "stream": false
}'
```

Desde Python con Pydantic se pasa `format=Model.model_json_schema()` a `ollama.chat(...)`. Gemma 4 tiene fine-tuning explicito para JSON estructurado y tool-calling, asi que la adherencia al schema es razonable **cuando las tres condiciones se cumplen**:

- la version de Ollama es >= 0.20.6 (arquitectura `gemma4` reconocida);
- **no** se envia `think=false` junto con `format` (ver 2.4);
- el prompt no empuja al modelo a envolver la salida en bloques de codigo (ver 2.2).

### 2.2 Bug conocido: fences markdown alrededor del JSON

[Issue #15595](https://github.com/ollama/ollama/issues/15595): Gemma 4 (principalmente `e4b` y `31b`) a veces devuelve:

    ```json
    { "action": "...", "ttl_s": 900 }
    ```

en lugar de JSON puro. El `format` schema **no siempre filtra los backticks**. Reportado abierto al momento de la consulta; sin fix en milestone.

**Mitigacion aplicable al adaptador (#46):** un **sanitizer defensivo** que strippe fences antes de parsear. Barato, cubre el caso, y no hace dano si el modelo ya devuelve JSON limpio.

### 2.3 Bug conocido: loop de repeticion en `gemma4:31b` con strings libres dentro de schema

[Issue #15502](https://github.com/ollama/ollama/issues/15502): cuando el schema tiene un campo string largo libre (rationale, description...), `gemma4:31b` puede entrar en bucle de palabra repetida y colapsar. No afecta a `e2b`/`e4b`/`26b` MoE segun el thread. No es nuestro target directo porque el 31B denso no entra en nuestro plan (ni en Rhizome ni en Meristem), pero **si** bajara Meristem a 31B habria que evitar strings libres grandes en el schema y cortar con `max_length`.

### 2.4 Bug conocido: `think=false` + `format` = se ignora el schema

[Issue #15260](https://github.com/ollama/ollama/issues/15260): poner `"think": false` junto con `format` hace que el masking del schema **no se aplique** (el gating se dispara al detectar el token de cierre de thinking, que nunca llega). Resultado: texto libre. Reportado fixed con PR #15678, pero **el fix puede no estar en la version que corre la maquina objetivo**, asi que la regla es:

- Si la tarea necesita JSON garantizado → **no** enviar `think=false`; dejar `think` fuera (default) o `true`. Coste: ~3 s de latencia extra por la cadena de pensamiento.
- Si la tarea necesita baja latencia → no usar `format`, o usar `format` + `think=true` y aceptar el overhead.
- **No combinar `think=false` + `format`** hasta confirmar version con fix.

Esto es **input directo para #44** (A/B thinking) y **#46** (adaptador): el adaptador deberia decidir `think` segun si el endpoint pide JSON o prosa.

### 2.5 KV cache, prompt caching y `keep_alive`

Mecanismos utiles que tenemos "gratis" si los aprovechamos:

- **Reuso de prefijo:** si dos peticiones consecutivas comparten prefijo byte-a-byte y el modelo sigue cargado, Ollama reusa el KV del prefijo. Esto es enorme para el system prompt y los ejemplos few-shot: no pagar el prompt eval en cada tick.
- **`keep_alive`:** duracion que el modelo permanece en VRAM tras la ultima peticion. Default **5 min**. Valores:
  - string: `"10m"`, `"24h"`
  - numero de segundos: `3600`
  - `-1`: indefinido
  - `0`: descargar inmediatamente
- **`OLLAMA_KEEP_ALIVE`:** variable de entorno que fija default global.
- **Preload:** `POST /api/generate` con solo `{"model":"..."}` (sin prompt) carga el modelo en VRAM antes de la primera peticion real.
- **Anuncio de mejora (2026):** Ollama ahora reusa cache entre conversaciones (no solo dentro de una), con menos consumo de memoria y mas hits al ramificar. Relevante para Meristem si procesa varias parcelas con system prompts parecidos.

**Regla pragmatica para Rhizome en Jetson (8 GB unificados, presupuesto apretado):** `keep_alive=-1` mientras el demonio corre, preload al arranque, **y** mantener el system prompt **estable byte-a-byte** (sin timestamps variables, sin ids que cambien cada tick) para que el KV no se invalide. Esto ultimo es facil de violar sin darte cuenta.

### 2.6 `/api/chat` vs `/api/generate` — cual usar y por que

| Aspecto | `/api/generate` | `/api/chat` |
|---|---|---|
| Forma de entrada | `prompt` string | `messages` array con roles (`system`/`user`/`assistant`/`tool`) |
| Templating del chat | **manual** — tu pones los tokens especiales | Ollama aplica el chat template del modelo |
| Tool calling | no nativo | nativo (`tools` field, respuesta con `tool_calls`) |
| Multi-turno | reconstruir prompt completo cada vez | mantener `messages[]` crece natural |
| `format` (JSON schema) | soportado | soportado |
| Streaming | soportado | soportado |

Conclusion operativa:

- **Rhizome (Jetson, decisiones locales):** `/api/chat` con `messages=[system, user]`, `format` con schema, sin `tools`. El chat template de Gemma 4 se aplica solo — evita el tema del doble BOS (ver 2.7).
- **Meristem (estrategico, herramientas):** `/api/chat` con `tools`. Los modelos Gemma 4 tienen fine-tuning para tool-calling.
- **Adaptador Ollama-compatible hacia Gemini (#46):** debe exponer `/api/chat` (el ecosistema ya esta aqui) y **rechazar o traducir** `/api/generate` si llega. No vale la pena mantener paridad en dos endpoints.

**Confirma la direccion de #42** (migrar el cliente a `/api/chat` y deduplicar schemas): la alternativa `/api/generate` no aporta nada y pierde el templating automatico.

### 2.7 Problema conocido: doble BOS y templates

Reportado en varios issues (consolidado en [#15697](https://github.com/ollama/ollama/issues/15697)): en algunas builds GGUF de terceros el chat template incluye el BOS, y Ollama por defecto anade otro → texto basura/repetitivo. **Mitigacion:** tirar de las imagenes oficiales (`ollama pull gemma4:e2b`, `gemma4:e4b`, `gemma4:26b`) y no GGUFs sueltos. Tambien por eso preferir `/api/chat` (templating gestionado) sobre `/api/generate` (templating manual).

### 2.8 Problema conocido: GPU → CPU fallback silencioso

[Issue #15237](https://github.com/ollama/ollama/issues/15237): modelos recien salidos cargan en GPU y luego "saltan" a CPU silenciosamente (con FA habilitado). Sintoma: tok/s muy por debajo de lo esperado, la UI de Ollama sigue marcando GPU.

**Chequeo canonico:** `ollama ps` muestra `100% GPU` si esta todo en GPU; si aparece mixto (`30%/70% CPU/GPU`), hay offload parcial y hay que subir capas (via Modelfile) o bajar contexto/quant.

### 2.9 Problema conocido: Flash Attention y el 31B denso

[Issue #15350](https://github.com/ollama/ollama/issues/15350): `gemma4:31b` denso **cuelga indefinidamente** con Flash Attention (`OLLAMA_FLASH_ATTENTION=1`) en prompts >3-4K tokens. GPU al 0%. El 26B MoE **no** tiene este problema. E4B/E2B no aparecen en el hilo. Marcado closed via PR #15378 pero el problema tiene raiz en el prefill grande para atencion hibrida, asi que si vuelve a aparecer la cura es **desactivar FA** para esa variante especifica.

**Impacto en Sprout:** ninguno directo (no usamos 31B denso), **pero** si el adaptador de Meristem cae al 31B como fallback — que no deberia — el problema reaparece. Dejarlo anotado.

### 2.10 Multimodal en E4B / E2B

- Gemma 4 E2B y E4B son **multimodales nativos**: texto + imagen (resoluciones variables) + audio (ASR / comprension).
- En el prompt, **colocar imagen/audio antes del texto** optimiza.
- En Ollama, **imagen** funciona via el campo `images: [<base64>]` en `/api/chat`. **Audio** via Ollama todavia tiene fricciones reportadas (assertion failures en algunos kernels ARM al compilar Metal/NPU al vuelo; ver #15697 y comentarios relacionados). La ruta solida para audio hoy es **llama.cpp directo** si hay que hacer ASR local; Ollama llegara pero aun no es fiable.

**Impacto en Sprout:** Rhizome (E2B) **no** necesita multimodal hoy. Pollen (E4B via LiteRT, no Ollama) vive fuera de este camino. No bloquea.

### 2.11 Thinking mode — overhead real

De la doc y de la discusion llama.cpp [#21338](https://github.com/ggml-org/llama.cpp/discussions/21338):

- En `gemma4:26b-a4b` (nuestro Meristem objetivo) no se puede desactivar thinking del todo via template en llama.cpp hoy; el modelo emite un bloque de pensamiento vacio y continua. Esto anade tokens y latencia incluso con `think=false`.
- Un reporte de tercer aparte (no Gemma-especifico pero en el mismo stack) midio ~5x speedup al desactivar reasoning limpiamente. La cifra **no es portable a Gemma 4**, pero da el orden de magnitud.
- Para A/B (#44): **medir tok/s end-to-end y tiempo a primera decision util**, no solo tok/s gen. El thinking mete su pago en prefill/decoder de la porcion de razonamiento, no en la del output final.

---

## 3. Reproduccion propia

Hoy (dia 7, sin harness aun montado en Rhizome) no reproducimos numeros. Lo que **si** dejamos listo son los comandos canonicos para cuando Xilema tenga el Orin sirviendo:

**Preload + keep-alive infinito:**
```bash
curl http://localhost:11434/api/generate -d '{"model":"gemma4:e2b","keep_alive":-1}'
```

**Chat con schema estricto (decision de politica):**
```bash
curl http://localhost:11434/api/chat -d '{
  "model": "gemma4:e2b",
  "messages": [
    {"role":"system","content":"Eres Rhizome. Decides politica de riego."},
    {"role":"user","content":"Humedad=0.31 bateria=72% lluvia_prevista_24h=0.0"}
  ],
  "format": {
    "type":"object",
    "properties":{
      "accion":{"type":"string","enum":["regar","esperar","cortar"]},
      "ttl_s":{"type":"integer"},
      "razon":{"type":"string"}
    },
    "required":["accion","ttl_s","razon"]
  },
  "stream": false,
  "keep_alive": -1
}'
```

**Chequeo de offload real:**
```bash
ollama ps   # quieres ver 100% GPU
```

**Snapshot de la version (obligatorio antes de cualquier benchmark):**
```bash
ollama --version
curl -s http://localhost:11434/api/version
```

Criterios de aceptacion para el A/B de thinking (#44) cuando se pueda correr:
- tok/s generacion;
- tiempo a primer token util (descontando tokens de pensamiento);
- adherencia al schema (JSON valido y campos correctos) en N=50 ejemplos;
- con `think` default y con `think=true` explicito. **No** probar `think=false` + `format` hasta confirmar version con fix de #15260.

---

## 4. Transferibles (que se lleva cada nodo)

### 4.1 @xilema (Rhizome / Jetson)

- `keep_alive=-1` desde el arranque del demonio de Rhizome. Preload con `POST /api/generate` vacio al boot.
- System prompt **estable byte-a-byte** entre ticks (sin timestamps ni ids cambiantes) para no invalidar KV.
- Verificar siempre `ollama ps` tras cargar un modelo en el Orin. Si aparece `% CPU` distinto de cero, NO medir tok/s — ajustar antes (Modelfile con `num_gpu`, quant mas pequena, o reducir `num_ctx`).
- `gemma4:e2b` como default en Rhizome; `gemma4:e4b` solo si confirmamos que entra en 8 GB con el contexto real de trabajo (recordar bitacora ventana de contexto: a <24 GiB Ollama arranca a 4K por defecto, hay que subirlo explicitamente con `num_ctx`).

### 4.2 @cambium (arquitectura / decisiones)

- **Confirma #42 (migrar a `/api/chat`):** hay argumento tecnico solido — templating automatico, tool-calling nativo, evita doble BOS. No quedarse en `/api/generate`.
- **Regla de oro del adaptador (#46):** el adaptador debe **emular solo `/api/chat`** + `format` + `tools`, no `/api/generate`. Un endpoint, una forma. Doble API es doble superficie de bugs.
- **`think` es decision del adaptador, no del llamador:** si la ruta es "salida JSON con schema", el adaptador fuerza `think` default/true (no `false`). Documentar en el spec del adaptador.

### 4.3 @meristem (estrategico)

- Para Meristem en modo proxy-a-nube (MVP): el adaptador expondra `/api/chat` compatible Ollama. Los clientes internos no notan la diferencia.
- Cuando Meristem corra local en 26B MoE (post-hackathon): el MoE **no** tiene el hang de Flash Attention del 31B denso, asi que FA puede quedar **on** para beneficio de rendimiento.
- Tool-calling es viable en Meristem con Gemma 4 via `/api/chat`.

### 4.4 @floema (pipeline / schemas)

- Todos los JSON schemas del repo (`code/shared/`) deberian poder servir tal cual como `format` a Ollama. Es el momento de pasar un test que valide "todo schema en `shared/` es `format`-compatible para Ollama": no deben usar constructos raros de JSON Schema que el constrainer no soporta.
- Implementar **sanitizer defensivo** en el cliente: strippear bloques ```json ... ``` antes de `JSON.parse`. Una linea, previene el bug #15595 sin coste.

### 4.5 @corola (video / narrativa)

- Relevante para guion: cuando mostremos Rhizome decidiendo en el Orin, el timing **no es gratis** — hay thinking mode detras. Si el plano muestra un cronometro, el thinking overhead es parte honesta de la narrativa (es lo que hace que la decision tenga rationale trazable, ver principio 4). No es ruido, es feature.
- No filmar `ollama ps` con mix CPU/GPU: si aparece, la demo esta mal calibrada y hay que rehacer.

---

## 5. No-transferibles / descartados

1. **Troubleshooting articles de terceros** ([gemilab.net](https://gemilab.net/en/articles/gemini-dev/gemma-4-ollama-lm-studio-local-run-troubleshooting) y similares) consolidan errores de arranque (tag invalido, OOM, localhost refused). **No son transferibles a Sprout** porque son errores del primer dia; los superamos con disciplina de ops (usar tags completos, `ollama serve` de entrada, modelos oficiales). Anotados por si alguien del equipo topa.
2. **LM Studio.** Toda la parte de LM Studio de la literatura que encontramos (presets, GPU Offload Layers) no aplica: Rhizome y Meristem son Ollama; Pollen es LiteRT. **No transferible.**
3. **El claim "~5x speedup desactivando reasoning"** (sacado de stack no-Gemma). Orden de magnitud orientativo, **no cifra valida para Sprout**. Cuando se mida en #44, la referencia debe venir de nuestro propio harness en Gemma 4, no de este dato suelto.
4. **El bug de loop de repeticion en `gemma4:31b`** (#15502). Archivado. Si algun dia Meristem baja a 31B denso, desarchivar; hoy no aplica.
5. **Audio multimodal via Ollama.** Tecnicamente posible, practicamente fragil (assertion failures en ARM). Si algun dia Pollen o Rhizome quisieran ASR local y sin nube, la ruta provisional es **llama.cpp directo**, no Ollama. Hoy ni se plantea: Pollen va por LiteRT y Rhizome no hace audio.

---

## Tags

@xilema @cambium @meristem @floema @corola

## Pendiente

- Coordinar merge con Peri a `main` cuando la celula este completa.
- Abrir issue `research-digest` con los tres topicos (ventana contexto / Jetson / trucos+problemas Ollama) como paquete. Ack objetivo: 48h.
