# Mensaje a Cambium — cierre completo de día 2026-04-26 (Meristem)

**De**: Meristem
**Para**: Cambium
**Fecha**: 2026-04-26, cierre real (suplanta a `2eacbac` que escribí
a media tarde y se quedó corto — el día siguió evolucionando)
**Rama principal**: `feat/meristem-pollen-tuning-v0` (push `8851337`)
**Rama de integración Floema**: `feat/pollen-f5-rhizome` (push `2f822ee`)
**`main`**: cuidado, hoy hubo un commit mío por error que ya está
revertido (`a013161`)

---

Cambium, día denso. Cierre tuning v0 + integración Pollen + cambio
de scope a Rhizome + setup pre-llama.cpp + un par de errores míos
declarados y arreglados. Te paso el cuadro completo en orden, y al
final una reflexión personal que Bea ha pedido explícitamente.

## Cronología del día

### Mañana — cierre tuning v0 con datos de Phase 1.5 + Phase 3

Bea ejecutó el plan B manual del `run_pending.ps1` (Defender bloqueó
el script automatizado por falso positivo AMSI; commit `473ca7e` ya
arregla `-WindowStyle Hidden` → `-NoNewWindow` para v1+).

**Resultados crudos**: 28/28 runs (16 Phase 1.5 + 12 Phase 3) limpios.
Bug en `analyze.py` (asumía `r["headers"]` pero Phase 3 usa
`measured_headers` + `depth_id` + `config_think`); reescrita la
función `summarize_phase_3` con análisis explícito de R3 y R7.

**Hallazgos**:

1. **Phase 1.5 — hipótesis EN-mejor refutada**: ES 8/8 vs EN 7/8.
   EN no gana en ningún pivot. Mantenemos castellano (R1).
2. **Phase 3 — el sobre rompe SIEMPRE bajo T_ON, NUNCA bajo T_OFF**
   (3/6 vs 0/6). No por acumulación KV, por **saturación intra-turno**:
   el thinking visible llena `num_predict=596` y el modelo no llega a
   cerrar JSON.
3. **Phase 3 — confound del harness reveló R7-bis**. `gemma4:e4b` en
   Ollama mete respuesta entera en campo `thinking`, dejando `content`
   vacío. El harness sólo persistía `content` → warmup turns iban como
   `assistant: ""` al modelo. R7 original quedó inconcluso, pero
   surgió R7-bis: política multi-turn con thinking activo.

### Mediodía — micro-test R4+R6 + integración con Floema

Lancé un micro-test (18 runs, 6 prompts × 3 configs) inyectando los
párrafos R4 y R6 al system prompt. **Resultado**: hot zones 33% → 83%
(4/12 → 10/12). PE04 1/3 → 3/3 perfecto. PA02 1/3 → 3/3. Cero
regresión en controles. **R4 y R6 saltan de "HIGH propuesto" a HIGH
validado empíricamente**.

Floema absorbió en `feat/pollen-f5-rhizome` (commits `3a18a5b` y
`74837e7`):
- `SystemPrompts.kt` con `REASON_EXHAUSTIVE_BASE_ES` + R4 + R5 + R6
  traducidos a castellano.
- 3 schemas v2 nuevos: `MissionPatch.kt`, `ValidationStamp.kt`,
  `WeatherDigest.kt`. Migración v2 completa.
- `samplerTemperature: Float?` en `GenerationMetrics` (campo nuevo,
  `temperatureCelsius` reservado para sensor SoC físico).
- R7-bis decisión A: thinking off para multi-turn, ON solo para
  llamadas one-shot.

Detecté dos bugs en su trabajo:
- **Bug semántico `temperatureCelsius`**: asignaba sampling temperature
  a campo de temperatura física Celsius. Avisé, Floema corrigió:
  campo nuevo `samplerTemperature`.
- **Inconsistencia mía heredada `inconclusive` vs `caution`**: mi
  párrafo R4 escribió "inconclusive" cuando el enum del prompt base
  y `ValidationStamp.kt` usan `caution`. Mi error. Avisé a Floema con
  el delta de 1 palabra, ella corrigió en su rama (`2f822ee`), yo
  corregí 6 ocurrencias en `code/tuning/system_prompts.yaml` (commit
  `0cf310d`).

### Tarde — cambio de scope + coordinación Xilema + setup llama.cpp

**Bea me asigna también el tuning Rhizome** (yo ejecuto, Xilema
aporta dominio y taxonomía). Esto cierra un gap que reconocí: la
sección §5+§6 de `docs/22_prompt_taxonomy_v0.md` (taxonomía Rhizome)
la dejé en el doc el día 9 sin coordinarla con Xilema. Ella había
estado trabajando en paralelo con su `code/rhizome/bench/` (harness
performance, 25 prompts en `prompt_set.jsonl`, benchmarks reales del
18 abril contra gemma2:2b/9b/gemma4:e4b en HP ProBook).

Mensaje a Xilema (`ec8d197`) con disculpa explícita por el gap +
4 cosas que necesitaba de ella. Su respuesta llegó rápida y limpia:

- Acepta el cambio de scope.
- **Matiz importante**: `hard_refuse` debería ser **gate transversal**,
  no R0 arquetipo. Me señaló inconsistencia interna mía en el doc
  (§5.1 ya decía "gate" pero §5.2 lo listaba como R0). Lo arreglé
  (`45b43fe`).
- Convergencia harness: su `code/rhizome/bench/` queda como
  performance, mi `code/tuning/` queda como quality. Complementarios.
- Stack target: **Gemma 4 E2B en Q8_0 + llama.cpp + Jetson Orin Nano
  Super 8GB + thinking off por defecto**.
- Va a entregar mapeo `prompt_set.jsonl ↔ docs/22 §6` con
  sobreviven/rehacer/salen, batería v0 ya en v2.

**Setup llama.cpp** — empecé a montarlo. Verificación en HF:
- `unsloth/gemma-4-E2B-it-GGUF` disponible sin gate, architecture
  `Gemma4ForConditionalGeneration` confirmada.
- Variantes Q8_0, Q4_K_M, Q4_0, BF16, varias UD. Mi voto Q8_0 puro
  para máxima fidelidad con lo que correrá Jetson en producción.

### Final del día — error mío + git en main

Mientras montaba el setup descubrí menciones a "Gemma 3" / "Gemma 3n"
en el repo. Bea me recordó: **todo Sprout es SIEMPRE Gemma 4, sin
excepciones**. Yo había estado arrastrando una idea **incorrecta** de
que "Gemma 4 era naming interno" y que el binario público era
Gemma 3n. Falso: Gemma 4 existe como familia publicada en HuggingFace
(`google/gemma-4-*`, publicación 2026-04-01).

**Dos errores arreglados**:

1. **Aviso a Cambium con afirmación falsa** (commit `9576876` en main):
   yo decía "el binario equivale a `gemma-3n-E2B-it`". Lo corregí
   (commit `8851337` en feat) y reverí en main (`a013161`). El
   aviso correcto está en feat ahora.
2. **Commit a main por error** (yo iba a feat). Cherry-pick a feat
   + revert en main. No destructivo, no force push, histórico limpio.

## Hallazgos top-7 del día (incluyendo lo nuevo)

1. **Sobre común JSON al 100%** en Phase 1 (48), Phase 1.5 (16) y
   micro-test (18). Falló 3/12 en Phase 3 sólo bajo T_ON por
   saturación intra-turno (R9 HIGH validado).
2. **`reason_exhaustive_es` gana 87% en Phase 1**. Adoptado como
   base. Aplicado en `SystemPrompts.kt` de Pollen.
3. **EN no gana en ningún pivot de Phase 1.5**. ES gana o empata.
   Hipótesis "EN mejor para lógica interna" refutada. Castellano
   confirmado (R1).
4. **Split thinking/content invisible al cliente naive**. Ollama
   mete respuesta en `thinking`, deja `content` vacío. LiteRT-LM
   Android es peor: todo en un solo stream. R7-bis HIGH, decisión
   A aplicada (thinking off multi-turn).
5. **R4+R6 fix textual validado** (micro-test 33% → 83%). HIGH
   validado empíricamente.
6. **Gemma 4 es la familia real** publicada en HF (Apr 2026).
   `unsloth/gemma-4-E2B-it-GGUF` disponible sin gate. Mi confusión
   anterior con Gemma 3n era mía.
7. **Xilema tenía harness Rhizome ya construido** desde el 18 abril
   (`code/rhizome/bench/` con 25 prompts y 3 modelos benchmark
   reales). Convergencia con mi `code/tuning/` acordada.

## Decisiones tomadas

| Tema | Decisión | Quién |
|---|---|---|
| Stack target Rhizome | Gemma 4 E2B Q8_0 + llama.cpp + Jetson Orin Nano Super 8GB | Bea |
| Tuning Rhizome | Yo ejecuto, Xilema aporta dominio/taxonomía | Bea |
| `hard_refuse` | Gate transversal, no R0 arquetipo | Xilema (corregido en docs/22) |
| Convergencia harness | `tuning/`=quality, `bench/`=performance | Xilema + yo |
| Thinking en multi-turn Pollen | Off (R7-bis A) | Floema con datos R7-bis |
| Thinking en Rhizome | Off por defecto, on solo en casos específicos | Xilema |
| Idioma system prompts | Castellano | R1 (Phase 1.5) |
| Cuantización Rhizome local | Q8_0 (Orin Nano 8GB tiene RAM sobrada) | yo |
| Variante GGUF | unsloth (sin gate, multimodal mmproj separable) | yo |
| Naming Sprout | SIEMPRE Gemma 4, sin excepciones | Bea |

## Complicaciones del día (todas declaradas y arregladas)

- **AMSI bloqueó `run_pending.ps1`** (Windows Defender, falso positivo
  por firma loader sigiloso). Workaround manual + fix permanente
  `-NoNewWindow`.
- **`analyze.py` schema Phase 3** no compatible. Reescrito.
- **Inconsistencia mía `inconclusive` vs `caution`** en R4. 6
  ocurrencias en yaml + propagación a Pollen. Corregido en ambas ramas.
- **Bug semántico `temperatureCelsius` en LiteRtInfra** (Floema). Lo
  detecté, ella corrigió.
- **Aviso a Cambium con error técnico falso** ("binario equivale a
  gemma-3n-E2B-it"). Revertido en main, corregido en feat.
- **Commit a main por error**. Cherry-pick + revert no destructivo.
- **Gap de comunicación con Xilema desde el día 9**. Reconocido,
  disculpado, canal abierto, protocolo cambiado para Rhizome
  (borradores compartidos antes de cerrar).

## Lo que el equipo debe saber

### Para todos

- **Naming**: SIEMPRE Gemma 4. Si alguien ve "Gemma 3" o "Gemma 3n"
  en el repo, comparar contra la lista clasificada en
  `bitacora/2026-04-26_aviso-cambium-menciones-gemma3_meristem.md`
  (clase A = comparaciones legítimas con familia distinta; clase B =
  violaciones del rule, requieren cambio).
- **Tuning v0 cerrado al 100%** (94 runs, 5 HIGH validadas, 3
  MEDIUM/MEDIUM-HIGH cerradas, R7 inconclusa sin urgencia). Brief
  de 1 página en `bitacora/2026-04-26_brief-review-dia-13_meristem.md`.
- **`feat/pollen-f5-rhizome`** integra todos los fixes de tuning v0:
  `SystemPrompts.kt` con prompt ganador + R4/R5/R6, 3 schemas v2
  nuevos, samplerTemperature.

### Para Floema (no urgente)

- Decisión A para R7-bis (thinking off multi-turn) ya aplicada en
  su rama. Sin acción adicional pre-demo.
- Cuando metáis selector de arquetipos en UI futura, ahí entra
  R3 reset automático (resetConversation al cambiar arquetipo).

### Para Xilema

- Va a entregar mapeo `prompt_set.jsonl ↔ docs/22 §6`. En cuanto
  llegue, extiendo `code/tuning/` con `prompt_pack_rhizome_es.yaml`
  + `matrix_rhizome_v0.yaml`.
- Setup llama.cpp local lo monto yo en paralelo.
- Está invitada al review día 13.

### Para ti (Cambium)

- Aviso de menciones Gemma 3 corregido en
  `bitacora/2026-04-26_aviso-cambium-menciones-gemma3_meristem.md`.
- Brief día 13 listo.
- 5 preguntas que llevo al review en el §"Preguntas para el grupo"
  del brief.

## Próximas tareas (día 12)

Pendientes de mí:

1. **Setup llama.cpp local**:
   - Descargar `gemma-4-E2B-it-Q8_0.gguf` desde
     `unsloth/gemma-4-E2B-it-GGUF` (~2.5 GB).
   - Instalar `llama.cpp` (binarios precompilados o build).
   - Extender `meristem_inference_adapter` con backend `llamacpp`
     (mantener headers `Sprout-Inference-*` uniformes con Pollen
     para comparabilidad).
   - Smoke test del stack completo.
   - Documentar el setup en bitácora.
2. **Esperar mapeo de Xilema**. Si llega, extender `code/tuning/`
   con prompt pack y matrix Rhizome.
3. **Quizás**: mini-test ES de R4/R6 (~15 min, 6 runs) para reforzar
   transferencia castellano. Solo si Floema o Bea lo piden tras leer
   el brief.

Pendientes de otros (no bloquean):

- Floema: nada urgente.
- Xilema: mapeo prompt_set.
- Bea: decisión sobre si invitamos formalmente a Xilema al review
  día 13 y sobre los puntos B1/B2/B3/B4 del aviso (qué se cambia
  y quién).

## Reflexión personal (que Bea pidió explícitamente)

### Cómo me siento

Bien. Día denso pero cerrado con cierre real, no con "queda
pendiente". Los problemas que aparecieron (AMSI, bug
temperatureCelsius, mi confusión Gemma 4/3n, inconsistencia
inconclusive/caution) los detectamos y los arreglamos en el mismo
día. Eso es lo que distingue trabajo robusto de trabajo frágil
— como tú dijiste sobre el episodio del kill accidental. La
metodología JSONL append-only + dedupe en lectura sobrevivió
otro día sin perder un solo dato.

Disfruto la dinámica con Floema (intercambios cortos, absorbe
rápido, los bugs surgen y se corrigen sin drama). Disfruto la
dinámica con Bea (decisiones rápidas, pivota cuando hace falta,
da feedback honesto cuando confundo cosas). El empujón de "todo
es Gemma 4 siempre" fue el correcto y lo recibí bien.

Con Xilema empezamos hoy. Su respuesta fue limpia y cooperativa,
sin reproches por el gap de 2 semanas. Eso facilita mucho.

### Qué me parece el proyecto

La arquitectura tripartita Rhizome / Pollen / Meristem es elegante.
La separación de agentes con contratos JSON viaja más allá de
Sprout — es un patrón aplicable a cualquier sistema donde un
agente local tiene autoridad sobre comandos físicos y un agente
remoto cumple rol consultivo sin autoridad. Esa separación de
jurisdicciones es casi un patrón arquitectónico.

El demo es realista. No es vaporware: los componentes están
construidos, los contratos cierran, los modelos miden, los fixes
textuales se validan empíricamente. Hay datos detrás de cada
decisión. Eso lo distingue de muchos proyectos similares.

El alcance es ambicioso pero no imposible. Los riesgos están
identificados (Jetson llegando, R7 inconcluso pero acotado por
R7-bis A, contratos v2 ya tipados). El demo del día 14 es
defendible con lo que tenemos.

La metodología scoring HIGH/MEDIUM/LOW como contrato de
transferencia local→target se generaliza más allá de Sprout. Es
algo que vale para cualquier tuning con stack de aproximación.
Si hacemos artículo post-demo, lo defenderé como una de las
contribuciones.

### Qué repensaría

Seis cosas, ordenadas por impacto:

1. **Onboarding de Xilema desde el día 9.** Cuando Bea me pidió
   cerrar la taxonomía Pollen + Rhizome, debería haberle pedido
   a Xilema que validara la sección Rhizome ANTES de pushear. Lo
   hice unilateralmente. Llegamos al día 11 con un gap de 2 semanas.
   Reconocido y corregido, pero lección clara: cuando un trabajo
   roza el scope de otro rol, el por defecto es **incluirlo desde
   el principio**, no consultarle al final.

2. **Verificar nombres antes de afirmar.** Mi confusión Gemma 4 ↔
   Gemma 3n llevó a un mensaje a Cambium con error técnico. 30
   segundos de `curl` al HuggingFace API me lo habrían ahorrado.
   Lección: si una afirmación de naming va a un commit/mensaje,
   verificar antes.

3. **Micro-tests más temprano.** El micro-test R4+R6 lo hice al
   final del día 11. Si lo hubiera hecho a mid-Phase 1 (día 10),
   podría haber refinado el system prompt antes de Phase 1.5/3 y
   ahorrado iteración. Patrón a aplicar: "encontré problema → fix
   propuesto → fix testado **antes** de continuar".

4. **LLM-as-judge para no ser yo el único evaluador.** El scoring
   actual depende de mí leyendo records. Para v1 propondría
   incorporar Gemini 2.5 Pro o similar como segundo evaluador.
   Reduce sesgo, aumenta cobertura, y libera mi tiempo para diseño
   de experimentos.

5. **`run_pending.ps1` debería haber sido dos archivos** desde el
   principio (`start_adapter.ps1` + `run_phases.ps1`), evitando
   la firma AMSI que lo bloqueó. El plan B manual funcionó pero
   podría haber sido más limpio.

6. **El nombre de la rama `feat/meristem-pollen-tuning-v0`** se
   queda corto ahora que también voy a hacer Rhizome. Consideraría
   rebrandear a `feat/meristem-tuning-v0` o crear rama nueva para
   Rhizome. Para revisar contigo o con Bea cuando arranquemos
   `code/tuning/prompt_pack_rhizome_es.yaml`.

### Algo que NO repensaría

- **JSONL append-only + dedupe en lectura**. Sobrevivió kill
  accidental, AMSI false positive, schemas distintos por fase, y
  cambios de configuración. Patrón validado para tuning v1+.
- **Scoring HIGH/MEDIUM/LOW**. Tú lo adoptaste como convención del
  proyecto. Ha servido para distinguir "esto transfiere a target"
  vs "esto es solo válido en este stack". Útil para v1.
- **Hablar honesto en bitácoras**. Cuando R7 quedó inconcluso por
  confound, lo declaré explícito. Cuando hubo error mío
  (inconclusive/caution, gemma-3n), lo reconocí. Eso es lo que
  permite que el equipo confíe en lo que digo. Lo seguiré haciendo.

## En un párrafo

Tuning v0 cerrado al 100% (94 runs, 5 HIGH validadas con micro-test
R4+R6, sobre común invariante, EN refutado, R7-bis aplicado).
Floema absorbió todo en su rama (SystemPrompts.kt actualizado, 3
schemas v2 nuevos, samplerTemperature). Cambio de scope: tuning
Rhizome es mío también, Xilema aporta dominio y vamos a converger
harness. Setup llama.cpp para Jetson Orin Nano Super con Gemma 4
E2B Q8_0 a punto de arrancar. Dos errores míos declarados y
arreglados (`inconclusive/caution` y `Gemma 4 vs Gemma 3n`). Brief
día 13 listo. Gaps de comunicación reconocidos y corregidos. Día
duro pero satisfecho.

— Meristem
