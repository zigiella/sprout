# Shot list — Sprout v1.5 (apilado completo: escenas 1-9)

**Versión:** v1.5 (día 16 — invariante traducción "prevails" confirmada, carteles físicos extendidos a maceta + caja electrónica, contingencia "sin meteo" anotada, refuerzo nombres de nodos en planos. Pendientes operativos: copies bilingües ES/EN, formato Xylem para montaje, captura real Pollen/Floema en E5, refinar traducciones first pass.)
**Fecha:** 2026-05-01 (día 16)
**Autora:** Corola
**Rodaje previsto:** días 26-27 abril 2026
**Equipo de rodaje:** Bea (dirección + VO castellano + posible voz humana real escena 5) + Corola (dirección de arte + segunda cámara) + apoyo técnico de Xilema/Floema en sus nodos.

**Regla de idiomas (proyecto v1.1):** todas las cartelas, overlays, textos on-screen y el cartel físico van en **inglés**. VO en **castellano** (Bea).

---

## Decisión de rodaje — un solo Rhizome físico haciendo dos roles

Las dos parcelas lógicas (`rhizome_01` con estación meteo + `rhizome_02` sin meteo) que aparecen en escena 6 se filman con **un solo Rhizome físico**. La diferenciación visual se resuelve con:

- **Cartel físico identificador en la maceta** — **"PLOT_01 with RHIZOME_01"** en la primera (visible desde escena 1), **"PLOT_02 with RHIZOME_02"** en la segunda (aparece en escena 6). Impresión sobria, tipografía limpia, fijado a la maceta o clavado al lado en estaca.
- **Cartel físico en la caja de la electrónica** (Jetson + ESP32) — **"RHIZOME_01"** y **"RHIZOME_02"** respectivamente. Identifica el nodo en su contenedor físico. Refuerza el nombre del nodo en el plano material — coherente con los IDs `rhizome_01` y `rhizome_02` en pantalla.
- Decisión Bea día 16: los carteles físicos anclan la identidad lógica de cada parcela y cada nodo en el plano físico, hacen la diferenciación inmediata para el espectador, y refuerzan los nombres de los nodos durante todo el rodaje.
- **Distinto ángulo de cámara** (frontal vs lateral, o cenital corto vs medio).
- **Distinta planta** (visualmente diferente — mejor si una más frondosa que la otra para que el ojo distinga).
- **Distinta zona de la terraza** como fondo (mover el Rhizome y los accesorios entre tomas).
- **IDs distintos en pantalla** (`rhizome_01` y `rhizome_02` aparecen literal en cartelas, log y receipts) — los IDs hacen el trabajo lógico, y el cartel físico hace el trabajo visual.
- **Estación meteo presente/ausente al lado** (con anemómetro y panel solar visible para `rhizome_01` (PLOT_01); sin nada al lado para `rhizome_02` (PLOT_02)). **Posible contingencia (decisión Bea día 16, no firme):** si prescindimos de meteo, las dos parcelas se quedan sin estación; la diferencia entre ellas pasa a ser solo el ID y el ángulo. Decisión condicional.

Honesto con el MVP: simula la federación tal como ocurriría en una explotación que empezó con un nodo y añadió otro más adelante. Misma decisión documentada en `docs/40_pitch_video.md §4` cabecera.

**Producción:** preparar **cuatro carteles físicos** antes del rodaje — los prepara Bea (Helvetica, mayúsculas, fondo neutro, en inglés):
- **2 carteles de maceta:** "PLOT_01 with RHIZOME_01" y "PLOT_02 with RHIZOME_02"
- **2 carteles de caja electrónica:** "RHIZOME_01" y "RHIZOME_02"

Pueden ser laminados o estampados sobre madera/cartón rígido. El estilo debe ser sobrio (no rotulación de huerto turístico, no infantil), coherente con la estética técnica del proyecto. Los carteles de caja van fijados a la cajita Jetson+ESP32 (cinta o etiqueta) — visibles cuando se filme el primer plano del Rhizome.

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
| 01a | 0:00–0:06 | real, plano fijo | Maceta sola sobre la terraza con cartel físico **"PLOT_01 with RHIZOME_01"** visible (laminado, sobrio, junto a la maceta o fijado a ella). Tarde temprana, luz ámbar suave. La hoja se mueve con el aire. Encuadre limpio con el horizonte ligeramente desenfocado al fondo. | 6s | Cámara fija, trípode, lente normal. Sin movimiento. | **Hora ideal de rodaje: 17:00–18:30 abril** para captar la luz ámbar suave. El cartel "PLOT_01 with RHIZOME_01" debe ser legible al primer vistazo pero no dominar el plano. |
| 01b | 0:06–0:11 | real + cartela | Mismo plano. Cartela central inglés entra. | 5s | Mismo encuadre. | **Cartela central** (5s): *"Imagine this pot is a whole plot."* Tipografía sobria, espacio negativo generoso. Es invitación al espectador y contrato narrativo: aceptar el truco visual. |
| 01c | 0:11–0:16 | real + cartela | Mismo plano. Primera cartela se desvanece, entra la segunda. | 5s | Mismo encuadre. | **Cartela central** (5s): *"This plot is visited periodically by a human."* Afirmación sobre la parcela ya aceptada. |
| 01d | 0:16–0:20 | real, plano fijo | Cartela se desvanece. Plano final sobre la maceta sola con el cartel "PLOT_01 with RHIZOME_01" visible. La hoja sigue moviéndose. | 4s | Mismo encuadre. | — |

**Notas de dirección de arte:**
- La maceta tiene que estar **sola** en cuadro, con su cartel "PLOT_01 with RHIZOME_01". Sin macetas vecinas visibles. El espectador entiende: una parcela, sola, identificada.
- La planta debe verse viva pero no exuberante. La estética es de cuidado humilde, no de jardín de revista.
- El cartel **"PLOT_01 with RHIZOME_01"** debe estar diseñado para coherencia con la estética técnica del proyecto — tipografía limpia (Helvetica/Inter o similar), todo mayúsculas, sobre fondo neutro (blanco roto, beige, kraft natural). No rotulación de huerto turístico.
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
| 04a | 1:00–1:06 | real, plano medio | Cambio de luz. Persona entra en plano con móvil en la mano. **No vemos su cara** — vemos manos y móvil. Cartel **"PLOT_01 with RHIZOME_01"** visible al fondo + cartel **"RHIZOME_01"** en la caja electrónica. La persona se acerca a la maceta. | 6s | Cámara con plano medio. Estabilizador para seguir el movimiento de la persona. | Continuidad: misma persona que aparecerá en escenas 5 y 6. Cara siempre fuera de plano o en perfil borroso (agnóstico al portador). |
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

**Producción crítica: rotación del Rhizome físico entre PLOT_01 y PLOT_02 en la misma terraza.** Cambio de ángulo, planta, fondo y conexión de la estación meteo. Carteles físicos "PLOT_01 with RHIZOME_01" y "PLOT_02 with RHIZOME_02" visibles + cartel "RHIZOME_01" / "RHIZOME_02" en la caja electrónica respectivamente. **El cartel de la caja se cambia físicamente entre tomas** (etiqueta intercambiable o impresión en tarjeta clipable) para reflejar el ID lógico, aunque el hardware sea el mismo.

| Plano | t | Tipo | Descripción | Duración | Cámara / Equipo | Notas |
|-------|---|------|-------------|----------|-----------------|-------|
| 06a | 1:50–1:53 | real, plano medio | Persona junto a **PLOT_01** (cartel maceta "PLOT_01 with RHIZOME_01" visible + cartel caja electrónica "RHIZOME_01" + estación meteo conectada con anemómetro y panel solar). El móvil descarga el `WeatherDigest`. | 3s | Cámara plano medio, persona y maceta + estación meteo + caja electrónica en cuadro. | Estación meteo visible al lado del Rhizome 01. **Cartela superpuesta** (2s): `WeatherDigest ferry`. |
| 06b | 1:53–1:55 | real + screen | Pantalla del móvil: lectura del `WeatherDigest` viajando del Rhizome al teléfono. **VO** sobre el plano: *"Pollen trae preguntas, respuestas y contexto."* (6 palabras castellano). | 2s | Captura cerrada al móvil. | El digest en pantalla muestra: `source_type: rhizome_with_station`, `window_h: 24`, `summary: "Bajada térmica nocturna"`. Texto on-screen en inglés. |
| 06c | 1:55–1:56 | corte limpio | **Corte seco.** Sin transición, sin pasos en plano. | 1s | — | Decisión narrativa: el ferry no se ve en el desplazamiento. Se ve la entrega. |
| 06d | 1:56–2:00 | real, plano medio | Persona junto a **PLOT_02** (cartel maceta "PLOT_02 with RHIZOME_02" visible + cartel caja electrónica "RHIZOME_02", **sin estación meteo**, distinta planta, distinta zona de la terraza, distinto ángulo de cámara). Pollen entrega el digest al Rhizome 02. | 4s | Plano medio. La diferencia visual respecto a 06a tiene que ser inmediata. | **Verificación de continuidad antes del corte:** misma persona, mismo móvil. Lo que cambia es cartel de caja (RHIZOME_01 → RHIZOME_02), planta, ángulo, fondo, ausencia de estación meteo. **Si Bea decide prescindir de meteo (contingencia día 16):** el plano se queda sin estación tampoco en 06a, y la diferencia se sostiene solo en cartel + planta + ángulo. |
| 06e | 2:00–2:04 | screen capture | Pantalla del Rhizome 02 (visible al fondo o en captura) mostrando: *"WeatherDigest accepted. Source: Pollen ferry from rhizome_01."* | 4s | Captura cerrada o sobre la pantalla del Jetson 02. | **Cartela en pantalla del Rhizome** (visible 4s): `WeatherDigest accepted · Source: rhizome_01`. La frase explicita que viene de la otra parcela. |
| 06f | 2:04–2:07 | real | Silencio breve. Plano del Rhizome 02 con el digest aceptado. La cámara respira. | 3s | Mismo encuadre que 06d. | Espacio para que el espectador asimile. |
| 06g | 2:07–2:10 | real | **VO** (sentencia, plana, cerrada): frase fuerte 5 — *"Pollen convierte esas visitas en inteligencia federada."* (8 palabras castellano). | 3s | Mismo encuadre. | El "esas" hace eco a "cada visita" de escena 4. Coherencia interna del par frase 2 ↔ frase 5. |

**Notas de dirección de arte:**
- Las dos parcelas tienen que **distinguirse visualmente al primer vistazo**. PLOT_01 con estación meteo + planta más frondosa; PLOT_02 sin estación + planta más sobria. La rotación física del Rhizome entre las dos zonas es solo el cerebro — los IDs en pantalla, los carteles físicos de maceta y los carteles de caja (RHIZOME_01 / RHIZOME_02) hacen el trabajo lógico. **Si prescindimos de meteo (contingencia día 16):** las dos parcelas se distinguen solo por cartel + planta + ángulo, sin estación.
- El corte 1:55–1:56 **es seco**. No fade, no cross-dissolve. Decisión narrativa del día 11.
- Los IDs `rhizome_01` y `rhizome_02` deben aparecer **literal en pantalla** durante 06b y 06e respectivamente. Coherencia hardware/software/cartel físico.

---

### Escena 7 — Criterion updated (2:10–2:30)

| Plano | t | Tipo | Descripción | Duración | Cámara / Equipo | Notas |
|-------|---|------|-------------|----------|-----------------|-------|
| 07a | 2:10–2:13 | screen capture | Pantalla del Jetson llenando el plano. Fondo casi negro. **Bloque 1** entra: `MissionPatch accepted` con `id: mp_004` y `ttl: 21600s`. Cadencia musical (1 línea por segundo). | 3s | Captura del Jetson o mock fiel. | Resaltado fuerte: el bloque entra con color cálido sobre fondo gris. |
| 07b | 2:13–2:16 | screen capture | **Bloque 2** entra: `Policy diff` con dos campos resaltados: `soil_thresholds.dry: 35 → 25`, `daily_budget_ml: 1500 → 900`. Los demás campos atenuados. **Cartela esquina inferior derecha** entra a 2:14: invariante de jerarquías (4 líneas, tipografía técnica pequeña, paleta sobria). | 3s | Misma captura + diseño post de cartela esquina. | Los dos campos del diff son el corazón de la escena. Resaltado especialmente fuerte. **Cartela esquina inf. der.** (entra a 2:14, visible 5s — desaparece a 2:19): *"Physical layer prevails."* / *"Rhizome arbitrates."* / *"Pollen mediates."* / *"Meristem refines."* No compite con el diff (paleta sobria, tipografía pequeña, esquina). |
| 07c | 2:16–2:19 | screen capture | **Bloque 3** entra: `Next decision changed` con `policy_id: pol_009 → pol_010`, `final_action: 12s`, `why_short: "Mission compiled from human voice"`. La cartela esquina sigue visible. | 3s | Misma captura. | El `why_short` en inglés on-screen — explícitamente cita el origen humano de la decisión. |
| 07d | 2:19–2:22 | screen + cartela | Cartela ancla central (3s): *"Criterion updated."* — tipografía editorial, dominante. Los tres bloques quedan al fondo en gris atenuado. **La cartela esquina se desvanece a 2:19** cuando entra la ancla — no compiten. | 3s | Mismo plano con cartela superpuesta. | **Cartela central** (3s): *"Criterion updated."* — first pass, refinable con Bea. La salida de la cartela esquina con el fade de la cartela ancla son sincrónicos. |
| 07e | 2:22–2:30 | real, plano medio | Salida al campo. Plano de la maceta y la válvula. Se abre. Chorro corto, controlado, austero (12s real cronometrado vs 18s en escena 2). **VO** (5 palabras castellano): *"El sistema ajusta los cuidados."* | 8s | Cámara fija. Sonido en directo. | El chorro corto es la prueba física. **Cronometrar en rodaje: exactamente 12 segundos** de agua. La diferencia con la escena 2 (6s menos de agua) hace el trabajo narrativo. |

**Notas de dirección de arte:**
- **Cadencia musical de los tres bloques:** uno por segundo aproximado. No torrencial. Deliberada. El espectador puede leer cada bloque en su entrada.
- La cartela ancla *"Criterion updated."* es **first pass**. Refinable con Bea (alternativas: *"Policy modified"*, *"Criteria modified"*, *"Updated criterion"*).
- **Cartela esquina invariante de jerarquías** (07b-07c, 5s visibles): tipografía técnica pequeña, paleta sobria (gris medio o blanco roto sobre el fondo oscuro del log), esquina inferior derecha. **No compite** con el diff resaltado ni con la cartela ancla central. Es presencia textual sutil que **nombra el sistema entero** mientras se ve trabajando. Decisión Cambium ella día 15 (voto sí en ejercicio frases fuertes).
- **Traducción confirmada (voto Bea día 16):** *"Physical layer prevails."* / *"Rhizome arbitrates."* / *"Pollen mediates."* / *"Meristem refines."* — *"prevails"* gana sobre *"commands"* por claridad semántica manteniendo el ritmo de tripleta paralela.
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

### Escena 9 — Cenital federado + Meristem real (2:40–3:00)

**Decisión Meristem firme (día 14): entra al MVP.** Cenital flat editorial con 8 parcelas + Pollen-nodo recorriendo + llegada al nodo Meristem **en el cenital flat**. **Corte limpio** a imagen real del portátil del agricultor con app Meristem. Dos cartelas on-screen (*"Pulling Rhizome data..."* + *"Adjusting policies..."*). Tarjeta logo final por fade.

**Producción crítica:**
- **Cenital flat (Veo3):** prompt actualizado para incluir el nodo Meristem (más grande, forma distinta a las 8 parcelas, color complementario, ubicado más al centro del mosaico).
- **Corte 2:54–2:55:** seco, sin transición, sin fade. Quiebre estético deliberado.
- **Imagen real (2:55–3:00):** plano del portátil del agricultor abierto sobre una mesa doméstica (cocina o similar). Pantalla con app Meristem corriendo (Meristem la prepara) o mock fiel.

| Plano | t | Tipo | Descripción | Duración | Cámara / Equipo | Notas |
|-------|---|------|-------------|----------|-----------------|-------|
| 09a | 2:40–2:42 | real → Veo3 morph | Plano de la maceta del rodaje (continuidad con escena 8 si la pantalla del Jetson estaba en plano). **Morph sutil** durante 2 segundos: la maceta se difumina, los bordes se expanden, aparece la primera parcela del cenital flat. | 2s | Diseño post: morph generado o efecto de cross-dissolve hacia el frame inicial de Veo3. | El morph debe sentirse como "lo real se transforma en abstracción". Si Veo3 lo permite, prompt explícito de transición; si no, post-producción con keyframes. |
| 09b | 2:42–2:46 | Veo3 cenital flat | 8 parcelas apareciendo progresivamente en mosaico irregular sobre paleta tierra. Sin cielo realista, sin sombras realistas, fondo abstracto. Cartela dosificada sincronizada con la aparición. | 4s | Veo3 generado. | **Cartela progresiva (3 beats sincronizados con la aparición de las parcelas):** *"One plot."* (s1, primera parcela) → *"Two."* (s2, segunda) → *"Eight."* (s4, mosaico completo). Tipografía editorial integrada al diseño flat. |
| 09c | 2:46–2:48 | Veo3 cenital flat | Pollen-nodo aparece y arranca recorrido entre las parcelas. Movimiento limpio, no parpadeo agresivo. | 2s | Veo3 generado. | **Cartela** (2s, central): *"Autonomous."* |
| 09d | 2:48–2:51 | Veo3 cenital flat | Pollen-nodo recorre parcelas. **Mensajes técnicos breves** apareciendo y desapareciendo en cada toque del nodo (mismo lenguaje del proyecto): `WeatherDigest accepted`, `MissionPatch delivered`, `DecisionReceipt synced`. | 3s | Veo3 generado con texto integrado. | **Cartela cumbre** (3s, dominante): *"Federated intelligence, carried by Pollen."* |
| 09e | 2:51–2:54 | Veo3 cenital flat | Pollen-nodo **llega al nodo Meristem** dentro del cenital. El nodo Meristem está representado **distinto** a las 8 parcelas: más grande, forma diferente (triángulo o círculo donde las parcelas son rectángulos/cuadrados), color complementario. Pausa breve de conexión visual. | 3s | Veo3 generado. El nodo Meristem ubicado más al centro del mosaico o ligeramente desplazado para que el recorrido de Pollen tenga dirección. | El nodo Meristem es **el primer elemento del cenital que no es una parcela**. Visualmente marca al espectador que algo distinto pasa aquí. |
| **09f** | **2:54–2:55** | **CORTE LIMPIO** | **Cambio seco** de Veo3 flat a imagen real. Sin transición, sin fade. | 1s | — | Este corte es estructural. Lo abstracto demuestra el sistema funcionando a escala; lo real demuestra que el cerebro lento existe en una cocina. |
| 09g | 2:55–2:58 | real | Plano del **portátil del agricultor** abierto sobre una mesa doméstica (cocina o similar). Pantalla del portátil mostrando la app Meristem corriendo. Cartela on-screen integrada en la pantalla del portátil. | 3s | Cámara con plano medio del portátil sobre la mesa. Luz natural si es posible. Detalle pero no extremo close-up — el espectador tiene que entender que es un portátil real, no un mock cinematográfico. | **Cartela on-screen** (3s, en pantalla del portátil): *"Pulling Rhizome data..."* (con elipsis indicando proceso). El "..." es deliberado — sentir proceso en marcha. Idealmente la cartela aparece **dentro de la app Meristem** (parte de su UI), no superpuesta al plano. |
| 09h | 2:58–3:00 | real + tarjeta cierre | Pantalla del portátil cambia. Nueva cartela on-screen. **Tarjeta logo final** entra por fade sobre la imagen del portátil al final. | 2s | Mismo encuadre. | **Cartela on-screen** (2s): *"Adjusting policies..."* + **Tarjeta logo final** entrando por fade en los últimos 2s, visible sobre el portátil difuminado al fondo. |
| (cierre) | 3:00 | tarjeta logo final | Tarjeta logo visible 2-3s al final. Diseño post. | 2-3s | Diseño post. | **Tarjeta logo:** `Sprout` / *"Local, safe, explainable decisions."* / `zigiella · Apache 2.0` / `github.com/zigiella/sprout` |

**Notas de dirección de arte:**
- **Estilo flat editorial moderno:** paleta sobria de tierra (siena, tostado, ocre suave, blanco roto), contornos limpios, tipografía integrada al diseño (Helvetica, Inter o similar), sin cielo realista, sin sombras realistas, fondo abstracto neutro. La estética flat de la cartela progresiva conecta con la estética del cartel físico "PLOT 1" / "PLOT 2" del rodaje real (mismo registro tipográfico) — coherencia entre los dos mundos.
- **Pollen-nodo:** punto luminoso pequeño, animación de cadencia limpia (no parpadeo agresivo). Movimiento entre parcelas con trayectoria suave, no en línea recta robótica.
- **Nodo Meristem:** distinto a las 8 parcelas. Mi propuesta: forma de **círculo grande** (Pollen-nodo es punto pequeño, Meristem es disco), color complementario a la paleta tierra (azul muy desaturado o blanco roto destacado). Ubicado más al centro del mosaico o ligeramente desplazado al borde para que el recorrido de Pollen tenga dirección hacia él.
- **Mensajes técnicos en cenital (`WeatherDigest accepted`, `MissionPatch delivered`, `DecisionReceipt synced`):** aparecen brevemente al ritmo del Pollen-nodo tocando cada parcela. Tipografía limpia integrada al diseño flat. No saturan: cada mensaje aparece 1-1.5s y desaparece. 5 mensajes distribuidos a lo largo de los 3 segundos del recorrido (09d).
- **Corte 2:54–2:55:** **clave estructural del video.** Sin fade. Sin transición. El espectador siente "ahora estamos en otro mundo". El sonido también cambia bruscamente: del silencio puro del cenital flat al ambiente real doméstico (cocina, viento muy suave si la ventana está abierta).
- **Plano del portátil:** real, no estilizado. La estética cambia radicalmente respecto al cenital — eso es feature. Mesa de cocina, portátil normal, luz natural. La app Meristem en pantalla puede tener un diseño cuidado pero **fiel al MVP** que Meristem prepara, no maquillaje cinematográfico.
- **Cartelas on-screen del portátil:** idealmente aparecen **dentro de la app Meristem** como parte de su UI, no superpuestas al plano. Eso es más honesto: el espectador ve el sistema funcionando, no anotaciones del editor.
- **Tarjeta logo final:** entrando por fade sobre el portátil. La pantalla del portátil queda difuminada al fondo. La tarjeta domina los últimos 2s.

**Prompt Veo3 actualizado (con Meristem):**

> *"Editorial flat illustration, top-down view of 8 small farm plots arranged in irregular mosaic, muted earth tones, clean line work, modern infographic style, animated luminous small node moving between plots, larger central node distinct in shape (circle vs rectangles) and color (cool tone vs warm earth) representing a hub, the small node moves through several plots and finally connects to the larger central node, minimalist text overlays integrated into design (`WeatherDigest accepted`, `MissionPatch delivered`, `DecisionReceipt synced`), no realistic sky, no realistic shadows, abstract neutral background."*

Refinar con Bea antes de generar. La diferencia con el prompt v1.0 (que era cenital sin Meristem) es la adición del nodo central distinto y la trayectoria del Pollen-nodo terminando en él.

**Equipo y material adicional para escena 9:**
- Portátil del agricultor (puede ser el portátil de Meristem propiamente — coherencia técnica) con app Meristem corriendo
- Mesa doméstica (cocina o mesa de comedor) como fondo del plano real
- Luz natural si la hora del rodaje lo permite

**Recurso de Cambium NO aplicado en E9:** la cartela invariante de Xilema *"Physical layer rules. Rhizome arbitrates. Pollen mediates. Meristem refines."* queda **fuera de escena 9**. La escena ya tiene 9 elementos textuales en 20s (cartela progresiva en 3 beats + 5 mensajes técnicos en cenital + 2 cartelas on-screen del portátil + tarjeta logo). Añadir 4 líneas más de invariante satura. Queda como recurso writeup. Decisión documentada.

---

## Equipo y logística

**Material confirmado para rodaje 26-27:**

- 1 Jetson Orin Nano Super (Xilema) — corre Rhizome real con Gemma 4 E2B vía llama.cpp
- 1 ESP32 con firmware (Xilema) — coprocesador de seguridad
- 1 Pixel 10 Pro (Floema) — Pollen real con Gemma 4 E4B vía LiteRT-LM
- 2 macetas con planta (visualmente diferenciables — sugerencia: una más frondosa que otra)
- **4 carteles físicos identificadores** (los prepara Bea: Helvetica, mayúsculas, fondo neutro, en inglés):
  - 2 de maceta: **"PLOT_01 with RHIZOME_01"** y **"PLOT_02 with RHIZOME_02"**
  - 2 de caja electrónica: **"RHIZOME_01"** y **"RHIZOME_02"** (intercambiables/clipables sobre la cajita Jetson+ESP32 entre tomas)
- 1 estación meteo simple (anemómetro + panel solar) — para `rhizome_01` (PLOT_01) **— condicional, posible contingencia día 16: prescindir de meteo**
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

- **v1.5 — refuerzo nombres de nodos + traducción confirmada** (2026-05-01, día 16, Corola) — cuatro cambios tras mensaje de Bea día 16:
  1. **Traducción invariante E7:** *"Physical layer prevails."* (swap "commands" → "prevails") confirmado por Bea.
  2. **Carteles físicos extendidos** — 4 carteles en lugar de 2: maceta (`PLOT_01 with RHIZOME_01` / `PLOT_02 with RHIZOME_02`) + caja electrónica (`RHIZOME_01` / `RHIZOME_02`, intercambiables). Refuerzo de nombres en plano físico durante todo el rodaje.
  3. **Contingencia "sin meteo"** anotada en E6 + sección decisión rodaje + equipo material — decisión Bea pendiente.
  4. **Refuerzo de nombres de nodos** en planos 04a, 06a, 06d, descripción decisión rodaje.
- **v1.4 — invariante de jerarquías en E7** (2026-04-30, día 15, Corola) — añadida cartela esquina inferior derecha en plano 07b (entra a 2:14, visible 5s, desaparece a 2:19 cuando entra la cartela ancla central). Cuatro líneas tipografía técnica pequeña paleta sobria. No compite con el diff resaltado ni con la cartela ancla. Decisión Cambium ella día 15. Coincide con propuesta Corola del ejercicio frases fuertes. Traducción first pass *"Physical layer commands."*; variante *"Physical layer prevails."* pendiente voto Bea.
- **v1.3 — apilado completo** (2026-04-29, día 14, Corola) — escena 9 reescrita con Meristem entrando al MVP (decisión firme Bea + Cambium + Meristem día 14). Estructura: cenital flat editorial con 8 parcelas + Pollen-nodo recorriendo + llegada al nodo Meristem en cenital, **corte limpio** a imagen real del portátil del agricultor con app Meristem ejecutando, dos cartelas on-screen (*"Pulling Rhizome data..."* + *"Adjusting policies..."*), tarjeta logo final por fade. Tres niveles narrativos en el cierre: máquina (E1-E7) → abstracción de red (E9 inicio) → cerebro lento doméstico real (E9 final). Prompt Veo3 actualizado para incluir nodo Meristem distinto a las 8 parcelas. Cartela invariante de Xilema NO aplicada — saturación de elementos textuales. Carteles físicos PLOT 1 / PLOT 2 los prepara Bea (Helvetica, mayúsculas, fondo neutro, inglés). Escena 5 con TBD UI compilador pendiente de coordinación asíncrona con Floema (mensaje preparado por Corola para que Bea relaye).
- **v1.2 — apilado parcial extendido** (2026-04-29, día 14, Corola) — apilado de escenas 4, 5 (parcial), 6, 7, 8 con detalle equivalente a 1-3. Escena 5 con TBD en UI del compilador `MissionPatch` pendiente de llamada con Floema (F5 cerrada). Escena 9 pendiente de decisión firme Meristem día 14: si entra al MVP, ampliación con plano portátil + `rationale`; si no entra, mantiene Veo3 flat puro. Recurso disponible para escena 9: invariante de Xilema *"Lo físico manda, Rhizome arbitra, Pollen media, Meristem afina."* (cartela inglés *"Physical layer rules. Rhizome arbitrates. Pollen mediates. Meristem refines."*) — aplicable solo si Meristem entra (cuatro sujetos visibles). Origen recado: Cambium tras review meeting día 13 (`bitacora/2026-04-28_review-meeting-tuning_cambium.md`).
- **v1.1 — apilado parcial** (2026-04-28, día 13, Corola) — ajustes tras review de Bea en PR #59:
  - **Regla de idiomas (proyecto):** cartelas/overlays/textos on-screen y cartel físico en inglés. VO en castellano (Bea).
  - **Cartel físico "PLOT 1" / "PLOT 2"** añadido como elemento de producción visible. PLOT 1 desde escena 1; PLOT 2 entra en escena 6. Coherencia con IDs `rhizome_01` y `rhizome_02` que aparecen en pantalla.
  - **Escena 1 reestructurada:** dos cartelas en cascada en lugar de una bilingüe. Beat 1 (0:00–0:06) plano sin cartela / Beat 2 (0:06–0:11) cartela *"Imagine this pot is a whole plot."* / Beat 3 (0:11–0:16) cartela *"This plot is visited periodically by a human."* / Beat 4 (0:16–0:20) plano final.
  - Cartela escena 3 *"Cuando duda, riega menos."* → *"When in doubt, water less."*.
  - Material para rodaje incluye los dos carteles físicos.
- **v1.0 — apilado parcial inicial** (2026-04-28, día 13, Corola) — primer apilado real en `shot_list.md` tras pitch doc consolidado en main (commit `8bf1fe3`). Escenas 1, 2, 3 desarrolladas. Decisión de rodaje (un Rhizome físico haciendo dos roles) en cabecera explícita.
- **v0.x descartados** — versiones del v0 cerradas en PRs #40/#41 sin merge tras pivote v2 día 8.
