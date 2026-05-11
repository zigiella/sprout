# Copies bilingües del vídeo Sprout — ES / EN

> **AVISO IMPORTANTE DE LECTURA — día 26**
>
> La **fuente viva de verdad** sobre el copy del video día 26 (master 3:08.5, voz pro DbwW activa) es:
>
> **`C:\DATA\PETS\CLAUDE\equipo-agentes\video-proyecto\produccion\handoffs\corola-video-snapshot.md`** (regenerable, sección "VOs (ES + EN side-by-side)" + "Cartelas con texto visible" + "Vocabulario controlado" + "Decisiones de copy (orden cronológico)").
>
> Este `copies_bilingual.md` v0.7 preserva la trazabilidad histórica y las versiones estables hasta v1.8.3. Las decisiones de copy días 24-26 (vocabulario `policy`/`criteria`, voz humana E5 doblada con DbwW, cenital reescrito, E8 eliminado, refinamientos Z99 y E10) están consolidadas como historial pero NO sustituyen al snapshot vivo. Para edición de copy operativa: ir al snapshot y a los `data/*.json` que lo alimentan.

**Versión:** v0.7 (consolidación post-rodaje día 26 — apuntada al snapshot Bract como fuente viva. Historial preserva versiones estables v1.8.x)
**Fecha:** 2026-05-11 (día 26)
**Autora:** Corola
**Origen:** decisión Bea día 16 — *"Necesitaré tener siempre los copies del video (textos VO, voz en off, cartelas, etc en ES y EN)."* Actualizado al giro estratégico día 18-19 (12 escenas, VO inglés master, frases fuertes reformuladas, Meristem en MVP). **Convención day 26:** doc estable + fuente viva (snapshot Bract).

---

## Convenciones (v1.7 — actualizadas tras giro estratégico día 18-19)

- **VO master** — **inglés** grabado por Bea (cambio v1.7 sobre v1.6: era castellano). Versión ES dub aparte.
- **Subtítulos master** — **inglés** (mismo idioma que VO).
- **Cartelas y overlays on-screen** — **inglés** en pantalla. La columna ES es referencia interna para conversaciones del equipo.
- **Cartel físico** — inglés en plano.
- **Voz humana real escena 5 (`operator_note`)** — **castellano literal**, **no se traduce** ni en pantalla ni en doblaje. Es la única excepción a la regla de bilingüismo: se respeta como voz humana auténtica. Subtítulo inglés en master entre comillas marca que es voz humana, no VO.
- **"AI Local-first"** sustituye sistemáticamente a "Local-first" (decisión v1.7).

---

## Estado de las escenas en v0.2

| Escena | Estado | Notas |
|--------|--------|-------|
| **E0** Cartela apertura Sprout | ✅ **Estable v1.8** | Wordmark Sprout + subtítulo "AI Local-first irrigation decisions." + "Safe · explainable · open-source." Microcartela atribución Gemma trademark NO va aquí (va en cierre). |
| **E1** La ausencia con datos globales | ✅ **Estable v1.8** | 4 datos globales (UNCCD, OECD, FAO, ITU) + microcorte 0.5s tierra agrietada + pregunta abierta. |
| **E2** Rhizome decide offline | ✅ **Estable v1.8.2** | Frase fuerte 1 reformulada. VO en inglés. **Cartela bisagra apertura recuperada v1.8.2** (*"Imagine this pot is a whole plot."* full-screen estilo "Three days later", 0:25–0:28, 3s). |
| **E3** ESP32 SAFE LIMIT | ✅ **Estable v1.7** | Frase fuerte 3 reformulada (proposes/disposes). Cartela técnica nueva (AI proposes / ESP32 validates). |
| **E3b** Meristem prepara | ✅ **Estable v1.8** | Plano cocina + portátil + Pollen recibiendo política. VO Extra E3b: *"Meristem composes the policy."* |
| **E4** Llega Pollen | ✅ **Estable v1.7** | Frase fuerte 2 reformulada (con Pollen explícito). |
| **E5** La persona da una misión | ✅ **Estable v1.7** | Voz humana castellano literal. Subtítulo inglés en master. |
| **E6** Ferry A→B | ✅ **Estable v1.8.3** | Frase fuerte 5 sin cambios. **Ruta principal v1.8.3:** solo `Context`, sin meteo en rodaje (decisión Bea día 21, Venation tiene captura `WeatherDigest` reactivable como plan B en CapCut). |
| **E7** Watering criteria updated | ✅ **Estable v1.7** | Climax. Cartela ancla `Watering criteria updated.` + invariante esquina. |
| **E8** Caducidad | ✅ **Estable v1.8 — NO se mata** | Decisión Bea día 20. F4 + plano `expired → rejected` se quedan. Vale para Safety & Trust. |
| **E9** Cenital federado | ✅ **Estable v1.8 — Opción B firme** | 20s con cadencia Venation completa (5 cartelas asimétricas + pausa tensa + cierre largo + sello SYNCED ✓). Cartela final v1.6: *"Federated intelligence, carried by Pollen."* Decisión Bea día 20. |
| **E9b** Meristem recibe + cierre | ✅ **Estable v1.8** | Plano íntimo cocina + frase 6 ubicada aquí (decisión Bea día 20) + tagline bookend cierre + tarjeta logo final con atribución Gemma. |

---

## Escena 2 — Rhizome decide offline (0:25–0:50) ✅ ESTABLE v1.8.2

### VO master (inglés grabado por Bea, ES dub aparte)

| Elemento | EN (master VO) | ES (dub) | Posición / Tiempo |
|----------|----------------|----------|-------------------|
| VO 2A | **"This plot is not alone. It has a local brain. It reads the soil. It decides."** | *"Esta parcela no está sola. Tiene un cerebro local. Lee el suelo. Decide."* | Sobre el log del Jetson · 0:29–0:37 (~14 palabras EN) |
| VO 2B | **"And signs what it does, so it can be explained."** | *"Y firma lo que hace, para que se pueda explicar."* | Sobre el `DecisionReceipt` · 0:37–0:43 (~10 palabras EN) |
| VO 2C (**frase fuerte 1 reformulada**) | **"Rhizome keeps the plot alive — without a person, without a signal."** | *"Rhizome mantiene viva la parcela — sin nadie, sin red."* | Sobre el agua de la válvula · 0:48–0:50 (~12 palabras EN) |

### Cartelas y overlays on-screen (inglés)

| Elemento | EN (en pantalla) | ES (referencia) | Posición / Tiempo |
|----------|------------------|-----------------|-------------------|
| **Cartela bisagra apertura E2 (NUEVA v1.8.2)** | **"Imagine this pot is a whole plot."** | *"Imagina que esta maceta es una parcela entera."* | **Centro full-screen · 0:25–0:28 (3s) · misma gráfica que `"Three days later"` E8: Manrope titular sobre fondo casi-negro `soil.graphite`, sin plano físico debajo, sin VO** |
| Overlay persistente | **`OFFLINE`** | "Sin red" | Esquina sup. izq. · entra a 0:28, persistente resto del bloque (0:28–0:50) |
| Cartela técnica 1 | **`Rhizome: Jetson Orin Nano · Gemma 4 E2B · local · llama.cpp`** | "Rhizome: Jetson Orin Nano · Gemma 4 E2B local llama.cpp" | Esquina sup. der. · ~0:29–0:32 (3s) |
| Sub-cartela técnica | **`LLM called only when ambiguous`** | "LLM solo en casos ambiguos" | Esquina sup. der. · ~0:32–0:35 (3s) |
| Cartela `DecisionReceipt` | **`DecisionReceipt`** | "Recibo de decisión" | Centro/superpuesta · 0:41–0:43 (2s) |

**Nota cartela bisagra (v1.8.2):** recuperada de E1 v1.6 (era cartela inicial bilingüe sobre plano de maceta). En v1.7 cayó cuando E1 pasó a opener tipográfico con 4 datos globales. En v1.8.2 vuelve al inicio de E2 con gráfica de E8 *"Three days later"* — bisagra tipográfica entre E1 (datos globales) y E2 (plano técnico). Decisión Bea día 21.

### Log diseñado en pantalla del Jetson (Venation, sin traducción — es código del sistema)

```
SOIL READ
plot: PLOT_01
soil: 31%
threshold: 34%

DECISION
candidate: WATER
final_action: 18s
why_short: Soil below minimum. Budget available.
```

`WATER` y `final_action` resaltados en `signal.seed`. Resto en gris atenuado.

---

## Escena 3 — ESP32 SAFE LIMIT (0:50–1:05) ✅ ESTABLE v1.7

### VO master

| Elemento | EN (master VO) | ES (dub) | Posición / Tiempo |
|----------|----------------|----------|-------------------|
| VO 3 (**frase fuerte 3 reformulada**) | **"AI proposes. Physical safety disposes."** | *"La IA propone, la capa física dispone."* | Sobre el ESP32 modulando · 0:53–0:58 (~6 palabras EN) |

### Cartelas y overlays on-screen (inglés)

| Elemento | EN (en pantalla) | ES (referencia) | Posición / Tiempo |
|----------|------------------|-----------------|-------------------|
| Cartela técnica esquina | **`AI proposes / ESP32 validates`** | "La IA propone / el ESP32 valida" | Esquina sup. der. · 0:50–0:53 (3s) |
| Overlay `ESP32 SAFE LIMIT` | **`ESP32 SAFE LIMIT`** | "Límite seguro del ESP32" | Esquina sup. der. · entrada a 0:50, persistente |
| Cartela ancla central | **"When in doubt, water less."** | *"Cuando duda, riega menos."* | Centro dominante · 0:58–1:01 (3s) — sobre el `DecisionReceipt` atenuado |

### Cambios v1.7 sobre v1.6

- Cartela técnica: `function/read tools · no actuator tools` → `AI proposes / ESP32 validates` (Venation, voto Bea aceptado).
- Frase fuerte 3 reformulada: `"La IA propone. El agua la gobierna una capa física prudente."` → `"AI proposes. Physical safety disposes."` (juego proposes/disposes).

---

## Escena 4 — Llega Pollen (1:15–1:40) ✅ ESTABLE v1.7

### VO master

| Elemento | EN (master VO) | ES (dub) | Posición / Tiempo |
|----------|----------------|----------|-------------------|
| VO 4 (**frase fuerte 2 reformulada**) | **"Every Pollen visit can change the local criterion."** | *"Cada visita de Pollen puede cambiar el criterio local."* | Sobre el plano de la persona mirando la planta · 1:32–1:40 (~8 palabras EN) |

### Cartelas y overlays on-screen (inglés)

| Elemento | EN (en pantalla) | ES (referencia) | Posición / Tiempo |
|----------|------------------|-----------------|-------------------|
| Cartela técnica esquina | **`Pollen: Android · Gemma 4 E4B · LiteRT-LM · on-device`** | "Gemma 4 E4B LiteRT-LM en el dispositivo" | Esquina sup. der. · 1:20–1:23 (3s) |
| Pregunta UI (en pantalla del móvil) | **`What happened since my last visit?`** | "¿Qué ha pasado desde mi última visita?" | Pantalla del móvil · 1:20–1:25 (5s) |
| Bloque resumen UI (en pantalla del móvil) | **`SINCE LAST VISIT / 2 watering events / 1 skipped decision / 0 blocked actions`** + receipts (`WATER · 18s · 14:00`, `WATER · 12s · 09:30`, `SKIP · 22:00 · soil above threshold`) | "Desde la última visita..." | Pantalla del móvil · 1:25–1:32 (7s) |

### Cambios v1.7 sobre v1.6

- Frase fuerte 2 reformulada: `"Cada visita puede cambiar el criterio local."` → `"Every Pollen visit can change the local criterion."` (Pollen explícito).
- Recortada de 30s a 25s.

---

## Escena 5 — La persona da una misión (1:40–2:00) ✅ ESTABLE v1.7

### Voz humana real (CASTELLANO LITERAL — excepción narrativa deliberada)

| Elemento | ES (grabación literal Bea) | EN (subtítulo en master, entre comillas) | Posición / Tiempo |
|----------|----------------------------|------------------------------------------|-------------------|
| Voz humana E5 | **"Vuelvo el viernes. Esta planta aguanta más seca de lo que crees, riega un poco menos."** | *"I'll be back Friday. This plant takes drier than you think — water it a bit less."* | Sobre plano cercano del móvil · 1:43–1:50 (14 palabras ES) |

**No se traduce en pantalla del móvil ni en `operator_note`. Subtítulo inglés en master entre comillas marca que es voz humana, no VO.**

### VO master (inglés)

| Elemento | EN (master VO) | ES (dub) | Posición / Tiempo |
|----------|----------------|----------|-------------------|
| VO 5 cierre | **"What the person says becomes policy."** | *"Lo que la persona dice se convierte en política."* | Plano cerrado del móvil · 1:58–2:00 (~6 palabras EN) |

### Cartelas y overlays on-screen (inglés)

| Elemento | EN (en pantalla) | ES (referencia) | Posición / Tiempo |
|----------|------------------|-----------------|-------------------|
| UI motion procesamiento Pollen | **`listening → compiling → validating`** | "escuchando → compilando → validando" | Pantalla del móvil · 1:50–1:53 (3 estados secuenciales 1s cada uno) |
| UI compilación `MissionPatch` | **`VOICE NOTE`** + frase castellana literal + **`COMPILED PATCH`** + cuatro campos resaltados con `signal.seed` (`horizon_h: 72`, `soil_thresholds.dry: 35 → 25`, `budget_cap_ml: 900`, `operator_note: preserved`) | UI sistema (sin traducción — es output del compilador) | Pantalla del móvil · 1:53–1:58 (5s) |
| Cartela superpuesta | **`MissionPatch validated`** | "MissionPatch validado" | Centro/superpuesta · 1:55–1:57 (2s) |

### Notas críticas

- **`operator_note: preserved`** es la etiqueta del sistema que indica que la voz humana literal se almacena sin recortar. La frase coloquial castellana queda en `VOICE NOTE` arriba.
- Bea graba la voz humana en días 24-25 antes del rodaje principal.
- Coordinación pendiente con Floema sobre UI exacta del compilador (mock fiel si captura real no llega a tiempo).

---

## Escena 6 — Ferry A→B (2:00–2:20) ✅ ESTABLE v1.7

### VO master

| Elemento | EN (master VO) | ES (dub) | Posición / Tiempo |
|----------|----------------|----------|-------------------|
| VO 6A | **"Pollen brings questions, answers, and context."** | *"Pollen trae preguntas, respuestas y contexto."* | Sobre el ferry · 2:00–2:05 (~6 palabras EN) |
| VO 6B (**frase fuerte 5**) | **"Pollen turns those visits into federated intelligence."** | *"Pollen convierte esas visitas en inteligencia federada."* | Sobre el Rhizome 02 con bundle aceptado · 2:17–2:20 (~8 palabras EN) |

**Eco interno:** *"those"* en F5 hace eco directo a *"every Pollen visit"* en F2 (E4). Coherencia narrativa cross-escena.

### Cartelas y overlays on-screen (inglés)

**Decisión Bea día 21 (v1.8.3):** ruta principal **sin meteo** (`Context`). Plan B reactivable con `WeatherDigest` si en rodaje al final hay tiempo (Venation tiene captura producida).

#### Ruta principal v1.8.3 — sin estación meteo, solo `Context`

| Elemento | EN (en pantalla) | ES (referencia) | Posición / Tiempo |
|----------|------------------|-----------------|-------------------|
| Cartela superpuesta ferry | **`Context ferry`** | "Ferry de contexto" | Centro/superpuesta · 2:02–2:04 (2s) |
| Cartela en pantalla Rhizome 02 | **`Context accepted · Source: rhizome_01`** | "Contexto aceptado · Origen: rhizome_01" | Pantalla Rhizome 02 · 2:08–2:12 (4s) |

#### Plan B reactivable — con estación meteo, `WeatherDigest`

Solo se usa si en rodaje al final hay tiempo y Bea decide incluir estación meteo física al lado del PLOT_01. **Cartelas ya producidas por Venation en iteraciones anteriores — sustitución directa de 2 PNGs en CapCut, no requiere re-producir.**

| Elemento | EN (en pantalla) | ES (referencia) | Posición / Tiempo |
|----------|------------------|-----------------|-------------------|
| Cartela superpuesta ferry | **`WeatherDigest ferry`** | "Ferry de WeatherDigest" | Centro/superpuesta · 2:02–2:04 (2s) |
| Cartela en pantalla Rhizome 02 | **`WeatherDigest accepted · Source: rhizome_01`** | "WeatherDigest aceptado · Origen: rhizome_01" | Pantalla Rhizome 02 · 2:08–2:12 (4s) |

### Carteles físicos visibles en escena 6

| Elemento | EN (en plano) | ES (referencia) |
|----------|---------------|-----------------|
| Cartel maceta PLOT_01 | **`PLOT_01 with RHIZOME_01`** | "Parcela 01 con Rhizoma 01" |
| Cartel caja electrónica RHIZOME_01 | **`RHIZOME_01 / EDGE NODE`** | "Rhizoma 01 / Nodo edge" |
| Cartel maceta PLOT_02 | **`PLOT_02 with RHIZOME_02`** | "Parcela 02 con Rhizoma 02" |
| Cartel caja electrónica RHIZOME_02 | **`RHIZOME_02 / EDGE NODE`** | "Rhizoma 02 / Nodo edge" |

---

## Escena 7 — Watering criteria updated (2:20–2:40) ✅ ESTABLE v1.7 — CLIMAX

### VO master

| Elemento | EN (master VO) | ES (dub) | Posición / Tiempo |
|----------|----------------|----------|-------------------|
| VO 7 (sobrio) | **"The system updates its care."** | *"El sistema ajusta los cuidados."* | Sobre el plano del agua (chorro corto) · 2:32–2:40 (~5 palabras EN) |

### Cartelas y overlays on-screen (inglés)

| Elemento | EN (en pantalla) | ES (referencia) | Posición / Tiempo |
|----------|------------------|-----------------|-------------------|
| Cartela esquina invariante | **`Physical layer prevails. / Rhizome arbitrates. / Pollen mediates. / Meristem refines.`** | "La capa física prevalece. / Rhizome arbitra. / Pollen media. / Meristem afina." | Esquina inferior derecha · 2:24–2:29 (5s, IBM Plex Mono pequeña, paleta sobria) |
| Cartela ancla central | **"Watering criteria updated."** | *"Criterios de riego actualizados."* | Centro dominante · 2:29–2:32 (3s) — sobre los tres bloques de evidencia atenuados |

### Log diseñado en pantalla del Jetson (sin traducción — es código del sistema)

```
MISSION PATCH ACCEPTED
id: mp_004
ttl: 21600s

POLICY DIFF
soil_thresholds.dry    35 → 25
daily_budget_ml        1500 → 900

NEXT DECISION CHANGED
final_action           12s
why_short              Mission compiled from human voice
```

`POLICY DIFF` con dos campos resaltados en `signal.seed` (los que cambian). Resto en gris atenuado.

### Cambios v1.7 sobre v1.6

- Cartela ancla central confirmada: `Watering criteria updated.` (era `Criterion updated.` en v1.4 → cambio Venation día 17 ratificado).
- Climax narrativo confirmado en E7 (no E6 transferencia A→B) por Bea día 18-19.

---

## Escena 0 — Cartela apertura Sprout (0:00–0:05) ✅ ESTABLE v1.8

**Sin VO.** Marco visual antes de la ausencia.

| Elemento | EN (en pantalla) | ES (referencia) | Posición / Tiempo |
|----------|------------------|-----------------|-------------------|
| Wordmark | **`Sprout`** | "Sprout" | Centro · Manrope titular grande, `soil.oat` sobre `soil.graphite` |
| Subtítulo | **"AI Local-first irrigation decisions."** | *"Decisiones de riego local-first con IA."* | Centro · Manrope mediano |
| Línea inferior | **"Safe · explainable · open-source."** | *"Seguras · explicables · open-source."* | Centro · Manrope pequeña |

**Atribución Gemma trademark NO va en E0** (decisión Bea día 19 — va en cierre concentrado por reglas hackathon).

---

## Escena 1 — La ausencia con datos globales (0:05–0:25) ✅ ESTABLE v1.8

**Sin VO.** Opener tipográfico con 4 datos globales + microcorte tierra agrietada (0.5s) + pregunta abierta. Cataluña como ejemplo del patrón global.

| Tiempo | Elemento | EN (en pantalla) | ES (referencia) |
|--------|----------|------------------|-----------------|
| 0:05–0:09 (4s) | Dato 1 | **"In 2023, 48% of the world's land area suffered at least one month of extreme drought."** + microcita `[UNCCD World Drought Atlas]` | "En 2023, el 48% de la superficie terrestre mundial sufrió al menos un mes de sequía extrema." |
| 0:09–0:13 (4s) | Dato 2 | **"1.8 billion people affected. $300 billion per year in losses."** + microcita `[UNCCD]` | "1.800 millones de personas afectadas. 300.000 millones al año en pérdidas." |
| 0:13–0:13.5 (0.5s) | Microcorte tierra agrietada | (sin texto) | (bisagra emocional macro→concreto) |
| 0:13.5–0:17.5 (4s) | Dato 3 | **"In Catalonia 2024, agriculture cut water for irrigation by 80%."** + microcita `[Generalitat de Catalunya]` | "En Cataluña 2024, la agricultura redujo el agua para riego un 80%." |
| 0:17.5–0:21.5 (4s) | Dato 4 | **"58% of the rural population uses internet. In low-income countries: only 14%."** + microcita `[ITU 2025]` | "El 58% de la población rural usa internet. En países de bajos ingresos: solo el 14%." |
| 0:21.5–0:25 (3.5s) | Pregunta abierta | **"When network is absent — and the human is far — what makes the right call?"** | "Cuando no hay red, y nadie está cerca — ¿quién decide bien?" |

**Microcorte tierra agrietada (0.5s)** — bisagra emocional + corte respiratorio + anticipación de Cataluña. Pendiente confirmar producible con Venation o se descarta.

---

## Escena 3b — Meristem prepara la política (1:05–1:15) ✅ ESTABLE v1.8

**Plano cocina + portátil + Pollen recibiendo política.** Bookend con E9b.

### VO master

| Elemento | EN (master VO) | ES (dub) | Posición / Tiempo |
|----------|----------------|----------|-------------------|
| VO E3b (Extra E3b — cerrada Bea día 19) | **"Meristem composes the policy."** | *"Meristem compone la política."* | Sobre el plano del Pollen recibiendo · 1:12–1:15 (~5 palabras EN) |

### Cartelas y overlays on-screen (inglés)

| Elemento | EN (en pantalla) | ES (referencia) | Posición / Tiempo |
|----------|------------------|-----------------|-------------------|
| Cartela cierre escena | **`Meristem composes.`** | "Meristem compone." | Centro/superpuesta · 1:13–1:15 (2-3s, Manrope) |

**Notas:**
- UI Meristem en pantalla del portátil — coordinación con Meristem (real preferida o mock fiel).
- `signal.seed` activo en el momento donde el sistema decide.
- Pollen (móvil) sobre la mesa recibiendo la política — **eco visual con E9b** (Pollen entrega de vuelta los datos recogidos).

---

## Escena 8 — Caducidad (2:40–2:50) ✅ ESTABLE v1.8 — DECISIÓN BEA DÍA 20: NO SE MATA

**E8 sobrevive.** Frase fuerte 4 + plano `expired → rejected` valen para Safety & Trust del concurso.

### VO master

| Elemento | EN (master VO) | ES (dub) | Posición / Tiempo |
|----------|----------------|----------|-------------------|
| VO E8 (frase fuerte 4) | **"Every intelligence has jurisdiction. And expiry."** | *"Toda inteligencia tiene jurisdicción. Y caducidad."* | Sobre la pantalla del rechazo · 2:46–2:50 (~7 palabras EN) |

### Cartelas y overlays on-screen (inglés)

| Elemento | EN (en pantalla) | ES (referencia) | Posición / Tiempo |
|----------|------------------|-----------------|-------------------|
| Cartela salto temporal | **"Three days later"** | "Tres días después" | Centro · 2:40–2:42 (2s, Manrope) |
| Cartela superpuesta rechazo | **`expired → rejected`** + borde doble `status.blocked` | "Caducado → Rechazado" | Centro/superpuesta sobre log · 2:44–2:46 (2s, IBM Plex Mono) |

### Log diseñado en pantalla del Jetson (sistema, sin traducción)

```
WeatherDigest #2026-05-04-001
status: EXPIRED → REJECTED
reason: ttl exceeded
```

---

## Escena 9 — Cenital federado (2:50–3:10) ✅ ESTABLE v1.8 — OPCIÓN B FIRME

**Sin VO.** Cadencia Venation completa 5 cartelas asimétricas + pausa tensa + cierre largo. Decisión Bea día 20 (revierte modulación Cambium ella v1.7 → cadencia v1.6 con cierre largo).

### Cartelas progresivas (Manrope, sobre cenital flat editorial 20s)

| Beat | EN (en pantalla) | ES (referencia) | Tiempo |
|------|------------------|-----------------|--------|
| 1 | **"One plot."** | *"Una parcela."* | 2:52–2:53.5 (1.5s) |
| 2 | **"Two."** | *"Dos."* | 2:53.5–2:55 (1.5s) |
| 3 | **"Eight."** | *"Ocho."* | 2:55–2:57.5 (2.5s) |
| (PAUSA TENSA) | (sin texto, Pollen recorre con halos) | — | 2:57.5–2:59 (1.5s) |
| 4 | **"Autonomous."** | *"Autónomas."* | 2:59–3:02 (3s) |
| (transición) | (sin texto) | — | 3:02–3:04 (2s) |
| 5 (cumbre) | **"Federated intelligence, carried by Pollen."** + sello **`SYNCED ✓`** | *"Inteligencia federada, llevada por Pollen."* | 3:04–3:10 (6s sostén) |

### Mensajes técnicos en cenital (durante pausa tensa, IBM Plex Mono — sistema, sin traducción)

5 mensajes apareciendo y desapareciendo en cada toque del Pollen-nodo:

```
WeatherDigest accepted
MissionPatch delivered
DecisionReceipt synced
ValidationStamp issued
Context cached
```

---

## Escena 9b — Meristem recibe + cierre íntimo (3:10–3:20) ✅ ESTABLE v1.8

**Plano íntimo cocina** + portátil casero con UI Meristem + Pollen entregando datos + cutaway opcional macetas reales.

### VO master

| Elemento | EN (master VO) | ES (dub) | Posición / Tiempo |
|----------|----------------|----------|-------------------|
| VO E9b (frase fuerte 6 — ubicada aquí, decisión Bea día 20) | **"Meristem stores and processes. Tomorrow, it will learn."** | *"Meristem guarda y procesa. Mañana, aprenderá."* | Sobre plano de la cocina · 3:18–3:20 (~10 palabras EN) |

### Cartelas y overlays on-screen (inglés)

| Elemento | EN (en pantalla) | ES (referencia) | Posición / Tiempo |
|----------|------------------|-----------------|-------------------|
| Cartela on-screen UI Meristem 1 | **`Pulling Rhizome data...`** | "Descargando datos del Rhizome..." | Pantalla del portátil · 3:10–3:13 (3s, IBM Plex Mono) |
| Cartela on-screen UI Meristem 2 | **`Adjusting policies...`** | "Ajustando políticas..." | Pantalla del portátil · 3:13–3:15 (2s, IBM Plex Mono) |
| Tagline bookend cierre | **"When network is absent — and the human is far — local criteria still irrigate."** | *"Cuando no hay red, y nadie está cerca, el criterio sigue regando."* | Centro · 3:18–3:20 (2s, Manrope sobre fondo difuminado del portátil) |

### Tarjeta logo final (cierre concentrado, 2-3s sostén)

```
Sprout
AI Local-first irrigation decisions.
Safe · explainable · open-source

zigiella · Apache 2.0
github.com/zigiella/sprout

Built on Gemma 4 by Google.
Gemma is a trademark of Google LLC.
```

**Microcartela atribución Gemma trademark confirmada en cierre por Bea día 19** (por reglas hackathon).

---

## Historial

- **v0.7** (2026-05-11, día 26, Corola) — consolidación post-rodaje día 26. Tras 5 días de ausencia operativa de Corola (días 22-25, Bea tiró millas con rodaje + Bract por presión de timing), retomo en día 26: leo snapshot Bract `corola-video-snapshot.md` (master 3:08.5, 3 bloques, voz pro DbwW), respondo 5 preguntas de copy día 26 con voto razonado, formalizo cambios en docs. Cambios estructurales del periodo días 22-26 + 5 votos día 26 documentados en el aviso de lectura al inicio del documento + en el historial v1.8.7 de `script.md`. **Convención day 26: doc estable + fuente viva.** Este `copies_bilingual.md` v0.7 preserva trazabilidad histórica hasta v1.8.3; el snapshot Bract es el copy vivo del video. Cambios consolidados:
  1. **VO master EN definitivo con voz pro ElevenLabs DbwW** (21 MP3, settings 0.7/0.9/0.1/0.9 multilingual_v2). Bea confirmó *"BUAH! queda fetén."*
  2. **Voz humana E5 doblada con DbwW** (no Bea castellano literal). Decisión consciente Bea día 26: *"la mía quedaba fatal."* La excepción narrativa cerrada día 18-19 (voz humana E5 castellano sin traducir) **se retira conscientemente.**
  3. **E8 Caducidad eliminado** del video. Concepto `expiry` comprimido en VO E4b: *"Pollen brings new policies (with expiry) to each Rhizome."* F4 (*"Every intelligence has jurisdiction. And expiry."*) **se mueve a writeup/landing** — recuperable como argumento Safety & Trust del Gemma Hackathon.
  4. **Cenital v1.8 Opción B (cadencia escalonada `One plot. Two. Eight. Autonomous.`) eliminada.** Sustituida por discurso lineal explicativo sobre fondo claro (`soil.oat`, texto oscuro `soil.graphite`): *"It also supports two plots. / And many more plots. / Meristem composes policies. Pollen distributes them. / Pollen turns visits into federated intelligence."* La poesía v1.8 (3-2-2-3 sílabas martilleando) queda para writeup/landing — funciona mejor en texto.
  5. **Vocabulario unificado:** `policy` (regla Meristem, caduca, viaja con Pollen) vs `criteria` (criterio LOCAL del Rhizome). **NO se unifican** — asimetría intencional preservada. Z99 tagline NO se toca.
  6. **5 votos Corola día 26 aplicados:** Z99 con adverbios potentes recuperados (*"Sprout: When network is absent, and the human is far, local criteria still irrigate."*) + cartelas E10 verbos viscerales (`Holds / Carries between plots / Composes`) + refinamientos VO cenital (*"Sprout starts with one plot."* + *"And many more plots."*) + distinción policy/criteria documentada + bilingüe en cartelas: solo EN.
  7. **Cartela `Imagine this pot is a whole plot.` (v1.8.2) dividida en 2 cartelas** para mejor cadencia visual (decisión Bract día ~24).

  Detalle vivo en snapshot Bract. Detalle histórico-narrativo aquí.

- **v0.6** (2026-05-06, día 21, Corola) — cierre decisión Bea Asset 9 E6: ruta principal `Context`, `WeatherDigest` plan B reactivable. Cambio sobre v0.5: sección "Cartelas y overlays on-screen E6" reescrita — ruta principal v1.8.3 = sin meteo (`Context`), plan B reactivable = con meteo (`WeatherDigest`, captura ya producida por Venation, sustitución directa en CapCut). Decisión Bea día 21 cerrada en caliente con Venation: *"no da tiempo a hacer la meteo. Si al final da tiempo, ella ya tiene hecha la captura."* Actualizado estado E6 en tabla resumen + cabecera + sección detalle + carteles físicos (sin estación meteo en plano físico). Origen del cambio en docs (no en producción): Venation entregó lote ya con decisión aplicada, yo (Corola) hice review pidiendo inicialmente que añadiese `WeatherDigest`, Bea aclaró, retiré petición y registro decisión aquí.
- **v0.5** (2026-05-06, día 21, Corola) — recuperación cartela *"Imagine this pot is a whole plot."* al inicio de E2 con misma gráfica que `"Three days later"` (E8). Cambio sobre v0.4: añadida cartela bisagra apertura E2 (Manrope full-screen sobre `soil.graphite`, 0:25–0:28, 3s, sin VO). Función narrativa: bisagra tipográfica entre E1 (datos globales) y E2 (plano técnico) — recupera contrato visual con el espectador (filmamos macetas, hablamos de parcelas) que vivía en E1 v1.6 y se cayó en v1.7. Decisión Bea día 21 tras pregunta retrospectiva sobre v1.6. Actualizada la tabla de Escena 2 + nota explicativa al final de la sección + estado v1.7 → v1.8.2.
- **v0.4** (2026-05-06, día 21, Corola) — refinamiento de cartelas técnicas E2 y E4 por petición de Bea: ampliadas con nodo + dispositivo. E2: `Gemma 4 E2B · local · llama.cpp` → `Rhizome: Jetson Orin Nano · Gemma 4 E2B · local · llama.cpp`. E4: `Gemma 4 E4B · LiteRT-LM · on-device` → `Pollen: Android · Gemma 4 E4B · LiteRT-LM · on-device`. Refuerza jerarquía visible nodo → dispositivo → modelo → runtime y conecta con carteles físicos PLOT_01/02 + RHIZOME_01/02 EDGE NODE.
- **v0.3** (2026-05-05, día 20, Corola) — apilado completo post-v1.8 tras Bea cerrar los 4 abiertos día 20. Añadidas escenas inestables E0, E1, E3b, E8, E9, E9b con copies bilingües completos. Decisiones consolidadas: E8 sobrevive, E9 Opción B firme (20s con cadencia Venation completa + cierre largo *"Federated intelligence, carried by Pollen."* + sello SYNCED ✓), F6 ubicada en E9b. Cartela final E9 revierte de modulación Cambium ella v1.7 (3 beats) a cadencia v1.6 con cierre largo. Tarjeta logo final con microcartela atribución Gemma confirmada en cierre por reglas hackathon.
- **v0.2** (2026-05-05, día 20, Corola) — actualización post-giro estratégico día 18-19 (v1.7 del guion). Cambios: VO master pasa a inglés (era castellano), añadidas escenas E2-E7 con copies bilingües completos, frases fuertes reformuladas (F1, F2, F3, F5 sin cambios), voz humana E5 castellano literal preservada con subtítulo EN entre comillas, contingencia meteo E6 documentada (con/sin), cartela invariante E7 con texto firme. Escenas inestables (E0, E1, E3b, E8, E9, E9b) marcadas TBD-sesión día 20.
- **v0.1** (2026-05-01, día 16, Corola) — primer apilado de copies bilingües tras petición Bea día 16. Escenas 1-3 completas en formato v1.6 (VO castellano). Convenciones documentadas. Excepción única (voz humana E5) anotada.
