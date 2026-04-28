# Review meeting día 13 — bitácora en directo

**Fecha:** 2026-04-28 (día 13)
**Modera:** Cambium
**Aprueba:** Bea
**Participan:** Floema, Meristem
**Invitada (lectura):** Xilema
**Formato:** asíncrono por bloques. Cada miembra responde en `CAJON/review_meeting_dia13/bloque_X_*/respuesta_[nombre].md`. Cambium consolida y solo Cambium escribe en esta bitácora.

---

## Agenda

| # | Bloque | Quién responde | Estado |
|---|--------|----------------|--------|
| 0 | Apertura + reglas | (lectura para todas) | Disparado |
| 1 | Triage 7 observaciones de Meristem sobre código Pollen | Floema + Meristem | Pendiente |
| 2 | `rhizome_balanced_es_v05` como base v1 de Rhizome | Meristem + Xilema | Pendiente |
| 3 | Meristem (nodo) en MVP | Solo Meristem | Pendiente |

---

## Bloque 1 — Triage 7 observaciones Pollen

**Cerrado.** Tres respuestas en `CAJON/review_meeting_dia13/bloque_1_triage_pollen/respuesta_{floema,meristem,xilema}.md`. Convergencia muy alta (8 etiquetas alineadas), una decisión escalada a Bea (7b), aprobada como `apply now`.

### Hallazgos colaterales del bloque

- **División 7 → 7a/7b** propuesta por Xilema (invitada como lectora) y adoptada por Meristem retroactivamente. La observación original juntaba dos cosas categóricamente distintas: reflection sobre `Message` (deuda contenida) y `catch(t: Throwable)` vacío (riesgo de rehearsal). La división evita que la deuda menor tape la deuda peligrosa.
- **El intercambio Floema → Meristem sobre la observación #6** se resolvió en directo dentro del bloque. Floema preguntó si Meristem aceptaba el trade-off del prompt unificado en español como estándar MVP; Meristem respondió sí con datos: *"R1 cerrado en Phase 1.5: ES gana 8/8 vs EN 7/8"*. Su hipótesis original ("EN mejor por training data dominante") quedó refutada empíricamente.
- **La invitación a Xilema rindió.** No era owner de Pollen y no hizo triage principal, pero su lectura desde Rhizome y su crítica de la mezcla 7a/7b aportó valor que ninguna otra miembra había levantado.

### Resultado — tabla consolidada

| # | Observación | Etiqueta | Dueña / Estado | Plazo |
|---|-------------|----------|----------------|-------|
| 1 | `maxNumTokens` hardcoded | `post-demo backlog` | — | Post-hackathon |
| 2 | `SamplerConfig` no expuesto en `sendPrompt` | `already done` | Floema F5 día 12 (`samplerTemperature` separado, expuesto en `sendPrompt` + `GenerationMetrics`) | — |
| 3 | `resetConversation()` no conectado a arquetipos | `already done` | Floema F5 día 12 (`ChatFeature.kt:81` `onArchetypeSelected` con 4 arquetipos dispara reset + ajusta `isThinkingEnabled`) | — |
| 4 | Métricas en `outputChars`, no tokens | `post-demo backlog` (mitigado por headers `Sprout-Inference-*` del adapter que sí cuentan tokens reales) | — | Post-hackathon |
| 5 | `filter_channel_content_from_kv_cache` | `already done` | Floema F5 día 12 (inyectado en `extraContext` cuando thinking on) | — |
| 6 | `SystemPrompts.kt` 4 arquetipos en EN | `post-demo backlog` con dato R1 (ES gana 8/8 vs EN 7/8 en Phase 1.5; coherencia con UI/voz/pitch en castellano) | — | Post-hackathon |
| 7a | Reflection para construir `Message` | `post-demo backlog` | — | Post-hackathon |
| 7b | `catch(t: Throwable) {}` vacío silencia errores | **`apply now`** | **Floema** | **≤1 hora antes del próximo rehearsal (día 14 o 15)** |

### Acción derivada (única)

**Floema (≤1 hora):** sustituir el `catch(t: Throwable) {}` vacío de `LiteRtInfra.kt` línea 199 por `Log.e(TAG, "generation chunk failed", t)` o métrica equivalente `generation_failed`. Sin lógica nueva, solo observabilidad. Razón: si Pollen falla en rehearsal o demo (OOM, SIGSEGV, timeout, truncamiento), tener log estructurado da segundos para diagnosticar en vez de respuesta truncada sin pista. Decisión aprobada por Bea tras propuesta de Cambium con argumentos de Meristem y Xilema (riesgo de rehearsal) frente a lectura pragmática de Floema (no nos matará en MVP).

---

## Bloque 2 — `rhizome_balanced_es_v05` como base v1

*[Cambium escribe aquí cuando Bea avise que ambas miembras han respondido. Decisión binaria + condición opcional.]*

### Resultado

*[pendiente]*

---

## Bloque 3 — Meristem (nodo) en MVP

*[Cambium escribe aquí cuando Bea avise que Meristem ha respondido. Si Meristem dice "sí": entra al MVP con scope mínimo. Si vacila o dice "diferir": queda en exploración con Bea + Cambium para día 14. Si dice "no": queda fuera limpiamente.]*

### Resultado

*[pendiente]*

---

## Cierre del review

*[Cambium escribe aquí al cierre del último bloque. Recap de las tres decisiones, dueñas, plazos. Parking lot si hubo temas nuevos abiertos.]*

### Acciones derivadas

*[pendiente]*

---

*Bitácora abierta el 2026-04-28 al iniciar el review. Modo "en directo": Cambium actualiza tras cada bloque cerrado.*
