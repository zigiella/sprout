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

**Cerrado.** Tres archivos en `CAJON/review_meeting_dia13/bloque_3_meristem_mvp/`: respuesta principal de Meristem + comentario de Floema (saltándose la barrera de lectora) + parking lot de Xilema.

### Hallazgos colaterales del bloque

- **El formato asíncrono permitió que Floema rompiera su rol de lectora con un compromiso espontáneo** que cambió la viabilidad del bloque. Su parking lot ofrece absorber el 100% de la fricción de red y UI móvil (`MeristemNetworkClient` + `VisitarMeristemScreen`), reduciendo el coste de Meristem en ~0.5-1 día. *"Solo tendrá que pensar en el LLM"*. Es exactamente el tipo de aportación que un formato síncrono cargado de turnos hubiera silenciado.
- **Xilema dio dos invariantes que merecen adoptarse independientemente de la decisión Meristem.** No vota entrada/salida pero define el rol con dos cláusulas críticas:
  - *"Lo físico manda, Rhizome arbitra, Pollen media, Meristem afina."* — jerarquía explícita.
  - *"Ningún `PolicyPacket` de Meristem puede reducir hard limits físicos."* — barandilla.
- **Meristem responde "sí condicional"** con tres preguntas que necesita conversar día 14 con Bea + Cambium antes de comprometer firme: cuándo llega Jetson, si se ve en vídeo, prioridad si las cosas chocan.

### Resultado

**Etiqueta: `sí condicional a conversación día 14`** + **adopción de las dos invariantes de Xilema** (independientes de la decisión final).

**Decisiones tomadas hoy (no esperan al día 14):**

1. **Adopción de la jerarquía explícita** *"Lo físico manda, Rhizome arbitra, Pollen media, Meristem afina"* — pasa al writeup §3 como cita. Cambium edita.
2. **Adopción de la barandilla de hard limits** — el contrato `PolicyPacket` (`docs/20_data_contracts.md §3.4`) gana cláusula explícita de que ningún campo del paquete puede reducir hard limits del firmware ESP32. Solo recomendar más conservador. Cambium edita.
3. **Presencia de Meristem en vídeo** decidida por Bea: **se ve, breve, ampliando el cenital final**. Coordinación con Corola en mensaje post-review. *"La narrativa gana mucho"*.
4. **Información operativa Jetson**: Bea confirma que Jetson llega máximo mañana día 14. Eso responde la pregunta 1 de Meristem en su vacilación principal.
5. **Postura de Bea sobre Meristem-nodo minimal**: *"No me importa que sea minimal. Le da sentido a nuestro proyecto. Si Meristem necesitase ayuda con sus tareas, sumaríamos una ayuda."* — voto fuerte a entrada al MVP, con red de seguridad de apoyo si hace falta.

**Decisión que sí queda pendiente para el día 14:**

| # | Acción | Dueña | Plazo |
|---|--------|-------|-------|
| 1 | **Conversación Bea + Cambium + Meristem** — Jetson en mesa día 14 + sí en vídeo (breve, cenital final) + Bea apoya Meristem-nodo minimal con red de seguridad si hace falta. **Output**: decisión firme sí/no de Meristem | Bea agenda | día 14 |
| 2 | **Si decisión firme = sí (probable):** arranque construcción Meristem-nodo con scope ultra-mínimo según Meristem | Meristem + Floema + Xilema | día 14 tarde — día 17 |
| 3 | **Demo-ready** | Meristem | día 18 |

### Acciones derivadas que se asume entran (probabilidad alta de "sí" tras conversación día 14)

Si la conversación día 14 cierra con "sí firme" (probable dado que Jetson estará y Bea confirma apoyo si hace falta):

**Floema:**
- Construye `MeristemNetworkClient` (Retrofit) — POST `/visit` + GET `/policy/latest`. ~0.5 día. Día 14-15.
- Construye `VisitarMeristemScreen` (UI similar a `VisitarRhizomeScreen`). Sumando con anterior, ~0.5 día más.
- Confirma a Meristem (~30 min) que Pollen acepta el shape del `PolicyPacket` que Meristem va a producir.

**Xilema:**
- Antes del día 15: ejemplo canónico de bundle mínimo desde Rhizome (Meristem confirma shape exacto que quiere ingerir).
- Antes del día 16: caso de safety para validar `PolicyPacket` sin actuadores reales (`RA04` como gate obligatorio: si intenta bajar `tank_minimum_pct`, debe rechazar).
- ~30 min validación del prompt único de Meristem.

**Meristem:**
- 2.5 días estimados (con apoyo de Floema absorbiendo móvil): service Meristem mínimo (FastAPI tiny), prompt único, lógica determinista, mini-tuning v0 con 5-6 prompts, integración con Pollen.
- Plan B defensivo: CLI Python ~1 día si dependencias se complican.

**Corola:**
- Coordinación para ampliar el cenital final del vídeo con un beat breve sobre Meristem-nodo en portátil del agricultor. Ajuste menor al guion (no nueva escena).

**Cambium:**
- Edita writeup §3: añade cita de jerarquía + cláusula de barandilla.
- Edita `docs/20_data_contracts.md §3.4`: cláusula explícita en contrato `PolicyPacket`.

---

## Cierre del review

**Tres decisiones consolidadas:**

| # | Bloque | Decisión | Acción activa con plazo |
|---|--------|----------|-------------------------|
| 1 | Triage 7 observaciones Pollen | 4 already done + 3 backlog + 1 apply now (7b) | Floema: log estructurado en `LiteRtInfra.kt:199`, ≤1 hora antes del rehearsal día 14-15 |
| 2 | `rhizome_balanced_es_v05` como base v1 Rhizome | Aprobado sin condición | Meristem: 12 prompts adicionales en PC, ~10 min, antes del día 15 |
| 3 | Meristem (nodo) en MVP | Sí condicional a conversación día 14 + invariantes de Xilema adoptadas + presencia en vídeo confirmada | Bea agenda conversación día 14; si sí firme, construcción día 14-17, demo-ready día 18 |

### Reflexión sobre el formato — síncrono por turnos, no asíncrono

Bea apuntó al cierre del review una observación que merece registrarse como herramienta del proyecto:

> *"No ha sido asíncrona bien bien, ha sido síncrona por turnos, porque estamos todas aquí conectadas a la vez."*

Es un formato distinto al asíncrono puro (días entre respuestas) y al síncrono puro (todas en sala simultáneamente). **Síncrono por turnos**: todas conectadas en la misma ventana temporal, pero respuestas en serie con tiempo de pensamiento entre cada turno + moderación que digiere bloque a bloque sin interrumpir el siguiente.

Ventajas observadas hoy:
- **Respuestas afinadas, no improvisadas**. Cada miembra responde con calma.
- **El parking lot rinde de verdad**. Floema rompió el rol de lectora con un compromiso espontáneo que cambió la viabilidad del bloque 3 — eso no hubiera salido en una agenda síncrona cerrada con turnos rígidos.
- **La moderación es invisible**. Cambium digiere sin fricción para las miembras.
- **La bitácora se redacta sola**. Lo escrito durante el review es el material consolidado.
- **Bea aprueba cada bloque** antes de pasar al siguiente sin necesidad de estar en cada conversación técnica.

Anotado como herramienta reutilizable para futuros reviews complejos del proyecto.

### Parking lot

Ningún tema nuevo abierto que no se cerrara dentro de los tres bloques. Las observaciones de Xilema y Floema en sus parking lots se integraron al cierre de cada bloque correspondiente.

---

*Bitácora del review meeting cerrada el 2026-04-28 a las [hora de cierre]. Modera: Cambium. Aprueba: Bea. Participan: Floema, Meristem. Invitada con voz: Xilema.*
