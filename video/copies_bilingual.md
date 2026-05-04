# Copies bilingües del vídeo Sprout — ES / EN

**Versión:** v0.1 (apilado parcial — escenas 1-3 completas. Escenas 4-9 pendientes)
**Fecha:** 2026-05-01 (día 16)
**Autora:** Corola
**Origen:** decisión Bea día 16 — "Necesitaré tener siempre los copies del video (textos VO, voz en off, cartelas, etc en ES y EN)."

---

## Convenciones

- **VO** (voice-over) — castellano grabado por Bea. La columna EN es referencia para subtítulos / doblaje EN si procede.
- **Cartelas y overlays on-screen** — inglés en pantalla. La columna ES es referencia interna para conversaciones del equipo.
- **Cartel físico** — inglés en plano (decisión Bea día 16).
- **Voz humana real escena 5 (`operator_note`)** — castellano literal, **no se traduce** ni en pantalla ni en doblaje. Es la única excepción a la regla de bilingüismo: se respeta como voz humana auténtica.

---

## Escena 1 — La ausencia (0:00–0:20)

**Sin VO.** Cero palabras habladas. Apertura silenciosa.

| Elemento | ES (referencia) | EN (en pantalla) | Posición / Tiempo |
|----------|-----------------|------------------|-------------------|
| Cartela 1 | "Imagina que esta maceta es una parcela entera." | **"Imagine this pot is a whole plot."** | Centro · 0:06–0:11 (5s) |
| Cartela 2 | "Esta parcela tiene visita humana cada cierto tiempo." | **"This plot is visited periodically by a human."** | Centro · 0:11–0:16 (5s) |
| Cartel físico maceta | "Parcela 01 con Rhizoma 01" | **"PLOT_01 with RHIZOME_01"** | En la maceta · todo el plano |
| Cartel físico caja electrónica | "Rhizoma 01" | **"RHIZOME_01"** | En la cajita Jetson+ESP32 (visible cuando se filme detalle del Rhizome en escenas 2-3) |

---

## Escena 2 — Rhizome decide offline (0:20–0:45)

| Elemento | ES (grabación VO) | EN (referencia) | Posición / Tiempo |
|----------|-------------------|-----------------|-------------------|
| VO 2A | "Esta parcela no está sola. Tiene un cerebro local. Lee el suelo. Decide." | "This plot is not alone. It has a local brain. It reads the soil. It decides." | Sobre el log del Jetson · 0:24–0:32 (13 palabras ES) |
| VO 2B | "Y firma lo que hace, para que se pueda explicar." | "And signs what it does, so it can be explained." | Sobre el `DecisionReceipt` · 0:32–0:38 (10 palabras ES) |
| VO 2C (frase fuerte 1) | **"Rhizome mantiene viva la parcela cuando nadie está."** | "Rhizome keeps the plot alive when no one is there." | Sobre el agua de la válvula · 0:43–0:45 (8 palabras ES) |

| Elemento | ES (referencia) | EN (en pantalla) | Posición / Tiempo |
|----------|-----------------|------------------|-------------------|
| Overlay `OFFLINE` | "SIN RED" | **`OFFLINE`** | Esquina sup. izq. · persistente todo el bloque (0:20–0:45) |
| Stack cartela técnica 1 | "Gemma 4 E2B · local · llama.cpp" | **`Gemma 4 E2B · local · llama.cpp`** | Esquina sup. der. · ~0:24–0:27 (3s) |
| Sub-cartela técnica | "LLM solo en casos ambiguos" | **`LLM called only when ambiguous`** | Esquina sup. der. · ~0:27–0:30 (3s, tras la stack) |
| Cartela `DecisionReceipt` | "Recibo de decisión" | **`DecisionReceipt`** | Centro/superpuesta · 0:36–0:38 (2s) |

---

## Escena 3 — ESP32 SAFE LIMIT (0:45–1:00)

| Elemento | ES (grabación VO) | EN (referencia) | Posición / Tiempo |
|----------|-------------------|-----------------|-------------------|
| VO 3 (frase fuerte 3) | **"La IA propone. El agua la gobierna una capa física prudente."** | "AI proposes. Water is governed by a prudent physical layer." | Sobre el ESP32 modulando · 0:48–0:53 (11 palabras ES) |

| Elemento | ES (referencia) | EN (en pantalla) | Posición / Tiempo |
|----------|-----------------|------------------|-------------------|
| Cartela técnica esquina | "tools de lectura/función · sin tools de actuador" | **`function/read tools · no actuator tools`** | Esquina sup. der. · 0:45–0:48 (3s) |
| Overlay `ESP32 SAFE LIMIT` | "Límite seguro del ESP32" | **`ESP32 SAFE LIMIT`** | Esquina sup. der. · entrada a 0:48, persistente |
| Cartela ancla central | "Cuando duda, riega menos." | **"When in doubt, water less."** | Centro dominante · 0:53–0:56 (3s) — sobre el `DecisionReceipt` atenuado |

---

## Pendiente

Escenas 4-9 a apilar en este documento. Plan:
- Día 16 cierre / día 17 mañana: escenas 4, 5, 6.
- Día 17 / día 18: escenas 7, 8, 9 + revisión final ES↔EN.

**Nota voz humana escena 5:** la frase de la persona — *"Vuelvo el viernes. Esta planta aguanta más seca de lo que crees, riega un poco menos."* — se graba en castellano literal por Bea y **no se traduce al inglés en pantalla**. Es la única excepción a la regla de bilingüismo del documento.

---

## Historial

- **v0.1** (2026-05-01, día 16, Corola) — primer apilado de copies bilingües tras petición Bea día 16. Escenas 1-3 completas. Convenciones documentadas. Excepción única (voz humana E5) anotada.
