# Montage brief para Bract (CapCut) — Sprout vídeo v1.8

**Versión:** v0.4 (recuperación cartela *"Imagine this pot is a whole plot."* al inicio de E2 con gráfica "Three days later", día 21 — apilado completo de las 12 escenas v1.8.2)
**Fecha:** 2026-05-06 (día 21)
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

## Estado de las escenas en v0.2 del montage_brief (post-v1.8)

| Escena | Estado | Notas para Bract |
|--------|--------|-------------------|
| **E0** Cartela apertura Sprout | ✅ **Estable v1.8** | Wordmark + lema + open-source. Detalle abajo. |
| **E1** La ausencia con datos globales | ✅ **Estable v1.8** | 4 datos UNCCD/OECD/FAO/ITU + microcorte tierra agrietada + pregunta abierta. Detalle abajo. |
| **E2** Rhizome decide offline | ✅ **Estable v1.8.2** | Esquema completo abajo. **Cartela bisagra apertura nueva** (*"Imagine this pot is a whole plot."* full-screen estilo "Three days later", 0:25–0:28). |
| **E3** ESP32 SAFE LIMIT | ✅ **Estable v1.7** | Esquema completo abajo. |
| **E3b** Meristem prepara | ✅ **Estable v1.8** | Plano cocina + portátil + Pollen recibe política. VO Extra E3b. Detalle abajo. |
| **E4** Llega Pollen | ✅ **Estable v1.7** | Esquema completo abajo. |
| **E5** La persona da una misión | ✅ **Estable v1.7** | Voz humana castellano literal. UI Pollen pendiente coordinación con Floema. |
| **E6** Ferry A→B | ✅ **Estable v1.7** | Contingencia meteo (con/sin) documentada. |
| **E7** Watering criteria updated (CLIMAX) | ✅ **Estable v1.7** | Esquema completo abajo. |
| **E8** Caducidad | ✅ **Estable v1.8 — NO se mata** | Decisión Bea día 20. F4 + plano `expired → rejected`. Detalle abajo. |
| **E9** Cenital federado | ✅ **Estable v1.8 — Opción B firme** | 20s con cadencia Venation completa. Detalle abajo. |
| **E9b** Meristem recibe + cierre | ✅ **Estable v1.8** | Plano íntimo cocina + F6 + tagline bookend + tarjeta logo final. Detalle abajo. |

---

## Escena 2 · 0:25 – 0:50 · Rhizome decide en local ✅ ESTABLE v1.8.2

**Plano 2A-pre · 0:25–0:28 (3s)** · **Cartela bisagra full-screen tipográfica** sobre fondo casi-negro `soil.graphite` (#1A1A18). Texto centrado en Manrope titular `soil.oat`. **Misma gráfica que `"Three days later"` (E8)** — sin plano físico debajo, sin VO.
- **Origen:** `venation-asset` (cartela tipográfica producida por Venation, idéntico tratamiento gráfico que cartela `"Three days later"` E8).
- **VO EN:** ninguno (cartela respiratoria sin VO).
- **VO ES:** ninguno.
- **Cartela EN central full-screen** (3s, Manrope titular, fondo `soil.graphite`): *"Imagine this pot is a whole plot."*
- **Cartela ES (referencia interna):** *"Imagina que esta maceta es una parcela entera."*
- **Función narrativa:** bisagra tipográfica entre E1 (cartelas datos globales sobre `soil.graphite`) y E2 (plano físico del Rhizome). Equivalente a `"Three days later"` en E8 — misma jerarquía visual, mismo lenguaje. Recupera contrato visual con el espectador (filmamos macetas, hablamos de parcelas) que vivía en E1 v1.6 y se cayó en v1.7. Decisión Bea día 21.
- **Transición a 2A:** fade rápido al plano del Jetson, ~0.3s.
- **#sfx:** silencio respiratorio (el espectador procesa el contrato visual).

**Plano 2A · 0:28–0:29 (1s)** · Plano cerrado del Jetson en su caja con cartel **"PLOT_01 with RHIZOME_01"** + cartel caja **"RHIZOME_01 / EDGE NODE"**. LED en `signal.seed` (#C5F26B) parpadea cuando el sistema decide. Cámara baja al sensor de humedad clavado en la tierra. (Antes 4s en v1.8.1; recortado a 1s en v1.8.2 para acomodar cartela bisagra 2A-pre y mantener E2 a 25s totales.)
- **Origen:** `rodaje` (terraza con Jetson y carteles físicos visibles).
- **VO EN:** ninguno (el VO empieza en plano 2B).
- **VO ES:** ninguno.
- **Overlay EN (entra a 0:28, persistente resto del bloque hasta 0:50):** `OFFLINE` esquina sup. izq.
- **Transición a 2B:** corte seco.
- **#sfx:** ambiente terraza (viento sutil, lejano).

**Plano 2B · 0:29–0:37 (8s)** · Pantalla del Jetson llenando el plano. Fondo `soil.graphite` (#1A1A18). Tipografía IBM Plex Mono. Log diseñado entrando con cadencia musical (1 línea/s). Bloque `SOIL READ` primero, bloque `DECISION` después.
- **Origen:** `screen-jetson` (captura real Xilema, mock fiel si no llega).
- **VO EN:** *"This plot is not alone. It has a local brain. It reads the soil. It decides."* (~14 palabras).
- **VO ES (referencia):** *"Esta parcela no está sola. Tiene un cerebro local. Lee el suelo. Decide."*
- **Cartela EN esquina sup. der.** (3s, ~0:29–0:32): `Rhizome: Jetson Orin Nano · Gemma 4 E2B · local · llama.cpp` (IBM Plex Mono pequeña).
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
- **Cartela EN esquina sup. der.** (3s, IBM Plex Mono): `Pollen: Android · Gemma 4 E4B · LiteRT-LM · on-device`.
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

## Escena 0 · 0:00 – 0:05 · Cartela apertura Sprout ✅ ESTABLE v1.8

**Plano 0A · 0:00–0:05 (5s)** · Fondo casi-negro (`soil.graphite` o más oscuro). Cartela centrada compuesta: wordmark `Sprout` + subtítulo + línea inferior "Safe · explainable · open-source". Entrada con stagger 120ms (kicker → wordmark → tag). Sostén ~3.5s. Salida fade 0.4s al negro.
- **Origen:** `venation-asset` (cartela apertura compuesta).
- **VO EN:** ninguno.
- **VO ES:** ninguno.
- **Cartela EN central:** `Sprout` (Manrope titular grande, `soil.oat` sobre `soil.graphite`) + **"AI Local-first irrigation decisions."** (Manrope mediano) + **"Safe · explainable · open-source."** (Manrope pequeña).
- **Microcartela atribución Gemma NO va aquí** (decisión Bea día 19 — va en cierre concentrado).
- **Transición a E1:** fade al negro.
- **#sfx:** silencio sostenido o ambiente muy sutil.

---

## Escena 1 · 0:05 – 0:25 · La ausencia con datos globales ✅ ESTABLE v1.8

**Sin VO.** Opener tipográfico con 4 datos globales + microcorte 0.5s tierra agrietada + pregunta abierta. Cataluña como ejemplo del patrón global.

**Plano 1A · 0:05–0:09 (4s)** · Dato 1 sobre fondo casi-negro.
- **Origen:** `venation-asset` (cartela tipográfica).
- **VO EN:** ninguno.
- **Cartela EN:** **"In 2023, 48% of the world's land area suffered at least one month of extreme drought."** + microcita pequeña `[UNCCD World Drought Atlas]` (IBM Plex Mono `soil.ash`).
- **Transición a 1B:** fade out + fade in.
- **#sfx:** silencio o ambiente muy sutil.

**Plano 1B · 0:09–0:13 (4s)** · Dato 2 sobre fondo casi-negro.
- **Origen:** `venation-asset` (cartela tipográfica).
- **VO EN:** ninguno.
- **Cartela EN:** **"1.8 billion people affected. $300 billion per year in losses."** + microcita pequeña `[UNCCD]`.
- **Transición a 1C:** **microcorte seco** (sin fade).
- **#sfx:** silencio.

**Plano 1C · 0:13–0:13.5 (0.5s)** · **Microcorte tierra agrietada.** Bisagra emocional macro→concreto.
- **Origen:** `b-roll` (tierra real agrietada). **Pendiente confirmar producible con Venation o se descarta.**
- **VO EN:** ninguno.
- **Sin cartela.**
- **Transición a 1D:** corte limpio.
- **#sfx:** silencio (o sonido sutil de tierra crujiendo).

**Plano 1D · 0:13.5–0:17.5 (4s)** · Dato 3 (Cataluña) sobre fondo casi-negro.
- **Origen:** `venation-asset`.
- **Cartela EN:** **"In Catalonia 2024, agriculture cut water for irrigation by 80%."** + microcita pequeña `[Generalitat de Catalunya]`.
- **Transición a 1E:** fade out + fade in.
- **#sfx:** silencio.

**Plano 1E · 0:17.5–0:21.5 (4s)** · Dato 4 (ITU — bisagra con conectividad) sobre fondo casi-negro.
- **Origen:** `venation-asset`.
- **Cartela EN:** **"58% of the rural population uses internet. In low-income countries: only 14%."** + microcita pequeña `[ITU 2025]`.
- **Transición a 1F:** fade out a negro.
- **#sfx:** silencio.

**Plano 1F · 0:21.5–0:25 (3.5s)** · **Pregunta abierta** centro grande.
- **Origen:** `venation-asset` (cartela tipográfica grande).
- **Cartela EN:** **"When network is absent — and the human is far — what makes the right call?"** (Manrope grande, `soil.oat` sobre `soil.graphite`).
- **Transición a E2:** corte seco a la cajita Jetson.
- **#sfx:** silencio sostenido sobre la pregunta.

---

## Escena 3b · 1:05 – 1:15 · Meristem prepara la política ✅ ESTABLE v1.8

**Plano 3bA · 1:05–1:08 (3s)** · Plano cocina (continuidad visual con E9b — bookend doméstico). Bea de espaldas o en perfil borroso (no vemos cara, agnóstico al portador). Portátil casero abierto sobre mesa.
- **Origen:** `rodaje` (cocina doméstica).
- **VO EN:** ninguno.
- **Sin cartela.**
- **Transición a 3bB:** plano sostenido, detalle a pantalla.
- **#sfx:** ambiente cocina sutil.

**Plano 3bB · 1:08–1:12 (4s)** · Detalle pantalla del portátil. UI Meristem componiendo política. `signal.seed` activo en momento clave.
- **Origen:** `screen-meristem` (UI real Meristem preferida o mock fiel basado en `docs/12_meristem_spec.md`).
- **VO EN:** ninguno.
- **Sin cartela on-screen** (la UI Meristem en pantalla del portátil habla por sí sola).
- **Transición a 3bC:** plano sobre la mesa.
- **#sfx:** click suave de teclado o procesamiento.

**Plano 3bC · 1:12–1:15 (3s)** · Plano sobre la mesa: Pollen (móvil) recibe la política de Meristem. Posible animación de transferencia o conexión visual entre los dos dispositivos.
- **Origen:** `rodaje` + `screen-pollen` (transferencia visible en pantalla del móvil).
- **VO EN (Extra E3b — cerrada Bea día 19):** *"Meristem composes the policy."* (~5 palabras).
- **VO ES (referencia):** *"Meristem compone la política."*
- **Cartela EN superpuesta** (2-3s, Manrope): `Meristem composes.` o `Policy composed.` (eligir una).
- **Transición a E4:** corte limpio a persona en plano.
- **#sfx:** click de transferencia.

---

## Escena 8 · 2:40 – 2:50 · Caducidad ✅ ESTABLE v1.8 — NO SE MATA

**Plano 8A · 2:40–2:42 (2s)** · Cartela limpia salto temporal sobre fondo casi-negro.
- **Origen:** `venation-asset` (cartela compuesta).
- **VO EN:** ninguno.
- **Cartela EN central:** **"Three days later"** (Manrope sobre fondo casi-negro).
- **Transición a 8B:** corte seco a pantalla del Jetson.
- **#sfx:** silencio.

**Plano 8B · 2:42–2:46 (4s)** · Pantalla del Jetson. El `WeatherDigest` que Pollen entregó en E6 ha llegado a su `valid_until`. El sistema lo evalúa y rechaza. Tres líneas en pantalla.
- **Origen:** `screen-jetson` (captura real o mock fiel).
- **VO EN:** ninguno.
- **Cartela EN superpuesta** (2s, IBM Plex Mono con borde doble `status.blocked`): `expired → rejected`.
- **Log diseñado en pantalla:**
  ```
  WeatherDigest #2026-05-04-001
  status: EXPIRED → REJECTED
  reason: ttl exceeded
  ```
- **Transición a 8C:** plano sostenido sobre el rechazo.
- **#sfx:** sello seco al rechazo (sin glitch).

**Plano 8C · 2:46–2:50 (4s)** · Plano sostenido sobre la pantalla del rechazo.
- **Origen:** `screen-jetson` (continuación 8B).
- **VO EN (frase fuerte 4 — cerrada Bea día 19):** *"Every intelligence has jurisdiction. And expiry."* (~7 palabras).
- **VO ES (referencia):** *"Toda inteligencia tiene jurisdicción. Y caducidad."*
- **Sin cartela adicional** (deja respirar la frase).
- **Transición a E9:** corte limpio + morph a parcela flat.
- **#sfx:** silencio sobre la frase.

---

## Escena 9 · 2:50 – 3:10 · Cenital federado ✅ ESTABLE v1.8 — OPCIÓN B FIRME (20s)

**Sin VO.** Cadencia Venation completa: 5 cartelas asimétricas + pausa tensa + cierre largo + sello SYNCED ✓.

**Plano 9A · 2:50–2:52 (2s)** · **Morph maceta real → parcela flat.** La maceta de la última toma se difumina, los bordes se expanden, aparece la primera parcela flat.
- **Origen:** `rodaje` + `venation-asset` (animación HTML del cenital con morph inicial).
- **VO EN:** ninguno.
- **Sin cartela.**
- **Transición a 9B:** continuidad de la animación Venation.
- **#sfx:** transición sutil.

**Plano 9B · 2:52–2:53.5 (1.5s)** · Pollen-nodo aparece como punto luminoso `signal.seed`. Cartela progresiva 1.
- **Origen:** `venation-asset` (animación cenital).
- **VO EN:** ninguno.
- **Cartela progresiva 1** (Manrope): **"One plot."**
- **Transición a 9C:** continuidad animación.
- **#sfx:** silencio.

**Plano 9C · 2:53.5–2:55 (1.5s)** · Segunda parcela aparece sincronizada con cartela 2.
- **Origen:** `venation-asset`.
- **Cartela progresiva 2** (Manrope): **"Two."**
- **Transición a 9D:** continuidad.

**Plano 9D · 2:55–2:57.5 (2.5s)** · Resto de parcelas aparecen progresivamente hasta completar las 8.
- **Origen:** `venation-asset`.
- **Cartela progresiva 3** (Manrope): **"Eight."**
- **Transición a 9E:** PAUSA TENSA narrativa.

**Plano 9E · 2:57.5–2:59 (1.5s)** · **PAUSA TENSA NARRATIVA.** Pollen-nodo recorre las parcelas con halos progresivos encendiéndose en cada toque (modo B1 cascada). Mensajes técnicos breves apareciendo.
- **Origen:** `venation-asset`.
- **Sin cartela progresiva.**
- **Mensajes técnicos en pantalla** (IBM Plex Mono integrado en diseño flat, apareciendo y desapareciendo en cada toque del nodo): `WeatherDigest accepted`, `MissionPatch delivered`, `DecisionReceipt synced`, `ValidationStamp issued`, `Context cached`.
- **Transición a 9F:** continuidad.
- **#sfx:** click suave en cada toque del nodo.

**Plano 9F · 2:59–3:02 (3s)** · Pollen-nodo llega al nodo Meristem (disco mayor azul desaturado o grafito claro). Cartela progresiva 4.
- **Origen:** `venation-asset`.
- **Cartela progresiva 4** (Manrope): **"Autonomous."**
- **Transición a 9G:** continuidad.

**Plano 9G · 3:02–3:04 (2s)** · Transición a cartela cumbre.
- **Origen:** `venation-asset`.
- **Sin cartela visible.**
- **Transición a 9H:** entrada cartela cumbre.

**Plano 9H · 3:04–3:10 (6s sostén)** · **Cartela cumbre** + sello SYNCED ✓.
- **Origen:** `venation-asset`.
- **Cartela progresiva 5 cumbre** (Manrope, sostén 6s): **"Federated intelligence, carried by Pollen."** + sello **`SYNCED ✓`**.
- **Transición a E9b:** corte seco a imagen real cocina.
- **#sfx:** silencio sostenido sobre la cartela final.

**Notas Bract:** la animación Venation viene como secuencia PNG transparente (480 frames a 24fps a 1920×1080). Bract codifica MP4 con ffmpeg sobre los PNG. Si en montaje final se decide compresión a 10s, recortar pausa tensa + sostén final largo (manteniendo cartelas 1-4 + cumbre).

---

## Escena 9b · 3:10 – 3:20 · Meristem recibe + cierre íntimo ✅ ESTABLE v1.8

**Bookend con E3b.** La política sale de casa al campo (E3b) → campo decide (E2-E8) → datos vuelven a casa (E9b).

**Plano 9bA · 3:10–3:13 (3s)** · Plano cocina (continuidad visual con E3b). Bea de espaldas o en perfil borroso. Portátil casero abierto. Pollen (móvil) sobre la mesa entregando datos al portátil.
- **Origen:** `rodaje` (cocina doméstica) + `screen-meristem`.
- **VO EN:** ninguno.
- **Cartela EN on-screen** (3s, IBM Plex Mono en pantalla del portátil): `Pulling Rhizome data...`
- **Transición a 9bB:** plano sostenido, pantalla cambia.
- **#sfx:** ambiente cocina sutil + click suave de transferencia.

**Plano 9bB · 3:13–3:16 (3s)** · Pantalla del portátil cambia. UI Meristem procesando. `signal.seed` activo.
- **Origen:** `screen-meristem`.
- **VO EN:** ninguno.
- **Cartela EN on-screen** (2s, IBM Plex Mono): `Adjusting policies...`
- **Transición a 9bC:** opcional cutaway.

**Plano 9bC · 3:16–3:18 (2s)** · **Cutaway opcional** micro a las macetas reales en la terraza (Sprout escala 1 corriendo en la terraza de Bea en Castellar). Si no se rueda, plano cocina sigue.
- **Origen:** `rodaje` (macetas reales en terraza). **Decisión Bea día 19: posible, no asegurado.**
- **VO EN:** ninguno.
- **Sin cartela.**
- **Transición a 9bD:** corte de vuelta a la cocina.
- **#sfx:** ambiente exterior breve si se rueda.

**Plano 9bD · 3:18–3:20 (2s)** · Vuelta a la cocina.
- **Origen:** `rodaje` (cocina, continuación 9bB).
- **VO EN (frase fuerte 6 — ubicada aquí, decisión Bea día 20):** *"Meristem stores and processes. Tomorrow, it will learn."* (~10 palabras).
- **VO ES (referencia):** *"Meristem guarda y procesa. Mañana, aprenderá."*
- **Tagline bookend cierre** entra por fade sobre la pantalla difuminada del portátil al final del plano.
- **Cartela EN tagline bookend** (Manrope, sostén 2s): **"When network is absent — and the human is far — local criteria still irrigate."**
- **Transición a tarjeta logo final:** fade.
- **#sfx:** silencio sobre la frase 6 + tagline.

**Plano 9bE · ~3:20+ (2-3s sostén)** · Tarjeta logo final.
- **Origen:** `venation-asset` (tarjeta logo compuesta).
- **VO EN:** ninguno.
- **Tarjeta logo final:**
  ```
  Sprout
  AI Local-first irrigation decisions.
  Safe · explainable · open-source

  zigiella · Apache 2.0
  github.com/zigiella/sprout

  Built on Gemma 4 by Google.
  Gemma is a trademark of Google LLC.
  ```
- **Transición:** fade out final.
- **#sfx:** silencio sostenido.

**Microcartela atribución Gemma trademark CONFIRMADA en cierre** (Bea día 19, por reglas hackathon).

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

- **v0.4** (2026-05-06, día 21, Corola) — recuperación cartela *"Imagine this pot is a whole plot."* al inicio de E2 con misma gráfica que `"Three days later"` (E8). Cambio sobre v0.3: split del Plano 2A (4s) en Plano 2A-pre (3s, cartela full-screen tipográfica) + Plano 2A (1s, plano del Jetson). E2 mantiene 25s totales. Función narrativa: bisagra tipográfica entre E1 (datos globales) y E2 (plano técnico) — equivalente visual a `"Three days later"` en E8. Recupera contrato visual con el espectador (filmamos macetas, hablamos de parcelas) que vivía en E1 v1.6 y se cayó en v1.7. Decisión Bea día 21 tras pregunta retrospectiva sobre v1.6.
- **v0.3** (2026-05-06, día 21, Corola) — refinamiento de cartelas técnicas E2 y E4 por petición de Bea: ampliadas con nodo + dispositivo. E2: `Gemma 4 E2B · local · llama.cpp` → `Rhizome: Jetson Orin Nano · Gemma 4 E2B · local · llama.cpp`. E4: `Gemma 4 E4B · LiteRT-LM · on-device` → `Pollen: Android · Gemma 4 E4B · LiteRT-LM · on-device`. Sin cambios estructurales, solo texto de cartelas.
- **v0.2** (2026-05-05, día 20, Corola) — apilado completo sobre v1.8 tras Bea cerrar los 4 abiertos día 20. Añadidas escenas inestables E0, E1, E3b, E8, E9, E9b con detalle plano-por-plano. Decisiones consolidadas en v1.8: E8 sobrevive (NO se mata), E9 Opción B firme (20s con cadencia Venation completa: 5 cartelas asimétricas + pausa tensa + cierre largo + sello SYNCED ✓), F6 ubicada en E9b. La animación cenital E9 viene como secuencia PNG transparente de Venation (480 frames a 24fps a 1920×1080); Bract codifica MP4 con ffmpeg. **Recortable en post si se decide compresión a 10s** (cortar pausa tensa + sostén final largo).
- **v0.1** (2026-05-05, día 20, Corola) — primer apilado del montage_brief en formato Bract (CapCut). Escenas estables E2-E7 desarrolladas plano-por-plano con tiempo, origen, VO EN/ES, cartelas, transiciones y sfx. Escenas inestables E0/E1/E3b/E8/E9/E9b marcadas TBD-sesión día 20. Notas operativas para Bract sobre carteles físicos, decisión de rodaje un Rhizome dos roles, voz humana E5, master de exportación, pendientes coordinación cross-frente.
