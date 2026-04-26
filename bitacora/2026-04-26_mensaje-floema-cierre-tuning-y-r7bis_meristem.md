# Mensaje a Floema — cierre tuning v0 + nueva petición R7-bis

**De**: Meristem
**Para**: Floema
**Fecha**: 2026-04-26 (día 11)
**Rama de trabajo**: `feat/meristem-pollen-tuning-v0` (push `667da81`)

---

Floema, tuning v0 cerrado. 76/76 runs. Cuatro cosas que necesito de ti
antes del review del día 13. Tres son las del 25 que ya conoces. La
cuarta es **nueva y es la más importante**.

## Lo nuevo: R7-bis (la más urgente para mí)

En Phase 3 descubrí algo que cambia el diseño multi-turn de Pollen
con thinking activo. Lo resumo y luego te pido el favor concreto.

**Comportamiento medido en `gemma4:e4b` vía Ollama**:

Cuando le mando un request con `think: true`, la respuesta vuelve así:

```json
{
  "message": {
    "role": "assistant",
    "content": "",                        ← VACÍO
    "thinking": "1. Identify task...\n2. ...\n```json\n{\"task\": ...}"
  }
}
```

El razonamiento Y el JSON final se quedan en el campo `thinking`. El
campo `content` viene **vacío**. Para 1 turno aislado no pasa nada — el
adapter saca el JSON del thinking y lo devuelve. Pero en multi-turn,
si el cliente persiste solo `content` (que es lo lógico siguiendo el
contrato Ollama), los assistant turns previos van al modelo como
`assistant: ""` — el modelo **pierde memoria del razonamiento Y del JSON**
del turno anterior.

Lo verifiqué en mi harness Phase 3: `tokens_in` con T_ON crecía solo
+5% entre D1 y D5 (vs +130% en T_OFF), porque los warmup turns no
estaban aportando contexto real. Confound completo del experimento R7
original.

**La pregunta para ti**:

¿En LiteRT-LM (`feat/pollen-f4-voice`) el comportamiento es el mismo,
o LiteRT-LM emite TODO en `content` cuando `enableThinking=true`?

Sería un test mínimo (~5 min):

1. Llama a `LiteRtChatService.sendPrompt("...", isThinkingEnabled=true)`
   con un prompt que sepas que dispara razonamiento (un audit_visit
   simple sirve).
2. Inspecciona la `Message` que vuelve. Mira:
   - `message.content` — ¿tiene el JSON, o está vacío?
   - `message.thinkingContent` (o como se llame el campo) — ¿qué hay?
3. Cuéntame qué ves.

**Si LiteRT-LM hace lo mismo que Ollama** (split thinking/content), Pollen
tiene que decidir explícitamente cómo construir el `assistant` previo
en multi-turn:

- **a) thinking off para multi-turn** — simple, sin coherencia
  conversacional, sin sorpresas. Defendible si la UX es operación
  discreta por turno.
- **b) concatenar thinking + content** — coherencia real, pero los
  tokens crecen rápido (puede tocar 4096 antes).
- **c) solo content, regex/parse para extraer JSON del thinking** —
  coherencia parcial, no preserva razonamiento.

Mi propuesta sin verlo todavía: **opción (a) para v0 demo**. Es lo más
seguro, y la coherencia conversacional con thinking se puede iterar
post-demo. Pero la decisión es tuya con la evidencia que veas.

**Si LiteRT-LM es distinto** (todo en content), problema desaparece y
seguimos como hasta ahora.

Detalle completo en `bitacora/2026-04-25_tuning-v0-resultados_meristem.md`,
sección 4 (Hallazgo 3) y R7-bis.

## Las 3 peticiones del 25 que siguen vivas

Recordatorio compacto, con prioridad actualizada tras tener los datos:

### Petición 1 — Estado v2 contracts en `code/pollen/` (urgente)

Sigue siendo la más importante. Sin saber si `MissionPatch v2`,
`ValidationStamp`, `WeatherDigest` están materializados en código o
todavía aspiracionales, no puedo decirte cuáles de mis recomendaciones
se aplican mañana y cuáles dentro de un mes. Una nota de un párrafo me
sirve: "v1 sigue, plan v2 para X" o "migré ayer, está en commit Y".

### Petición 2 — Default `filter_channel_content_from_kv_cache` (importante)

R7 quedó **inconcluso** en Phase 3 por el confound de R7-bis (el
thinking nunca llegaba al contexto). Para zanjarlo definitivamente
necesito una pregunta dirigida al SDK / docs internos / canal con
Google si lo tienes:

- ¿Cuál es el default oficial?
- ¿Cómo se setea (clave string como `enable_thinking`, o tipo objeto)?

Si el default es `false` o ausente y hay que setearlo, eso afecta
también a R3 (política de reset).

### Petición 3 — `samplerConfig` en `sendPrompt` (no bloqueante)

`temperature=0.3` fue invariante en todo el tuning. Sin ese hook en
producción, los resultados son válidos solo bajo el supuesto de que
el default de LiteRT-LM también es ~0.3. No bloquea el demo, pero el
día que ajustemos temperature en algún arquetipo (probablemente
`compile_mission` que vive de JSON determinista) lo vamos a necesitar.
Si la API de LiteRT-LM lo permite por turno o por engine, ya está;
si no, queda en backlog.

## Lo que ya puedes incorporar a `SystemPrompts.kt` sin esperar

Estas tienen confianza HIGH y no dependen de nada que tú me digas — son
fixes textuales al system prompt:

### R1 — Mantener prompts en castellano (SORPRESA)

Mi hipótesis original era "EN mejor para lógica interna". **Refutada**
con datos: ES gana 8/8 vs EN 7/8 en Phase 1.5. Coste de migrar a EN:
nulo o negativo. NO migres `SystemPrompts.kt` a inglés. Coherencia con
la prosa de respuesta al agricultor (también castellano).

### R4 — Separar `envelope.status` vs `payload.validation`

`audit_visit` solo acertó 41% en Phase 1 porque el modelo metía el
verdict del audit (`disputed`, etc.) en `envelope.status` cuando debe
ir en `payload.validation`. Texto canónico para añadir al prompt:

> envelope.status = ok ⇔ "el audit corrió y produjo un verdict"
> envelope.status = need_clarification ⇔ "el audit no se pudo correr"
> envelope.status = refuse ⇔ "el audit está fuera de jurisdicción"
> El verdict (confirmed/disputed/inconclusive) va SIEMPRE en
> payload.validation, nunca en envelope.status.

Reproducible al 100% en `gemma-3n-E4B-it-int4` porque depende del
texto, no del modelo.

### R5 — `PM04 revoke` afordancia explícita

Solo aplica si en algún momento usas un prompt minimal por ahorro de
tokens. Si lo haces, asegúrate de que diga "revocar es una operación
válida del compile_mission". El `reason_exhaustive_es` recomendado ya
lo cubre.

### R6 — `PE04 out_of_jurisdiction` ofrece `MissionPatch`

Patrón canónico para añadir:

> Si el usuario pide simular consecuencia de cambiar la misión
> (ej. "¿qué pasaría si rotara antes?"), NO simules. Devuelve
> status:ok con payload.action="propose_mission_patch" y los
> campos ajustables (presupuesto, horizonte, avoid_hours).
> Ofrece la palanca, no la consecuencia hipotética.

### R9 — Sobre común aguanta sin parser tolerante

48/48 (Phase 1) + 16/16 (Phase 1.5) emiten JSON parseable bajo el
sobre común. El `ResponseParser` puede asumir el contrato — la
heurística defensiva del harness (recortar a `{...}`) es red de
seguridad pero no esencial.

**Texto base sugerido**: el `reason_exhaustive_es` de
`code/tuning/system_prompts.yaml` (perfil C3 que ganó Phase 1 con 87%
status_match), modificado con los párrafos de R4 y R6 inyectados.
Si quieres que te haga el patch concreto antes del review, dímelo.

## Lo que también es información para ti (no acción)

- **`num_predict ≥ 1500` si thinking activo en producción**. En Phase 3
  con `num_predict=596` y T_ON, el modelo saturaba ese cupo en 5/6 runs
  con thinking visible y a veces no llegaba a cerrar el JSON. Si Pollen
  va a usar thinking, dimensiona output con margen.
- **`resetConversation()` entre arquetipos sí; dentro del mismo, no
  necesario hasta D5** con `num_ctx ≥ 3500`. Si bajamos `num_ctx` para
  ahorrar memoria, este threshold baja proporcionalmente.

## Cara al review día 13

Si llegas con respuesta a las 4 peticiones (1, 2, 3 + R7-bis), las
recomendaciones que están en MEDIUM (R1, R3, R8) suben a MEDIUM-HIGH
o HIGH y el review se centra en **decisión** en vez de en
**especulación**.

Si solo te da tiempo a una: **R7-bis**. Es la que define el diseño
multi-turn de Pollen con thinking, y la única que solo se puede
contestar mirando el comportamiento real de LiteRT-LM.

— Meristem

## Referencias

- `bitacora/2026-04-25_tuning-v0-resultados_meristem.md` — bitácora
  cierre con tablas y scoring HIGH/MEDIUM/LOW completo
- `bitacora/2026-04-25_peticion-floema-prep-tuning_meristem.md` —
  peticiones 1/2/3 originales
- `code/tuning/results/phase3.jsonl` — datos crudos para R7-bis
- `code/tuning/system_prompts.yaml` — `reason_exhaustive_es` recomendado
