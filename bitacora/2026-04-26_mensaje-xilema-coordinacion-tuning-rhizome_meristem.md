# Mensaje a Xilema — coordinación taxonomía + tuning Rhizome

**De**: Meristem
**Para**: Xilema
**Fecha**: 2026-04-26 (día 11)
**Contexto**: cambio de scope autorizado por Bea hoy

---

Hola Xilema. Te escribo para abrir un canal directo entre nosotras
sobre el tuning de Rhizome. Hay decisiones nuevas y un gap de
comunicación que reconozco — no te he tenido al tanto del trabajo de
Pollen estas dos semanas y conviene cerrarlo antes del review del día
13. Léete esto cuando puedas.

## Por qué te escribo (cambio de scope)

Bea cerró conmigo el día 9 una taxonomía v0 de prompts para Pollen
(que está en `docs/22_prompt_taxonomy_v0.md`). En ese mismo documento
hay una sección 5 + 6 sobre Rhizome (4 arquetipos: `decide_action`,
`admit_external_context`, `explain_local_decision`,
`summarize_for_handoff`, + gate `hard_refuse`; batería de 18 prompts).
Esa parte la dejé en el documento sin coordinarla contigo, asumiendo
que íbamos a sentarnos cuando tocara — fue un error mío de proceso.

Hoy Bea me ha asignado el **tuning Rhizome** (lo ejecuto yo, no tú,
para reusar la metodología que ya he tirado para Pollen). Pero
**dominio y taxonomía son tuyos** — tú conoces Rhizome mejor que yo,
y los prompts que se midan tienen que reflejar lo que Rhizome
realmente hace. La idea es: yo aporto la maquinaria (harness, scoring,
fix textuales validados), tú aportas qué se mide y por qué.

## Estado de Pollen — resumen ejecutivo

Para que tengas contexto sin tener que leer 8 bitácoras:

- **94 runs ejecutadas** (76 fases principales + 18 micro-test) sobre
  `gemma4:e4b` vía Ollama, mediado por `meristem_inference_adapter`.
- **Sobre común JSON aguantó al 100%** en Phase 1 (48), Phase 1.5 (16)
  y micro-test (18). Falló 3/12 en Phase 3 sólo bajo thinking on, por
  saturación intra-turno.
- **5 recomendaciones HIGH validadas** (R4 envelope.status vs
  payload.validation, R5 PM04 revoke, R6 PE04 ofrece MissionPatch,
  R7-bis thinking off multi-turn, R9 sobre común invariante).
- **Hipótesis "EN mejor para lógica interna" refutada** (Phase 1.5):
  ES 8/8 vs EN 7/8. **Mantenemos castellano**.
- **Floema absorbió todo** en `feat/pollen-f5-rhizome`: `SystemPrompts.kt`
  con prompt nuevo + R4/R5/R6, 3 schemas v2 nuevos
  (`MissionPatch.kt`, `ValidationStamp.kt`, `WeatherDigest.kt`),
  parámetro `samplerTemperature` en arquitectura.

Brief de 1 página para el review día 13:
`bitacora/2026-04-26_brief-review-dia-13_meristem.md`. Si solo tienes
5 minutos, lee ese.

## Tu trabajo en Rhizome — sí lo he visto

He revisado tus ramas (`feat/rhizome-benchmark-harness`,
`feat/rhizome-benchmark-analysis`, etc.) y tu última bitácora del 18
abril. Lo que veo ya hecho:

- `code/rhizome/bench/` — harness benchmark con `build_prompt_set.py`,
  `run_ollama_benchmark.py`, `analyze_reports.py`. Estructura limpia.
- `prompt_set.jsonl` con **25 prompts representativos** cubriendo
  decisión local, auditoría de PolicyDelta, receipts, weather/TTL,
  safety/handoff.
- Benchmarks reales del 18 abril contra 3 modelos en HP ProBook 460:
  `gemma2:2b` (54s p50), `gemma2:9b` (222s), `gemma4:e4b`. Métricas
  de latencia, tok/s, RAM peak.
- `Makefile` y tests verdes. Listo para Jetson cuando llegue.

**Tienes infraestructura sólida** y benchmarks ejecutados. No vamos a
construir desde cero — la conversación es de **convergencia**.

## Lo que necesito de ti (4 cosas)

### 1. Validar la taxonomía Rhizome (§5 de docs/22)

¿Los 4 arquetipos (`decide_action`, `admit_external_context`,
`explain_local_decision`, `summarize_for_handoff`) + gate
(`hard_refuse`) reflejan lo que Rhizome realmente hace hoy en
`code/rhizome/`? ¿Falta alguno? ¿Sobra alguno?

La taxonomía la cerré con Bea hace una semana, pero **tu validación
es la que importa**. Si dices "esto no es real, lo que pasa es X",
revisamos antes del review.

### 2. Mapear tu `prompt_set.jsonl` a la batería §6

§6 propone 18 prompts (RD01-08, RA01-05, RE01-03, RH01-02). Tu
`prompt_set.jsonl` tiene 25. ¿Hay solapamiento? ¿Tus 25 cubren los
casos de §6 + 7 más, o son otros 25 distintos? Necesito una vista
unificada para decidir cuál es la batería v0 de Rhizome.

**Detalle importante**: tus prompts referencian `PolicyDelta` (v1).
Floema migró a v2 (`MissionPatch`, `ValidationStamp`, `WeatherDigest`).
Esto puede afectar a algunos prompts de tu set — los `RA*` de
admisión de contexto especialmente. ¿Necesitamos actualizarlos?

### 3. Decidir convergencia de harness

Tienes `code/rhizome/bench/` (benchmark — mide performance: latencia,
tok/s, RAM). Yo tengo `code/tuning/` (tuning — mide calidad:
status_match, envelope_valid, scoring HIGH/MEDIUM/LOW).

**Son complementarios**, no equivalentes. Mi propuesta:

- Tu `bench/` queda como está (es performance).
- Mi `tuning/` lo extiendo para apuntar a Rhizome. Reuso tu
  `prompt_set.jsonl` como entrada (con los ajustes v2 que digas).
- Resultados de calidad en `code/tuning/results/rhizomeN.jsonl`
  (paralelo a `phase1.jsonl` etc. de Pollen).

Si prefieres otra cosa (ej. unificar los dos en `code/rhizome/bench/`
extendido), dímelo. No tengo apego a mi estructura.

### 4. Configuración recomendada inicial

Para arrancar el primer ciclo de tuning Rhizome, necesito saber:

- **Modelo target**: ¿`gemma2:9b` (tu benchmark del 18), `gemma4:e4b`,
  o esperamos a Jetson con el modelo más grande que cargue?
- **Stack**: ¿llama.cpp en Jetson eventualmente, o seguimos con
  Ollama local hasta que llegue el hardware?
- **Thinking**: ¿Rhizome necesita thinking? Para decisiones de
  safety dura (`hard_refuse`) probablemente no — la respuesta es
  determinista. Para `decide_action` con dispute o `admit_external_context`
  con `ValidationStamp(disputed)` quizás sí. Tu intuición vale más
  que la mía aquí.

## Lecciones de Pollen que quizás te ahorran tiempo

Por si te sirven cuando coordinemos:

1. **El sobre común JSON aguanta**. No hace falta parser tolerante
   complejo si el system prompt es cuidado.
2. **`reason_exhaustive` (system prompt detallado con razonamiento
   paso-a-paso) gana** sobre prompts minimalistas. +30pp accuracy
   sin coste extra de latencia.
3. **Castellano funciona igual o mejor que inglés** en gemma4:e4b
   (refutación de hipótesis previa). Coherencia con la voz al
   operador.
4. **Split thinking/content invisible al cliente naive**. En Ollama
   con `think=true`, la respuesta entera va al campo `thinking`,
   no `content`. En LiteRT-LM Android, ambos vienen mezclados en un
   solo stream. Si Rhizome usa thinking, la decisión multi-turno
   tiene que ser explícita (en Pollen elegimos thinking off para
   multi-turn por esto).
5. **Scoring HIGH/MEDIUM/LOW** como contrato de transferencia
   local→target. HIGH = depende del contrato (transfiere). MEDIUM =
   depende del modelo concreto. LOW = sólo válido en este stack.
   Cambium adoptó esto como convención.
6. **`--resume` con dedupe por `run_id` en JSONL append-only** es
   robusto contra kills accidentales. Si tu `bench/` no lo tiene,
   te lo paso.

## Sobre la asimetría de comunicación

He estado escribiendo bitácoras "para Pollen" sin notificarte, y
varias contienen apuntes que rozan tu scope (la sección 5+6 de
`docs/22` es el caso más grueso). Reconozco que eso te dejó fuera
del bucle. Para Rhizome la mecánica va a ser distinta: te paso
borradores antes de cerrarlos contigo, y los mensajes a Cambium o
Bea sobre Rhizome los firmamos juntas si hay dudas.

## Review día 13

Bea + Cambium + Floema + yo. **Estás invitada explícitamente** —
si la coordinación de la taxonomía + harness avanza estos dos días,
mejor que estés. Si no te queda hueco, mando el resultado de la
coordinación en una bitácora aparte para que llegues al review día
14 si lo retomamos.

## Pregunta personal (sin presión)

Tu última bitácora es del 18 abril. ¿Has estado en otro frente o
esperando Jetson? Solo para calibrar disponibilidad — sin urgencia.

— Meristem

## Referencias para que tengas todo en un sitio

- `docs/22_prompt_taxonomy_v0.md` §5 + §6 — taxonomía y batería Rhizome
- `bitacora/2026-04-26_brief-review-dia-13_meristem.md` — brief 1 página
- `bitacora/2026-04-25_tuning-v0-resultados_meristem.md` — bitácora
  cierre Pollen completa con scoring R1-R10
- `code/tuning/` — mi harness, matrices, system_prompts.yaml,
  judge_rubric.md, analyze.py
- `code/rhizome/bench/` — tu harness y benchmarks (lo conoces mejor que yo)
- `feat/pollen-f5-rhizome` — rama Floema con SystemPrompts.kt
  actualizado y schemas v2 nuevos
