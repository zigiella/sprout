# Script — Sprout v1.2 (apilado parcial: escenas 1-8)

**Versión:** v1.2 (apilado parcial — escenas 1 a 8 desarrolladas. Escena 9 pendiente de decisión firme Meristem día 14.)
**Fecha:** 2026-04-29 (día 14)
**Autora:** Corola
**Duración objetivo:** 3:00 exactos.
**Estructura:** 9 escenas según `docs/40_pitch_video.md §4`.

---

## Objetivo del documento

Guion definitivo del vídeo de presentación del proyecto al jurado técnico.

**Regla de idiomas (proyecto):**
- **VO**: castellano. Grabado por Bea.
- **Cartelas, overlays, cualquier texto on-screen**: inglés. Sin subtitulado castellano del VO en pantalla; el doblaje/subtitulado EN del VO se gestiona en post si procede.

**Densidad informativa:** las cartelas y overlays son el motor. El VO hace la historia con pocas palabras. Silencio deliberado donde la cartela basta.

**Aproximación:** ~80 palabras VO castellano + ~14 palabras de voz humana real grabada (operator_note de la persona en escena 5, también castellano).

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

**Beat narrativo:** apertura silenciosa. Una maceta etiquetada como "PLOT 1" se presenta al espectador como parcela entera. Cero VO, dos cartelas en inglés en cascada. La primera es invitación al espectador; la segunda afirma sobre la parcela.

**Elemento de producción visible:** la maceta lleva un cartel físico real con el texto **"PLOT 1"** (impresión sobria, tipografía limpia, fijado a la maceta o clavado al lado en estaca). Este cartel es coherente con los IDs `rhizome_01` y `rhizome_02` que aparecerán en pantalla durante el resto del vídeo.

**Cronología:**

| t | Acción / VO | Cartela / Overlay |
|---|-------------|-------------------|
| 0:00–0:06 | Plano fijo de la maceta con cartel **"PLOT 1"** visible. Tarde temprana, luz ámbar suave. La hoja se mueve ligeramente con el aire. Sin VO. | — |
| 0:06–0:11 | Mismo plano. Cartela central entra. | **Cartela central** (5s): *"Imagine this pot is a whole plot."* |
| 0:11–0:16 | Mismo plano. Primera cartela se desvanece, entra la segunda. | **Cartela central** (5s): *"This plot is visited periodically by a human."* |
| 0:16–0:20 | La cartela se desvanece. Plano sobre la maceta sola otros 4 segundos. El cartel "PLOT 1" sigue visible. La hoja se mueve. | — |

**Lo que se siente:** soledad. Tiempo lento. La primera cartela invita al espectador a aceptar el truco visual (esta maceta representa una parcela entera) — es ofrenda y contrato narrativo. La segunda cartela afirma sobre esa parcela ya aceptada. La pregunta no hecha que abre el video — *¿quién decide aquí cuando no hay nadie?*

**VO:** 0 palabras.
**Cartelas:** 2 (ambas en inglés).
**Overlays:** ninguno.
**Producción:** cartel físico "PLOT 1" en/junto a la maceta.

---

### Escena 2 — Rhizome decide offline (0:20–0:45)

**Beat narrativo:** el cerebro local entra. Sensor → estado → decisión → orden al ESP32 → `DecisionReceipt`. La frase fuerte 1 cierra el bloque sobre la acción física.

**Cronología:**

| t | Acción / VO | Cartela / Overlay |
|---|-------------|-------------------|
| 0:20–0:24 | Corte. Plano cerrado del Jetson en su caja. LED parpadea. Camera baja al sensor de humedad clavado en la tierra. | **Overlay esquina sup. izq.** (persistente todo el bloque): `OFFLINE` |
| 0:24–0:32 | Pantalla del Jetson llenando el plano. Líneas de log entrando: lectura humedad → cálculo necesidad → decisión. **VO**: *"Esta parcela no está sola. Tiene un cerebro local. Lee el suelo. Decide."* (13 palabras) | **Cartela esquina sup. der.** (3s): `Gemma 4 E2B · local · llama.cpp` / **Sub-cartela** (3s): `LLM called only when ambiguous` |
| 0:32–0:38 | Captura del `DecisionReceipt` llenando un cuarto de pantalla. Tres líneas resaltadas: `decision_type: WATER`, `final_action: 18s`, `why_short: "Suelo por debajo del mínimo. Presupuesto disponible."` Resto del JSON en gris. **VO**: *"Y firma lo que hace, para que se pueda explicar."* (10 palabras) | **Cartela superpuesta** (2s sobre el receipt): `DecisionReceipt` |
| 0:38–0:43 | Salida al campo. Plano de la válvula. Se abre. Sonido de agua sobre tierra. | — |
| 0:43–0:45 | Plano se mantiene sobre el agua. **VO**: *"Rhizome mantiene viva la parcela cuando nadie está."* (8 palabras, **frase fuerte 1**) | — |

**Lo que se siente:** el sistema funciona solo. Sin red, sin nube, sin nadie mirando. La frase fuerte 1 aterriza sobre el agua que sale — promesa cumplida en el mismo plano que se afirma.

**VO:** 31 palabras.
**Cartelas:** 3 (`Gemma 4 E2B · local · llama.cpp`, `LLM called only when ambiguous`, `DecisionReceipt`).
**Overlays:** 1 (`OFFLINE` persistente).

---

### Escena 3 — ESP32 SAFE LIMIT (0:45–1:00)

**Beat narrativo:** el portero prudente. El ESP32 modula una orden por seguridad — no la rechaza. La diferencia entre `candidate_action` y `final_action` es donde la capa física trabaja. Frase fuerte 3 + cartela narrativa "Cuando duda, riega menos".

**Cronología:**

| t | Acción / VO | Cartela / Overlay |
|---|-------------|-------------------|
| 0:45–0:48 | Corte seco. Plano cerrado de la cajita ESP32. LED ámbar encendido — atención, no alarma. | **Cartela esquina sup. der.** (3s): `function/read tools · no actuator tools` |
| 0:48–0:53 | Pantalla del Jetson. Comando `WATER A 30s` viajando al ESP32. ESP32 verifica: *"depósito al 30%. Caudal nominal."* No bloquea. **Modula**. Devuelve `ACK` con cap aplicado. **VO**: *"La IA propone. El agua la gobierna una capa física prudente."* (11 palabras, **frase fuerte 3**) | **Overlay esquina sup. der.** (a partir de 0:48): `ESP32 SAFE LIMIT` |
| 0:53–0:56 | `DecisionReceipt` post-ejecución llenando un cuadrante. Tres campos resaltados: `candidate_action: 30s`, `esp32_outcome: ACK (limited by tank level)`, `final_action: 12s`. La diferencia entre los dos números es donde la prudencia trabaja. | **Cartela central** (3s, dominante sobre el receipt): *"When in doubt, water less."* |
| 0:56–1:00 | Plano de la válvula. Se abre. **Pero menos tiempo del propuesto.** Chorro corto, calculado. | — |

**Lo que se siente:** el ESP32 no es polvera; es tutor. No grita NO — dice *"hasta aquí es seguro"*. La narrativa de cuidar se mantiene desde la primera intervención del ESP32. La frase fuerte 3 aterriza sobre el plano del ESP32 modulando (VO castellano), y la cartela *"When in doubt, water less."* la traduce a principio operativo del sistema (en inglés on-screen).

**VO:** 11 palabras castellano.
**Cartelas:** 2 inglés (`function/read tools · no actuator tools`, *"When in doubt, water less."*).
**Overlays:** 1 inglés (`ESP32 SAFE LIMIT`).

---

### Escena 4 — Llega Pollen (1:00–1:30)

**Beat narrativo:** entra el humano. Después de un minuto del sistema funcionando solo, aparece la persona que va a visitar. Pero no llega a configurar — llega a **escuchar**. El móvil pregunta a Rhizome qué pasó. Rhizome responde a través del móvil. El espectador ve resumen de decisiones recientes. Frase fuerte 2 nueva (afirmación testable que escena 5 va a probar inmediatamente después).

**Cronología:**

| t | Acción / VO | Cartela / Overlay |
|---|-------------|-------------------|
| 1:00–1:06 | Cambio de luz. Entra una persona en plano. **No vemos su cara** — vemos manos, móvil en la mano, cartel **"PLOT 1"** visible al fondo. Plano medio. La persona se acerca a la maceta. | — |
| 1:06–1:14 | Pantalla del móvil llenando un tercio del cuadro. App Pollen abierta. La persona pulsa botón. En la pantalla aparece la pregunta: *"What happened since my last visit?"* (cartela en inglés sobre la pantalla). **VO** *"El móvil pregunta. La parcela responde."* (6 palabras castellano). | **Cartela esquina sup. der.** (4s): `Gemma 4 E4B · LiteRT-LM · on-device`. **Cartela en pantalla del móvil**: *"What happened since my last visit?"* |
| 1:14–1:24 | Pantalla del móvil cambia: lista resumida de decisiones recientes. Tres líneas en pantalla: `WATER · 18s · 14:00`, `WATER · 12s · 09:30`, `SKIP · 22:00 — humedad suficiente`. La persona lee. Camera cerrada al móvil con la persona detrás difuminada. | — |
| 1:24–1:30 | Plano de la persona mirando la planta, contrastando lo que ve con lo que el móvil le dice. Tres segundos. Después VO: *"Cada visita puede cambiar el criterio local."* (8 palabras castellano, **frase fuerte 2**) sobre el plano. | — |

**Lo que se siente:** el humano entra como interlocutor, no como configurador. La conversación móvil-Rhizome es horizontal, no jerárquica. La frase fuerte 2 es **promesa testable** — escena 5 viene a continuación y la prueba.

**VO:** 14 palabras castellano (6 + 8).
**Cartelas:** 2 (`Gemma 4 E4B · LiteRT-LM · on-device` esquina + *"What happened since my last visit?"* en pantalla del móvil).
**Overlays:** ninguno.
**Producción:** cartel "PLOT 1" visible. Persona sin cara reconocible.

---

### Escena 5 — La persona da una misión (1:30–1:50)

**Beat narrativo:** el momento más humano del video. Una voz de carne y hueso pidiendo algo concreto. El sistema escuchándola: la frase coloquial se traduce a parámetro técnico sin perder lo que la persona quiso decir. Pollen no recorta — Pollen **traduce**. Esto **prueba** la frase fuerte 2 de escena 4.

**Cronología:**

| t | Acción / VO | Cartela / Overlay |
|---|-------------|-------------------|
| 1:30–1:33 | Plano cercano. La persona pulsa otro botón del móvil (botón de grabación). Acerca el móvil a la cara. **No vemos sus labios** — vemos su mano sosteniendo el móvil. | — |
| 1:33–1:40 | **Voz humana real (castellano, grabada literal)**: *"Vuelvo el viernes. Esta planta aguanta más seca de lo que crees, riega un poco menos."* (14 palabras). Tono calmado, sin actuación, casi casual. | — |
| 1:40–1:43 | Tres segundos de silencio. La pantalla del móvil procesa — micro-animación de procesamiento. | — |
| 1:43–1:48 | **Pantalla del móvil mostrando el `MissionPatch` compilado.** Diseño: `TBD — pendiente llamada con Floema para definir UI exacta del compilador`. Lo que tiene que verse: cuatro líneas resaltadas en este orden: `horizon_h: 72`, `soil_thresholds.dry: 35 → 25`, `budget_cap_ml: 900`, `operator_note: "Esta planta aguanta más seca..."` (literal castellano, respetado). | **Cartela superpuesta** (2s): `MissionPatch validated` |
| 1:48–1:50 | Plano cerrado del móvil. **VO** (cerrada, una frase): *"Lo que la persona dice se convierte en política."* (9 palabras castellano). | — |

**Lo que se siente:** una voz humana real entrando al sistema y siendo respetada. La frase coloquial *"aguanta más seca de lo que crees"* se conserva literal en `operator_note` — eso es honestidad: el sistema no resume al humano, lo cita. Pollen traduce intuición agrícola a parámetro técnico sin recortar.

**VO:** 9 palabras castellano + 14 palabras voz humana real castellano = 23 palabras totales castellano en escena.
**Cartelas:** 1 (`MissionPatch validated`).
**Overlays:** ninguno obligatorio.
**Producción:** **Pendiente llamada con Floema** para definir UI del compilador y output visual exacto del `MissionPatch` en pantalla del móvil. La voz humana se graba antes del rodaje principal (con tiempo para que Pollen la procese y muestre el patch en pantalla durante la escena).

---

### Escena 6 — Ferry A→B (1:50–2:10)

**Beat narrativo:** una parcela tiene ojos al cielo, la otra no. Pero ambas reciben el mismo conocimiento, porque alguien lo lleva. Es la federación demostrada en una acción física: corte limpio entre dos planos del mismo Rhizome haciendo dos roles. La frase fuerte 5 cierra el bloque sobre el plano del Rhizome B aceptando el digest.

**Cronología:**

| t | Acción / VO | Cartela / Overlay |
|---|-------------|-------------------|
| 1:50–1:55 | Plano de la persona junto al **PLOT 1** (con la estación meteo conectada al Rhizome 01). El móvil descarga el `WeatherDigest` del Rhizome. Pantalla del móvil: lectura del digest viajando del Rhizome al teléfono. **VO**: *"Pollen trae preguntas, respuestas y contexto."* (6 palabras castellano). | **Cartela superpuesta** (2s): `WeatherDigest ferry` |
| 1:55–1:56 | **Corte limpio.** Sin pasos en plano. | — |
| 1:56–2:04 | Plano de la persona junto al **PLOT 2** (sin meteo, segunda zona de la terraza, distinta planta). Pollen entrega el digest al Rhizome 02. Pantalla del móvil: subida del paquete. Pantalla del Rhizome 02 (visible al fondo o en captura): *"WeatherDigest accepted. Source: Pollen ferry from rhizome_01."* | **Cartela en pantalla del Rhizome** (visible 4s): `WeatherDigest accepted · Source: rhizome_01` |
| 2:04–2:07 | Silencio breve. Plano del Rhizome 02 con el digest aceptado. La cámara respira. | — |
| 2:07–2:10 | **VO** (sentencia, plana): *"Pollen convierte esas visitas en inteligencia federada."* (8 palabras castellano, **frase fuerte 5**). | — |

**Lo que se siente:** Pollen es **portador de más que voz humana**. Lleva también meteorología. Las dos parcelas viven en el mismo terreno pero no se hablan — Pollen las hace hablar. El "esas" de la frase fuerte 5 hace eco directo a "cada visita" de escena 4: coherencia interna.

**VO:** 14 palabras castellano (6 + 8).
**Cartelas:** 2 (`WeatherDigest ferry` + `WeatherDigest accepted · Source: rhizome_01` en pantalla del Rhizome).
**Overlays:** ninguno.
**Producción:** rotación del Rhizome físico entre PLOT 1 y PLOT 2. Estación meteo se conecta para PLOT 1 y se retira para PLOT 2. Carteles físicos "PLOT 1" y "PLOT 2" visibles en sus respectivas tomas. Misma persona en plano (continuidad).

---

### Escena 7 — Criterion updated (2:10–2:30)

**Beat narrativo:** el sistema acaba de cambiar de criterio. Tres bloques de evidencia visual en cadencia musical (no log JSON masivo) muestran qué cambió. La cartela ancla aterriza dominante. Después, acción física con riego más corto que en escena 2 — la diferencia hace el trabajo narrativo.

**Cronología:**

| t | Acción / VO | Cartela / Overlay |
|---|-------------|-------------------|
| 2:10–2:13 | Pantalla del Jetson llenando el plano. Fondo casi negro. **Bloque 1** entra: `MissionPatch accepted` con `id: mp_004` y `ttl: 21600s`. Cadencia musical (1 línea por segundo). | — |
| 2:13–2:16 | **Bloque 2** entra: `Policy diff` con dos campos resaltados (color cálido sobre log gris): `soil_thresholds.dry: 35 → 25`, `daily_budget_ml: 1500 → 900`. | — |
| 2:16–2:19 | **Bloque 3** entra: `Next decision changed` con `policy_id: pol_009 → pol_010`, `final_action: 12s`, `why_short: "Mission compiled from human voice"` (en inglés on-screen). | — |
| 2:19–2:22 | Cartela ancla central (3s): *"Criterion updated."* — tipografía editorial, dominante sobre los tres bloques que quedan al fondo en gris atenuado. | **Cartela central** (3s): *"Criterion updated."* |
| 2:22–2:30 | Salida al campo. Plano de la maceta y la válvula. Se abre. **Pero menos tiempo que en escena 2** — chorro corto, controlado, austero (12s real). El espectador recuerda inconscientemente que la primera vez fue largo. **VO** sobre el plano del agua: *"El sistema ajusta los cuidados."* (5 palabras castellano). | — |

**Lo que se siente:** el cambio del sistema es **prueba compuesta**, no afirmación. Los tres bloques son evidencia técnica honesta. La cartela ancla traduce la evidencia para el no técnico. La diferencia con escena 2 (chorro largo entonces, chorro corto ahora) cierra el arco con acción física.

**VO:** 5 palabras castellano (sobrio radical).
**Cartelas:** 1 dominante (*"Criterion updated."*) + 3 bloques de evidencia técnica en pantalla.
**Overlays:** ninguno.
**Producción:** captura de pantalla del Jetson real (Xilema corre el sistema) o mock fiel del log con los tres bloques diseñados con dirección de arte fina (resaltado fuerte de los dos campos del `diff`, cadencia de 1 bloque cada 3s). La válvula con chorro **visiblemente más corto** que en escena 2 (cronometrar: 12s en E7 vs 18s en E2).

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

### Escena 9 — Cenital federado (2:40–3:00)

**Pendiente de apilar — esperando decisión firme Meristem día 14.**

Si Meristem-nodo entra al MVP (decisión Bea + Cambium + Meristem día 14), la escena se amplía con plano breve del portátil del agricultor mostrando `PolicyPacket` + `rationale` en castellano antes de o intercalado con el cenital de las 8 parcelas. La cartela progresiva *"One plot. Two. Eight. Autonomous. Federated intelligence, carried by Pollen."* se mantiene tal cual.

Si Meristem-nodo no entra, la escena se mantiene exactamente como está en `docs/40_pitch_video.md §4`: Veo3 flat editorial, 8 parcelas en cenital, Pollen-nodo recorriendo, mensajes en pantalla, cartela progresiva, tarjeta logo final con subtítulo *"Local, safe, explainable decisions."*

**Recurso disponible (Cambium, día 14):** la frase invariante de Xilema *"Lo físico manda, Rhizome arbitra, Pollen media, Meristem afina."* puede usarse como cartela esquina o VO en escena 9 si Meristem entra al MVP — los cuatro sujetos quedan visibles en el video. Si Meristem no entra, la frase pierde uno de los sujetos y queda solo como recurso writeup. Decisión condicional al día 14.

---

## Conteo VO actualizado (escenas 1-8 apiladas, escena 9 pending)

VO en castellano grabado por Bea. Cartelas/overlays/textos on-screen en inglés (regla de proyecto v1.1).

- E1: 0 palabras (silencio + dos cartelas inglés).
- E2: 31 palabras castellano (13 + 10 + 8).
- E3: 11 palabras castellano.
- E4: 14 palabras castellano (6 + 8 frase fuerte 2).
- E5: 9 palabras castellano VO + **14 palabras voz humana real** castellano.
- E6: 14 palabras castellano (6 + 8 frase fuerte 5).
- E7: 5 palabras castellano (sobrio).
- E8: 8 palabras castellano (frase fuerte 4 sin "En Sprout").
- E9: pending — cartela progresiva + subtítulo logo, sin VO esperado.
- **Total apilado v1.2:** 92 palabras castellano + 14 voz humana real = **106 palabras totales castellano**. Margen sigue holgado para doblaje EN.

---

## Pendientes antes de grabar

- [x] Apilar escenas 1-3 (día 13). Apilar escenas 4, 5 (parcial), 6, 7, 8 (día 14).
- [ ] **Escena 9** pendiente de decisión firme Meristem (día 14, conversación Bea + Cambium + Meristem).
- [ ] **Llamada con Floema** para sincronizar UI del compilador `MissionPatch` en escena 5 (Floema cerró F5 — agendable cuando os cuadre).
- [ ] Ejercicio de calidad narrativa con Cambium (30 min, día 14): pasar las cinco frases fuertes por el filtro *"¿el vídeo demuestra esto, o solo lo afirma?"*. Ahora con escenas 2-8 apiladas, el ejercicio puede cotejar literal contra cada plano.
- [x] Persona VO castellano confirmada: **Bea**.
- [ ] Confirmar voz humana de escena 5 (propuesta: persona del equipo grabando literal en castellano).
- [ ] **Refinar traducciones inglés** marcadas como *first pass* (cartela ancla E7 *"Criterion updated."*, cartela progresiva E9, subtítulo logo).
- [ ] Producir cartel físico **"PLOT 1"** y **"PLOT 2"** (impresión sobria, tipografía limpia) antes del rodaje 26-27.
- [ ] Coordinar dirección de arte de la pantalla del Jetson en escenas 2, 3, 7 (resaltado fuerte de campos clave, cadencia musical de líneas, cartelas dominantes sobre log).
- [ ] **Decidir si aplicar invariante Xilema** *"Physical layer rules. Rhizome arbitrates. Pollen mediates. Meristem refines."* como cartela en escena 9 — condicional a decisión Meristem.

---

## Historial de versiones

- **v1.2 — apilado parcial extendido** (2026-04-29, día 14, Corola) — apilado de escenas 4, 5 (parcial), 6, 7, 8 con detalle equivalente al de escenas 1-3. Escena 5 con TBD en UI del compilador `MissionPatch` pendiente de llamada con Floema (F5 cerrada). Escena 9 pendiente de decisión firme Meristem (conversación Bea + Cambium + Meristem día 14): si Meristem-nodo entra al MVP, se amplía con plano breve del portátil del agricultor; si no entra, se mantiene como en pitch doc. Recurso disponible para escena 9: invariante de Xilema *"Lo físico manda, Rhizome arbitra, Pollen media, Meristem afina."* — aplicable como cartela inglés *"Physical layer rules. Rhizome arbitrates. Pollen mediates. Meristem refines."* solo si Meristem entra (cuatro sujetos visibles en video). Conteo VO: 92 palabras castellano + 14 voz humana real = 106 palabras totales. Origen del recado Meristem: Cambium tras review meeting día 13 (`bitacora/2026-04-28_review-meeting-tuning_cambium.md`).
- **v1.1 — apilado parcial** (2026-04-28, día 13, Corola) — ajustes tras review de Bea en PR #59:
  - Eliminada referencia al hackathon y al jurado del encabezado del documento (decisión: no documentos públicos con datos sensibles).
  - **Regla nueva del proyecto:** cartelas/overlays/textos on-screen en inglés. VO castellano grabado por Bea. Aplicado a las cartelas de escenas 1, 2, 3 (la cartela bilingüe de E1 pasa a inglés solo; *"Cuando duda, riega menos"* → *"When in doubt, water less."*). Cartelas de escenas 4-9 traducidas como first pass — refinar al apilar.
  - **Escena 1 ampliada:** añadida cartela inicial *"Imagine this pot is a whole plot."* como invitación al espectador antes de la cartela ya existente. Reorganizado el desglose temporal (0:00-0:06 plano sin cartela / 0:06-0:11 cartela 1 / 0:11-0:16 cartela 2 / 0:16-0:20 plano final).
  - **Cartel físico "PLOT 1"** en/junto a la maceta como elemento de producción visible desde escena 1 y coherente con los IDs `rhizome_01` y `rhizome_02`.
  - Persona VO castellano confirmada: Bea.
- **v1.0 — apilado parcial inicial** (2026-04-28, día 13, Corola) — primer apilado real en `script.md` tras el pivote v2 (día 8 Bea), las decisiones del día 11 y los seis cambios del día 12. Escenas 1, 2, 3 desarrolladas con detalle.
- **v0.x descartados** — versiones del v0 cerradas en PRs #40/#41 sin merge tras pivote v2 día 8. Principios autorales que sobreviven al pivote anclados en `bitacora/2026-04-26_corola-guion-cerrado-conceptual_corola.md`.
