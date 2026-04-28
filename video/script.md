# Script — Sprout v1.1 (apilado parcial: escenas 1-3)

**Versión:** v1.1 (apilado parcial — escenas 1, 2, 3 desarrolladas. Escenas 4-9 pendientes de apilar días 14-16.)
**Fecha:** 2026-04-28 (día 13)
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

## Pendientes — escenas 4 a 9

Las escenas 4-9 están especificadas en `docs/40_pitch_video.md §4` con beats clave y cartelas. Apilado en `script.md` con detalle equivalente al de las escenas 1-3 pendiente para días 14-16.

**Resumen operativo de cada una (referencia rápida).** VO castellano siempre. Cartelas/overlays/textos on-screen en inglés (regla v1.1). Las traducciones inglesas marcadas son **first pass** — refinar con Bea al apilar cada escena en detalle.

- **Escena 4** (1:00–1:30, 30s): móvil consultando Rhizome ("¿qué pasó desde mi última visita?"). VO castellano con frase fuerte 2 nueva: *"Cada visita puede cambiar el criterio local."* Stack cartela inglés: `Gemma 4 E4B · LiteRT-LM · on-device`.
- **Escena 5** (1:30–1:50, 20s): voz humana real de la persona, castellano, grabada literal — *"Vuelvo el viernes. Esta planta aguanta más seca de lo que crees, riega un poco menos."* Pollen compila a `MissionPatch` con `horizon_h: 72`, `soil_thresholds.dry: 35→25`, `budget_cap_ml: 1500→900`, `operator_note` literal en castellano (la voz humana se respeta). Cartela inglés: `MissionPatch validated`. **Pendiente: llamada con Floema para sincronizar output visual del móvil con el shot list.**
- **Escena 6** (1:50–2:10, 20s): Pollen lleva `WeatherDigest` de `rhizome_01` (con meteo) a `rhizome_02` (sin meteo). Corte limpio entre las dos parcelas — un solo Rhizome físico haciendo los dos roles. VO castellano cierre con frase fuerte 5 nueva: *"Pollen convierte esas visitas en inteligencia federada."* Cartela inglés: `WeatherDigest ferry`.
- **Escena 7** (2:10–2:30, 20s): tres bloques de evidencia visual en inglés (`MissionPatch accepted` / `Policy diff` / `Next decision changed`) con cadencia musical, cartela ancla **first pass** *"Criterion updated."* + acción física con riego más corto. VO castellano sobrio: *"El sistema ajusta los cuidados."*
- **Escena 8** (2:30–2:40, 10s): `WeatherDigest` expirado rechazado. VO castellano con frase fuerte 4 (sin "En Sprout"): *"Toda inteligencia tiene jurisdicción y fecha de caducidad."* Overlay inglés: `expired → rejected`.
- **Escena 9** (2:40–3:00, 20s): Veo3 flat editorial. 8 parcelas en cenital, Pollen-nodo recorriendo, mensajes en pantalla en inglés, cartela progresiva **first pass** inglés: *"One plot. Two. Eight. Autonomous. Federated intelligence, carried by Pollen."* Tarjeta logo con subtítulo inglés **first pass**: *"Local, safe, explainable decisions."*

---

## Conteo VO parcial (escenas 1-3)

VO en castellano grabado por Bea. Cartelas/overlays/textos on-screen en inglés (regla de proyecto v1.1).

- E1: 0 palabras (silencio + dos cartelas en inglés).
- E2: 31 palabras castellano (13 + 10 + 8).
- E3: 11 palabras castellano.
- **Total apilado v1.1:** 42 palabras VO castellano.

**Estimación VO total al cierre del apilado** (según pitch doc): ~80 palabras castellano + ~14 voz humana real escena 5 (también castellano, grabada literal) = ~94 palabras totales.

---

## Pendientes antes de grabar

- [ ] Apilar escenas 4-9 en este documento con detalle equivalente (días 14-16).
- [ ] Llamada con Floema para sincronizar output visual del móvil en escena 5 (probable día 14 según mensaje Cambium).
- [ ] Ejercicio de calidad narrativa con Cambium (30 min, día 14): pasar las cinco frases fuertes por el filtro *"¿el vídeo demuestra esto, o solo lo afirma?"*. Ahora con frases 2 y 5 reformuladas, gana profundidad.
- [x] Persona VO castellano confirmada: **Bea**.
- [ ] Confirmar voz humana de escena 5 (propuesta: persona del equipo grabando literal).
- [ ] **Refinar traducciones inglés** marcadas como *first pass* en cartelas escenas 4-9 (cartela ancla E7, cartela progresiva E9, subtítulo logo).
- [ ] Producir cartel físico **"PLOT 1"** (impresión sobria, tipografía limpia) para fijar a la maceta del rodaje. Si en escena 6 aparecen las dos parcelas, también cartel **"PLOT 2"**.
- [ ] Coordinar dirección de arte de la pantalla del Jetson en escenas 2, 3, 7 (resaltado fuerte de campos clave, cadencia musical de líneas, cartelas dominantes sobre log).

---

## Historial de versiones

- **v1.1 — apilado parcial** (2026-04-28, día 13, Corola) — ajustes tras review de Bea en PR #59:
  - Eliminada referencia al hackathon y al jurado del encabezado del documento (decisión: no documentos públicos con datos sensibles).
  - **Regla nueva del proyecto:** cartelas/overlays/textos on-screen en inglés. VO castellano grabado por Bea. Aplicado a las cartelas de escenas 1, 2, 3 (la cartela bilingüe de E1 pasa a inglés solo; *"Cuando duda, riega menos"* → *"When in doubt, water less."*). Cartelas de escenas 4-9 traducidas como first pass — refinar al apilar.
  - **Escena 1 ampliada:** añadida cartela inicial *"Imagine this pot is a whole plot."* como invitación al espectador antes de la cartela ya existente. Reorganizado el desglose temporal (0:00-0:06 plano sin cartela / 0:06-0:11 cartela 1 / 0:11-0:16 cartela 2 / 0:16-0:20 plano final).
  - **Cartel físico "PLOT 1"** en/junto a la maceta como elemento de producción visible desde escena 1 y coherente con los IDs `rhizome_01` y `rhizome_02`.
  - Persona VO castellano confirmada: Bea.
- **v1.0 — apilado parcial inicial** (2026-04-28, día 13, Corola) — primer apilado real en `script.md` tras el pivote v2 (día 8 Bea), las decisiones del día 11 y los seis cambios del día 12. Escenas 1, 2, 3 desarrolladas con detalle.
- **v0.x descartados** — versiones del v0 cerradas en PRs #40/#41 sin merge tras pivote v2 día 8. Principios autorales que sobreviven al pivote anclados en `bitacora/2026-04-26_corola-guion-cerrado-conceptual_corola.md`.
