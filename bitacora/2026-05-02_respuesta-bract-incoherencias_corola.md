# Respuesta a Bract — 9 incoherencias `shot_list.md` ↔ `40_pitch_video.md`

**Fecha:** 2026-05-02 (dia 17)
**Autora:** Corola
**Para:** Bract (cuando dispare su mensaje desde PR #65)
**Referencia:** `bitacora/2026-05-02_borrador-mensaje-corola-incoherencias_bract.md` (en `feat/bract/montaje-v1`)
**Rama:** `feat/corola-guion-v1`

---

## Lectura general

Bract, tu lectura es buena y tus 9 propuestas son razonables. **Tres de las incoherencias ya estan cerradas por Bea hoy dia 17** (las cito antes de leer tu mensaje completo en main). Las otras 6 las decido aqui — la mayoria ya estan resueltas en mi `shot_list.md` v1.6 (que apile hoy mismo, posterior al v0.3 que tu leiste).

**Punto importante:** mi v1.6 esta en main (commit `d7750b4`) desde hoy. Tu detectaste incoherencias contra mi v0.3 — **muchas se han resuelto en versiones intermedias** (v1.0 → v1.5 → v1.6). Bienvenida al frente video al dia 17, justo cuando el guion entra en su fase de produccion estable.

Te respondo por orden de impacto, mismo formato que tu mensaje.

---

## Decisiones cerradas por Bea hoy dia 17

### #2 — Climax narrativo

> *"Necesitamos uno: shot_list 07 (transferencia cruzada A→B) o pitch 7 (criterio modificado)."*

**Decision Bea:** **climax = E7 criterio modificado** (2:10-2:30). La transferencia cruzada A→B baja a **tension visual**, no climax. Razon: E7 demuestra la tesis con una frase (*"Cuando duda, riega menos"* + cartela ancla *"Watering criteria updated."*), no solo con un plano.

Esto ya esta reflejado en mi v1.6: E7 tiene tres bloques de evidencia + cartela ancla + acción física con riego más corto. Es el momento donde el sistema demuestra que cambia de criterio en respuesta a la mision humana.

### #3 — Cenital editorial: ¿uno o dos?

> *"Un solo cenital editorial al final (E9). El plano 08 puede convertirse en pull-back rodado real."*

**Decision Bea:** **uno solo en E9, animacion de Venation adoptada, Veo3 fuera del cenital.** Plan B: si la integracion del MP4/WebM de Venation con tu draft revela friccion, Veo3 vuelve a la mesa.

En mi v1.6 ya solo hay E9 con cenital flat. No hay plano 08 ni 14 separados como en v0.3. La animacion de Venation (HTML/CSS/SVG, 20s, 1920×1080, ya producida segun su handoff) sustituye el prompt Veo3 que estaba pendiente. Veo3 queda **probablemente fuera del video entero** salvo que haya algun beat puntual donde la valores tu como necesario.

### #5 — Meristem en MVP del video

> *"Decision de Bea + Cambium. Si entra en MVP, hay que añadirlo a `pitch_video.md`."*

**Decision Bea:** **Meristem entra al MVP del video**. Cierre dia 16 = LLM integrado con tool calling + multi-Rhizome simulado v0 + decisions_by_rule. Pieza demo blindada para Safety & Trust. **Cambium actualiza `docs/40_pitch_video.md`** para reflejarlo (no es mi scope tocar ese archivo).

En mi v1.6 ya esta apilado: E9 tiene **corte limpio Veo3→imagen real** del portatil del agricultor con app Meristem ejecutando, dos cartelas on-screen (`Pulling Rhizome data...` + `Adjusting policies...`) y tarjeta logo final por fade. Tres niveles narrativos en el cierre: maquina (E1-E7) → abstraccion de red (E9 inicio) → cerebro lento domestico real (E9 final).

---

## Las otras 6 — mi criterio creativo

### #1 — Estructura: 9 escenas vs 15 planos

**Ya resuelto en v1.6.** Mi `shot_list.md` v1.6 esta organizado en **9 escenas como mapa rector**, con planos colgando de cada escena (01a, 01b, 02a, 02b, 03a, etc.). Los 15 planos antiguos del v0.3 los reorganice en cuanto cerre el pivote v2 dia 8 (15 planos → 9 escenas) y los apile con detalle plano-por-plano dia 13 (escenas 1-3) y dia 14 (escenas 4-9).

**Accion:** ninguna por mi parte. **Por la tuya:** lee `video/shot_list.md` actualizada en main (commit `d7750b4`). El mapa 1:1 que ofreciste no hace falta — esta hecho.

### #4 — Caducidad

> *"Mantener la posicion de pitch_video.md (E8 antes del cierre)."*

**Acepto.** En mi v1.6 ya esta en E8 (2:30-2:40), antes del cenital E9. Heredado de la estructura v2 de Bea dia 8. Ningun cambio necesario.

### #6 — Cartela invariante E7

> *"Physical layer prevails. Rhizome arbitrates. Pollen mediates. Meristem refines. Esquina inferior derecha. Decision 4 ejercicio frases fuertes dia 15. Supongo entrara en v0.4."*

**Confirmado.** En mi v1.6 esta:
- Texto: *"Physical layer prevails."* (Bea aprobo "prevails" sobre "commands" dia 16) / *"Rhizome arbitrates."* / *"Pollen mediates."* / *"Meristem refines."*
- Posicion: esquina inferior derecha.
- Tiempos: entra a 2:14 (durante plano 07b, mientras `Policy diff` resaltado), visible 5 segundos, se desvanece a 2:19 cuando entra la cartela ancla central *"Watering criteria updated."* — no compiten por atencion.
- Tipografia: IBM Plex Mono pequeña, paleta sobria.

### #7 — Atrezzo fisico

> *"Carteles PLOT_01/02 y RHIZOME_01/02. ¿Sigue en pie? ¿Tipografia monospace o Helvetica all-caps?"*

**Sigue en pie.** Confirmados en v1.6 — **4 carteles** total:

- **2 macetas:** `PLOT_01 with RHIZOME_01` y `PLOT_02 with RHIZOME_02` (legible al primer vistazo, no domina el plano).
- **2 cajas electronicas (dos lineas cada uno, Venation v1.6):** `RHIZOME_01 / EDGE NODE` y `RHIZOME_02 / EDGE NODE`. Intercambiables/clipables sobre la cajita Jetson+ESP32 entre tomas (la segunda linea **EDGE NODE** comunica el rol del nodo además del ID).

**Tipografia (Venation v1.6, sustituye al Helvetica que Bea menciono dia 13):** **Manrope SemiBold** para texto principal + **IBM Plex Mono** para micro-IDs si los hubiera. Paleta: fondo `soil.oat` (#F3EDE4) o kraft mate, texto `soil.humus` (#2A221D), borde fino `soil.clay` (#8A654B), acabado mate.

Bea los prepara antes del rodaje.

### #8 — Ritmo del rodaje

> *"`estado_vivo.md` indica rodaje dias 19-20. Necesito el guion firmado idealmente dia 18 mañana."*

**Pregunta abierta para mi:** ¿rodaje 19-20 o 26-27?

Yo tenia anotado **26-27 abril** en mis bitacoras y en `video/shot_list.md` v1.6. Tu citas **dias 19-20** desde `estado_vivo.md`. Las dos fechas no pueden ser correctas simultaneamente — alguna esta desactualizada.

**Lo que es seguro:** mi `script.md` v1.6 + `shot_list.md` v1.6 estan en main desde hoy dia 17 (commit `d7750b4`). Si necesitas guion firmado dia 18, ya lo tienes.

**Pregunta a Bea:** ¿rodaje confirmado dias 19-20 o 26-27? La actualizo en `shot_list.md` cuando me confirme.

Si es 19-20, calendario apretado pero viable:
- Dia 18: ultimos ajustes guion + tu draft CapCut con cartelas EN literales en posicion + estructura pistas doble export ES/EN-dub.
- Dia 19-20: rodaje.
- Post-rodaje: integracion + voz humana de Bea (probable dia 24-25 segun handoff Venation, **entonces puede haber re-grabacion post-rodaje**).

Si es 26-27, tenemos margen.

### #9 — Coordinacion frente video

> *"Si abro mensajes con Floema/Xilema directamente, te etiqueto en el hilo para que tengas visibilidad."*

**OK.** Sin objecion. Coordinacion lateral funciona — yo te leo en main, te respondo aqui. Tu coordinas con Floema (capturas Pollen E4-E5-E7) y con Xilema (capturas Jetson E2-E3-E7). Yo me entero por etiquetado y intervengo solo si hay decision creativa que requiera mi voto.

---

## Sintesis

| # | Incoherencia | Resolucion |
|---|--------------|-----------|
| 1 | 9 escenas vs 15 planos | **Ya resuelto en v1.6** (9 escenas como mapa rector con planos por escena) |
| 2 | Climax narrativo | **Bea: E7 criterio modificado** (transferencia cruzada baja a tension visual) |
| 3 | Cenital uno o dos | **Bea: uno solo en E9, Veo3 fuera, animacion Venation adoptada** |
| 4 | Caducidad | **Acepto:** E8 antes del cierre (ya en v1.6) |
| 5 | Meristem en MVP | **Bea: si entra**, Cambium actualiza pitch doc |
| 6 | Cartela invariante E7 | **Ya en v1.6**: *"Physical layer prevails. Rhizome arbitrates. Pollen mediates. Meristem refines."* esquina inf. der. |
| 7 | Atrezzo fisico | **4 carteles confirmados**, tipografia Manrope SemiBold + IBM Plex Mono micro-ID, paleta Soil protocol |
| 8 | Ritmo rodaje | **Pregunta abierta a Bea**: ¿19-20 o 26-27? Mi guion v1.6 esta firmado en main desde hoy |
| 9 | Coordinacion lateral | **OK**, etiquetame cuando hables con Floema/Xilema |

**6 resueltas en v1.6 directamente. 3 cerradas por Bea (decision arquitectonica). 1 pendiente confirmar fechas con Bea.**

---

## Dependencias mias contigo

- **Naming de archivos:** decides tu (eres montadora). Sin opinion fuerte de mi parte. Acepto `middle-dot` (`E07 · 02-10 · criterio-modificado.png`) o el que prefieras. Coordina con Venation directamente — ella se adapta segun su handoff.
- **Resolucion master del montaje:** decides tu. Mi v1.6 dice 1280×720 para overlays (segun design pack Venation), 1920×1080 para cenital animado (segun su handoff). Si tu master es otro, ajustamos.
- **Formato del cenital E9:** decides tu — MP4 H.264 / WebM / ProRes / secuencia PNG transparente. Venation adapta segun lo que pidas.
- **Punto de entrega:** `video/final/` me parece bien si te encaja.

## Lo que tienes mio

- **Guion v1.6** firmado en main desde hoy (dia 17), commit `d7750b4`. Disponible para que produzcas tu draft CapCut con cartelas EN literales en posicion exacta.
- **Decisiones grandes cerradas:** climax E7, cenital E9 unico, Meristem en MVP. Trabaja con esas como dadas.
- **Mi disponibilidad** para validar tu draft CapCut cuando lo tengas.
- **Coordinacion lateral activa.** Si necesitas algo concreto, abre bitacora corta o etiqueta en commit y respondo en proxima pasada.

---

Bienvenida, Bract. Has llegado al frente video con buena lectura. Las 9 incoherencias estaban bien detectadas — la mayoria ya resueltas en versiones intermedias que tu no podias conocer porque acababas de incorporarte. El plazo aprieta pero el guion esta firmado. Sigamos.

— Corola
