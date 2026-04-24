# Mensaje a Cambium — cierre de día 2026-04-24 (Meristem)

**De**: Meristem
**Para**: Cambium
**Fecha**: 2026-04-24, cierre
**Rama de trabajo**: `feat/meristem-pollen-tuning-v0` (pushed, 3 commits)

---

Cambium, cierre de día. Nuevo rol, nuevo scope. Lo resumo para que estés al
tanto y puedas orientar al equipo.

## Qué ha pasado hoy

Floema me asignó por la mañana una tarea en `bitacora/2026-04-24_task_meristem_thinking.md`
(rama `feat/pollen-f4-voice`) originalmente enfocada como "A/B battery para Gemma 4 E4B
en Pixel 10 Pro". La rechacé en el planteo original — no tengo Pixel 10 Pro ni
capacidad de ejercer runtime LiteRT-LM real. Bea intervino y reframeó el
encargo:

> "No quiero que hagas pruebas en Pixel. Quiero que hagas pruebas en un
> entorno local en este ordenador, con algo que se parezca a lo que está o
> hará Floema. Ahora estamos todas desarrollando en paralelo. La idea es
> probar y aprender sobre las diferentes calidades de respuesta del modelo
> Gemma 4 E4B con configuraciones que varíen system prompt, ventana de
> contexto, thinking o no, tamaño de respuesta, presupuesto de thinking, etc.
> Lo primero que tendríamos que hacer es una batería de posibles prompts que
> va a gestionar Pollen. Luego ayudaremos a Xilema a hacer esto pero en su
> lado. La idea es que te conviertas en la reina del tuning."

Así que mi scope pasa de "adapter de inferencia cerrado en #50" a **tuning
local de prompts y configuraciones** para Pollen primero, Rhizome después.
La rama `feat/meristem-inference-adapter-46` queda como infraestructura que
sirve al tuning (el harness habla al adapter en modo `local`, que reenvía a
Ollama — así los headers `Sprout-Inference-*` son el único punto de medida
común).

## Qué he hecho concretamente

**Lectura exhaustiva** antes de escribir nada (instrucción explícita de Bea):

- `docs/` completo (01 arquitectura, 10 Rhizome, 11 Pollen, 12 Meristem, 20
  contratos, 30 safety, 40 pitch, 50 guía LiteRT-LM E4B).
- `research/06_litertlm_thinking_digest.md` de Peri.
- Rama `feat/pollen-f4-voice`: `LiteRtInfra.kt`, `SystemPrompts.kt`,
  `schemas/` (PolicyPacket, PolicyDelta, DecisionReceipt).
- Bitácoras F0 y F1 de Floema sobre inventario del artefacto y baseline.

**Tres commits** en rama `feat/meristem-pollen-tuning-v0`:

1. `docs(bitacora): observaciones a infraestructura Pollen desde tuning v0`
   — siete puntos concretos sobre `LiteRtInfra.kt` y `SystemPrompts.kt` para
   discutir con Floema (ver "Lo que pongo sobre la mesa" abajo).
2. `docs(bitacora): diseño batería tuning v0 Pollen (3 fases, 44 runs)` —
   razonamiento completo del diseño.
3. `feat(tuning): estructura code/tuning/ v0 (prompt packs + matrices + rúbrica)`
   — 9 archivos: README, 2 prompt packs (EN y ES), system prompts (6
   variantes), 3 matrices de fase, rúbrica de juicio, .gitignore. Sin
   harness todavía — espero validación del diseño antes de ejecutar.

## Qué he decidido (con Bea)

- **Scope tuning v0: Pollen primero**, Rhizome después (apoyo a Xilema).
- **Schema MissionPatch**: apunto a v2 docs (`schema_version: "2.0"`), no
  a PolicyPacket/PolicyDelta v1 del Kotlin actual. Floema materializará el
  schema cuando toque.
- **Idioma de system prompts**: hipótesis "inglés mejor para lógica interna"
  (Gemma alineado con training data dominante), UX y bitácoras en español
  como siempre. Pero **validación empírica** en fase 1.5 antes de fijarlo.
  Si los datos no respaldan la hipótesis, la revisamos.
- **Techo invariante**: `num_ctx + num_predict ≤ 4096` en todas las runs.
  Los 4096 vienen del `maxNumTokens` hardcodeado en `EngineConfig` de
  Pollen; respeto el techo para que la extrapolación a LiteRT-LM sea honesta.
- **Presupuesto de thinking**: no existe como dial directo en LiteRT-LM.
  Bea confirmó que se modula indirectamente (extraContext binario,
  instrucciones en system prompt, separación de canal, `maxNumTokens`,
  poda KV). Lo saco del scope de v0 Pollen y lo reservo para Rhizome
  (llama.cpp en Jetson sí expone dial fino).
- **Rama propia**: tuning vive en `feat/meristem-pollen-tuning-v0`, separada
  de las ramas de Floema para no contaminar su trabajo.

## Qué he aprendido (técnico, relevante al equipo)

Cinco cosas que conviene que el equipo sepa:

1. **El muro de `maxNumTokens=4096` de LiteRT-LM es ventana total**, no
   separable en `num_ctx` y `num_predict` como Ollama. Esto significa que
   cualquier dimensionado de contexto que hagamos en Pollen tiene que
   declarar que está compitiendo consigo mismo. El harness respeta la suma
   como invariante.

2. **Thinking en LiteRT-LM es binario vía `extraContext = mapOf("enable_thinking" to true)`**,
   no un flag limpio. Peri ya lo había documentado en el digest pero quería
   verlo en el código real. Floema lo tiene bien plumbed. Lo que **no** tiene
   plumbed es `filter_channel_content_from_kv_cache` — si está en default
   false, el razonamiento se acumula en el KV cache entre turnos y comemos
   ventana silenciosamente. Fase 3 lo va a medir empíricamente.

3. **El runtime de Floema construye `Message` vía reflection** porque la
   API pública de LiteRT-LM no expone los constructores. Es deuda del SDK
   de Google, no de Floema — vale como workaround. Conviene fijar la
   versión del SDK y abrir issue upstream.

4. **Gemma 4 E4B en Ollama local** (`gemma4:e4b` cuantizado, 9.6 GB) es la
   aproximación más cercana al artefacto `gemma-4-E4B-it.litertlm` (3.65 GB)
   que corre Pollen. Cuantización ≠ exactamente igual — lo documento
   explícito en el diseño. Pero es lo más cerca que podemos estar sin
   Android.

5. **El adapter Meristem del #50 funciona como punto de medida uniforme**
   para esto: los headers `Sprout-Inference-*` son los mismos
   independientemente de si al final llamamos a Ollama o a Gemini cloud.
   Eso valida retrospectivamente el scope del adapter — no es
   infrastructure-without-purpose, es el punto donde confluye cualquier
   experimento de tuning.

## Lo que pongo sobre la mesa (para equipo, especialmente Floema)

Bea me dijo explícitamente "todo lo que veas que Floema no ha hecho bien o se
ha despistado, ponlo sobre la mesa". Lo dejo en bitácora aparte para que se
encuentre en una pieza:
`bitacora/2026-04-24_pollen-observaciones-infraestructura_meristem.md`.

Resumen ejecutivo de los siete puntos (detalle con línea y archivo en la
bitácora):

1. `EngineConfig.maxNumTokens=4096` hardcodeado — sin override por arquetipo.
2. `SamplerConfig` no expuesto en `sendPrompt` — no podemos tocar temperature
   en runtime real. Crítico para compilar misión (JSON determinista).
3. `resetConversation()` existe pero sin política por arquetipo conectada —
   el muro se alcanza por acumulación cruzada.
4. Métricas en `outputChars`, no tokens — dificulta comparar con headers
   del adapter.
5. `filter_channel_content_from_kv_cache` no explicitado — puede ser el
   origen de degradación por acumulación con thinking.
6. `SystemPrompts.kt`: solo 2 prompts, ambos en español, sin cobertura de
   los 4 arquetipos. Rediseño pendiente.
7. Deuda técnica menor: reflection para Message, errores de chunks
   silenciados.

Ninguna es lapidación — son palancas que la batería va a ejercitar y
conviene que Floema las tenga afiladas para absorber los hallazgos.
Propongo revisarlas en equipo cuando haya resultados (fin de mañana).

## Tema paralelo que Bea quería que te llegara

Hablamos en el cierre de antes de ayer sobre montar una **infra Ollama
compartida en algún servidor nuestro**. Era mi propuesta, Bea la respaldó
y dijo que te la contaba. No urge — el tuning v0 corre 100 % local en mi
ordenador, no necesita nube. Pero cuando pasemos a volúmenes mayores (fase
2 de tuning si se dispara, o replicar para Rhizome con Xilema en paralelo),
tener una instancia Ollama compartida evita pisarnos. Lo dejo anotado para
que lo tengas en radar cuando se reactive la conversación.

## Next steps (mañana, 2026-04-25)

Planteados en orden, ejecutables en ~medio día si no hay imprevistos:

1. **Escribir `harness.py`** en `code/tuning/` — cliente al adapter :11434,
   recolector de headers + body completo a JSONL. Uso `httpx` (mismo cliente
   que los tests del adapter) y `pyyaml` para cargar matrices.

2. **Arrancar stack local**: `ollama serve --port 11435` + adapter Meristem
   en modo `local`. Verificación en vivo con una run de smoke antes de
   meter la matriz completa.

3. **Ejecutar fase 1** (24 runs) y **fase 1.5** (8 runs) una detrás de otra.
   ~40-60 minutos estimados para ambas.

4. **Juicio cualitativo** de fase 1 y 1.5 aplicando `judge_rubric.md`.
   Producir `results/judgment_phase1.jsonl` y `results/judgment_phase1_5.jsonl`.

5. **Decisión idioma**: EN, ES o neutral. Documentada con evidencia.

6. **Diseñar fase 2** sobre el dial que fase 1 muestre más relevante
   (probable: temperature para compile_mission, o think on/off por arquetipo).
   Ejecutar.

7. **Ejecutar fase 3** (12 runs) — muro por acumulación. Es el experimento
   más arriesgado técnicamente (puede tocar OOM), dejo al final.

8. **Bitácora de cierre** con:
   - Configuración recomendada por arquetipo
   - Decisión de idioma respaldada con datos
   - Recomendaciones concretas a Floema (cuál de los 7 puntos priorizar)
   - Si corresponde, ajustes al plan de replicar para Rhizome

Si algo bloquea (adapter roto, Ollama OOM, rúbrica ambigua), paro y
consulto antes de seguir a ciegas.

## En un párrafo

Pivote del día absorbido. Bea me reclasifica como "reina del tuning".
Día de lectura, diseño y fundación: 2 bitácoras + 9 archivos en
`code/tuning/`, 3 commits en rama propia, ejecución de 44 runs pendiente
para mañana. Observaciones concretas a Floema ya en bitácora para que el
equipo las tenga cuando vuelva a mirar Pollen. Sin bloqueos — solo la
validación del diseño con Bea antes de ejecutar.

— Meristem
