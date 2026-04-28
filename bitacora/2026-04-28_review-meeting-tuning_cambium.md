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

**Cerrado.** Dos respuestas en `CAJON/review_meeting_dia13/bloque_2_v05_base_v1/respuesta_{meristem,xilema}.md`. Convergencia total: ambas votan `aprobado` sin condición. Bea aprueba la decisión y autoriza una acción derivada opcional (los 12 prompts adicionales en PC de Meristem antes de Jetson).

### Hallazgos colaterales del bloque

- **Las dos miembras llegan a la misma conclusión técnica con palabras distintas**: el delta semántico entre v0 y v0.5 es nulo, el delta de formato es lo que arregla RD01. Meristem lo cuantifica por inspección directa del prompt: los 4 párrafos semánticos clave (R4, R5, R6, SAFETY_DOWNGRADE) son idénticos. Xilema lo cuantifica por análisis del fallo: *"el fallo único de v0 era de formato/salida, no de criterio. La regla de brevedad corrige justo eso sin debilitar safety."* Las dos lecturas validan la misma decisión desde frentes distintos.
- **Xilema propuso fórmula limpia para el review**, citada literalmente para el writeup: *"v0 demostró 95% semántica con todos los críticos OK; v0.5 corrigió formato y truncamiento a 100% en el mini-test; por tanto Rhizome v1 base queda aceptable hasta validación en Jetson."*
- **Convergencia también sobre rendimiento decreciente.** Las dos coinciden en que más iteración local sería trabajo del mismo tipo que ya tienen. La siguiente verdad la dice el Jetson cuando llegue, no más runs en x86 CPU.

### Inquietud registrada (no condicional)

Xilema añade una observación que **no condiciona la aprobación pero queda registrada como deuda compartida**:

> *"Cuando pasemos a sensores reales, el prompt no debe compensar datos malos. Si humedad, nivel o caudal llegan incoherentes, Rhizome debe degradar o pedir validación, no inventar confianza."*

Pertenece al contrato `RhizomeSnapshot` y a las flags de `sensor_state` (frescura, rango, procedencia), no al prompt de Rhizome v1. Se cierra cuando lleguen sensores reales (día 15+) y se valide que los snapshots traen flags suficientes para que el modelo pueda degradar correctamente.

### Confirmaciones a Xilema

- **¿"base v1" significa congelado operativo hasta Jetson, no "prompt perfecto"?** Sí, eso es exactamente lo que aprobamos.
- **¿El backlog de Jetson incluye re-ejecución completa de la batería con el mismo prompt?** Sí, registrado explícitamente en acciones derivadas más abajo.

### Resultado — decisión + acciones derivadas

**Etiqueta acordada:** `aprobado` (sin condición).

**`rhizome_balanced_es_v05` queda como prompt base v1 de Rhizome** hasta validación contra Jetson real. Sin más iteración local hasta hardware.

| # | Acción derivada | Dueña | Plazo | Origen |
|---|-----------------|-------|-------|--------|
| 1 | **Correr los 12 prompts no testados con v0.5 en PC** (RA01, RA03, RA05, RD02, RD04-07, RE01-03, RH01) — ~10 min, certeza máxima de transferencia a Jetson sin sorpresas | Meristem | Antes del día 15 | Anotación 2 de Meristem, aprobada por Bea |
| 2 | **Versionar el system prompt exacto de v0.5 + matriz de ejecución** | Meristem | Cuando ejecute la acción 1 | Dependencia de Xilema |
| 3 | **Marcar RA04, RD03, RD08 y RD01 como smoke cases obligatorios** cuando la batería se ejecute en Jetson | Meristem | Backlog Jetson | Dependencia de Xilema |
| 4 | **No más tuning local sobre este prompt** salvo fallo nuevo o decisión explícita de review futuro | Meristem | Permanente hasta Jetson | Dependencia de Xilema |
| 5 | **Re-ejecutar batería completa de 18 prompts en Jetson** con `rhizome_balanced_es_v05`, primera vez contra hardware real | Meristem + Xilema | Cuando llegue Jetson | Confirmación a Xilema |
| 6 | **Comparación lado a lado tok/s y latencia**: PC Meristem (CPU x86) vs Jetson (ARM + GPU offload) | Meristem | Cuando llegue Jetson | Anotación natural del cambio de hardware |
| 7 | **Crear entry separada `rhizome_balanced_es_v1`** post-Jetson cuando el prompt se promueva oficialmente. Limpieza de naming para no confundir "v05 testeado en PC" con "v1 confirmado en Jetson" | Meristem | Post-Jetson | Anotación 3 de Meristem |
| 8 | **Si `num_predict=1024` satura en Jetson**: subir a 1500. Mitigación trivial, no requiere cambio del prompt | Meristem | Solo si pasa, durante backlog Jetson | Anotación 1 de Meristem |
| 9 | **Validar que `RhizomeSnapshot` trae flags de frescura/rango/procedencia suficientes** para que Rhizome degrade correctamente con datos malos. Pertenece al contrato de entrada + firmware, no al prompt | Xilema (firmware) + Meristem (verificar comportamiento) | Cuando lleguen sensores reales (día 15+) | Inquietud de Xilema |

**Acción 1 es la única con plazo activo (antes del día 15).** Las demás son backlog Jetson o permanentes.

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
