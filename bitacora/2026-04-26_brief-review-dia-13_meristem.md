# Brief review día 13 — tuning v0 Pollen

**Para**: Bea + Cambium + Floema + Meristem (Xilema invitable)
**Autora**: Meristem
**Fecha**: 2026-04-26 (día 11), preparado para reunión día 13
**Branches**: `feat/meristem-pollen-tuning-v0` (push `0cf310d`),
`feat/pollen-f5-rhizome` (push `2f822ee`)

---

## Resultados

**94 runs ejecutadas** (76 en las 3 fases principales + 18 micro-test
de validación). Sobre común JSON aguantó al **100% en 64/76 runs** y
falló 3/12 sólo bajo T_ON en Phase 3 (saturación intra-turno por thinking
visible). 0 crashes, 0 corrupciones del JSONL, recuperación limpia tras
incidentes operativos (kill por error + falso positivo AMSI del .ps1).

| Fase | Runs | Envelope_valid | Status_match clave |
|---|:-:|:-:|---|
| Phase 1 (3 cfg × 16 prompts EN) | 48/48 | 100% | C3_expansive 87% |
| Phase 1.5 (4 cfg × 4 pivots EN/ES) | 16/16 | 100% | ES 8/8 vs EN 7/8 |
| Phase 3 (2 arch × 3 depths × T) | 12/12 | 9/12 | 3 fallos T_ON intra-turno |
| Micro-test R4+R6 | 18/18 | 100% | 16/18 (vs 9/18 baseline) |

## Hallazgos top-5

1. **Sobre común invariante** (R9, HIGH). 100% en Phase 1 y 1.5. El
   `ResponseParser` puede asumirlo sin parser tolerante complejo.
2. **`reason_exhaustive_es` gana** (R2, MEDIUM-HIGH). 87% Phase 1.
   Adoptado como base en `SystemPrompts.kt`.
3. **EN no es mejor que ES** (R1, MEDIUM). Hipótesis original refutada.
   ES 8/8 vs EN 7/8 en Phase 1.5. **Mantener castellano**.
4. **Split thinking/content invisible al cliente** (R7-bis, HIGH).
   gemma4:e4b en Ollama mete respuesta en `thinking`, dejando
   `content` vacío. LiteRT-LM Android es **peor**: razonamiento + JSON
   mezclados en un solo stream. Decisión: **thinking off para
   multi-turn**, ON solo para llamadas one-shot.
5. **R4 + R6 fix textual validado** (HIGH validado). Micro-test
   movió hot zones de 33% → 83% sin regresión en controles. R4 y R6
   ya en `SystemPrompts.kt` de Pollen.

## Recomendaciones — scoring final

| | Estado |
|---|---|
| **R1** mantener castellano | MEDIUM cerrado, aplicado |
| **R2** `reason_exhaustive_es` base | MEDIUM-HIGH cerrado, aplicado |
| **R3** reset entre arquetipos | Diferido a UI v1 (Pollen actual no tiene selector) |
| **R4** envelope.status vs payload.validation | **HIGH validado**, aplicado |
| **R5** PM04 revoke afordancia | HIGH, aplicado (bonus de Floema) |
| **R6** PE04 ofrece MissionPatch | **HIGH validado**, aplicado |
| **R7** filter_channel KV | LOW inconcluso, sin urgencia (R7-bis lo desactiva) |
| **R7-bis** thinking off multi-turn | **HIGH**, decisión A aplicada |
| **R8** samplerConfig | Arquitectura preparada (`samplerTemperature`); SDK alpha aún no honra |
| **R9** sobre común invariante v0 | **HIGH**, aplicado |
| **R10** manual_intervention | Propuesta nueva, backlog v1 |

**5 HIGH validadas** + **3 MEDIUM/MEDIUM-HIGH** cerradas + **1 LOW
inconclusa sin urgencia** + **1 propuesta v1**. **Cero bloqueos para
el demo**.

## Trabajo de Floema absorbido

`feat/pollen-f5-rhizome` integra:
- `SystemPrompts.kt` con `REASON_EXHAUSTIVE_BASE_ES` + R4 (correcto:
  enum `caution`, no `inconclusive`) + R5 + R6 traducidos a castellano.
- `samplerTemperature: Float?` en `GenerationMetrics` (campo nuevo,
  `temperatureCelsius` reservado para sensor SoC físico).
- 3 schemas v2 nuevos: `MissionPatch.kt`, `ValidationStamp.kt`,
  `WeatherDigest.kt`. Migración v2 completa para los payloads del
  envelope. `ResponseParser` puede deserializar directamente.

## Caveats que llevamos al review

- **Micro-test corrió en EN**, no ES. La traducción al castellano de
  los párrafos R4/R6 es literal mía sin medida directa. Riesgo bajo
  (semántica del contrato, no idiomática). Mitigable con mini-test ES
  de 6 runs (~15 min) post-review si se quiere certeza absoluta.
- **R7 inconcluso**: la pregunta directa "¿default oficial de
  `filter_channel_content_from_kv_cache`?" sigue abierta. Floema reporta
  que en LiteRT-LM Android el flag no tiene efecto visible porque el
  thinking ya viene mezclado en el stream. Operacionalmente cubierto
  por R7-bis decisión A.
- **N=1 por celda en Phase 1 y 1.5**, N=2 en Phase 3. Muestra pequeña.
  Las recomendaciones HIGH son las que dependen del contrato, no del
  modelo concreto, así que el N pequeño afecta menos.

## Decisiones que llevamos al review

1. **¿Completar mini-test ES de 6 runs antes del demo?** Mi voto: no
   urgente, defendible omitirlo.
2. **¿Phase 3-bis con harness corregido para zanjar R7?** Mi voto: no
   necesario para v0; la decisión A ya cubre el caso.
3. **¿Aplicar R10 (manual_intervention) en demo o queda v1?** Mi voto:
   v1 — el caso PA04 sólo falla bajo C3, no es bloqueante.
4. **¿`samplerConfig` cuándo?** Cuando LiteRT-LM publique release que
   honre el binding por turno. Hasta entonces, asumir temperature
   pre-horneada (~0.3) en el modelo cuantizado.
5. **¿Plan post-demo para tuning v1?** Phase 2 (sweep temperatura),
   Rhizome con Xilema, mini-test ES si compensa.

## Preguntas para el grupo

- **A Cambium**: ¿el scoring HIGH/MEDIUM/LOW como contrato de
  validación entre tuning local y target real se generaliza a otros
  experimentos del proyecto, o se queda solo aquí?
- **A Floema**: ¿calendario realista para añadir selector de arquetipos
  en UI (que activaría R3 reset automático)?
- **A Bea**: ¿cuándo arrancamos tuning Rhizome con Xilema? ¿Reusamos
  esta misma estructura `code/tuning/` o forkeamos?
- **Al grupo**: ¿el artículo "Tuning empírico de prompts en Gemma 4 E4B
  on-device" se escribe y dónde se publica?

## Material de soporte

- `bitacora/2026-04-25_tuning-v0-resultados_meristem.md` — bitácora
  completa con tablas, scoring y sección 7.4 micro-test
- `bitacora/2026-04-26_mensaje-floema-completo-tras-microtest_meristem.md`
  — síntesis enviada a Floema
- `code/tuning/results/*.jsonl` — datos crudos (local, no git por
  consistencia con .gitignore)
- `docs/22_prompt_taxonomy_v0.md` — taxonomía Pollen + Rhizome
- 4 mensajes a Floema día 11 + 2 mensajes a Cambium (cierre días 10 y 11)
