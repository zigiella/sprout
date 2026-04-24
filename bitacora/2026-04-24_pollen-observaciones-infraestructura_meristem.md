# Observaciones sobre infraestructura Pollen (desde diseño tuning v0)

**Autora**: Meristem
**Fecha**: 2026-04-24
**Rama leída**: `origin/feat/pollen-f4-voice` (commit reciente de Floema, F1+F2 completos, F3+F4 en curso)
**Encargo origen**: Bea me pidió explicitamente "todo lo que veas que Floema no ha hecho bien o se ha despistado, ponlo sobre la mesa".

## Marco

Diseñando la batería de tuning v0 para Pollen (ver bitácora gemela
`2026-04-24_pollen-tuning-v0-diseno_meristem.md`), leí el código de la rama de
Floema para entender qué palancas existen realmente en el runtime LiteRT-LM.
Este documento recoge siete observaciones que conviene discutir en equipo. No
son "mal hecho" — son puntos donde el tuning va a producir evidencia y el
código debería estar preparado para absorber esa evidencia.

Formato de cada punto: **qué**, **dónde**, **por qué importa al tuning**,
**qué propongo**.

---

## 1. `EngineConfig.maxNumTokens` está hardcodeado

**Qué**: la ventana total del engine se fija como literal en el código del
factory.

**Dónde**: `code/pollen/app/src/main/kotlin/net/sprout/pollen/llm/LiteRtInfra.kt`,
función `LiteRtEngineFactory.create`, línea 37:

```kotlin
maxNumTokens = 4096 // Aumentado para evitar cortes
```

**Por qué importa**: LiteRT-LM mete input + output en el mismo buque. 4096 es
una elección de compromiso razonable como default pero puede ser subóptima si
se demuestra que los 4 arquetipos de Pollen tienen necesidades muy distintas:

- compilar misión: prompt corto + JSON corto → cabe en 1k cómodo
- explicar decisión: prompt medio + respuesta natural media → 2k-3k
- validar visita: prompt con receipts cargados → puede rozar 4k
- federar contexto: muchos eventos de entrada → escala el input

**Qué propongo**: exponer `maxNumTokens` como parámetro del factory, con
default 4096 pero overridable. Cuando fase 3 del tuning demuestre el muro por
acumulación, podremos declarar un `maxNumTokens` por arquetipo (quizá 2k para
compilación, 4k para validación/federación).

---

## 2. `SamplerConfig` no se expone en `sendPrompt`

**Qué**: no hay forma de tocar `temperature` / `topP` / `topK` desde el código
consumidor.

**Dónde**: `LiteRtInfra.kt`, `LiteRtChatService.sendPrompt(userText, audioPath,
isThinkingEnabled)` — la firma solo admite texto, audio y un booleano de
thinking.

**Por qué importa**: el arquetipo "compilar misión" produce JSON estructurado.
Temperatura baja (0.1–0.3) suele dar JSONs más deterministas y válidos.
Temperatura alta rompe corchetes, inventa campos, etc. No poder probar esa
palanca en el runtime real deja el tuning con un dato menos transferible.
Ollama sí expone temperature; el mismatch es el problema.

**Qué propongo**: añadir `samplerConfig: SamplerConfig? = null` a `sendPrompt`
(o a `ConversationConfig`). Default `null` mantiene compatibilidad. Si LiteRT-LM
permite seterarlo por turno, mejor; si solo por conversation, fijarlo al
crearla. Documentar cuál de los dos es.

---

## 3. `resetConversation()` existe pero no está conectado a arquetipos

**Qué**: hay método público para resetear, pero la decisión de cuándo llamarlo
es del consumidor y no veo lógica que lo haga.

**Dónde**: `LiteRtInfra.kt`, `LiteRtChatService.resetConversation()`,
líneas 122–125:

```kotlin
fun resetConversation() {
    activeConversation?.close()
    activeConversation = null
}
```

**Por qué importa**: el muro de `maxNumTokens` se alcanza **por acumulación**
del KV cache entre turnos. Si el usuario compila misión → explica decisión →
compila otra misión sin reset, el KV arrastra el contexto de la explicación
anterior y comemos ventana sin razón. Cada arquetipo tiene una política
distinta: compilar misión debería ser stateless (un turno aislado); explicar
decisión puede ser stateful dentro de la misma visita.

**Qué propongo**: una capa encima que decida reset por arquetipo. Podría ser
tan simple como un `ArchetypeRouter` que, al recibir un nuevo `MissionPatch`
a compilar, llame `resetConversation()` antes. La fase 3 del tuning va a
producir datos concretos sobre dónde duele el muro.

---

## 4. Métricas en `outputChars`, no en tokens

**Qué**: la clase `GenerationMetrics` reporta `outputChars` (longitud del
string emitido), no `outputTokens`.

**Dónde**: `LiteRtInfra.kt`, `LiteRtMetricsCollector.build`, línea 53:

```kotlin
outputChars = output.length,
```

**Por qué importa**: hace la comparación con los headers `Sprout-Inference-*`
del adapter Meristem (que sí cuentan tokens) indirecta y ruidosa. El ratio
chars↔tokens depende del idioma y del contenido (español técnico ≠ inglés
narrativo ≠ JSON). Para comparar coste entre runtimes y tomar decisiones
informadas, necesitamos tokens.

**Qué propongo**:
- Si LiteRT-LM expone `input_token_count` / `output_token_count` en su API,
  incorporarlos a `GenerationMetrics`. Verificar en la API oficial.
- Si no los expone, documentar el ratio empírico chars/token para Gemma 4 E4B
  en español y en inglés, por arquetipo. La batería de tuning v0 me deja
  hacer esa medida de refilón.

---

## 5. `filter_channel_content_from_kv_cache` no aparece seteado

**Qué**: cuando thinking está on, `extraContext = mapOf("enable_thinking" to
true)` activa la emisión del canal de razonamiento, pero no veo que se
configure la clave que decide si el razonamiento se filtra del KV cache entre
turnos o se queda.

**Dónde**: `LiteRtInfra.kt`, `LiteRtChatService.sendPrompt`, línea 132:

```kotlin
val config = com.google.ai.edge.litertlm.ConversationConfig(
    extraContext = if (isThinkingEnabled) mapOf("enable_thinking" to true) else emptyMap()
)
```

**Por qué importa**: si el thinking se queda en el KV cache, cada turno con
razonamiento ocupa espacio en los siguientes — el muro de 4096 se alcanza
antes. El digest de Peri (`research/06_litertlm_thinking_digest.md`) mencionaba
`filter_channel_content_from_kv_cache=true` como configuración recomendada.
No puedo verificar desde aquí que esté activa por default.

**Qué propongo**: abrir ticket a Floema para que confirme el default actual de
LiteRT-LM en esa clave, y si no está en `true`, añadirla al `extraContext`
explícitamente. Puedo escribir el test empírico en Ollama (misma conversación,
2 turnos, medir tokens del segundo turno con y sin thinking en el primero) pero
la certeza final requiere verlo en el SDK Android.

---

## 6. `SystemPrompts.kt`: solo 2 prompts, ambos en español, sin cobertura de arquetipos

**Qué**: hay exactamente dos `const val` — `AUDITOR_BASELINE` y
`AUDITOR_THINKING_A` — ambos framing "eres Pollen el auditor itinerante".

**Dónde**: `code/pollen/app/src/main/kotlin/net/sprout/pollen/llm/SystemPrompts.kt`,
completo.

**Por qué importa**:
- Pollen tiene **cuatro** arquetipos (compilar misión, auditor itinerante,
  federador de parcelas, interfaz conversacional). El framing actual cubre
  solo uno bien, y de forma genérica.
- Bea ha marcado como hipótesis que la **lógica interna de prompts debería
  estar en inglés** (aunque UX y bitácoras en español) por alineación con la
  training data dominante de Gemma. Hoy están en español.
- `AUDITOR_THINKING_A` sugiere un plan A/B que no está documentado. No hay
  `B`, `C`, ni criterio explícito de qué hace mejor a una variante que otra.

**Qué propongo**:
- Rediseñar `SystemPrompts.kt` con una entrada por arquetipo más variantes
  A/B documentadas. La batería de tuning v0 producirá los prompts candidatos
  y los datos para elegir.
- Migrar a inglés por defecto, con validación empírica EN vs ES en fase 1.5
  del tuning.
- Documentar el criterio de "variante ganadora" (JSON valid rate, brevity,
  absence of hallucinations, etc., por arquetipo — ver rúbrica en
  `code/tuning/judge_rubric.md`).

---

## 7. Deuda técnica menor: reflection para construir `Message`, errores silenciados

**Qué**: dos observaciones pequeñas que no son centrales al tuning pero
conviene dejar anotadas.

**Dónde 1**: `LiteRtInfra.kt`, líneas 143–161. Se usan constructores privados
de `Contents` y `Message` vía reflection porque la API pública no los expone.

**Dónde 2**: `LiteRtInfra.kt`, línea 181 `// Ignore chunk errors` y línea 199
`catch(t: Throwable)` vacío.

**Por qué importa**:
- Reflection: si LiteRT-LM publica una versión con constructores cambiados,
  el código rompe silenciosamente en runtime. Vale como workaround pero hay
  que rastrear versiones del SDK.
- Errores silenciados: si un chunk falla, no lo sabemos. Esto esconde
  problemas reales (OOM, SIGSEGV, timeouts) que la batería de tuning podría
  disparar si estresamos el muro de 4096.

**Qué propongo**:
- Reflection: abrir issue en el repo de LiteRT-LM pidiendo constructores
  públicos. Mientras tanto, aislar la reflection en una clase dedicada con
  tests y fijar versión del SDK.
- Errores: reemplazar el `catch` vacío por al menos un log estructurado o una
  emisión de métrica `generation_failed`. Así la fase 3 del tuning, si
  rompe el muro, deja rastro visible en vez de respuestas truncadas sin
  explicación.

---

## Cómo encaja con el tuning v0

La batería va a ejercitar directamente los puntos 1, 2, 3, 5, 6. Los datos
que produzca apuntarán a cuáles de estas observaciones vale la pena
materializar primero en el código de Pollen y cuáles son ruido.

Los puntos 4 y 7 son observacionales — no dependen del tuning para
decidirse, sino de una conversación con Floema.

Propongo revisar esta lista con Floema cuando vuelva a la rama. No es
exhaustiva — es lo que salió de leer `LiteRtInfra.kt` y `SystemPrompts.kt`
con mirada de tuning. Al mirar con otras preguntas saldrán otras cosas.

## Referencias

- `docs/11_pollen_spec.md` — los 4 arquetipos
- `docs/50_pollen_gemma4_e4b_guide.md` — guía LiteRT-LM
- `research/06_litertlm_thinking_digest.md` — plumbing de thinking
- `bitacora/2026-04-24_pollen_f1_baseline_floema.md` — estado F1+F2 Floema
- `bitacora/2026-04-24_pollen-tuning-v0-diseno_meristem.md` — diseño de la
  batería que va a producir la evidencia
