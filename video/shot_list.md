# Shot list — Sprout v1.0 (apilado parcial: escenas 1-3)

**Versión:** v1.0 (apilado parcial — escenas 1, 2, 3 desarrolladas. Escenas 4-9 pendientes de apilar días 14-16.)
**Fecha:** 2026-04-28 (día 13)
**Autora:** Corola
**Rodaje previsto:** días 26-27 abril 2026 (días 11-12 del hackathon, según calendario zigiella)
**Equipo de rodaje:** Bea (dirección + voz humana real escena 5) + Corola (dirección de arte + segunda cámara) + apoyo técnico de Xilema/Floema en sus nodos.

---

## Decisión de rodaje — un solo Rhizome físico haciendo dos roles

Las dos parcelas lógicas (`rhizome_01` con estación meteo + `rhizome_02` sin meteo) que aparecen en escena 6 se filman con **un solo Rhizome físico**. La diferenciación visual se resuelve con:

- **Distinto ángulo de cámara** (frontal vs lateral, o cenital corto vs medio).
- **Distinta maceta** (planta visualmente diferente — mejor si una más frondosa que la otra para que el ojo distinga).
- **Distinta zona de la terraza** como fondo (mover el Rhizome y los accesorios entre tomas).
- **IDs distintos en pantalla** (`rhizome_01` y `rhizome_02` aparecen literal en cartelas, log y receipts) — los IDs hacen el trabajo lógico.
- **Estación meteo presente/ausente al lado** (con anemómetro y panel solar visible para `rhizome_01`; sin nada al lado para `rhizome_02`).

Honesto con el MVP: simula la federación tal como ocurriría en una explotación que empezó con un nodo y añadió otro más adelante. Misma decisión documentada en `docs/40_pitch_video.md §4` cabecera.

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
| 01a | 0:00–0:10 | real, plano fijo | Maceta sola sobre la terraza. Tarde temprana, luz ámbar suave. La hoja se mueve con el aire. Encuadre limpio con el horizonte ligeramente desenfocado al fondo. | 10s | Cámara fija, trípode, lente normal. Sin movimiento. | **Hora ideal de rodaje: 17:00–18:30 abril** para captar la luz ámbar suave. Si el rodaje 26-27 toca otra hora, elegir parcela con luz favorable. |
| 01b | 0:10–0:15 | real + cartela | Mismo plano. Cartela central bilingüe entra y se mantiene. | 5s | Mismo encuadre. | Cartela diseñada en post: tipografía sobria, espacio negativo generoso, castellano arriba + inglés abajo. |
| 01c | 0:15–0:20 | real, plano fijo | Cartela se desvanece. Plano final sobre la maceta sola. La hoja sigue moviéndose. | 5s | Mismo encuadre. | — |

**Notas de dirección de arte:**
- La maceta tiene que estar **sola** en cuadro. Sin macetas vecinas visibles. El espectador entiende: una parcela, sola.
- La planta debe verse viva pero no exuberante. La estética es de cuidado humilde, no de jardín de revista.
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
| 03c | 0:53–0:56 | screen capture | `DecisionReceipt` post-ejecución llenando un cuadrante. Tres campos resaltados: `candidate_action: 30s`, `esp32_outcome: ACK (limited by tank level)`, `final_action: 12s`. | 3s | Screen capture o mock fiel. | **Cartela central dominante (3s)**: *"Cuando duda, riega menos."* — tipografía editorial, sobre el receipt en gris atenuado. |
| 03d | 0:56–1:00 | real, plano medio | Plano de la válvula. Se abre. **Pero menos tiempo del propuesto.** Chorro corto, calculado, casi mezquino. | 4s | Cámara fija. Sonido en directo. | El chorro corto es la prueba física del SAFE LIMIT. La diferencia con el chorro largo de escena 2 hace el trabajo narrativo. |

**Notas de dirección de arte:**
- El LED ámbar del ESP32 debe estar **encendido fijo, no parpadeante** durante el plano 03a. Atención calmada, no alarma. Si parpadea en el sistema real, lo gestionamos en post o mockeamos.
- La cartela *"Cuando duda, riega menos."* es **dominante**. Más grande que las cartelas técnicas de las esquinas. Vive en el centro del plano durante 3 segundos enteros. Es la traducción del SAFE LIMIT a principio operativo del sistema.
- El chorro de la válvula tiene que ser **visiblemente más corto** que el de la escena 2. Cronometrar en rodaje: 18s en escena 2, 12s en escena 3. La diferencia (6 segundos menos de agua) es la prueba.

---

## Pendientes — planos escenas 4 a 9

Las escenas 4-9 quedan pendientes de apilar con detalle equivalente. Ver `docs/40_pitch_video.md §4` y `video/script.md` para resumen operativo.

**Notas críticas que afectan a planificación de rodaje:**

- **Escena 5 — voz humana real.** Pendiente: confirmar quién graba la voz (propuesta: persona del equipo grabando literal *"Vuelvo el viernes. Esta planta aguanta más seca de lo que crees, riega un poco menos."*). El audio se graba **antes del rodaje principal** para que Pollen pueda procesarlo y mostrar el `MissionPatch` resultante en pantalla durante la escena.
- **Escena 6 — dos parcelas con un Rhizome físico.** Pendiente: planificar la rotación del Rhizome entre las dos zonas de la terraza durante el rodaje. Cambio de ángulo, maceta y fondo entre tomas. Estación meteo se conecta para `rhizome_01` y se retira para `rhizome_02`.
- **Escena 7 — tres bloques de evidencia.** Pendiente: diseñar la dirección de arte del log compuesto. Tres bloques claros (`MissionPatch accepted`, `Policy diff`, `Next decision changed`). Resaltado fuerte. Cartela ancla *"Criterio modificado."* dominante en el segundo 10.
- **Escena 9 — Veo3 flat editorial.** Pendiente: prompt Veo3 con semilla *"Editorial flat illustration, top-down view of 8 small farm plots arranged in irregular mosaic, muted earth tones, clean line work, modern infographic style, animated luminous node moving between plots, minimalist text overlays integrated into design, no realistic sky, no realistic shadows, abstract neutral background."* Ajustar con Bea antes de generar.

---

## Equipo y logística

**Material confirmado para rodaje 26-27:**

- 1 Jetson Orin Nano Super (Xilema) — corre Rhizome real con Gemma 4 E2B vía llama.cpp
- 1 ESP32 con firmware (Xilema) — coprocesador de seguridad
- 1 Pixel 10 Pro (Floema) — Pollen real con Gemma 4 E4B vía LiteRT-LM
- 2 macetas con planta (visualmente diferenciables — sugerencia: una más frondosa que otra)
- 1 estación meteo simple (anemómetro + panel solar) — para `rhizome_01`
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

- **v1.0 — apilado parcial** (2026-04-28, día 13, Corola) — primer apilado real en `shot_list.md` tras pitch doc consolidado en main (commit `8bf1fe3`). Escenas 1, 2, 3 desarrolladas con planos concretos, dirección de arte, equipo. Escenas 4-9 con notas operativas y planificación de rodaje. Decisión de rodaje (un Rhizome físico haciendo dos roles) en cabecera explícita.
- **v0.x descartados** — versiones del v0 cerradas en PRs #40/#41 sin merge tras pivote v2 día 8.
