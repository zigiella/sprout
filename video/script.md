# Script — Sprout v1.6 (apilado completo: escenas 1-9 + sistema visual Venation aplicado)

**Versión:** v1.6 (día 17 — sistema visual de Venation adoptado: Soil protocol + Water ledger con tokens, tipografía Manrope + IBM Plex Mono, `signal.seed` como acento cross-escena de "inteligencia activa". Tres cambios de copy aplicados: cartela ancla E7 a *"Watering criteria updated."*, cartela técnica E3 a *"AI proposes / ESP32 validates"*, contingencia E6 *"Context ferry"*. Tarjeta logo final reformulada en inglés. Log E2 diseñado con campos concretos. Motion E5 procesamiento Pollen tres estados. `EDGE NODE` segunda línea cartel caja electrónica.)
**Fecha:** 2026-05-02 (día 17)
**Autora:** Corola
**Duración objetivo:** 3:00 exactos.
**Estructura:** 9 escenas según `docs/40_pitch_video.md §4`.
**Dirección de arte:** sistema *Soil protocol + Water ledger* de Venation (`sprout_design_pack_v1`).

---

## Objetivo del documento

Guion definitivo del vídeo de presentación del proyecto al jurado técnico.

**Regla de idiomas (proyecto):**
- **VO**: castellano. Grabado por Bea.
- **Cartelas, overlays, cualquier texto on-screen**: inglés. Sin subtitulado castellano del VO en pantalla; el doblaje/subtitulado EN del VO se gestiona en post si procede.

**Densidad informativa:** las cartelas y overlays son el motor. El VO hace la historia con pocas palabras. Silencio deliberado donde la cartela basta.

**Aproximación:** ~80 palabras VO castellano + ~14 palabras de voz humana real grabada (operator_note de la persona en escena 5, también castellano).

---

## Sistema visual del video (Venation, día 16-17)

**Soil protocol + Water ledger.** Sistema visual unificado para video, app móvil, landing y cartelería física.

**Paleta — tokens:**
| Token | HEX | Uso en video |
|---|---|---|
| `soil.oat` | `#F3EDE4` | fondo cálido, cartelas editoriales, cartel físico |
| `soil.humus` | `#2A221D` | texto principal, titulares, autoridad |
| `soil.clay` | `#8A654B` | acentos físicos, bordes, señalética |
| `soil.moss` | `#667554` | estabilidad vegetal sobria sin cliché |
| `soil.graphite` | `#1A1A18` | logs Jetson, terminal diseñado, datos técnicos |
| `soil.kraft` | `#C9A97E` | cartón, materialidad opcional carteles físicos |
| `water.blue` | `#3B82F6` | agua, riego, caudal, presupuesto hídrico |
| `status.warning` | `#F59E0B` | prudencia, dato viejo, modo conservador |
| `status.blocked` | `#B94A3D` | bloqueo, rechazo, fallo físico |
| `signal.seed` | `#C5F26B` | **acento único de "inteligencia activa"**, regla 3% |

**Tipografía:**
- **Manrope** (humano/producto): cartelas principales, titulares, voz humana.
- **IBM Plex Mono** (sistema/datos): logs, `DecisionReceipt`, `MissionPatch`, IDs, métricas, timestamps, snippets JSON.

**`signal.seed` aplicado cross-escena (regla del 3%, decisión Corola día 17):**
- E2: LED Jetson cuando decide + resaltado `WATER` y `final_action: 18s`.
- E3: resaltado `final_action: 12s` (donde ESP32 modula).
- E5: pulso del procesamiento Pollen (listening → compiling → validating).
- E7: resaltado de los dos campos del `Policy diff`.
- E9: nodo Pollen recorriendo cenital + luminosidad de mensajes técnicos al aparecer.

Pista visual única que el espectador asocia con sistema decidiendo/actuando con criterio. Conecta video con app móvil + cartelería + landing.

---

## Resumen — 9 escenas

| # | Escena | Tiempo | Beat clave |
|---|--------|--------|------------|
| 1 | La ausencia | 0:00–0:20 (20s) | apertura silenciosa, una parcela visitada periódicamente |
| 2 | Rhizome decide offline | 0:20–0:45 (25s) | sensor → estado → decisión → orden → `DecisionReceipt` + frase fuerte 1 |
| 3 | ESP32 SAFE LIMIT | 0:45–1:00 (15s) | modulación + frase fuerte 3 + cartela "Cuando duda, riega menos" |
| 4 | Llega Pollen | 1:00–1:30 (30s) | móvil pregunta "¿qué pasó?" + frase fuerte 2 |
| 5 | La persona da una misión | 1:30–1:50 (20s) | voz humana coloquial → `MissionPatch` (prueba la frase 2) |
| 6 | Ferry A→B | 1:50–2:10 (20s) | Pollen lleva digest entre Rhizomes + frase fuerte 5 |
| 7 | Criterio modificado | 2:10–2:30 (20s) | tres bloques de evidencia + cartela ancla + acción física distinta |
| 8 | Caducidad | 2:30–2:40 (10s) | `expired → rejected` + frase fuerte 4 (sin "En Sprout") |
| 9 | Cenital federado | 2:40–3:00 (20s) | Veo3 flat editorial · cartela progresiva · subtítulo logo |

---

## Detalle apilado v1.0

`VO` = texto hablado castellano (lo que se oye).
`Cartela` = texto en pantalla que el espectador lee.
`Overlay` = superposición persistente sobre la imagen (esquina o banda).
`—` = silencio intencional.

### Escena 1 — La ausencia (0:00–0:20)

**Beat narrativo:** apertura silenciosa. Una maceta etiquetada como "PLOT_01 with RHIZOME_01" se presenta al espectador como parcela entera. Cero VO, dos cartelas en inglés en cascada. La primera es invitación al espectador; la segunda afirma sobre la parcela.

**Elementos de producción visibles:**
- **Cartel maceta:** **"PLOT_01 with RHIZOME_01"** (impresión sobria, tipografía limpia, fijado a la maceta o clavado al lado en estaca).
- **Cartel caja electrónica:** **"RHIZOME_01"** (etiqueta sobre la cajita Jetson+ESP32, visible cuando se filme el primer plano del Rhizome).

Los carteles físicos refuerzan los nombres de los nodos en el plano material — coherentes con los IDs `rhizome_01` y `rhizome_02` que aparecerán en pantalla durante el resto del vídeo. Decisión Bea día 16: refuerzo de nombres de nodos en el video.

**Cronología:**

| t | Acción / VO | Cartela / Overlay |
|---|-------------|-------------------|
| 0:00–0:06 | Plano fijo de la maceta con cartel **"PLOT_01 with RHIZOME_01"** visible. Tarde temprana, luz ámbar suave. La hoja se mueve ligeramente con el aire. Sin VO. | — |
| 0:06–0:11 | Mismo plano. Cartela central entra. | **Cartela central** (5s): *"Imagine this pot is a whole plot."* |
| 0:11–0:16 | Mismo plano. Primera cartela se desvanece, entra la segunda. | **Cartela central** (5s): *"This plot is visited periodically by a human."* |
| 0:16–0:20 | La cartela se desvanece. Plano sobre la maceta sola otros 4 segundos. El cartel "PLOT_01 with RHIZOME_01" sigue visible. La hoja se mueve. | — |

**Lo que se siente:** soledad. Tiempo lento. La primera cartela invita al espectador a aceptar el truco visual (esta maceta representa una parcela entera) — es ofrenda y contrato narrativo. La segunda cartela afirma sobre esa parcela ya aceptada. La pregunta no hecha que abre el video — *¿quién decide aquí cuando no hay nadie?*

**VO:** 0 palabras.
**Cartelas:** 2 (ambas en inglés).
**Overlays:** ninguno.
**Producción:** cartel maceta "PLOT_01 with RHIZOME_01" en/junto a la maceta + cartel caja electrónica "RHIZOME_01" sobre la cajita Jetson+ESP32.

---

### Escena 2 — Rhizome decide offline (0:20–0:45)

**Beat narrativo:** el cerebro local entra. Sensor → estado → decisión → orden al ESP32 → `DecisionReceipt`. La frase fuerte 1 cierra el bloque sobre la acción física.

**Cronología:**

| t | Acción / VO | Cartela / Overlay |
|---|-------------|-------------------|
| 0:20–0:24 | Corte. Plano cerrado del Jetson en su caja. LED en `signal.seed` (#C5F26B) parpadea cuando el sistema decide. Camera baja al sensor de humedad clavado en la tierra. | **Overlay esquina sup. izq.** (persistente todo el bloque): `OFFLINE` |
| 0:24–0:32 | Pantalla del Jetson llenando el plano. Fondo `soil.graphite` (#1A1A18). Tipografía IBM Plex Mono. Log diseñado entrando con cadencia musical (1 línea/s). Bloque `SOIL READ` primero, bloque `DECISION` después. `WATER` y `final_action: 18s` resaltados en `signal.seed`. Resto del log en gris claro. **VO**: *"Esta parcela no está sola. Tiene un cerebro local. Lee el suelo. Decide."* (13 palabras) | **Cartela esquina sup. der.** (3s): `Gemma 4 E2B · local · llama.cpp` / **Sub-cartela** (3s): `LLM called only when ambiguous` |
| 0:32–0:38 | Captura del `DecisionReceipt` llenando un cuarto de pantalla. Tres campos resaltados (color `signal.seed`): `decision_type: WATER`, `final_action: 18s`, `why_short: "Soil below minimum. Budget available."` Resto del JSON atenuado en gris. **VO**: *"Y firma lo que hace, para que se pueda explicar."* (10 palabras) | **Cartela superpuesta** (2s sobre el receipt, tipografía Manrope editorial): `DecisionReceipt` |
| 0:38–0:43 | Salida al campo. Plano de la válvula. Se abre. Sonido de agua sobre tierra. | — |
| 0:43–0:45 | Plano se mantiene sobre el agua. **VO**: *"Rhizome mantiene viva la parcela cuando nadie está."* (8 palabras, **frase fuerte 1**) | — |

**Log diseñado E2 (Venation, día 17):**

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

Resaltados: `WATER` y `final_action` en `signal.seed`. Contexto en gris atenuado. Cadencia musical 1 línea por segundo, deliberadamente lenta.

**Lo que se siente:** el sistema funciona solo. Sin red, sin nube, sin nadie mirando. La frase fuerte 1 aterriza sobre el agua que sale — promesa cumplida en el mismo plano que se afirma.

**VO:** 31 palabras.
**Cartelas:** 3 (`Gemma 4 E2B · local · llama.cpp`, `LLM called only when ambiguous`, `DecisionReceipt`).
**Overlays:** 1 (`OFFLINE` persistente).
**Tokens dirección de arte:** fondo `soil.graphite`, texto base gris claro, resaltados en `signal.seed`. Tipografía log en IBM Plex Mono. Cartelas en Manrope.

---

### Escena 3 — ESP32 SAFE LIMIT (0:45–1:00)

**Beat narrativo:** el portero prudente. El ESP32 modula una orden por seguridad — no la rechaza. La diferencia entre `candidate_action` y `final_action` es donde la capa física trabaja. Frase fuerte 3 + cartela narrativa "Cuando duda, riega menos".

**Cronología:**

| t | Acción / VO | Cartela / Overlay |
|---|-------------|-------------------|
| 0:45–0:48 | Corte seco. Plano cerrado de la cajita ESP32 con cartel "RHIZOME_01 / EDGE NODE" visible. LED ámbar encendido — atención, no alarma. | **Cartela esquina sup. der.** (3s, Manrope): `AI proposes / ESP32 validates` |
| 0:48–0:53 | Pantalla del Jetson. Comando `WATER A 30s` viajando al ESP32. ESP32 verifica: *"deposito al 30%. Caudal nominal."* No bloquea. **Modula**. Devuelve `ACK` con cap aplicado. **VO**: *"La IA propone. El agua la gobierna una capa física prudente."* (11 palabras, **frase fuerte 3**) | **Overlay esquina sup. der.** (a partir de 0:48): `ESP32 SAFE LIMIT` |
| 0:53–0:56 | `DecisionReceipt` post-ejecución llenando un cuadrante. Tres campos resaltados: `candidate_action: 30s`, `esp32_outcome: ACK (limited by tank level)`, `final_action: 12s` en `signal.seed`. La diferencia entre los dos números es donde la prudencia trabaja. | **Cartela central** (3s, Manrope dominante sobre el receipt): *"When in doubt, water less."* |
| 0:56–1:00 | Plano de la válvula. Se abre. **Pero menos tiempo del propuesto.** Chorro corto, calculado. | — |

**Lo que se siente:** el ESP32 no es polvera; es tutor. No grita NO — dice *"hasta aquí es seguro"*. La narrativa de cuidar se mantiene desde la primera intervención del ESP32. La frase fuerte 3 aterriza sobre el plano del ESP32 modulando (VO castellano), y la cartela *"When in doubt, water less."* la traduce a principio operativo del sistema (en inglés on-screen).

**Cambio v1.6:** la cartela técnica `function/read tools · no actuator tools` queda sustituida por `AI proposes / ESP32 validates` (propuesta Venation, día 17). Más universal, comunica directamente la jerarquía.

**VO:** 11 palabras castellano.
**Cartelas:** 2 inglés (`AI proposes / ESP32 validates`, *"When in doubt, water less."*).
**Overlays:** 1 inglés (`ESP32 SAFE LIMIT`).
**Tokens dirección de arte:** cartelas en Manrope. Overlay en IBM Plex Mono. Resaltado `final_action` en `signal.seed`.

---

### Escena 4 — Llega Pollen (1:00–1:30)

**Beat narrativo:** entra el humano. Después de un minuto del sistema funcionando solo, aparece la persona que va a visitar. Pero no llega a configurar — llega a **escuchar**. El móvil pregunta a Rhizome qué pasó. Rhizome responde a través del móvil. El espectador ve resumen de decisiones recientes. Frase fuerte 2 nueva (afirmación testable que escena 5 va a probar inmediatamente después).

**Cronología:**

| t | Acción / VO | Cartela / Overlay |
|---|-------------|-------------------|
| 1:00–1:06 | Cambio de luz. Entra una persona en plano. **No vemos su cara** — vemos manos, móvil en la mano, cartel **"PLOT_01 with RHIZOME_01"** visible al fondo. Plano medio. La persona se acerca a la maceta. | — |
| 1:06–1:14 | Pantalla del móvil llenando un tercio del cuadro. App Pollen abierta. La persona pulsa botón. En la pantalla aparece la pregunta: *"What happened since my last visit?"* (cartela en inglés sobre la pantalla). **VO** *"El móvil pregunta. La parcela responde."* (6 palabras castellano). | **Cartela esquina sup. der.** (4s): `Gemma 4 E4B · LiteRT-LM · on-device`. **Cartela en pantalla del móvil**: *"What happened since my last visit?"* |
| 1:14–1:24 | Pantalla del móvil cambia: lista resumida de decisiones recientes. Tres líneas en pantalla: `WATER · 18s · 14:00`, `WATER · 12s · 09:30`, `SKIP · 22:00 — humedad suficiente`. La persona lee. Camera cerrada al móvil con la persona detrás difuminada. | — |
| 1:24–1:30 | Plano de la persona mirando la planta, contrastando lo que ve con lo que el móvil le dice. Tres segundos. Después VO: *"Cada visita puede cambiar el criterio local."* (8 palabras castellano, **frase fuerte 2**) sobre el plano. | — |

**Lo que se siente:** el humano entra como interlocutor, no como configurador. La conversación móvil-Rhizome es horizontal, no jerárquica. La frase fuerte 2 es **promesa testable** — escena 5 viene a continuación y la prueba.

**VO:** 14 palabras castellano (6 + 8).
**Cartelas:** 2 (`Gemma 4 E4B · LiteRT-LM · on-device` esquina + *"What happened since my last visit?"* en pantalla del móvil).
**Overlays:** ninguno.
**Producción:** cartel "PLOT_01 with RHIZOME_01" visible. Persona sin cara reconocible.

---

### Escena 5 — La persona da una misión (1:30–1:50)

**Beat narrativo:** el momento más humano del video. Una voz de carne y hueso pidiendo algo concreto. El sistema escuchándola: la frase coloquial se traduce a parámetro técnico sin perder lo que la persona quiso decir. Pollen no recorta — Pollen **traduce**. Esto **prueba** la frase fuerte 2 de escena 4.

**Cronología:**

| t | Acción / VO | Cartela / Overlay |
|---|-------------|-------------------|
| 1:30–1:33 | Plano cercano. La persona pulsa otro botón del móvil (botón de grabación). Acerca el móvil a la cara. **No vemos sus labios** — vemos su mano sosteniendo el móvil. UI del móvil muestra `VOICE NOTE` activo. | — |
| 1:33–1:40 | **Voz humana real (castellano, grabada literal)**: *"Vuelvo el viernes. Esta planta aguanta más seca de lo que crees, riega un poco menos."* (14 palabras). Tono calmado, sin actuación, casi casual. | — |
| 1:40–1:43 | Tres segundos de **procesamiento Pollen en tres estados consecutivos**: micro-animación con pulso `signal.seed`. Estados visibles en pantalla del móvil (1 segundo cada uno): `listening` → `compiling` → `validating`. | — |
| 1:43–1:48 | **Pantalla del móvil mostrando el `MissionPatch` compilado.** Layout recomendado por Venation (pendiente confirmación llamada Floema): `VOICE NOTE` con la frase castellana + `COMPILED PATCH` debajo con cuatro campos: `horizon_h: 72`, `soil_thresholds.dry: 35 → 25`, `budget_cap_ml: 900`, `operator_note: preserved` (etiqueta — la voz literal queda almacenada, no se imprime de nuevo en pantalla aquí). Resaltados con `signal.seed`. | **Cartela superpuesta** (2s, Manrope): `MissionPatch validated` |
| 1:48–1:50 | Plano cerrado del móvil. **VO** (cerrada, una frase): *"Lo que la persona dice se convierte en política."* (9 palabras castellano). | — |

**Motion procesamiento Pollen (Venation, día 17):**

Tres estados secuenciales con pulso `signal.seed`:

```
listening
compiling
validating
```

Aparecen uno tras otro (1s cada uno). Pulso suave, no parpadeo agresivo. Marca el momento donde el sistema **escucha → traduce → valida** la voz humana. El pulso `signal.seed` aquí es la pista visual de "Pollen pensando con criterio".

**Lo que se siente:** una voz humana real entrando al sistema y siendo respetada. La frase coloquial *"aguanta más seca de lo que crees"* se conserva literal en `operator_note` — eso es honestidad: el sistema no resume al humano, lo cita. Pollen traduce intuición agrícola a parámetro técnico sin recortar.

**VO:** 9 palabras castellano + 14 palabras voz humana real castellano = 23 palabras totales castellano en escena.
**Cartelas:** 1 (`MissionPatch validated`).
**Overlays:** ninguno obligatorio.
**Tokens dirección de arte:** UI del móvil con paleta del sistema (fondo `soil.oat` o claro). Resaltados de campos cambiantes (`soil_thresholds.dry`, `budget_cap_ml`) en `signal.seed`. Pulso `signal.seed` durante procesamiento.
**Producción:** **Pendiente llamada con Floema** para confirmar/ajustar UI del compilador (diseño exacto VOICE NOTE + COMPILED PATCH + motion procesamiento). Layout propuesto por Venation alineado con sistema visual del proyecto. La voz humana se graba antes del rodaje principal.

---

### Escena 6 — Ferry A→B (1:50–2:10)

**Beat narrativo:** una parcela tiene ojos al cielo, la otra no. Pero ambas reciben el mismo conocimiento, porque alguien lo lleva. Es la federación demostrada en una acción física: corte limpio entre dos planos del mismo Rhizome haciendo dos roles. La frase fuerte 5 cierra el bloque sobre el plano del Rhizome B aceptando el digest.

**Cronología:**

| t | Acción / VO | Cartela / Overlay |
|---|-------------|-------------------|
| 1:50–1:55 | Plano de la persona junto al **PLOT_01** (cartel maceta "PLOT_01 with RHIZOME_01" + cartel caja "RHIZOME_01 / EDGE NODE" + **estación meteo conectada al Rhizome 01 si la incluimos**). El móvil descarga el `WeatherDigest` (o `Context bundle` si no hay meteo) del Rhizome. Pantalla del móvil: lectura del bundle viajando del Rhizome al teléfono. **VO**: *"Pollen trae preguntas, respuestas y contexto."* (6 palabras castellano). | **Cartela superpuesta** (2s, Manrope): `WeatherDigest ferry` (con meteo) o `Context ferry` (sin meteo) |
| 1:55–1:56 | **Corte limpio.** Sin pasos en plano. | — |
| 1:56–2:04 | Plano de la persona junto al **PLOT_02** (cartel maceta "PLOT_02 with RHIZOME_02" + cartel caja "RHIZOME_02 / EDGE NODE", sin meteo, segunda zona de la terraza, distinta planta). Pollen entrega el bundle al Rhizome 02. Pantalla del móvil: subida del paquete. Pantalla del Rhizome 02 (visible al fondo o en captura): aceptación con cita de origen `rhizome_01`. | **Cartela en pantalla del Rhizome** (visible 4s, IBM Plex Mono): `WeatherDigest accepted · Source: rhizome_01` (con meteo) o `Context accepted · Source: rhizome_01` (sin meteo) |
| 2:04–2:07 | Silencio breve. Plano del Rhizome 02 con el digest aceptado. La cámara respira. | — |
| 2:07–2:10 | **VO** (sentencia, plana): *"Pollen convierte esas visitas en inteligencia federada."* (8 palabras castellano, **frase fuerte 5**). | — |

**Lo que se siente:** Pollen es **portador de más que voz humana**. Lleva también meteorología. Las dos parcelas viven en el mismo terreno pero no se hablan — Pollen las hace hablar. El "esas" de la frase fuerte 5 hace eco directo a "cada visita" de escena 4: coherencia interna.

**VO:** 14 palabras castellano (6 + 8).
**Cartelas:** 2 (`WeatherDigest ferry` + `WeatherDigest accepted · Source: rhizome_01` en pantalla del Rhizome).
**Overlays:** ninguno.
**Producción:** rotación del Rhizome físico entre PLOT_01 y PLOT_02. Estación meteo se conecta para PLOT_01 y se retira para PLOT_02. Carteles físicos visibles en cada toma — maceta ("PLOT_01 with RHIZOME_01" / "PLOT_02 with RHIZOME_02") y caja electrónica ("RHIZOME_01" / "RHIZOME_02", intercambiables entre tomas). Misma persona en plano (continuidad). **Contingencia día 16 (no firme):** si Bea decide prescindir de meteo, el plano 06a se queda sin estación; las dos parcelas se distinguen por cartel + planta + ángulo, sin ferry de meteo. La frase fuerte 5 ("Pollen convierte esas visitas en inteligencia federada") se sostiene igual — la federación es de contexto en general, no solo de meteo.

---

### Escena 7 — Criterion updated (2:10–2:30)

**Beat narrativo:** el sistema acaba de cambiar de criterio. Tres bloques de evidencia visual en cadencia musical (no log JSON masivo) muestran qué cambió. La invariante de jerarquías aterriza como cartela esquina sobre el momento donde se ven las cuatro jerarquías trabajando simultáneamente. La cartela ancla aterriza dominante después. Después, acción física con riego más corto que en escena 2 — la diferencia hace el trabajo narrativo.

**Cronología:**

| t | Acción / VO | Cartela / Overlay |
|---|-------------|-------------------|
| 2:10–2:13 | Pantalla del Jetson llenando el plano. Fondo casi negro. **Bloque 1** entra: `MissionPatch accepted` con `id: mp_004` y `ttl: 21600s`. Cadencia musical (1 línea por segundo). | — |
| 2:13–2:16 | **Bloque 2** entra: `POLICY DIFF` con dos campos resaltados (color `signal.seed` sobre log atenuado): `soil_thresholds.dry: 35 → 25`, `daily_budget_ml: 1500 → 900`. **Cartela esquina inferior derecha** entra (4 líneas IBM Plex Mono pequeña, paleta sobria). | **Cartela esquina inf. der.** (entra a 2:14, visible 5s, IBM Plex Mono): *"Physical layer prevails."* / *"Rhizome arbitrates."* / *"Pollen mediates."* / *"Meristem refines."* |
| 2:16–2:19 | **Bloque 3** entra: `NEXT DECISION CHANGED` con `policy_id: pol_009 → pol_010`, `final_action: 12s`, `why_short: "Mission compiled from human voice"`. La cartela esquina sigue visible. | — |
| 2:19–2:22 | Cartela ancla central (3s, Manrope editorial dominante): *"Watering criteria updated."* sobre los tres bloques que quedan al fondo en gris atenuado. La cartela esquina **se desvanece a 2:19** cuando entra la ancla — no compiten por atención. | **Cartela central** (3s, Manrope): *"Watering criteria updated."* |
| 2:22–2:30 | Salida al campo. Plano de la maceta y la válvula. Se abre. **Pero menos tiempo que en escena 2** — chorro corto, controlado, austero (12s real). El espectador recuerda inconscientemente que la primera vez fue largo. **VO** sobre el plano del agua: *"El sistema ajusta los cuidados."* (5 palabras castellano). | — |

**Log diseñado E7 (Venation, día 17):**

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

Cadencia musical: 1 bloque cada 3 segundos. Los dos campos del `Policy diff` resaltados en `signal.seed`. Resto en gris atenuado.

**Cambio v1.6:** la cartela ancla central pasa de *"Criterion updated."* a *"Watering criteria updated."* (propuesta Venation día 17, voto Bea aceptado). Razón: más concreto, más ligado al agua que es el tema central del video.

**Lo que se siente:** el cambio del sistema es **prueba compuesta**, no afirmación. Los tres bloques son evidencia técnica honesta. La invariante en esquina nombra el sistema entero **mientras está trabajando** — el espectador ve simultáneamente la capa física esperando (válvula a punto de abrir), Rhizome arbitrando (los bloques de evidencia), Pollen mediando (el `MissionPatch` que llegó vía Pollen escena 5), Meristem refinando (futuro implícito en la cadena temporal). La cartela ancla traduce todo para el no técnico. La diferencia con escena 2 cierra el arco con acción física.

**Por qué la invariante aterriza aquí (decisión Cambium ella día 15, voto sí; coincidente con propuesta Corola del ejercicio frases fuertes):** E7 es el único plano del vídeo donde **las cuatro jerarquías son visibles simultáneamente**:
- En E3 solo se ven la física + la IA (no Pollen, no Meristem).
- En E6 hay Pollen mediando entre dos Rhizomes pero no física ni Meristem.
- En E9 la abstracción flat las representa pero ya están desacopladas en el cenital.
- **En E7 las cuatro están operativamente juntas**: válvula esperando, Rhizome decidiendo, Pollen entregó hace segundos, Meristem refinará después.

La cartela esquina aterriza sobre la imagen exacta que la sostiene, y se desvanece antes de la cartela ancla central — sin compresión visual.

**VO:** 5 palabras castellano (sobrio radical).
**Cartelas:** 1 dominante (*"Watering criteria updated."*) + 1 esquina (invariante 4 líneas) + 3 bloques de evidencia técnica en pantalla.
**Overlays:** ninguno.
**Tokens dirección de arte:** fondo `soil.graphite`, resaltados `signal.seed` (los dos campos del diff), texto base IBM Plex Mono. Cartela ancla central Manrope. Cartela esquina invariante IBM Plex Mono pequeña. La cartela esquina inferior derecha en tipografía técnica pequeña, paleta sobria — **no compite** con la cartela ancla central que vendrá después.
**Producción:** captura de pantalla del Jetson real (Xilema corre el sistema) o mock fiel del log con los tres bloques diseñados con dirección de arte fina. La válvula con chorro **visiblemente más corto** que en escena 2 (cronometrar: 12s en E7 vs 18s en E2).

**Traducción confirmada (voto Bea día 16):** *"Physical layer prevails."* / *"Rhizome arbitrates."* / *"Pollen mediates."* / *"Meristem refines."* La opción "prevails" gana sobre "commands" por claridad semántica (prevalece, manda al final, se impone) manteniendo el ritmo de tripleta paralela con los tres verbos siguientes.

---

### Escena 8 — Caducidad (2:30–2:40)

**Beat narrativo:** el sistema rechaza algo viejo. La caducidad como virtud. Frase fuerte 4 lapidaria sobre el rechazo del `WeatherDigest` expirado.

**Cronología:**

| t | Acción / VO | Cartela / Overlay |
|---|-------------|-------------------|
| 2:30–2:32 | Cartela limpia (2s): *"Three days later"*. | **Cartela central** (2s): *"Three days later"* |
| 2:32–2:36 | Pantalla del Jetson. El `WeatherDigest` que Pollen entregó en escena 6 está llegando a su `valid_until`. El sistema lo evalúa y rechaza. Tres líneas en pantalla: `WeatherDigest #2026-04-26-001`, `status: EXPIRED → REJECTED`, `reason: ttl exceeded`. | **Cartela superpuesta** (2s): `expired → rejected` |
| 2:36–2:40 | **VO** sobre la pantalla del rechazo: *"Toda inteligencia tiene jurisdicción y fecha de caducidad."* (8 palabras castellano, **frase fuerte 4** sin "En Sprout"). | — |

**Lo que se siente:** la negación es virtud. El sistema no acumula contexto viejo — lo rechaza con aviso. La frase fuerte 4 aterriza sobre el rechazo literal en pantalla; coherencia total entre frase y plano.

**VO:** 8 palabras castellano (frase fuerte 4).
**Cartelas:** 2 (*"Three days later"* + `expired → rejected`).
**Overlays:** ninguno.

---

### Escena 9 — Cenital federado + Meristem (2:40–3:00)

**Decisión Meristem firme (día 14):** Meristem-nodo entra al MVP. Bea cierra la visión de la escena: el cenital flat editorial mantiene su comienzo (8 parcelas + Pollen recorriendo), pero después Pollen llega al nodo Meristem **en el cenital flat**, hay **corte limpio a imagen real** del portátil del agricultor donde Meristem ejecuta, dos mensajes en pantalla con la operación, y cierre con tarjeta logo. Tres niveles narrativos: máquina (E1-E7) → abstracción de red (E9 inicio) → cerebro lento doméstico real (E9 final).

**Beat narrativo:** el video pasa de **filmado** a **diagramado** (corte 2:40 al cenital flat) y de **diagramado** a **filmado otra vez** (corte 2:54 al portátil real). El segundo corte es estructural: lo abstracto demuestra el sistema funcionando a escala; lo real demuestra que el cerebro lento existe en una cocina, no en una nube.

**Cronología:**

| t | Acción / VO | Cartela / Overlay |
|---|-------------|-------------------|
| 2:40–2:42 | Plano real de la maceta del rodaje (continuidad con la última imagen de E8 si la hubiera, o transición desde la pantalla del Jetson). **Morph sutil** durante 2 segundos: la maceta se difumina, los bordes se expanden, aparece la parcela vista en cenital. Fondo neutro abstracto. | — |
| 2:42–2:46 | Cenital flat editorial. Parcelas apareciendo progresivamente: una, dos, hasta ocho en mosaico irregular. Paleta tierra sobria. Cartela dosificada sincronizada con la aparición. | **Cartela progresiva (4s, dosificada en 3 beats al ritmo de las parcelas):** *"One plot."* (s1) → *"Two."* (s2) → *"Eight."* (s4) |
| 2:46–2:48 | Pollen-nodo aparece y **arranca recorrido** entre las parcelas. Cartela única en s47. | **Cartela** (2s): *"Autonomous."* |
| 2:48–2:51 | Pollen-nodo recorre parcelas. **Mensajes técnicos breves** (3-5 según ritmo, IBM Plex Mono integrado al diseño flat) apareciendo y desapareciendo en cada toque del nodo: `WeatherDigest accepted`, `MissionPatch delivered`, `DecisionReceipt synced`, `ValidationStamp issued`, `Context cached`. Pulso `signal.seed` en el nodo. Cartela cumbre. | **Cartela** (3s, Manrope): *"Federated intelligence, carried by Pollen."* |
| 2:51–2:54 | Pollen-nodo **llega al nodo Meristem** dentro del cenital flat. El nodo Meristem está representado como un **disco mayor azul desaturado o grafito claro** (Venation, día 17), distinto a las 8 parcelas (que son celdas rectangulares irregulares). Pausa de conexión visual. | — |
| **2:54–2:55** | **Corte limpio.** Quiebre estético deliberado. Cambio de Veo3 flat a imagen real. | — |
| 2:55–2:58 | Plano real del **portátil del agricultor abierto sobre una mesa de cocina** (o equivalente doméstico). Pantalla del portátil mostrando la app Meristem. **Cartela en pantalla del portátil** (3s): *"Pulling Rhizome data..."* (con elipsis indicando proceso). | **Cartela on-screen** (3s): *"Pulling Rhizome data..."* |
| 2:58–3:00 | Pantalla cambia. **Cartela on-screen** (2s): *"Adjusting policies..."* La tarjeta logo final entra por fade sobre la pantalla del portátil al final. | **Cartela on-screen** (2s): *"Adjusting policies..."* + **Tarjeta logo** entrando por fade |
| (cierre) | Tarjeta logo final visible 2-3s sobre la pantalla del portátil difuminada al fondo. | **Tarjeta logo (reformulada Venation, día 17):** `Sprout` / *"Local-first irrigation decisions."* / *"Safe · explainable · open-source"* / `zigiella · Apache 2.0` / `github.com/zigiella/sprout` |

**Lo que se siente:** el video pasa de **abstracción** a **realidad doméstica**. El cerebro lento no vive en la nube — vive en un portátil sobre una mesa. Eso es lo más Sprout que el video puede demostrar al final: la inteligencia consolidada está al alcance de una persona, en su casa, no en un data center remoto. La cartela progresiva cierra la tesis (federación), los dos mensajes de Meristem cierran la operación (consolidación), y la tarjeta logo cierra el producto (firma).

**VO:** 0 palabras (la escena 9 es puramente visual + cartelas).
**Cartelas:** 6 en total (cartela progresiva en 3 beats + 2 mensajes Meristem + tarjeta logo).
**Overlays:** ninguno.

**Producción:**

- **Cenital flat (2:40–2:54):** **Venation prepara cenital animado** según design pack día 17. Si Veo3 sigue siendo necesario en este beat, prompt refinado por Venation: *"Editorial flat illustration, top-down view of 8 small farm plots arranged in an irregular mosaic, muted earth tones, clean line work, modern infographic style, warm oat background, no realistic sky, no realistic shadows. A small luminous seed-lime node moves between plots, carrying context. Minimal technical labels appear briefly near touched plots: WeatherDigest accepted, MissionPatch delivered, DecisionReceipt synced. The node finally connects to a larger distinct Meristem hub, a desaturated blue-gray circle, visually different from the plot cells. Calm precise motion, not playful, not videogame-like."* Negative prompt: *"no cartoon farm, no happy plants, no neon AI, no futuristic city, no glossy 3D, no realistic drone shot, no childish icons, no saturated green, no sci-fi interface."* **Decisión pendiente día 17 con Bea:** ¿Veo3 sigue siendo necesario en E9 si Venation entrega cenital animado, o queda Veo3 limitado a planos 08 y 14 que Bract acotó?
- **Corte 2:54–2:55:** corte limpio, sin transición, sin fade. El quiebre estético es feature.
- **Imagen real (2:55–3:00):** plano del portátil del agricultor abierto sobre una mesa (cocina o similar doméstico). Luz natural si es posible. La pantalla del portátil tiene que mostrar **algo real** — la app Meristem corriendo (Meristem la prepara) o mock fiel.
- **Tarjeta logo (reformulada Venation, día 17):** diseño en post con paleta `soil.oat` o `soil.humus`. Tipografía Manrope para `Sprout` (titular) y subtítulo (`Local-first irrigation decisions.` / `Safe · explainable · open-source`). IBM Plex Mono para los IDs (`zigiella · Apache 2.0` y URL repo). **Cambio v1.6:** subtítulo ahora en inglés (corrige inconsistencia v1.4 que tenía castellano *"Decisiones locales, seguras y explicables."*). Coherente con regla "todo on-screen en inglés".

**Recurso de Cambium NO aplicado:** la cartela invariante de Xilema *"Physical layer rules. Rhizome arbitrates. Pollen mediates. Meristem refines."* queda **fuera de escena 9**. Razonamiento: la escena ya tiene cartela progresiva (3 beats) + 2 mensajes Meristem + tarjeta logo (4 líneas) = 9 elementos textuales en 20 segundos. Añadir una cartela invariante de 4 líneas más satura. La invariante queda como recurso writeup donde tiene más espacio. Si Bea o Cambium reabren la decisión, busco hueco.

---

## Conteo VO completo (escenas 1-9 apiladas)

VO en castellano grabado por Bea. Cartelas/overlays/textos on-screen en inglés (regla de proyecto v1.1).

- E1: 0 palabras (silencio + dos cartelas inglés).
- E2: 31 palabras castellano (13 + 10 + 8).
- E3: 11 palabras castellano.
- E4: 14 palabras castellano (6 + 8 frase fuerte 2).
- E5: 9 palabras castellano VO + **14 palabras voz humana real** castellano.
- E6: 14 palabras castellano (6 + 8 frase fuerte 5).
- E7: 5 palabras castellano (sobrio).
- E8: 8 palabras castellano (frase fuerte 4 sin "En Sprout").
- E9: 0 palabras VO (escena puramente visual + cartelas inglés).
- **Total apilado v1.3:** 92 palabras castellano + 14 voz humana real = **106 palabras totales castellano**. Margen sigue holgado para doblaje EN.

---

## Pendientes antes de grabar

- [x] Apilar escenas 1-3 (día 13). Apilar escenas 4, 5 (parcial), 6, 7, 8 (día 14). Apilar escena 9 con Meristem (día 14, decisión firme).
- [ ] **Coordinación asíncrona con Floema** para UI del compilador `MissionPatch` en escena 5 (Bea relaya mensaje).
- [ ] **Ejercicio de calidad narrativa de las cinco frases fuertes** — Bea me pide que tome la iniciativa. Pasar cada frase por el filtro *"¿el vídeo demuestra esto, o solo lo afirma?"*. Iniciado en `bitacora/2026-04-29_corola-frases-fuertes-ejercicio_corola.md`. Bea + Cambium revisan después.
- [x] Persona VO castellano confirmada: **Bea**.
- [ ] Confirmar voz humana de escena 5 (propuesta: persona del equipo grabando literal en castellano).
- [ ] **Refinar traducciones inglés** marcadas como *first pass* (cartela ancla E7 *"Criterion updated."*, cartela progresiva E9, subtítulo logo).
- [x] **Carteles físicos** los prepara Bea (Helvetica, mayúsculas, fondo neutro, en inglés). **Cuatro carteles totales:** 2 de maceta (`PLOT_01 with RHIZOME_01` / `PLOT_02 with RHIZOME_02`) + 2 de caja electrónica intercambiables (`RHIZOME_01` / `RHIZOME_02`).
- [ ] Coordinar dirección de arte de la pantalla del Jetson en escenas 2, 3, 7 (resaltado fuerte de campos clave, cadencia musical de líneas, cartelas dominantes sobre log).
- [x] **Invariante Xilema NO aplicada en E9** — la escena ya tiene 9 elementos textuales en 20s. La invariante queda como recurso writeup. Decisión documentada en E9.

---

## Historial de versiones

- **v1.6 — sistema visual Venation aplicado** (2026-05-02, día 17, Corola) — adoptado design pack `sprout_design_pack_v1` de Venation. Cambios consolidados:
  1. **Sistema visual:** Soil protocol + Water ledger con tokens hex precisos (`soil.oat`, `soil.humus`, `soil.clay`, `soil.moss`, `soil.graphite`, `soil.kraft`, `water.blue`, `status.warning`, `status.blocked`, `signal.seed`). Tipografía: Manrope (humano/producto) + IBM Plex Mono (sistema/datos). Documentado en sección "Sistema visual del video" al inicio.
  2. **`signal.seed` (#C5F26B) aplicado cross-escena como acento único de "inteligencia activa"** (regla 3%). E2: LED Jetson + resaltado WATER y final_action. E3: resaltado final_action. E5: pulso procesamiento Pollen. E7: resaltado Policy diff. E9: nodo Pollen + mensajes técnicos. Decisión Corola día 17 (voto delegado por Cambium ella).
  3. **E2 log diseñado con campos concretos** (Venation): bloque `SOIL READ` + bloque `DECISION` con campos cotejables con `DecisionReceipt`. Cadencia 1 línea/segundo.
  4. **E3 cartela técnica:** `function/read tools · no actuator tools` → `AI proposes / ESP32 validates` (Venation, voto Bea aceptado).
  5. **E5 motion procesamiento Pollen:** tres estados secuenciales `listening → compiling → validating` con pulso `signal.seed` (Venation).
  6. **E6 contingencia explícita meteo / sin meteo:** cartela `WeatherDigest ferry` (con meteo) o `Context ferry` (sin meteo); recepción `WeatherDigest accepted` o `Context accepted`. Limpio para las dos rutas (Venation, voto Bea aceptado).
  7. **E7 cartela ancla:** `Criterion updated.` → `Watering criteria updated.` (Venation, voto Bea aceptado). Más concreto, más ligado al agua.
  8. **E9 mensajes técnicos cenital:** ahora 5 mensajes (`WeatherDigest accepted`, `MissionPatch delivered`, `DecisionReceipt synced`, `ValidationStamp issued`, `Context cached`). Nodo Meristem como **disco mayor azul desaturado o grafito claro** (Venation).
  9. **E9 tarjeta logo reformulada:** `Sprout / Local-first irrigation decisions. / Safe · explainable · open-source / zigiella · Apache 2.0 / github.com/zigiella/sprout`. **Corrige inconsistencia v1.4** que tenía subtítulo en castellano violando regla "todo on-screen en inglés".
  10. **Prompt Veo3 E9 actualizado** con versión refinada de Venation. Decisión pendiente con Bea: ¿Veo3 sigue siendo necesario en E9 si Venation entrega cenital animado, o queda Veo3 limitado a planos 08 y 14 que Bract acotó?
- **v1.5 — refuerzo de nombres de nodos + traducción confirmada** (2026-05-01, día 16, Corola) — cinco cambios tras mensaje de Bea día 16:
  1. **Voto Bea sobre traducción invariante:** *"Physical layer prevails."* gana sobre *"commands"* — swap textual aplicado en E7 (script + shot list). "prevails" preserva ritmo de tripleta paralela y gana claridad semántica.
  2. **Carteles físicos extendidos.** Decisión Bea: dos carteles por parcela en lugar de uno — cartel maceta con nombre completo (`PLOT_01 with RHIZOME_01` / `PLOT_02 with RHIZOME_02`) + cartel caja electrónica (`RHIZOME_01` / `RHIZOME_02`, intercambiables sobre la misma cajita Jetson+ESP32 entre tomas). Total **4 carteles** en lugar de 2. Refuerza nombres de nodos en plano físico durante todo el rodaje.
  3. **Contingencia "sin meteo"** anotada en E6 (no firme, decisión Bea pendiente). Si prescindimos de meteo, el plano 06a se queda sin estación; las dos parcelas se distinguen por cartel + planta + ángulo. La frase fuerte 5 se sostiene igual — la federación es de contexto en general, no solo de meteo.
  4. **Refuerzo de nombres de nodos** en planos donde antes no aparecían explícitos — descripción de planos 04a, 06a, 06d ahora cita carteles con nombres completos.
  5. **Cambium ella formaliza regla "tres puntos de verificación git"** en `CONTRIBUTING.md` o `docs/conventions/git_safety.md` (mañana día 17). Aprendizaje del día 15 escala a convención de proyecto.
- **v1.4 — invariante de jerarquías en E7** (2026-04-30, día 15, Corola) — añadida cartela esquina inferior derecha en E7 con la invariante de jerarquías de Xilema (4 líneas en inglés, tipografía técnica pequeña, paleta sobria, visible 5s desde 2:14 a 2:19). Aterriza sobre el momento donde las cuatro jerarquías son visibles simultáneamente (válvula esperando, Rhizome decidiendo, Pollen entregó, Meristem refinará). Decisión Cambium ella día 15 — voto sí (4ª de las 4 propuestas del ejercicio frases fuertes) coincidente con propuesta Corola. Las otras 3 propuestas votadas no por consenso. Traducción first pass *"Physical layer commands."* (variante propuesta *"Physical layer prevails."* — pendiente voto Bea, swap textual de una palabra).
- **v1.3 — apilado completo** (2026-04-29, día 14, Corola) — escena 9 reescrita con Meristem entrando al MVP (decisión firme Bea + Cambium + Meristem día 14). Estructura: cenital flat editorial con 8 parcelas + Pollen-nodo recorriendo + llegada al nodo Meristem en el cenital, **corte limpio a imagen real** del portátil del agricultor con app Meristem ejecutando, dos cartelas on-screen (*"Pulling Rhizome data..."* + *"Adjusting policies..."*), tarjeta logo final entrando por fade. Tres niveles narrativos en el cierre: máquina (E1-E7) → abstracción de red (E9 inicio) → cerebro lento doméstico real (E9 final). Cartela invariante de Xilema NO aplicada en E9 (saturación de elementos textuales) — queda como recurso writeup. **Cambium es ella** — corrección registrada. Persona VO confirmada Bea. Carteles físicos PLOT 1 / PLOT 2 los prepara Bea (Helvetica, mayúsculas, fondo neutro, inglés). Coordinación con Floema asíncrona — mensaje preparado para que Bea relaye.
- **v1.2 — apilado parcial extendido** (2026-04-29, día 14, Corola) — apilado de escenas 4, 5 (parcial), 6, 7, 8 con detalle equivalente al de escenas 1-3. Escena 5 con TBD en UI del compilador `MissionPatch` pendiente de llamada con Floema (F5 cerrada). Escena 9 pendiente de decisión firme Meristem (conversación Bea + Cambium + Meristem día 14): si Meristem-nodo entra al MVP, se amplía con plano breve del portátil del agricultor; si no entra, se mantiene como en pitch doc. Recurso disponible para escena 9: invariante de Xilema *"Lo físico manda, Rhizome arbitra, Pollen media, Meristem afina."* — aplicable como cartela inglés *"Physical layer rules. Rhizome arbitrates. Pollen mediates. Meristem refines."* solo si Meristem entra (cuatro sujetos visibles en video). Conteo VO: 92 palabras castellano + 14 voz humana real = 106 palabras totales. Origen del recado Meristem: Cambium tras review meeting día 13 (`bitacora/2026-04-28_review-meeting-tuning_cambium.md`).
- **v1.1 — apilado parcial** (2026-04-28, día 13, Corola) — ajustes tras review de Bea en PR #59:
  - Eliminada referencia al hackathon y al jurado del encabezado del documento (decisión: no documentos públicos con datos sensibles).
  - **Regla nueva del proyecto:** cartelas/overlays/textos on-screen en inglés. VO castellano grabado por Bea. Aplicado a las cartelas de escenas 1, 2, 3 (la cartela bilingüe de E1 pasa a inglés solo; *"Cuando duda, riega menos"* → *"When in doubt, water less."*). Cartelas de escenas 4-9 traducidas como first pass — refinar al apilar.
  - **Escena 1 ampliada:** añadida cartela inicial *"Imagine this pot is a whole plot."* como invitación al espectador antes de la cartela ya existente. Reorganizado el desglose temporal (0:00-0:06 plano sin cartela / 0:06-0:11 cartela 1 / 0:11-0:16 cartela 2 / 0:16-0:20 plano final).
  - **Cartel físico "PLOT 1"** en/junto a la maceta como elemento de producción visible desde escena 1 y coherente con los IDs `rhizome_01` y `rhizome_02`.
  - Persona VO castellano confirmada: Bea.
- **v1.0 — apilado parcial inicial** (2026-04-28, día 13, Corola) — primer apilado real en `script.md` tras el pivote v2 (día 8 Bea), las decisiones del día 11 y los seis cambios del día 12. Escenas 1, 2, 3 desarrolladas con detalle.
- **v0.x descartados** — versiones del v0 cerradas en PRs #40/#41 sin merge tras pivote v2 día 8. Principios autorales que sobreviven al pivote anclados en `bitacora/2026-04-26_corola-guion-cerrado-conceptual_corola.md`.
