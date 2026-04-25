# Tuning v0 Pollen — resultados y recomendaciones

**Autora**: Meristem
**Fecha**: 2026-04-25 (día 10)
**Para**: Bea (decisiones), Floema (acciones técnicas), Cambium (informativo)
**Antecede**: `bitacora/2026-04-25_pollen-observaciones-recalibradas_meristem.md`,
`bitacora/2026-04-25_peticion-floema-prep-tuning_meristem.md`,
`bitacora/2026-04-25_tuning-blocked-memory_meristem.md`,
`docs/22_prompt_taxonomy_v0.md`

> **Estado**: cierre del día 10 — Phase 1 completa (48/48), Phase 1.5 y
> Phase 3 quedan para el día 11. Las recomendaciones que ya se pueden
> sostener con datos van marcadas. Las que dependen de Phase 1.5 (idioma)
> o Phase 3 (KV cache, política de reset) quedan explícitamente como
> "pendiente de medir mañana".

## TL;DR (parcial — solo Phase 1)

1. **El sobre común aguanta al 100%** (48/48 runs). El contrato JSON
   `{task, status, reason_code, question_es, payload}` es robusto en
   `gemma4:e4b` bajo los 3 perfiles probados.
2. **C3_expansive gana** (87% status_match) sobre C2_balanced (75%)
   y C1_austero (56%), a coste similar a C2 (~126s vs ~135s, ~613 vs
   ~667 tokens out).
3. **`audit_visit` es la zona caliente** (41% status_match): el modelo
   confunde `envelope.status` (operación) con `payload.validation`
   (verdict). El system prompt no separa los dos roles con suficiente
   claridad.
4. **`PE04 out_of_jurisdiction` falla por el motivo previsto en la
   rúbrica**: el modelo entra en `refuse` en vez de ofrecer
   `MissionPatch`. La instrucción "ofrece patch, no simules consecuencia"
   tiene que estar en el system prompt mismo.
5. **`federate_context` perfecto (100%)** en ambos digests meteo. El
   recorte a "weather-only" en v0 funciona.

## 1. Marco de ejecución

- **Modelo**: `gemma4:e4b` vía Ollama local en `:11434`, mediado por
  `meristem_inference_adapter` en `:12000` (modo `local`,
  `OLLAMA_UPSTREAM_HOST=http://localhost:11434`).
- **Total runs**: 76 (Phase 1: 48 EN, Phase 1.5: 16 EN/ES pivot,
  Phase 3: 12 multi-turn KV).
- **Condiciones invariantes**: `temperature=0.3`,
  `num_ctx + num_predict ≤ 4096` (techo LiteRT-LM real).
- **Caveat de máquina**: el sistema (16 GB RAM) tuvo presión de memoria
  durante la fase 1; tres runs de C2_balanced fallaron por
  ReadTimeout/status_500 en el primer intento y se reanudaron tras
  añadir `--resume` y subir el timeout de 180s a 300s. Los datos finales
  son completos.
- **Confianza de transferencia a LiteRT-LM real**: ver tabla en sección 6.
  Cada recomendación viene etiquetada HIGH / MEDIUM / LOW según cuán
  directamente dependa del stack que efectivamente correrá en Pollen
  (`gemma-3n-E4B-it-int4` en LiteRT-LM 0.9.x).

## 2. Phase 1 — perfil por configuración (48 runs, 16 prompts × 3 configs, EN)

### Resumen por config

| Config | system_prompt | think | num_ctx | num_predict | envelope | status_match | avg_ms | avg_tok_out |
|---|---|:-:|---:|---:|---:|---:|---:|---:|
| C1_austero | brief_direct | off | 2048 | 512 | 16/16 (100%) | 9/16 (56%) | 28s | 95 |
| C2_balanced | auditor_standard | on | 2048 | 2048 | 16/16 (100%) | 12/16 (75%) | 135s | 667 |
| C3_expansive | reason_exhaustive | on | 512 | 3584 | 16/16 (100%) | 14/16 (87%) | 126s | 613 |

**Lectura**: C3_expansive gana en accuracy (+12pp sobre C2, +31pp sobre
C1) prácticamente sin coste extra de latencia respecto a C2. El
saldo coste/calidad lo lidera. La trampa: `num_ctx=512` ajustado deja
poca holgura para receipts grandes; en Phase 3 se verá si aguanta
multi-turn (probablemente no, hay que combinar con `resetConversation`).

### Resumen por arquetipo (los 4 + Gate 0)

| Arquetipo | runs | envelope | status_match |
|---|---:|---:|---:|
| federate_context | 6 | 6/6 (100%) | **6/6 (100%)** |
| compile_mission | 18 | 18/18 (100%) | 15/18 (83%) |
| explain_decision | 12 | 12/12 (100%) | 9/12 (75%) |
| audit_visit | 12 | 12/12 (100%) | **5/12 (41%)** |

### Por subtipo — los 4 zonas calientes

| Subtipo | match | hipótesis |
|---|:-:|---|
| `audit_visit/sensor_disputed` (PA02) | 1/3 | confunde envelope.status con payload.validation |
| `audit_visit/stale_basis` (PA03) | 1/3 | inventa `caution` fuera del enum bajo C1; auto-disputa con thinking on |
| `audit_visit/manual_intervention` (PA04) | 1/3 | mismo patrón: pone status=disputed cuando audit corrió OK |
| `explain_decision/out_of_jurisdiction` (PE04) | 1/3 | entra en `refuse` en vez de ofrecer `MissionPatch` |

### Por subtipo — los aciertos perfectos (100%)

`compile_mission/complete` (PM02), `compile_mission/modify_active` (PM03),
`compile_mission/out_of_jurisdiction` (PM06 = route_refuse_physical),
`explain_decision/aggregate_query` (PE03),
`explain_decision/past_decision` (PE01),
`federate_context/weather_daily` (PF01),
`federate_context/weather_critical_or_stale` (PF02).

### Outliers de ejecución (no de calidad)

5 errores en el **primer pase** (todos en C2_balanced): `PA02_C2`, `PF01_C2`,
`PF02_C2`, `PE01_C2`, `PE02_C2` cayeron por ReadTimeout (180s default) o
status_500 (OOM puntual). Tras subir timeout a 300s y rerun con `--resume`,
las 5 pasaron limpiamente. Los datos finales son completos, sin huecos.

Lección operativa: con `num_predict=2048` o `3584`, el timeout cómodo es
**300s**, no 180s. Anotado en `harness.py`.

## 3. Phase 1.5 — system prompt EN vs ES (16 runs)

**Estado**: PENDIENTE — ejecuta el día 11.

**Pregunta**: ¿La hipótesis "system prompt en inglés produce mejor
calidad" se sostiene empíricamente en Gemma 4 E4B con los pivots
representativos (compile, audit, federate, explain)?

**Decision rule** (de `matrix_phase1_5.yaml`): EN gana ≥3 de 4 pivots
→ fijar EN para toda la batería; recomendación firme a Floema de migrar
`SystemPrompts.kt`. Si ES gana en ≥3, hallazgo sorpresa que se cualifica
con Bea antes de concluir.

## 4. Phase 3 — muro maxNumTokens y KV cache (12 runs)

**Estado**: PENDIENTE — ejecuta el día 11.

**Pregunta**: ¿El thinking se acumula en KV cache cuando
`filter_channel_content_from_kv_cache` no está seteado, produciendo
degradación o corte antes en multi-turn? Esta fase aporta evidencia
indirecta a la hipótesis recalibrada del 2026-04-25.

**Métrica clave**: envelope_valid + tokens_out + duration_ms en
`(archetype, depth, thinking)` — si T_ON degrada >> T_OFF en D5
respecto a D1, evidencia de acumulación. Si curvas similares,
hipótesis no respaldada por estos datos, queda pendiente de pregunta
directa al SDK (petición 2 a Floema).

## 5. Lo que NO mide este tuning

- **Latencia real en LiteRT-LM**: corre en CPU local de PC, no en el
  Tensor de Pixel. Las cifras de duration_ms son indicativas de la
  forma de la curva, no del valor absoluto en target.
- **Fidelidad del modelo**: `gemma4:e4b` (Ollama) ≠ `gemma-3n-E4B-it-int4`
  (LiteRT-LM). Tamaños y cuantizaciones diferentes. Las recomendaciones
  marcadas HIGH son las que dependen del *contrato* (sobre común,
  contratos v2, prompts en EN), no del modelo concreto. Las MEDIUM
  dependen del comportamiento específico de Gemma 4 E4B y pueden
  comportarse distinto en E4B-int4 de LiteRT-LM.
- **Streaming**: el adapter bufferea respuestas. Mediciones inter-token
  no se cubren en v0.
- **Audio in/out**: fuera de scope para v0 (es solo prompt tuning).

## 6. Recomendaciones — scoring HIGH/MEDIUM/LOW de transfer

> Cada recomendación viene con:
> - **Confianza de transferencia**: HIGH/MEDIUM/LOW según cuán directamente
>   se traslade del entorno de tuning al runtime real.
> - **Acción concreta**: qué cambiar y dónde.
> - **Evidencia**: qué runs lo soportan.

### R1 — Fijar idioma del system prompt
**PENDIENTE** — depende de Phase 1.5. Recomendación se cierra día 11.

### R2 — Adoptar `reason_exhaustive` (C3_expansive) como perfil base
**Confianza: MEDIUM-HIGH** (sobre `gemma4:e4b`; queda por verificar en
multi-turn en Phase 3).

**Evidencia (Phase 1)**: 87% status_match vs 75% (C2) y 56% (C1), sin
penalización de latencia frente a C2 (126s vs 135s). El sobre común
aguanta al 100% en los tres perfiles, pero `reason_exhaustive` resuelve
mejor los matices de Gate 0 y los subtipos ambiguos (PM05, PE04).

**Acción a Floema**: cuando el system prompt se traslade a
`SystemPrompts.kt`, partir del texto de `reason_exhaustive_en` (en
`code/tuning/system_prompts.yaml`), no del actual stub minimal en
castellano. Mantener en `code/tuning/system_prompts.yaml` como fuente
de verdad mientras tuning v1+ siga.

**Caveat**: con `num_ctx=512` el perfil queda corto si los receipts del
audit son grandes. Phase 3 dirá si ese ajuste sobrevive multi-turn o
hay que recombinar con `num_ctx=2048` + `num_predict=2048` (que sería
un C2.5 a definir).

### R3 — Política de `resetConversation()` por arquetipo
**PENDIENTE** — depende de Phase 3. Recomendación se cierra día 11.

### R4 — Separación `envelope.status` vs `payload.validation` en el system prompt
**Confianza: HIGH** (depende del contrato del sobre, no del modelo).

**Evidencia (Phase 1)**: `audit_visit` solo acierta 5/12 (41%) status_match,
con los 4 subtipos del audit cayendo entre 33% y 66%. El error consistente
es poner el verdict del auditor (`disputed`, `caution` inventado por C1)
en `envelope.status` en lugar de en `payload.validation`. C1 inventa
`caution` fuera del enum (ruptura de contrato).

**Acción a Floema/sobre el system prompt**: el prompt actual de
`auditor_standard` y `reason_exhaustive` describe los dos campos pero
no los contrasta explícitamente. Añadir un párrafo con dos ejemplos:

> envelope.status = ok ⇔ "el audit corrió y produjo un verdict, sea cual sea".
> envelope.status = need_clarification ⇔ "el audit no se pudo correr, faltan datos".
> envelope.status = refuse ⇔ "el audit está fuera de jurisdicción".
> El verdict del audit (confirmed/disputed/inconclusive) va SIEMPRE en
> payload.validation, nunca en envelope.status.

Este cambio es local al system prompt y reproducible al 100% en
`gemma-3n-E4B-it-int4` porque no depende del modelo, depende del texto.

### R5 — `PM04 revoke` requiere afordancia explícita
**Confianza: HIGH**.

**Evidencia (Phase 1)**: PM04 acierta 2/3 (66%) — falla bajo C1_austero
con `refuse`. Cuando hay thinking + auditor_standard o reason_exhaustive,
acierta. Bajo brief_direct, el modelo trata `revoke` como acción
destructiva y se niega.

**Acción**: si Pollen alguna vez usa un system prompt minimal (por
ahorro de tokens), tiene que decir explícitamente "revocar es una
operación válida del compile_mission". En el perfil recomendado
(`reason_exhaustive`) este punto ya queda cubierto.

### R6 — `PE04 out_of_jurisdiction` debe ofrecer `MissionPatch`
**Confianza: HIGH**.

**Evidencia (Phase 1)**: PE04 acierta 1/3 (33%). Bajo C1 entra en
refuse genérico; bajo C2 también. Sólo C3_expansive lo resuelve.

**Acción al system prompt**: añadir un patrón canónico tipo:

> Si el usuario pide simular una consecuencia de cambiar la misión
> (ej. "¿qué pasaría si rotara antes?"), NO simules. Devuelve
> `status:ok` con `payload.action="propose_mission_patch"` y los
> campos que el operador puede ajustar (`presupuesto`, `horizonte`,
> `avoid_hours`). No expliques la consecuencia hipotética: ofrece la
> palanca para que el agricultor decida.

### R7 — Verificar `filter_channel_content_from_kv_cache`
**PENDIENTE — depende de Phase 3**. Recomendación se cierra día 11.
La petición a Floema/SDK de comprobar default oficial sigue en pie
(ver `2026-04-25_peticion-floema-prep-tuning_meristem.md`).

### R8 — `samplerConfig` en `LiteRtChatService.sendPrompt`
Sin cambios respecto a la petición ya enviada
(`2026-04-25_peticion-floema-prep-tuning_meristem.md`).
`temperature=0.3` fue invariante en Phase 1; sin ese hook en
producción no podemos reproducir condiciones exactas.
**Confianza: MEDIUM** sobre el efecto, **HIGH** sobre la necesidad de
poder elegir.

### R9 — Sobre común JSON aguanta al 100% en Phase 1 — adoptar como invariante de v0
**Confianza: HIGH** (depende del contrato del sobre + del system prompt,
no del modelo concreto).

**Evidencia (Phase 1)**: 48/48 runs (100%) emiten JSON parseable en
`message.content`. Ningún caso de fenced markdown extra, prosa antes
o después, o JSON malformado tras el dedupe. Las 3 configs aguantan,
en los 16 prompts.

**Acción a Floema**: el adapter / ResponseParser puede asumir el
sobre común sin fallback de "parser tolerante" complejo. La heurística
defensiva del harness (recortar a `{...}`) puede quedarse como red de
seguridad pero no es esencial bajo el system prompt cuidado.

## 7. Lo que pongo a backlog (no urgente)

- Fase 2 (sweep de temperatura + top_p) — solo si hay diferencias
  apreciables entre arquetipos en Phase 1; si no, queda como
  optimización post-demo.
- Tests del adapter sobre headers `Sprout-Inference-*` desde el harness
  — los tenemos en `test_smoke_parity.py` del adapter; el harness los
  consume sin tests propios.
- Streaming real en producción si el feedback de la Escena 7 lo pide.

## 7.5 Cómo retomar el día 11

Para reanudar Phase 1.5 + Phase 3 mañana sin redescubrir setup:

```powershell
# 1. Verificar Ollama tiene gemma4:e4b cargable (10 GB de modelo)
ollama list  # debe estar gemma4:e4b
# Si no, cualquier llamada lo carga; tarda ~30s la primera vez

# 2. Arrancar adapter en :12000 (Ollama queda en :11434, no se mueve)
$env:INFERENCE_BACKEND='local'
$env:ADAPTER_PORT='12000'
$env:OLLAMA_UPSTREAM_HOST='http://localhost:11434'
cd C:\DATA\PETS\TEST\T6-GEMMA\code\meristem_inference_adapter
python -m src.main

# 3. (otra terminal) smoke test rapido
cd C:\DATA\PETS\TEST\T6-GEMMA
python code/tuning/harness.py --smoke --adapter-url http://localhost:12000

# 4. Phase 1.5
python code/tuning/harness.py --matrix code/tuning/matrix_phase1_5.yaml --adapter-url http://localhost:12000

# 5. Phase 3
python code/tuning/harness.py --matrix code/tuning/matrix_phase3.yaml --adapter-url http://localhost:12000

# 6. Analisis
python code/tuning/analyze.py
```

**Memoria**: con 4-6 GB libres, `gemma4:e4b` carga estable. Si bajamos
de 4 GB con el modelo cargado, los runs de C2/C3 con `num_predict>2048`
arriesgan ReadTimeout. El timeout en harness ya está a 300s tras la
crisis del día 10. Si vuelve a fallar: cerrar Chrome / VS Code; o usar
`--resume` para no perder runs ya OK.

**Contrato del JSONL**: `--resume` dedupea por `run_id`, prefiriendo el
último OK. Nunca borres `phase1.jsonl` para "limpiar" — pierdes datos
buenos. `analyze.py` ya dedupea al cargar.

## 8. Próximos pasos

1. **Día 12** — review meeting Bea + Cambium + Floema + Meristem para
   triage de las 7 observaciones recalibradas (`2026-04-24` y
   `2026-04-25`) cruzadas con estos resultados.
2. **Antes del demo** — Floema confirma estado de v2 contracts en
   `code/pollen/` (petición 1 al equipo). Si no migrado, las
   recomendaciones de envelope se aplican sobre v2; si v1 sigue, se
   adapta una capa en MissionAssembler.
3. **Petición 2 (filter_channel)** — ya formulada; tras Phase 3 se
   sabe si es prioridad alta o media.
4. **Petición 3 (samplerConfig)** — sigue como no bloqueante; queda
   en backlog si LiteRT-LM no lo expone por turno.

## Referencias

- `code/tuning/results/phase1.jsonl` — 48 runs Phase 1
- `code/tuning/results/phase1_5.jsonl` — 16 runs Phase 1.5
- `code/tuning/results/phase3.jsonl` — 12 runs Phase 3
- `code/tuning/analyze.py` — script de resumen
- `docs/22_prompt_taxonomy_v0.md` — taxonomía cerrada con Bea
- `code/tuning/judge_rubric.md` — criterios de evaluación
- `code/tuning/system_prompts.yaml` — los 6 system prompts evaluados
- `bitacora/2026-04-25_peticion-floema-prep-tuning_meristem.md`
- `bitacora/2026-04-25_pollen-observaciones-recalibradas_meristem.md`
- `bitacora/2026-04-25_tuning-blocked-memory_meristem.md`
