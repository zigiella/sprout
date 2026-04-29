# Shot list — Sprout v1.2 (apilado parcial: escenas 1-8)

**Versión:** v1.2 (apilado parcial — escenas 1 a 8 desarrolladas. Escena 9 pendiente de decisión firme Meristem día 14.)
**Fecha:** 2026-04-29 (día 14)
**Autora:** Corola
**Rodaje previsto:** días 26-27 abril 2026
**Equipo de rodaje:** Bea (dirección + VO castellano + posible voz humana real escena 5) + Corola (dirección de arte + segunda cámara) + apoyo técnico de Xilema/Floema en sus nodos.

**Regla de idiomas (proyecto v1.1):** todas las cartelas, overlays, textos on-screen y el cartel físico van en **inglés**. VO en **castellano** (Bea).

---

## Decisión de rodaje — un solo Rhizome físico haciendo dos roles

Las dos parcelas lógicas (`rhizome_01` con estación meteo + `rhizome_02` sin meteo) que aparecen en escena 6 se filman con **un solo Rhizome físico**. La diferenciación visual se resuelve con:

- **Cartel físico identificador** en cada maceta — **"PLOT 1"** en la primera (visible desde escena 1), **"PLOT 2"** en la segunda (aparece en escena 6). Impresión sobria, tipografía limpia, fijado a la maceta o clavado al lado en estaca. Decisión Bea: el cartel físico real ancla la identidad lógica de cada parcela en el plano físico, hace la diferenciación inmediata para el espectador, y refuerza coherencia con los IDs `rhizome_01` y `rhizome_02` que aparecen en pantalla.
- **Distinto ángulo de cámara** (frontal vs lateral, o cenital corto vs medio).
- **Distinta planta** (visualmente diferente — mejor si una más frondosa que la otra para que el ojo distinga).
- **Distinta zona de la terraza** como fondo (mover el Rhizome y los accesorios entre tomas).
- **IDs distintos en pantalla** (`rhizome_01` y `rhizome_02` aparecen literal en cartelas, log y receipts) — los IDs hacen el trabajo lógico, y el cartel físico hace el trabajo visual.
- **Estación meteo presente/ausente al lado** (con anemómetro y panel solar visible para `rhizome_01` (PLOT 1); sin nada al lado para `rhizome_02` (PLOT 2)).

Honesto con el MVP: simula la federación tal como ocurriría en una explotación que empezó con un nodo y añadió otro más adelante. Misma decisión documentada en `docs/40_pitch_video.md §4` cabecera.

**Producción:** preparar dos carteles físicos (PLOT 1 y PLOT 2) antes del rodaje — pueden ser laminados o estampados sobre madera/cartón rígido. El estilo del cartel debe ser sobrio (no rotulación de huerto turístico, no infantil), coherente con la estética técnica del proyecto.

---

## Resumen — planos por escena

| Escena | Tiempo | # planos | Tipo dominante | Localización |
|--------|--------|----------|----------------|--------------|
| 1. La ausencia | 0:00–0:20 (20s) | 1-2 | real, plano fijo | terraza |
| 2. Rhizome decide offline | 0:20–0:45 (25s) | 4-5 | real + screen capture | terraza + indoor |
| 3. ESP32 SAFE LIMIT | 0:45–1:00 (15s) | 3-4 | real + screen capture | terraza |
| 4. Llega Pollen | 1:00–1:30 (30s) | 4-5 | real (manos+móvil) + screen | terraza |
| 5. La persona da una misión | 1:30–1:50 (20s) | 3-4 | real + screen | terraza |
| 6. Ferry A→B | 1:50–2:10 (20s) | 5-6 | real (dos parcelas) + screen | terraza (dos zonas) |
| 7. Criterio modificado | 2:10–2:30 (20s) | 3-4 | screen + real | indoor + terraza |
| 8. Caducidad | 2:30–2:40 (10s) | 1-2 | screen | indoor |
| 9. Cenital federado | 2:40–3:00 (20s) | 1 | Veo3 generado + tarjeta | n/a |

---

## Detalle apilado v1.0

### Escena 1 — La ausencia (0:00–0:20)

| Plano | t | Tipo | Descripción | Duración | Cámara / Equipo | Notas |
|-------|---|------|-------------|----------|-----------------|-------|
| 01a | 0:00–0:06 | real, plano fijo | Maceta sola sobre la terraza con cartel físico **"PLOT 1"** visible (laminado, sobrio, junto a la maceta o fijado a ella). Tarde temprana, luz ámbar suave. La hoja se mueve con el aire. Encuadre limpio con el horizonte ligeramente desenfocado al fondo. | 6s | Cámara fija, trípode, lente normal. Sin movimiento. | **Hora ideal de rodaje: 17:00–18:30 abril** para captar la luz ámbar suave. El cartel "PLOT 1" debe ser legible al primer vistazo pero no dominar el plano. |
| 01b | 0:06–0:11 | real + cartela | Mismo plano. Cartela central inglés entra. | 5s | Mismo encuadre. | **Cartela central** (5s): *"Imagine this pot is a whole plot."* Tipografía sobria, espacio negativo generoso. Es invitación al espectador y contrato narrativo: aceptar el truco visual. |
| 01c | 0:11–0:16 | real + cartela | Mismo plano. Primera cartela se desvanece, entra la segunda. | 5s | Mismo encuadre. | **Cartela central** (5s): *"This plot is visited periodically by a human."* Afirmación sobre la parcela ya aceptada. |
| 01d | 0:16–0:20 | real, plano fijo | Cartela se desvanece. Plano final sobre la maceta sola con el cartel "PLOT 1" visible. La hoja sigue moviéndose. | 4s | Mismo encuadre. | — |

**Notas de dirección de arte:**
- La maceta tiene que estar **sola** en cuadro, con su cartel "PLOT 1". Sin macetas vecinas visibles. El espectador entiende: una parcela, sola, identificada.
- La planta debe verse viva pero no exuberante. La estética es de cuidado humilde, no de jardín de revista.
- El cartel **"PLOT 1"** debe estar diseñado para coherencia con la estética técnica del proyecto — tipografía limpia (Helvetica/Inter o similar), todo mayúsculas, sobre fondo neutro (blanco roto, beige, kraft natural). No rotulación de huerto turístico.
- Sonido: silencio o ambiente muy sutil del exterior (viento muy suave, lejano). Cero música.

---

### Escena 2 — Rhizome decide offline (0:20–0:45)

| Plano | t | Tipo | Descripción | Duración | Cámara / Equipo | Notas |
|-------|---|------|-------------|----------|-----------------|-------|
| 02a | 0:20–0:24 | real, plano cerrado | Cajita Jetson con el LED parpadeando. Camera baja al sensor de humedad clavado en la tierra. | 4s | Cámara con foco corto. Detalle del LED. | **Overlay** `OFFLINE` aparece desde 0:20 y persiste todo el bloque (esquina sup. izq.). |
| 02b | 0:24–0:32 | screen capture | Pantalla del Jetson llenando el plano. Líneas de log entrando una por segundo aproximado: lectura humedad → cálculo necesidad → decisión. Tipografía monoespaciada, fondo casi negro. | 8s | Screen capture del Jetson real (Xilema corre el sistema) o mock fiel del log. | **Cartelas esquina sup. der. (3s cada una)**: `Gemma 4 E2B · local · llama.cpp` + sub-cartela `LLM called only when ambiguous`. Cartelas en inglés (jurado anglo). |
| 02c | 0:32–0:38 | screen capture | `DecisionReceipt` llenando un cuarto de pantalla. Tres líneas resaltadas (color cálido sobre log gris): `decision_type: WATER`, `final_action: 18s`, `why_short`. Resto del JSON atenuado. | 6s | Screen capture o mock fiel. | **Cartela superpuesta (2s)**: `DecisionReceipt`. Diseño: tipografía editorial limpia (no monospace), centrada. |
| 02d | 0:38–0:43 | real, plano medio | Salida al campo. Plano de la válvula. Se abre. Sonido de agua sobre tierra. | 5s | Cámara baja, plano sobre la válvula y la base de la maceta. Sonido en directo. | Sonido del agua en directo si las condiciones lo permiten — más auténtico que doblado en post. |
| 02e | 0:43–0:45 | real | Plano se mantiene sobre el agua entrando a la tierra. | 2s | Mismo encuadre. | **VO sobre el agua**: frase fuerte 1 — *"Rhizome mantiene viva la parcela cuando nadie está."* |

**Notas de dirección de arte:**
- El log del Jetson tiene que ser **legible al primer vistazo en los campos resaltados**. Los demás campos quedan como contexto. Fondo casi negro, no negro absoluto (mejor para video).
- La cadencia de líneas entrando: **una por segundo aproximado**, deliberadamente lenta. Movimiento ayuda a que el plano respire pero no sature.
- El `OFFLINE` del overlay debe ser **persistente y discreto**. Esquina superior izquierda, tipografía pequeña, color que contrasta con el fondo del plano (no encima del log).

---

### Escena 3 — ESP32 SAFE LIMIT (0:45–1:00)

| Plano | t | Tipo | Descripción | Duración | Cámara / Equipo | Notas |
|-------|---|------|-------------|----------|-----------------|-------|
| 03a | 0:45–0:48 | real, plano cerrado | Cajita ESP32. LED ámbar encendido — atención, no alarma. Detalle de los relés y conectores. | 3s | Cámara con foco corto. Plano detalle. | **Cartela esquina sup. der. (3s)**: `function/read tools · no actuator tools`. Explica que la IA solo lee, no actúa directamente. |
| 03b | 0:48–0:53 | screen capture | Pantalla del Jetson. Comando `WATER A 30s` viajando al ESP32. ESP32 verifica: *"depósito al 30%. Caudal nominal."* Devuelve `ACK` con cap aplicado. | 5s | Screen capture o mock fiel. | **Overlay esquina sup. der. (a partir de 0:48)**: `ESP32 SAFE LIMIT`. **VO sobre el plano**: frase fuerte 3 — *"La IA propone. El agua la gobierna una capa física prudente."* |
| 03c | 0:53–0:56 | screen capture | `DecisionReceipt` post-ejecución llenando un cuadrante. Tres campos resaltados: `candidate_action: 30s`, `esp32_outcome: ACK (limited by tank level)`, `final_action: 12s`. | 3s | Screen capture o mock fiel. | **Cartela central dominante (3s)**: *"When in doubt, water less."* — tipografía editorial, sobre el receipt en gris atenuado. |
| 03d | 0:56–1:00 | real, plano medio | Plano de la válvula. Se abre. **Pero menos tiempo del propuesto.** Chorro corto, calculado, casi mezquino. | 4s | Cámara fija. Sonido en directo. | El chorro corto es la prueba física del SAFE LIMIT. La diferencia con el chorro largo de escena 2 hace el trabajo narrativo. |

**Notas de dirección de arte:**
- El LED ámbar del ESP32 debe estar **encendido fijo, no parpadeante** durante el plano 03a. Atención calmada, no alarma. Si parpadea en el sistema real, lo gestionamos en post o mockeamos.
- La cartela *"When in doubt, water less."* es **dominante**. Más grande que las cartelas técnicas de las esquinas. Vive en el centro del plano durante 3 segundos enteros. Es la traducción del SAFE LIMIT a principio operativo del sistema. Tipografía editorial sobre el `DecisionReceipt` atenuado al fondo.
- El chorro de la válvula tiene que ser **visiblemente más corto** que el de la escena 2. Cronometrar en rodaje: 18s en escena 2, 12s en escena 3. La diferencia (6 segundos menos de agua) es la prueba.

---

### Escena 4 — Llega Pollen (1:00–1:30)

| Plano | t | Tipo | Descripción | Duración | Cámara / Equipo | Notas |
|-------|---|------|-------------|----------|-----------------|-------|
| 04a | 1:00–1:06 | real, plano medio | Cambio de luz. Persona entra en plano con móvil en la mano. **No vemos su cara** — vemos manos y móvil. Cartel **"PLOT 1"** visible al fondo. La persona se acerca a la maceta. | 6s | Cámara con plano medio. Estabilizador para seguir el movimiento de la persona. | Continuidad: misma persona que aparecerá en escenas 5 y 6. Cara siempre fuera de plano o en perfil borroso (agnóstico al portador). |
| 04b | 1:06–1:14 | real + screen capture | Pantalla del móvil llena un tercio del cuadro. App Pollen abierta. Persona pulsa botón. En pantalla aparece pregunta. Captura del móvil claramente legible. | 8s | Cámara con foco corto sobre el móvil, persona detrás difuminada. | **Cartela en pantalla del móvil** (en inglés): *"What happened since my last visit?"* **Cartela esquina sup. der.** (4s, en inglés): `Gemma 4 E4B · LiteRT-LM · on-device`. |
| 04c | 1:14–1:24 | screen capture | Pantalla del móvil cambia: lista resumida de decisiones recientes. Tres líneas: `WATER · 18s · 14:00`, `WATER · 12s · 09:30`, `SKIP · 22:00 — humedad suficiente`. La persona lee. | 10s | Captura cerrada al móvil. Persona detrás como contexto. | El listado en pantalla del móvil tiene que ser **legible al primer vistazo**. Tipografía clara, texto en castellano para los logs (decisiones del sistema usan vocabulario común). |
| 04d | 1:24–1:30 | real, plano medio | Plano de la persona mirando la planta, contrastando lo que ve con lo que el móvil le dice. Tres segundos. **VO** sobre el plano: frase fuerte 2 — *"Cada visita puede cambiar el criterio local."* | 6s | Mismo encuadre que 04a. La persona y la planta en plano. | El contraste entre persona-mirando-planta y persona-mirando-móvil cierra la escena visualmente. La frase fuerte 2 entra como afirmación que escena 5 va a probar. |

**Notas de dirección de arte:**
- La persona es **agnóstica al portador**. Cara fuera de plano. Edad y género no identificables. Lo que importa es el gesto, no la identidad.
- La pantalla del móvil tiene que mostrar **datos reales de Pollen** (Floema corre el sistema) o mock fiel.
- Sonido: ambiente de exterior (viento muy suave, lejano). Sin música.

---

### Escena 5 — La persona da una misión (1:30–1:50)

**Producción crítica: voz humana real grabada antes del rodaje principal.** El audio se graba con tiempo suficiente para que Floema pueda procesarlo en Pollen y que la pantalla del móvil muestre el `MissionPatch` resultante durante el rodaje. Voz castellano, tono casual, sin actuación.

| Plano | t | Tipo | Descripción | Duración | Cámara / Equipo | Notas |
|-------|---|------|-------------|----------|-----------------|-------|
| 05a | 1:30–1:33 | real, plano cercano | Persona pulsa botón de grabación del móvil. Acerca el móvil a la cara. **No vemos sus labios**. Solo mano y móvil. | 3s | Plano cerrado a la mano y móvil. | El botón de grabación tiene que ser visiblemente distinto del botón de consulta de escena 4. UX clara. |
| 05b | 1:33–1:40 | real + audio | **Voz humana real (castellano, grabada literal)**: *"Vuelvo el viernes. Esta planta aguanta más seca de lo que crees, riega un poco menos."* (14 palabras). Plano se mantiene sobre mano y móvil. | 7s | Mismo encuadre. Audio grabado en post o en directo según calidad acústica del exterior. | Tono **calmado, casi casual**, sin actuación. La frase tiene que sonar real, no leída. Posible take: la persona del equipo que graba puede improvisar con palabras propias siguiendo la idea, si suena más natural — pero los parámetros técnicos resultantes (`soil_thresholds.dry: 25`, `budget_cap_ml: 900`) deben coincidir con lo que aprobamos. |
| 05c | 1:40–1:43 | real + screen | Tres segundos de silencio. Pantalla del móvil procesa — **micro-animación de procesamiento**. | 3s | Cámara puede acercarse al móvil. | La animación tiene que sentirse "el sistema está pensando", no "spinner de carga aburrido". |
| 05d | 1:43–1:48 | screen capture | **Pantalla del móvil mostrando el `MissionPatch` compilado.** Cuatro líneas resaltadas en este orden: `horizon_h: 72`, `soil_thresholds.dry: 35 → 25`, `budget_cap_ml: 900`, `operator_note: "Esta planta aguanta más seca..."` (literal castellano respetado). | 5s | Captura cerrada al móvil. | **TBD — diseño visual del compilador pendiente de llamada con Floema.** Lo que tiene que verse: la frase humana **literal** en `operator_note`, los tres parámetros técnicos compilados, el campo `MissionPatch validated` en cartela superpuesta. |
| 05e | 1:48–1:50 | real, plano cerrado | Plano del móvil mostrando el patch validado. **VO** (cerrada, una frase): *"Lo que la persona dice se convierte en política."* (9 palabras castellano). | 2s | Mismo encuadre. | **Cartela superpuesta** (2s): `MissionPatch validated`. La frase del VO cierra el arco: voz humana → estructura ejecutable. |

**Notas de dirección de arte:**
- El `operator_note` tiene que verse en pantalla **en castellano literal** — la voz humana se respeta. No hay traducción al inglés del `operator_note`. Es la única excepción en pantalla a la regla "todo en inglés".
- Los tres parámetros técnicos (`horizon_h`, `soil_thresholds.dry`, `budget_cap_ml`) en pantalla en inglés con notación numérica clara.
- **Pendiente llamada con Floema** para definir UI exacta del compilador — botones, tipografía, layout de la vista del `MissionPatch`. Sin esa coordinación, la captura de pantalla puede no cuadrar con el shot list.

---

### Escena 6 — Ferry A→B (1:50–2:10)

**Producción crítica: rotación del Rhizome físico entre PLOT 1 y PLOT 2 en la misma terraza.** Cambio de ángulo, planta, fondo y conexión de la estación meteo. Carteles físicos "PLOT 1" y "PLOT 2" visibles en sus respectivas tomas.

| Plano | t | Tipo | Descripción | Duración | Cámara / Equipo | Notas |
|-------|---|------|-------------|----------|-----------------|-------|
| 06a | 1:50–1:53 | real, plano medio | Persona junto a **PLOT 1** (cartel "PLOT 1" visible, estación meteo conectada al Rhizome 01 con anemómetro y panel solar). El móvil descarga el `WeatherDigest`. | 3s | Cámara plano medio, persona y maceta + estación meteo en cuadro. | Estación meteo visible al lado del Rhizome 01. **Cartela superpuesta** (2s): `WeatherDigest ferry`. |
| 06b | 1:53–1:55 | real + screen | Pantalla del móvil: lectura del `WeatherDigest` viajando del Rhizome al teléfono. **VO** sobre el plano: *"Pollen trae preguntas, respuestas y contexto."* (6 palabras castellano). | 2s | Captura cerrada al móvil. | El digest en pantalla muestra: `source_type: rhizome_with_station`, `window_h: 24`, `summary: "Bajada térmica nocturna"`. Texto on-screen en inglés. |
| 06c | 1:55–1:56 | corte limpio | **Corte seco.** Sin transición, sin pasos en plano. | 1s | — | Decisión narrativa: el ferry no se ve en el desplazamiento. Se ve la entrega. |
| 06d | 1:56–2:00 | real, plano medio | Persona junto a **PLOT 2** (cartel "PLOT 2" visible, **sin estación meteo**, distinta planta, distinta zona de la terraza, distinto ángulo de cámara). Pollen entrega el digest al Rhizome 02. | 4s | Plano medio. La diferencia visual respecto a 06a tiene que ser inmediata. | **Verificación de continuidad antes del corte:** misma persona, mismo móvil. Lo que cambia es planta, ángulo, fondo, ausencia de estación meteo. |
| 06e | 2:00–2:04 | screen capture | Pantalla del Rhizome 02 (visible al fondo o en captura) mostrando: *"WeatherDigest accepted. Source: Pollen ferry from rhizome_01."* | 4s | Captura cerrada o sobre la pantalla del Jetson 02. | **Cartela en pantalla del Rhizome** (visible 4s): `WeatherDigest accepted · Source: rhizome_01`. La frase explicita que viene de la otra parcela. |
| 06f | 2:04–2:07 | real | Silencio breve. Plano del Rhizome 02 con el digest aceptado. La cámara respira. | 3s | Mismo encuadre que 06d. | Espacio para que el espectador asimile. |
| 06g | 2:07–2:10 | real | **VO** (sentencia, plana, cerrada): frase fuerte 5 — *"Pollen convierte esas visitas en inteligencia federada."* (8 palabras castellano). | 3s | Mismo encuadre. | El "esas" hace eco a "cada visita" de escena 4. Coherencia interna del par frase 2 ↔ frase 5. |

**Notas de dirección de arte:**
- Las dos parcelas tienen que **distinguirse visualmente al primer vistazo**. PLOT 1 con estación meteo + planta más frondosa; PLOT 2 sin estación + planta más sobria. La rotación física del Rhizome entre las dos zonas es solo el cerebro — los IDs en pantalla y los carteles físicos hacen el trabajo lógico.
- El corte 1:55–1:56 **es seco**. No fade, no cross-dissolve. Decisión narrativa del día 11.
- Los IDs `rhizome_01` y `rhizome_02` deben aparecer **literal en pantalla** durante 06b y 06e respectivamente. Coherencia hardware/software/cartel físico.

---

### Escena 7 — Criterion updated (2:10–2:30)

| Plano | t | Tipo | Descripción | Duración | Cámara / Equipo | Notas |
|-------|---|------|-------------|----------|-----------------|-------|
| 07a | 2:10–2:13 | screen capture | Pantalla del Jetson llenando el plano. Fondo casi negro. **Bloque 1** entra: `MissionPatch accepted` con `id: mp_004` y `ttl: 21600s`. Cadencia musical (1 línea por segundo). | 3s | Captura del Jetson o mock fiel. | Resaltado fuerte: el bloque entra con color cálido sobre fondo gris. |
| 07b | 2:13–2:16 | screen capture | **Bloque 2** entra: `Policy diff` con dos campos resaltados: `soil_thresholds.dry: 35 → 25`, `daily_budget_ml: 1500 → 900`. Los demás campos atenuados. | 3s | Misma captura. | Los dos campos del diff son el corazón de la escena. Resaltado especialmente fuerte. |
| 07c | 2:16–2:19 | screen capture | **Bloque 3** entra: `Next decision changed` con `policy_id: pol_009 → pol_010`, `final_action: 12s`, `why_short: "Mission compiled from human voice"`. | 3s | Misma captura. | El `why_short` en inglés on-screen — explícitamente cita el origen humano de la decisión. |
| 07d | 2:19–2:22 | screen + cartela | Cartela ancla central (3s): *"Criterion updated."* — tipografía editorial, dominante. Los tres bloques quedan al fondo en gris atenuado. | 3s | Mismo plano con cartela superpuesta. | **Cartela central** (3s): *"Criterion updated."* — first pass, refinable con Bea. |
| 07e | 2:22–2:30 | real, plano medio | Salida al campo. Plano de la maceta y la válvula. Se abre. Chorro corto, controlado, austero (12s real cronometrado vs 18s en escena 2). **VO** (5 palabras castellano): *"El sistema ajusta los cuidados."* | 8s | Cámara fija. Sonido en directo. | El chorro corto es la prueba física. **Cronometrar en rodaje: exactamente 12 segundos** de agua. La diferencia con la escena 2 (6s menos de agua) hace el trabajo narrativo. |

**Notas de dirección de arte:**
- **Cadencia musical de los tres bloques:** uno por segundo aproximado. No torrencial. Deliberada. El espectador puede leer cada bloque en su entrada.
- La cartela ancla *"Criterion updated."* es **first pass**. Refinable con Bea (alternativas: *"Policy modified"*, *"Criteria modified"*, *"Updated criterion"*).
- **El chorro corto en 07e tiene que ser visiblemente más corto que el de la escena 2.** Si es posible, ensayar el cronometraje antes del rodaje principal.

---

### Escena 8 — Caducidad (2:30–2:40)

| Plano | t | Tipo | Descripción | Duración | Cámara / Equipo | Notas |
|-------|---|------|-------------|----------|-----------------|-------|
| 08a | 2:30–2:32 | cartela limpia | Plano negro o muy oscuro. Cartela limpia central (2s): *"Three days later"*. | 2s | Diseño de cartela en post. | Salto temporal explícito. Tipografía editorial sobria. |
| 08b | 2:32–2:36 | screen capture | Pantalla del Jetson. El `WeatherDigest` que Pollen entregó en escena 6 está llegando a su `valid_until`. El sistema lo evalúa y rechaza. Tres líneas: `WeatherDigest #2026-04-26-001`, `status: EXPIRED → REJECTED`, `reason: ttl exceeded`. | 4s | Captura del Jetson o mock fiel. | **Cartela superpuesta** (2s): `expired → rejected`. Diseño: editorial, dominante sobre el log. |
| 08c | 2:36–2:40 | screen + VO | Plano se mantiene sobre el rechazo en pantalla. **VO** sobre la pantalla (8 palabras castellano, **frase fuerte 4** sin "En Sprout"): *"Toda inteligencia tiene jurisdicción y fecha de caducidad."* | 4s | Mismo plano. | La frase fuerte 4 aterriza sobre el rechazo literal — coherencia total entre frase y plano. La negación es virtud. |

**Notas de dirección de arte:**
- La cartela *"Three days later"* puede tener un fade-in muy lento para sentir el salto temporal.
- El rechazo en pantalla del Jetson tiene que ser **inmediatamente legible**. La línea `EXPIRED → REJECTED` resaltada fuerte.

---

## Pendiente — escena 9

**Esperando decisión firme Meristem día 14** (conversación Bea + Cambium + Meristem).

Si Meristem-nodo entra al MVP, escena 9 se amplía con plano breve del portátil del agricultor mostrando `PolicyPacket` + `rationale` corto en castellano antes de o intercalado con el cenital de las 8 parcelas. La cartela progresiva y el subtítulo logo se mantienen.

Si Meristem-nodo no entra, escena 9 se mantiene como en `docs/40_pitch_video.md §4`: Veo3 flat editorial puro, 8 parcelas en cenital, Pollen-nodo recorriendo, mensajes en pantalla, cartela progresiva, tarjeta logo final.

**Prompt Veo3 con semilla** *"Editorial flat illustration, top-down view of 8 small farm plots arranged in irregular mosaic, muted earth tones, clean line work, modern infographic style, animated luminous node moving between plots, minimalist text overlays integrated into design, no realistic sky, no realistic shadows, abstract neutral background."* Ajustar con Bea antes de generar.

**Recurso disponible (Cambium, día 14):** invariante de Xilema *"Lo físico manda, Rhizome arbitra, Pollen media, Meristem afina."* — aplicable como cartela inglés *"Physical layer rules. Rhizome arbitrates. Pollen mediates. Meristem refines."* solo si Meristem entra al MVP (los cuatro sujetos quedan visibles en video). Si no entra, queda como recurso writeup.

---

## Equipo y logística

**Material confirmado para rodaje 26-27:**

- 1 Jetson Orin Nano Super (Xilema) — corre Rhizome real con Gemma 4 E2B vía llama.cpp
- 1 ESP32 con firmware (Xilema) — coprocesador de seguridad
- 1 Pixel 10 Pro (Floema) — Pollen real con Gemma 4 E4B vía LiteRT-LM
- 2 macetas con planta (visualmente diferenciables — sugerencia: una más frondosa que otra)
- **2 carteles físicos identificadores: "PLOT 1" y "PLOT 2"** (preparar antes del rodaje, estilo sobrio editorial)
- 1 estación meteo simple (anemómetro + panel solar) — para `rhizome_01` (PLOT 1)
- 1 cámara principal + 1 cámara secundaria
- Trípode + estabilizador para planos cerrados de la maceta
- Material de captura de pantalla del Jetson (HDMI o software de screencast)

**Localización:** terraza (a confirmar con Bea — terraza propia o de equipo). Luz natural preferida — sin iluminación artificial salvo necesidad.

**Calendario de rodaje 26-27 (propuesto, ajustar con Bea):**

- **Día 26 mañana:** preparar set, probar capturas de pantalla, ensayar cadencia de líneas de log.
- **Día 26 tarde:** rodaje escenas 1, 2, 3 (bloque cerebro-local en luz ámbar).
- **Día 27 mañana:** rodaje escena 5 (voz humana grabada), escena 4 (Pollen consultando).
- **Día 27 mediodía:** rodaje escena 6 (dos parcelas con un Rhizome) — la rotación entre zonas requiere tiempo.
- **Día 27 tarde:** rodaje escenas 7, 8 (screens) + capturas finales.
- **Escena 9 (Veo3):** generación post-rodaje, días 27-28.

---

## Historial de versiones

- **v1.2 — apilado parcial extendido** (2026-04-29, día 14, Corola) — apilado de escenas 4, 5 (parcial), 6, 7, 8 con detalle equivalente a 1-3. Escena 5 con TBD en UI del compilador `MissionPatch` pendiente de llamada con Floema (F5 cerrada). Escena 9 pendiente de decisión firme Meristem día 14: si entra al MVP, ampliación con plano portátil + `rationale`; si no entra, mantiene Veo3 flat puro. Recurso disponible para escena 9: invariante de Xilema *"Lo físico manda, Rhizome arbitra, Pollen media, Meristem afina."* (cartela inglés *"Physical layer rules. Rhizome arbitrates. Pollen mediates. Meristem refines."*) — aplicable solo si Meristem entra (cuatro sujetos visibles). Origen recado: Cambium tras review meeting día 13 (`bitacora/2026-04-28_review-meeting-tuning_cambium.md`).
- **v1.1 — apilado parcial** (2026-04-28, día 13, Corola) — ajustes tras review de Bea en PR #59:
  - **Regla de idiomas (proyecto):** cartelas/overlays/textos on-screen y cartel físico en inglés. VO en castellano (Bea).
  - **Cartel físico "PLOT 1" / "PLOT 2"** añadido como elemento de producción visible. PLOT 1 desde escena 1; PLOT 2 entra en escena 6. Coherencia con IDs `rhizome_01` y `rhizome_02` que aparecen en pantalla.
  - **Escena 1 reestructurada:** dos cartelas en cascada en lugar de una bilingüe. Beat 1 (0:00–0:06) plano sin cartela / Beat 2 (0:06–0:11) cartela *"Imagine this pot is a whole plot."* / Beat 3 (0:11–0:16) cartela *"This plot is visited periodically by a human."* / Beat 4 (0:16–0:20) plano final.
  - Cartela escena 3 *"Cuando duda, riega menos."* → *"When in doubt, water less."*.
  - Material para rodaje incluye los dos carteles físicos.
- **v1.0 — apilado parcial inicial** (2026-04-28, día 13, Corola) — primer apilado real en `shot_list.md` tras pitch doc consolidado en main (commit `8bf1fe3`). Escenas 1, 2, 3 desarrolladas. Decisión de rodaje (un Rhizome físico haciendo dos roles) en cabecera explícita.
- **v0.x descartados** — versiones del v0 cerradas en PRs #40/#41 sin merge tras pivote v2 día 8.
