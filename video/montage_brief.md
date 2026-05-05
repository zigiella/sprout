# Montage brief para Bract (CapCut) — Sprout vídeo v1.7

**Versión:** v0.1 (esquema parcial sobre v1.7 — escenas estables E2-E7 desarrolladas. Escenas inestables E0/E1/E3b/E8/E9/E9b TBD-sesión día 20.)
**Fecha:** 2026-05-05 (día 20)
**Autora:** Corola
**Para:** Bract (montadora CapCut, lectura repo)
**Formato:** según mensaje Bract en PR #65 / borrador-mensaje-corola-incoherencias_bract.md (el formato que ella pidió en su día).
**Estructura general:** plano · tiempo · origen · VO ES → EN · cartela EN · transición · sfx.

---

## Convenciones del documento

- **Origen** indica de dónde sale el material visual:
  - `rodaje` — filmación real (terraza, cocina, etc.).
  - `screen-jetson` — captura de pantalla del Jetson (Xilema corre el sistema o mock fiel).
  - `screen-pollen` — captura de pantalla del móvil Pollen (Floema corre la app o mock fiel).
  - `screen-meristem` — captura de pantalla del portátil Meristem (Meristem corre la app o mock fiel).
  - `venation-asset` — asset producido por Venation (PNG transparente, animación HTML, lower-third, overlay).
  - `b-roll` — material complementario (tierra agrietada, etc.).
- **VO ES** (entre paréntesis) es la versión castellana de referencia para dub. **VO EN** es la grabación master de Bea.
- **Cartela EN** es lo que aparece en pantalla. ES es referencia interna.
- **Transición** indica cómo entra/sale del plano siguiente (corte seco, fade, morph, etc.).
- **#sfx** marca pistas de sonido que Bract puede usar de su biblioteca o pedir a Bea/Venation.
- **#TBD-sesión** marca elementos pendientes de cierre en sesión conjunta los tres del día 20.

---

## Estado de las escenas en v0.1 del montage_brief

| Escena | Estado | Notas para Bract |
|--------|--------|-------------------|
| **E0** Cartela apertura Sprout | **TBD-sesión** | Diseño cartela cerrado v1.7. Texto pendiente sesión. |
| **E1** La ausencia con datos globales | **TBD-sesión** | Reformulada drásticamente. 4 datos globales + microcorte tierra agrietada + pregunta abierta. Texto definitivo pendiente revisión Cambium ella. |
| **E2** Rhizome decide offline | ✅ **Estable v1.7** | Esquema completo abajo. |
| **E3** ESP32 SAFE LIMIT | ✅ **Estable v1.7** | Esquema completo abajo. |
| **E3b** Meristem prepara | **TBD-sesión** | Nueva en v1.7. Cartela en pantalla pendiente. |
| **E4** Llega Pollen | ✅ **Estable v1.7** | Esquema completo abajo. |
| **E5** La persona da una misión | ✅ **Estable v1.7** | Voz humana castellano literal. UI Pollen pendiente coordinación con Floema. |
| **E6** Ferry A→B | ✅ **Estable v1.7** | Contingencia meteo (con/sin) documentada. |
| **E7** Watering criteria updated (CLIMAX) | ✅ **Estable v1.7** | Esquema completo abajo. |
| **E8** Caducidad | **TBD-sesión** | Pendiente decisión: ¿sobrevive? Si sí, esquema rápido de añadir. |
| **E9** Cenital federado | **TBD-sesión** | Cadencia + duración pendiente sesión + PR #88 a Venation. |
| **E9b** Meristem recibe + cierre | **TBD-sesión** | Nueva. Frase 6 + tagline bookend + tarjeta logo final. |

---

## Escena 2 · 0:25 – 0:50 · Rhizome decide en local ✅ ESTABLE v1.7

**Plano 2A · 0:25–0:29 (4s)** · Plano cerrado del Jetson en su caja con cartel **"PLOT_01 with RHIZOME_01"** + cartel caja **"RHIZOME_01 / EDGE NODE"**. LED en `signal.seed` (#C5F26B) parpadea cuando el sistema decide. Cámara baja al sensor de humedad clavado en la tierra.
- **Origen:** `rodaje` (terraza con Jetson y carteles físicos visibles).
- **VO EN:** ninguno (el VO empieza en plano 2B).
- **VO ES:** ninguno.
- **Overlay EN (todo el bloque):** `OFFLINE` esquina sup. izq.
- **Transición a 2B:** corte seco.
- **#sfx:** ambiente terraza (viento sutil, lejano).

**Plano 2B · 0:29–0:37 (8s)** · Pantalla del Jetson llenando el plano. Fondo `soil.graphite` (#1A1A18). Tipografía IBM Plex Mono. Log diseñado entrando con cadencia musical (1 línea/s). Bloque `SOIL READ` primero, bloque `DECISION` después.
- **Origen:** `screen-jetson` (captura real Xilema, mock fiel si no llega).
- **VO EN:** *"This plot is not alone. It has a local brain. It reads the soil. It decides."* (~14 palabras).
- **VO ES (referencia):** *"Esta parcela no está sola. Tiene un cerebro local. Lee el suelo. Decide."*
- **Cartela EN esquina sup. der.** (3s, ~0:29–0:32): `Gemma 4 E2B · local · llama.cpp` (IBM Plex Mono pequeña).
- **Sub-cartela EN esquina sup. der.** (3s, ~0:32–0:35): `LLM called only when ambiguous` (IBM Plex Mono pequeña).
- **Resaltados en log:** `WATER` y `final_action: 18s` en `signal.seed`. Resto del log en gris claro.
- **Transición a 2C:** dissolve corto.
- **#sfx:** soft-click al aparecer cada línea de log (cadencia 1/s).

**Plano 2C · 0:37–0:43 (6s)** · Captura del `DecisionReceipt` llenando un cuarto de pantalla. Tres campos resaltados (color `signal.seed`): `decision_type: WATER`, `final_action: 18s`, `why_short: "Soil below minimum. Budget available."` Resto del JSON atenuado en gris.
- **Origen:** `screen-jetson` (captura real o mock fiel).
- **VO EN:** *"And signs what it does, so it can be explained."* (~10 palabras).
- **VO ES (referencia):** *"Y firma lo que hace, para que se pueda explicar."*
- **Cartela EN superpuesta** (2s, ~0:41–0:43): `DecisionReceipt` (Manrope editorial, centro/superpuesta sobre el receipt).
- **Transición a 2D:** corte seco al campo.
- **#sfx:** soft-click cuando aparece el receipt.

**Plano 2D · 0:43–0:48 (5s)** · Salida al campo. Plano de la válvula. Se abre. Sonido de agua sobre tierra.
- **Origen:** `rodaje` (válvula real abriéndose).
- **VO EN:** ninguno (silencio sostenido del agua).
- **VO ES:** ninguno.
- **Transición a 2E:** plano sostenido, sin corte.
- **#sfx:** agua cayendo sobre tierra (en directo si las condiciones lo permiten).

**Plano 2E · 0:48–0:50 (2s)** · Plano se mantiene sobre el agua.
- **Origen:** `rodaje` (continuación plano 2D).
- **VO EN (#ancla, frase fuerte 1):** *"Rhizome keeps the plot alive — without a person, without a signal."* (~12 palabras).
- **VO ES (referencia):** *"Rhizome mantiene viva la parcela — sin nadie, sin red."*
- **Sin cartela EN** (deja respirar la frase ancla).
- **Transición a E3:** corte seco.
- **#sfx:** agua continúa, fade out al corte.

---

## Escena 3 · 0:50 – 1:05 · ESP32 SAFE LIMIT ✅ ESTABLE v1.7

**Plano 3A · 0:50–0:53 (3s)** · Corte seco. Plano cerrado de la cajita ESP32 con cartel **"RHIZOME_01 / EDGE NODE"** visible. LED ámbar encendido — atención, no alarma.
- **Origen:** `rodaje` (cajita ESP32 + cartel).
- **VO EN:** ninguno.
- **Cartela EN esquina sup. der.** (3s): `AI proposes / ESP32 validates` (Manrope).
- **Transición a 3B:** corte seco.
- **#sfx:** click electrónico sutil del LED.

**Plano 3B · 0:53–0:58 (5s)** · Pantalla del Jetson. Comando `WATER A 30s` viajando al ESP32. ESP32 verifica: *"deposito al 30%. Caudal nominal."* No bloquea. **Modula**. Devuelve `ACK` con cap aplicado.
- **Origen:** `screen-jetson` (captura real o mock fiel).
- **VO EN (frase fuerte 3 reformulada):** *"AI proposes. Physical safety disposes."* (~6 palabras).
- **VO ES (referencia):** *"La IA propone, la capa física dispone."*
- **Overlay EN esquina sup. der.** (a partir de 0:50, persistente): `ESP32 SAFE LIMIT` (IBM Plex Mono).
- **Transición a 3C:** dissolve corto.
- **#sfx:** soft-click ACK.

**Plano 3C · 0:58–1:01 (3s)** · `DecisionReceipt` post-ejecución llenando un cuadrante. Tres campos resaltados: `candidate_action: 30s`, `esp32_outcome: ACK (limited by tank level)`, `final_action: 12s` en `signal.seed`. La diferencia entre los dos números es donde la prudencia trabaja.
- **Origen:** `screen-jetson` (captura real o mock fiel).
- **VO EN:** ninguno (la cartela central toma el plano).
- **Cartela EN central** (3s, dominante, Manrope sobre el receipt en gris atenuado): **"When in doubt, water less."**
- **Cartela ES (referencia):** *"Cuando duda, riega menos."*
- **Transición a 3D:** corte seco al campo.
- **#sfx:** silencio durante la cartela central.

**Plano 3D · 1:01–1:05 (4s)** · Plano de la válvula. Se abre. **Pero menos tiempo del propuesto.** Chorro corto, calculado.
- **Origen:** `rodaje` (válvula con chorro corto, ~12s en realidad cronometrado vs 18s en E2).
- **VO EN:** ninguno.
- **VO ES:** ninguno.
- **Transición a E3b:** corte seco.
- **#sfx:** agua cayendo (más breve que en E2 — diferencia visible).

---

## Escena 4 · 1:15 – 1:40 · Llega Pollen ✅ ESTABLE v1.7

**Plano 4A · 1:15–1:20 (5s)** · Cambio de luz. Entra una persona en plano. **No vemos su cara** — vemos manos, móvil en la mano, cartel **"PLOT_01 with RHIZOME_01"** visible al fondo. Cartel caja **"RHIZOME_01 / EDGE NODE"**. Plano medio. La persona se acerca a la maceta.
- **Origen:** `rodaje` (persona con móvil acercándose a maceta).
- **VO EN:** ninguno.
- **VO ES:** ninguno.
- **Transición a 4B:** dissolve corto al plano del móvil.
- **#sfx:** ambiente exterior.

**Plano 4B · 1:20–1:25 (5s)** · Pantalla del móvil llenando un tercio del cuadro. App Pollen abierta. La persona pulsa botón. En la pantalla aparece la pregunta.
- **Origen:** `screen-pollen` (captura real Pollen Floema, mock fiel si no llega).
- **VO EN:** ninguno (la cartela en pantalla del móvil hace el trabajo).
- **Cartela EN esquina sup. der.** (3s, IBM Plex Mono): `Gemma 4 E4B · LiteRT-LM · on-device`.
- **Cartela EN en pantalla del móvil** (5s): `What happened since my last visit?`
- **Cartela ES (referencia):** "¿Qué ha pasado desde mi última visita?"
- **Transición a 4C:** la pantalla del móvil cambia (no corte de cámara).
- **#sfx:** click táctil al pulsar botón.

**Plano 4C · 1:25–1:32 (7s)** · Pantalla del móvil cambia: bloque resumen + receipts.
- **Origen:** `screen-pollen` (captura real o mock fiel).
- **VO EN:** ninguno.
- **Cartela EN en pantalla del móvil** (7s): bloque `SINCE LAST VISIT / 2 watering events / 1 skipped decision / 0 blocked actions` + receipts (`WATER · 18s · 14:00`, `WATER · 12s · 09:30`, `SKIP · 22:00 · soil above threshold`).
- **Transición a 4D:** corte a plano de la persona.
- **#sfx:** soft-click sutil al aparecer cada línea de receipts (cadencia rápida).

**Plano 4D · 1:32–1:40 (8s)** · Plano de la persona mirando la planta, contrastando lo que ve con lo que el móvil le dice.
- **Origen:** `rodaje` (persona mirando planta).
- **VO EN (frase fuerte 2 reformulada):** *"Every Pollen visit can change the local criterion."* (~8 palabras).
- **VO ES (referencia):** *"Cada visita de Pollen puede cambiar el criterio local."*
- **Sin cartela EN** (deja respirar la frase ancla).
- **Transición a E5:** corte a plano cercano del móvil.
- **#sfx:** ambiente exterior.

---

## Escena 5 · 1:40 – 2:00 · La persona da una misión ✅ ESTABLE v1.7

**EXCEPCIÓN NARRATIVA: voz humana real Bea castellano literal preservada. Subtítulo EN entre comillas en master.**

**Plano 5A · 1:40–1:43 (3s)** · Plano cercano. La persona pulsa botón de grabación. Acerca el móvil a la cara. **No vemos sus labios** — vemos su mano sosteniendo el móvil. UI del móvil muestra `VOICE NOTE` activo.
- **Origen:** `rodaje` + `screen-pollen` (UI VOICE NOTE).
- **VO EN:** ninguno.
- **Cartela EN en pantalla del móvil:** `VOICE NOTE` activo.
- **Transición a 5B:** plano sostenido.
- **#sfx:** click de grabación.

**Plano 5B · 1:43–1:50 (7s)** · **Voz humana real Bea (castellano, grabada literal)**: *"Vuelvo el viernes. Esta planta aguanta más seca de lo que crees, riega un poco menos."* (14 palabras castellano). Tono calmado, casi casual.
- **Origen:** `rodaje` + audio grabado por Bea (días 24-25).
- **Voz humana ES (literal):** *"Vuelvo el viernes. Esta planta aguanta más seca de lo que crees, riega un poco menos."*
- **Subtítulo EN en master (entre comillas, marca voz humana):** *"I'll be back Friday. This plant takes drier than you think — water it a bit less."*
- **No hay cartela EN** (la voz humana ocupa el plano).
- **Transición a 5C:** plano sostenido sobre el móvil.
- **#sfx:** silencio sobre la voz, sin música.

**Plano 5C · 1:50–1:53 (3s)** · **Procesamiento Pollen en tres estados consecutivos** (Venation): pulso `signal.seed`. Estados visibles en pantalla del móvil (1s cada uno): `listening` → `compiling` → `validating`.
- **Origen:** `screen-pollen` (UI motion procesamiento, mock fiel si captura real no llega).
- **VO EN:** ninguno.
- **Cartela EN en pantalla del móvil** (3s, secuencial 1s cada estado): `listening` → `compiling` → `validating`.
- **Transición a 5D:** la pantalla del móvil cambia.
- **#sfx:** pulso suave (sync con `signal.seed`).

**Plano 5D · 1:53–1:58 (5s)** · **Pantalla del móvil mostrando el `MissionPatch` compilado.** Layout Venation: `VOICE NOTE` con la frase castellana literal + `COMPILED PATCH` debajo con cuatro campos resaltados con `signal.seed`: `horizon_h: 72`, `soil_thresholds.dry: 35 → 25`, `budget_cap_ml: 900`, `operator_note: preserved`.
- **Origen:** `screen-pollen` (UI compilador, **pendiente coordinación con Floema** o mock Venation).
- **VO EN:** ninguno.
- **Cartela EN superpuesta** (2s, Manrope, ~1:55–1:57): `MissionPatch validated`.
- **Transición a 5E:** plano cerrado del móvil.
- **#sfx:** soft-click de validación.

**Plano 5E · 1:58–2:00 (2s)** · Plano cerrado del móvil.
- **Origen:** `rodaje` + `screen-pollen` (continuación 5D).
- **VO EN:** *"What the person says becomes policy."* (~6 palabras).
- **VO ES (referencia):** *"Lo que la persona dice se convierte en política."*
- **Transición a E6:** corte limpio a la persona junto al PLOT_01.
- **#sfx:** ambiente exterior empezando.

---

## Escena 6 · 2:00 – 2:20 · Ferry A→B ✅ ESTABLE v1.7

**Contingencia documentada: con / sin estación meteo.** Las cartelas cambian según ruta.

**Plano 6A · 2:00–2:05 (5s)** · Plano de la persona junto al **PLOT_01** (cartel maceta `PLOT_01 with RHIZOME_01` + cartel caja `RHIZOME_01 / EDGE NODE` + estación meteo conectada al Rhizome 01 si la incluimos). El móvil descarga el `WeatherDigest` (con meteo) o `Context bundle` (sin). Pantalla del móvil: lectura del bundle viajando del Rhizome al teléfono.
- **Origen:** `rodaje` (persona junto a PLOT_01) + `screen-pollen` (UI descarga).
- **VO EN:** *"Pollen brings questions, answers, and context."* (~6 palabras).
- **VO ES (referencia):** *"Pollen trae preguntas, respuestas y contexto."*
- **Cartela EN superpuesta** (2s, Manrope):
  - **Con meteo:** `WeatherDigest ferry`
  - **Sin meteo:** `Context ferry`
- **Transición a 6B:** **corte limpio.** Sin pasos en plano.
- **#sfx:** ambiente exterior + click de descarga.

**Plano 6B · 2:05–2:06 (1s)** · **Corte limpio.**
- **Transición:** corte seco.

**Plano 6C · 2:06–2:14 (8s)** · Plano de la persona junto al **PLOT_02** (cartel maceta `PLOT_02 with RHIZOME_02` + cartel caja `RHIZOME_02 / EDGE NODE`, sin meteo, segunda zona de la terraza, distinta planta). Pollen entrega el bundle al Rhizome 02. Pantalla del móvil: subida. Pantalla del Rhizome 02: aceptación con cita de origen.
- **Origen:** `rodaje` (persona junto a PLOT_02 — rotación del mismo Rhizome físico) + `screen-pollen` (UI subida) + `screen-jetson` (pantalla Rhizome 02 aceptando).
- **VO EN:** ninguno (cartela en pantalla del Rhizome hace el trabajo).
- **Cartela EN en pantalla del Rhizome 02** (4s, IBM Plex Mono):
  - **Con meteo:** `WeatherDigest accepted · Source: rhizome_01`
  - **Sin meteo:** `Context accepted · Source: rhizome_01`
- **Transición a 6D:** plano sostenido del Rhizome 02.
- **#sfx:** click de subida, click de aceptación.

**Plano 6D · 2:14–2:17 (3s)** · Silencio breve. Plano del Rhizome 02 con bundle aceptado. La cámara respira.
- **Origen:** `rodaje` (Rhizome 02 con bundle).
- **VO EN:** ninguno.
- **Transición a 6E:** plano sostenido.
- **#sfx:** ambiente exterior.

**Plano 6E · 2:17–2:20 (3s)** · Sentencia plana.
- **Origen:** `rodaje` (continuación 6D).
- **VO EN (frase fuerte 5):** *"Pollen turns those visits into federated intelligence."* (~8 palabras).
- **VO ES (referencia):** *"Pollen convierte esas visitas en inteligencia federada."*
- **Transición a E7:** corte a pantalla del Jetson.
- **#sfx:** ambiente que se desvanece.

**Eco interno F2↔F5:** *"those visits"* (E6) hace eco directo a *"every Pollen visit"* (E4). Coherencia narrativa.

---

## Escena 7 · 2:20 – 2:40 · Watering criteria updated ✅ ESTABLE v1.7 — CLIMAX

**Plano 7A · 2:20–2:23 (3s)** · Pantalla del Jetson llenando el plano. Fondo `soil.graphite`. **Bloque 1** entra: `MISSION PATCH ACCEPTED` con `id: mp_004` y `ttl: 21600s`. Cadencia musical (1 línea/s).
- **Origen:** `screen-jetson` (captura real o mock fiel).
- **VO EN:** ninguno.
- **Transición a 7B:** plano sostenido sobre la pantalla.
- **#sfx:** soft-click al aparecer cada línea.

**Plano 7B · 2:23–2:26 (3s)** · **Bloque 2** entra: `POLICY DIFF` con dos campos resaltados (color `signal.seed`): `soil_thresholds.dry: 35 → 25`, `daily_budget_ml: 1500 → 900`. Cartela esquina inferior derecha entra (4 líneas, IBM Plex Mono pequeña, paleta sobria).
- **Origen:** `screen-jetson` + `venation-asset` (cartela esquina invariante).
- **VO EN:** ninguno.
- **Cartela EN esquina inferior derecha** (5s, IBM Plex Mono pequeña, ~2:24–2:29):
  ```
  Physical layer prevails.
  Rhizome arbitrates.
  Pollen mediates.
  Meristem refines.
  ```
- **Transición a 7C:** plano sostenido.
- **#sfx:** soft-click al aparecer cada línea del bloque.

**Plano 7C · 2:26–2:29 (3s)** · **Bloque 3** entra: `NEXT DECISION CHANGED` con `policy_id: pol_009 → pol_010`, `final_action: 12s`, `why_short: "Mission compiled from human voice"`. La cartela esquina invariante sigue visible.
- **Origen:** `screen-jetson` (captura real o mock fiel).
- **VO EN:** ninguno.
- **Transición a 7D:** la cartela esquina se desvanece + entra cartela ancla central.
- **#sfx:** soft-click.

**Plano 7D · 2:29–2:32 (3s)** · Cartela ancla central dominante. Los tres bloques quedan al fondo en gris atenuado. La cartela esquina **se desvanece a 2:29** cuando entra la ancla — no compiten.
- **Origen:** `screen-jetson` + `venation-asset` (cartela ancla central).
- **VO EN:** ninguno.
- **Cartela EN central** (3s, Manrope dominante): **"Watering criteria updated."**
- **Cartela ES (referencia):** *"Criterios de riego actualizados."*
- **Transición a 7E:** corte a campo.
- **#sfx:** silencio durante la cartela.

**Plano 7E · 2:32–2:40 (8s)** · Salida al campo. Plano de la maceta y la válvula. Se abre. **Pero menos tiempo que en escena 2** — chorro corto, controlado, austero (12s real cronometrado vs 18s en E2).
- **Origen:** `rodaje` (válvula con chorro corto).
- **VO EN:** *"The system updates its care."* (~5 palabras).
- **VO ES (referencia):** *"El sistema ajusta los cuidados."*
- **Transición a E8:** corte seco.
- **#sfx:** agua cayendo (claramente más breve que en E2 — diferencia es la prueba narrativa).

---

## TBD-sesión día 20 — escenas inestables (esquema rápido cuando sesión cierre)

Las siguientes escenas tienen elementos pendientes de cierre:

- **E0 Cartela apertura Sprout** (5s) — diseño cerrado v1.7. Texto pendiente sesión.
- **E1 La ausencia con datos globales** (20s) — reformulada drásticamente. 4 datos UNCCD/OECD/FAO/ITU + microcorte 0.5s tierra agrietada (Venation pendiente confirmar B-roll producible) + pregunta abierta.
- **E3b Meristem prepara** (10s) — nueva. Plano cocina + portátil + Pollen (móvil). Coordinación pendiente con Meristem para UI.
- **E8 Caducidad** (10s) — pendiente decisión: ¿sobrevive? Si sí, esquema rápido (cartela `Three days later` + log `expired → rejected` + frase fuerte 4).
- **E9 Cenital federado** (10s o 20s pendiente sesión) — animación HTML + secuencia PNG transparente de Venation (PR #88). Cadencia cartela final pendiente sesión.
- **E9b Meristem recibe + cierre íntimo** (10s) — nueva. Plano cocina + portátil + Pollen entregando + cutaway opcional macetas reales + frase fuerte 6 + tagline bookend cierre + tarjeta logo final con microcartela atribución Gemma.

**Tras sesión, completar v0.2** con todas las escenas + revisión final de transiciones.

---

## Notas operativas para Bract

### Carteles físicos (todos los rodajes)

Bea los prepara antes del rodaje:
- 2 carteles maceta: `PLOT_01 with RHIZOME_01`, `PLOT_02 with RHIZOME_02`.
- 2 carteles caja electrónica: `RHIZOME_01 / EDGE NODE`, `RHIZOME_02 / EDGE NODE` (intercambiables sobre la cajita Jetson+ESP32 entre tomas).
- Tipografía Manrope SemiBold + IBM Plex Mono micro-IDs. Paleta `soil.oat` o kraft mate. Acabado mate.

### Decisión de rodaje — un solo Rhizome físico haciendo dos roles lógicos

Las dos parcelas (PLOT_01 con meteo, PLOT_02 sin meteo) se filman con **un solo Rhizome físico**. Cambio entre tomas:
- Cambio de ángulo de cámara.
- Cambio de planta (visualmente distinguibles).
- Cambio de zona de la terraza (fondo distinto).
- Cambio de cartel físico (`RHIZOME_01` ↔ `RHIZOME_02`).
- Conexión/desconexión de estación meteo.

Honesto con el MVP: simula la federación tal como ocurriría en una explotación que empezó con un nodo y añadió otro más adelante.

### Voz humana E5 — grabación previa al rodaje

Bea graba la frase castellana literal (*"Vuelvo el viernes. Esta planta aguanta más seca de lo que crees, riega un poco menos."*) en días 24-25 antes del rodaje principal. Subtítulo EN en master entre comillas marca que es voz humana (no VO).

### Master de exportación

- **Resolución master:** 1920×1080 (decisión Bract).
- **Formato cenital E9:** MP4 H.264 (Bract codifica con ffmpeg sobre los 480 PNG transparentes de Venation).
- **Naming:** snake_case (decisión Bract).
- **Punto de entrega:** `video/final/` (definitivos) + `video/wip/` (intermedios).

### Pendientes coordinación cross-frente

- **Floema:** UI compilador `MissionPatch` E5 (captura real Pollen preferida, mock Venation alternativo).
- **Xilema:** capturas de pantalla Jetson E2/E3/E7 (real preferida o mock fiel del log diseñado).
- **Meristem:** UI Meristem E3b/E9b (real preferida o mock fiel).
- **Venation:** cenital E9 animado (PR #88, esperando decisión cadencia post-sesión) + 4 PNG transparentes E1/E2/Z99 (PR #75 en main) + posible regeneración 2 PNG tras sesión.

---

## Historial

- **v0.1** (2026-05-05, día 20, Corola) — primer apilado del montage_brief en formato Bract (CapCut). Escenas estables E2-E7 desarrolladas plano-por-plano con tiempo, origen, VO EN/ES, cartelas, transiciones y sfx. Escenas inestables E0/E1/E3b/E8/E9/E9b marcadas TBD-sesión día 20. Notas operativas para Bract sobre carteles físicos, decisión de rodaje un Rhizome dos roles, voz humana E5, master de exportación, pendientes coordinación cross-frente.
