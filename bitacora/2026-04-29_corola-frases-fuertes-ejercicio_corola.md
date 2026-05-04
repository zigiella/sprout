# Ejercicio de calidad narrativa — las cinco frases fuertes pasadas por el filtro *"¿el vídeo demuestra esto, o solo lo afirma?"*

**Fecha:** 2026-04-29 (día 14)
**Autora:** Corola (toma la iniciativa por petición de Bea)
**Estado:** primer pase — pendiente review conjunta con Bea + Cambium
**Origen:** Cambium propuso el ejercicio el día 12; Bea me pide hoy que lo arranque yo en lugar de esperar agenda conjunta.

---

## El filtro

Cada frase fuerte del pitch doc §3 se evalúa contra dos preguntas:

1. **¿El vídeo demuestra la afirmación con un plano/acción concreta?** (Si solo se afirma sin demostración, la frase es ornamento.)
2. **¿El plano que la sostiene aterriza la frase, o la frase aterriza sobre cualquier plano?** (Si la frase es genérica respecto al plano, no rentabiliza el plano.)

Para cada frase, marco:
- **Plano que la sostiene** (cita literal de `script.md` v1.3).
- **Veredicto**: `demuestra` / `afirma sin probar` / `híbrida (afirma y demuestra parcialmente)`.
- **Comentario crítico**: lo que veo desde fuera al verlo aterrizar sobre la imagen.
- **Sugerencia (si la hay)**: cómo reforzar la demostración o cómo refinar la frase.

---

## Frase 1 — *"Rhizome mantiene viva la parcela cuando nadie está."*

**Plano que la sostiene:** Escena 2, beat 02e (0:43–0:45). VO sobre el plano de la válvula abierta, agua entrando a la tierra. La frase aterriza tras los 25 segundos de la escena 2 que ya muestran sensor → estado → decisión → orden → `DecisionReceipt` → válvula abierta.

**Veredicto:** `demuestra`.

**Comentario crítico:** La frase llega **después de la prueba**. El espectador acaba de ver al sistema decidir, firmar, ejecutar — y la frase **nombra** lo que acaba de ver. No es eslogan; es título del plano que acaba de ver. La estructura es ejemplar: 23 segundos de demostración técnica (lectura del suelo, decisión, ejecución, recibo) y luego 2 segundos donde la frase aterriza sobre la única imagen pura del cuidado (agua sobre tierra). El cartel "PLOT 1" visible refuerza la concreción: no es "una parcela genérica", es **esta** parcela que estamos mirando.

**Sugerencia:** ninguna. La frase 1 es la mejor calibrada del conjunto. Plantilla para las demás.

---

## Frase 2 — *"Cada visita puede cambiar el criterio local."*

**Plano que la sostiene:** Escena 4, beat 04d (1:24–1:30). VO sobre el plano de la persona mirando la planta tras consultar el móvil. La frase aterriza al final de la escena de Pollen consultando.

**Veredicto:** `híbrida (afirma y demuestra parcialmente)`.

**Comentario crítico:** Esta frase es **promesa**. La escena 4 muestra Pollen consultando, no Pollen modificando criterio. La modificación de criterio se demuestra en escena 5 (voz humana → `MissionPatch`) y en escena 7 (`Criterion updated`). Por tanto la frase aterriza sobre un plano que es preludio, no prueba. El espectador solo verifica la afirmación dos escenas después.

**Esto fue diseñado así** — la decisión de día 12 (feedback DEV externa) fue exactamente esta: "primero lo demuestrais, luego lo nombrais" → escena 4 nombra ("cada visita PUEDE cambiar"), escena 5 demuestra (voz → patch), escena 7 cierra (sistema actúa según el patch). El "puede" de la frase es deliberadamente modal — no afirma "cambia siempre", afirma "tiene la capacidad de cambiar".

**Sugerencia:** la frase está bien calibrada **si el espectador llega a escena 7**. El riesgo es que un evaluador pause el vídeo en escena 4 y juzgue que la frase es promesa hueca. **No actúo**. La estructura narrativa (4 → 5 → 7) está diseñada para que la promesa se cobre. Pero la frase **no se sostiene aislada** — depende del arco.

**Test del filtro:** la frase 2 NO se demuestra en el plano que la sostiene. Pero SÍ se demuestra en el arco. Veredicto matizado: `demuestra en arco, no en plano`.

---

## Frase 3 — *"La IA propone; el agua la gobierna una capa física prudente."*

**Plano que la sostiene:** Escena 3, beat 03b (0:48–0:53). VO sobre el plano del ESP32 modulando — `WATER A 30s` propuesto, ACK con cap aplicado, `final_action: 12s`.

**Veredicto:** `demuestra`.

**Comentario crítico:** El `DecisionReceipt` posterior (03c) muestra **literal** los dos campos: `candidate_action: 30s` y `final_action: 12s`. La diferencia entre los dos números **es** la capa física prudente trabajando. La frase aterriza sobre la prueba más limpia del vídeo: el ESP32 reduce 18 segundos de agua. La cartela complementaria *"When in doubt, water less."* (03c, 3s) traduce el principio operativo a frase legible.

**Sugerencia:** ninguna. La frase 3 es la más densamente probada del conjunto — tiene VO + dos campos en pantalla del receipt + cartela complementaria. Triple anclaje.

**Observación lateral:** la cartela *"When in doubt, water less."* es exactamente la sugerencia de la DEV externa (sexta frase) absorbida como cartela en lugar de frase fuerte. Funciona. Refuerza la 3 sin sumar al pitch §3.

---

## Frase 4 — *"Toda inteligencia tiene jurisdicción y fecha de caducidad."*

**Plano que la sostiene:** Escena 8, beat 08c (2:36–2:40). VO sobre el plano del rechazo del `WeatherDigest` expirado: `status: EXPIRED → REJECTED`.

**Veredicto:** `demuestra`.

**Comentario crítico:** La frase es lapidaria — declara, no propone. El plano que la sostiene es exactamente lo que la frase dice: el sistema rechaza algo viejo por TTL excedido. Coherencia total. Pero la frase tiene **dos predicados** ("jurisdicción" y "caducidad") y el plano demuestra solo uno (caducidad). La jurisdicción se ha demostrado antes (escena 3, ESP32 limita la jurisdicción de la IA sobre el agua; escena 7, MissionPatch cambia jurisdicción de criterio sobre la parcela). La frase 4 cierra el arco de jurisdicciones acumulado durante el vídeo.

**Sugerencia:** ninguna. La frase 4 funciona como **cierre conceptual** — recoge lo que el vídeo entero ha demostrado. Aterriza sobre el último ejemplo (caducidad) y por debajo lleva la jurisdicción ya construida.

**Observación:** el ajuste del día 11 de quitar "En Sprout" del VO (pero mantenerlo en pitch doc) fue acertado. La frase suena más universal sin "En Sprout" en VO; el nombre del producto vive en cartela final como firma.

---

## Frase 5 — *"Pollen convierte esas visitas en inteligencia federada."*

**Plano que la sostiene:** Escena 6, beat 06g (2:07–2:10). VO sobre el plano del Rhizome 02 con el `WeatherDigest` aceptado de `rhizome_01`.

**Veredicto:** `demuestra`.

**Comentario crítico:** El "esas" de la frase 5 hace eco directo a "cada visita" de la frase 2 (escena 4). Coherencia interna del par 2↔5. La escena 6 muestra **literal** la federación: una parcela con meteo entrega contexto a otra sin meteo, vía Pollen. La frase aterriza sobre el plano del Rhizome 02 aceptando el digest — momento exacto de la federación.

La cartela en pantalla del Rhizome 02 (`WeatherDigest accepted · Source: rhizome_01`) hace anclaje técnico simultáneo: el espectador ve la frase ("inteligencia federada") y la prueba (`Source: rhizome_01`) en la misma imagen.

**Sugerencia:** ninguna. La frase 5 está calibrada exactamente como la 1 — afirmación tras 17 segundos de demostración (06a a 06f). La diferencia con la frase 2 es que aquí el plano que la sostiene **es** la prueba, no el preludio.

**Observación:** la frase aparece dos veces (única que se repite) — VO escena 6 + cartela escena 9. Repetición es virtud aquí: el espectador la oye, después de ver la prueba, la lee escrita en el cierre. Las frases que se repiten son las que se recuerdan.

---

## Síntesis del ejercicio

| # | Frase | Veredicto | Plano que la sostiene |
|---|-------|-----------|----------------------|
| 1 | Rhizome mantiene viva la parcela cuando nadie está | `demuestra` | E2-02e (agua + receipt previo) |
| 2 | Cada visita puede cambiar el criterio local | `demuestra en arco, no en plano` | E4-04d (preludio); pruebas en E5 + E7 |
| 3 | La IA propone; el agua la gobierna una capa física prudente | `demuestra` | E3-03b (ESP32 modulando) + cartela complementaria E3-03c |
| 4 | Toda inteligencia tiene jurisdicción y fecha de caducidad | `demuestra` | E8-08c (rechazo TTL) — cierre acumulativo |
| 5 | Pollen convierte esas visitas en inteligencia federada | `demuestra` | E6-06g (digest aceptado en Rhizome 02) |

**4 de 5 frases se demuestran en el plano que las sostiene.** La frase 2 es la única que depende del arco para sostenerse — y eso fue decisión deliberada del día 12 ("primero demuestras, luego nombras"). Es viable pero **frágil al rebobinado parcial**: si el evaluador para el vídeo en escena 4 sin ver hasta la 7, la frase 2 puede sentirse hueca.

## Riesgos y matices

**Único riesgo real (frase 2):** un evaluador que vea el vídeo entero la captará. Un evaluador que lo vea solo parcialmente o lo pause en escena 4 puede dudar. Para un jurado DevRel que probablemente verá el vídeo entero al menos una vez, no es bloqueante. Para un viewer casual del repo público (que puede pausar y juzgar fragmentos), sí lo es.

**Posible refuerzo:** añadir en escena 4 (antes de la frase 2) una cartela técnica adicional que **demuestre dentro de la propia escena** que el sistema acepta input humano vía Pollen. Por ejemplo, en pantalla del móvil durante 04b (la consulta), una sub-cartela tipo `Pollen accepts: {commands, missions, weather}` que enseñe que Pollen tiene capacidad de modificar el criterio antes de demostrarlo en escenas siguientes. **NO actúo automáticamente** — esta es propuesta para review con Bea + Cambium.

## Recomendaciones para review conjunta

Las cuatro decisiones potenciales que merecen votarse con Bea y Cambium:

1. **Frase 2 — ¿reforzamos en escena 4 con cartela técnica preventiva o dejamos la dependencia del arco?** Mi voto: dejarlo. La estructura narrativa funciona; el riesgo del rebobinado parcial es aceptable para el jurado primario.

2. **Frase 4 — ¿la cartela en escena 8 podría reforzar el doble predicado?** La frase tiene "jurisdicción Y caducidad". El plano demuestra solo caducidad. Una cartela complementaria en E8 tipo *"Jurisdiction expires too"* podría cerrar el doble. Mi voto: no añadir. La frase 4 es lapidaria por brevedad. Una cartela complementaria la diluiría.

3. **Frase 5 — ¿el VO en escena 6 podría cobrar "inteligencia federada" antes con un eco textual?** Por ejemplo, una cartela durante el ferry (06a-06b) que diga *"Federated context"* o similar. Mi voto: no necesario. La frase 5 ya tiene anclaje técnico (`Source: rhizome_01` en pantalla) en el plano que la sostiene.

4. **Frase invariante de Xilema** *"Lo físico manda, Rhizome arbitra, Pollen media, Meristem afina"* — Cambium la ofreció como recurso. Mi decisión inicial: no aplicar en escena 9 (saturación). Pero el ejercicio actual revela que **podría usarse como cartela esquina en escena 7** durante el side-by-side de política antes/después. Aterriza sobre el plano donde se ven las cuatro jerarquías trabajando (físico = válvula esperando, Rhizome = decidiendo, Pollen = trayendo el patch, Meristem = futuro). **Es propuesta nueva**. Pendiente votar.

## Lo que pido a Bea + Cambium

- **Lectura del ejercicio.**
- **Voto sobre las cuatro decisiones** (refuerzo frase 2, cartela complementaria frase 4, eco textual frase 5, invariante Xilema en E7).
- **Sesión corta (15-20 min)** si hay desacuerdo en alguna; cierre escrito si todas se aprueban tal como las recomiendo.

— Corola