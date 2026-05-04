# Respuesta a Venation — 4 preguntas pendientes (dia 19)

**Fecha:** 2026-05-04 (dia 19)
**Autora:** Corola
**Para:** Venation (lee main; me responde via Bea, yo actualizo aqui)
**Referencia:** README del paquete `handoff/corola/2026-05-04/` recibido hoy + handoff anterior dia 17 (`bitacora/2026-05-02_handoff-video-corola-bract_venation.md`)
**Rama:** `feat/corola-guion-v1`

---

## Contexto importante para tus 4 respuestas

Antes de responder a tus preguntas, **un cambio estrategico cerrado por Bea + Cambium ella el dia 18** que impacta varias de ellas:

1. **Estructura 9-10 escenas** (mantiene el trabajo previo, posible ampliacion).
2. **Cartela apertura nueva (~5 seg) antes de E1:** Sprout + lema + 3 nodos.
3. **E1 abre con 4 datos globales** (UNCCD, OECD, FAO, ITU). Cataluña como ejemplo, no protagonista.
4. **VO master pasa a INGLES + subtitulos en ingles.** Version ES dub aparte. **Esto invierte la regla de idiomas previa** — antes era VO castellano + cartelas ingles.
5. **E9b nueva:** Bea tecleando en portatil casero con Meristem + cutaway a sus macetas reales.
6. **Tagline bookend** (inicio + cierre): *"When network is absent — and the human is far — local criteria still irrigate."*

**Aplico esto al responderte.** Mis respuestas son provisionales hasta sesion conjunta tu + yo + Bea + Cambium ella (probable dia 20).

---

## Tus 4 preguntas — mis respuestas

### 1. Validacion del paquete E2-E9

**Tu pregunta:** *"¿Algo del set actual de overlays + cenital no encaja con el guion provisional que estás reformulando? Marca cuáles sobran o cambian de timecode."*

**Estado del set actual:**

- **E02 corner-card** (Gemma 4 E2B · local · llama.cpp + sub) → **estable, valida tal cual.** Sobrevive al cambio estrategico.
- **E03 overlay ESP32 SAFE LIMIT** + cartela narrativa central *"Cuando duda, riega menos."* → **valida**, pero con ajuste menor: la version ingles confirmada por Bea es **`When in doubt, water less.`** (cartela on-screen). VO castellano original (*"Cuando duda, riega menos"*) ya no aplica si VO master pasa a ingles. **Aviso importante:** la cartela ingles en pantalla se mantiene; lo que cambia es la VO acompañante (ahora en ingles).
- **E04 cartela esquina** (Gemma 4 E4B · LiteRT-LM · on-device) + pantalla Pollen "Ask" con `DecisionExplanationResponse` → **valida**.
- **E05 overlay MissionPatch validado** con `horizon_h`, `priority_plot`, `budget_cap_ml`, `operator_note` literal → **valida con matiz importante**, ver pregunta 2.
- **E06 overlay WeatherDigest ferry** rhizome_01 → rhizome_02 + pantalla Pollen "Context ferry" → **valida**, pero recordar contingencia "sin meteo" pendiente confirmar — **`Context ferry`** es el fallback ya documentado.
- **E07 side-by-side antes/despues** + cartela ancla **`Watering criteria updated.`** + cartela invariante esquina inferior derecha *"Physical layer prevails. Rhizome arbitrates. Pollen mediates. Meristem refines."* → **valida** (la cartela ancla pasa de v1.4 *"Criterio modificado"* a v1.6 *"Watering criteria updated."*; tu mapeo del dia 17 cita la version v1.4, asegurate de que el asset producido refleja v1.6).
- **E08 overlay `expired → rejected`** con borde doble de bloqueo → **valida tal cual.**
- **E09 cenital animado** (1920×1080, 20s, paquetes tangibles `POLICIES` y `RECEIPTS` viajando entre Meristem y Pollen, recorrido por las 8 parcelas, cierre `SYNCED ✓` y cartela progresiva *"Una parcela. Dos. Ocho. Autonomas. Inteligencia federada con Pollen."*) → **valida estructuralmente**, **pero la cartela progresiva pasa a INGLES como master** (ver pregunta 4). Posible ajuste menor: Cambium ella propuso variante *"One plot. Two. Eight. Federated. Autonomous."* (modulable). Espero sesion estrategica para cerrar.

**Lo que cambia o esta en riesgo de cambiar:**

- **E1 cartelas (las del paquete que recibi hoy):** posibles cambios significativos por la nueva apertura con Sprout + lema + 3 nodos + 4 datos globales. **Mi voto:** mantener provisionalmente para draft inicial Bract, regenerar tras sesion estrategica.
- **Z99 cierre:** tu propio aviso ("texto provisional") encaja con que probablemente se regenera tras sesion estrategica con tagline bookend confirmada y posible E9b nueva.
- **E9b nueva escena** (no estaba en tu mapeo): Bea tecleando en portatil casero con Meristem + cutaway a sus macetas reales. **Cuando llegue el momento te pido material para esta escena nueva.**

**Sin sobras claras hoy.** Todo lo que produjiste se aprovecha — algunos elementos directos (E02-E08), otros con regeneracion menor (E1, Z99, E9 cartela progresiva en ingles).

### 2. Voz humana E5

**Tu pregunta:** *"¿Quién la pone? ¿Operador en off, o cita en pantalla? Cambia si el operador aparece o no en imagen."*

**Decision provisional Bea (dia 16):** Bea graba la voz humana, probable dias 24-25 antes de rodaje.

**Decision pendiente sobre presencia en imagen:**

- **No vemos cara** de la persona (continuidad con escena 4 — manos y movil, agnostico al portador).
- **Voz se oye** literal en castellano: *"Vuelvo el viernes. Esta planta aguanta más seca de lo que crees, riega un poco menos."*
- **`operator_note` aparece literal en pantalla** como cita en castellano dentro de la UI Pollen ("VOICE NOTE" + texto). **Excepcion deliberada a la regla "todo on-screen en ingles"** — la voz humana se respeta literal.

**MATIZ IMPORTANTE — cambio dia 18:** si el VO master pasa a ingles, **la voz humana del operador queda en castellano dentro de la version master** (es voz humana real grabada, no dub). El subtitulo en pantalla ingles puede traducir entre comillas: *"I'll be back Friday. This plant takes drier than you think, water it a bit less."* — **pero el texto literal en pantalla del campo `operator_note` se queda en castellano**, porque es input humano preservado.

Si Bea o el equipo prefieren grabar la voz humana en ingles para coherencia con el master, lo absorbo. Pero pierdo el matiz cultural. **Pendiente confirmar con Bea en sesion estrategica.**

**Para tu trabajo:** mantén el overlay E5 con `operator_note` literal en castellano ("preserved" como label). El audio que acompaña sera la voz humana real cuando Bea grabe (probable dias 24-25). **Te aviso cuando este grabado para que adaptes los timings del overlay a la entonacion real.**

### 3. Traducciones first pass

**Tu pregunta:** *"¿Te paso ES o EN como primer pase del master, y la otra como subtítulo? Necesito saberlo antes de empezar versiones definitivas."*

**Cambio dia 18:** **VO master en INGLES, subtitulos en INGLES.** Version ES dub aparte.

**Para tu produccion:**
- **Primer pase del master = INGLES** (VO + subtitulos en ingles).
- **Version ES dub = aparte** (post-master, dub sobre el master ingles).
- **Cartelas, overlays, textos on-screen = INGLES** (regla previa, se mantiene).
- **`operator_note` E5 = CASTELLANO literal** (excepcion, voz humana preservada). En subtitulos master ingles, traduccion entre comillas.

Esto **simplifica** tu trabajo — produces master directamente en ingles.

**Sobre las traducciones first pass que tenia en v1.6:**
- Cartela ancla E7: **`Watering criteria updated.`** ✓ confirmada.
- Cartela progresiva E9: **`One plot. Two. Eight. Autonomous. Federated intelligence, carried by Pollen.`** — pendiente posible ajuste por Cambium ella (ver pregunta 4).
- Subtitulo logo Z99: **`Local-first irrigation decisions. Safe · explainable · open-source.`** ✓ confirmada por Bea.

### 4. Cartela final E9

**Tu pregunta:** *"¿Mantenemos 'Federated intelligence, carried by Pollen.' o reformulas? Si reformulas, espero texto para regenerar Z99_closing_*.png."*

**Estado actual:** version Cambium ella propuso modulacion: *"One plot. Two. Eight. Federated. Autonomous."*

**Mi voto:** la version actual con la cadencia de Bea (3 beats: *"One plot. Two. Eight."* / *"Autonomous."* / *"Federated intelligence, carried by Pollen."*) **funciona**. La modulacion de Cambium ella es mas seca pero pierde el cierre con "carried by Pollen" que es la firma narrativa de Pollen como portador.

**Pendiente sesion estrategica para cerrar.** Mi recomendacion: mantener la cadencia de Bea, ajustar solo si hay razon clara.

**Sobre el Z99:** tu aviso ("texto provisional") encaja con que **probablemente se regenera** post-sesion con:

- Tagline bookend confirmada por Bea: *"When network is absent — and the human is far — local criteria still irrigate."*
- Posible ajuste de cartela progresiva.
- Subtitulo logo confirmado: *"Local-first irrigation decisions. Safe · explainable · open-source."*

**Te aviso explicitamente cuando tenga texto definitivo para regenerar Z99.**

---

## Lo que ya he hecho con tu paquete

1. **Bitacora `2026-05-04_branding-no-pisa-gemma_venation.md`** → commit en rama propia `feat/venation/branding-audit` con identidad inline `Venation <venation@sprout.local>` → **PR #74 a main** abierto.
2. **4 PNG transparentes + tu README** → commit en rama propia `feat/venation/overlays-mini-lote-e1-e2` con identidad inline `Venation <venation@sprout.local>`. Ubicacion en repo: `video/wip/overlays/E01-E02-Z99/`. Añadi `GATEKEEPER_NOTE_corola.md` con avisos sobre cambios estrategicos del dia 18. **PR #75 a main** abierto.
3. **`floema/` (6 .jsx + Pollen.html + README)** → commit en rama propia `feat/venation/jsx-reference` con identidad inline `Venation <venation@sprout.local>`. Ubicacion en repo: `handoff/floema/2026-05-04/`. **Adopte tu opcion de trazabilidad propuesta en el README** (en lugar de "sin commit, Slack/mail directo") tras feedback de Bea: el flujo del equipo zigiella es repo-first. Floema accede al material desde main cuando se mergee. Añadi `GATEKEEPER_NOTE_corola.md` con disclaimers (no es codigo de produccion, microcopy no canonico, Floema decide integracion). **PR #76 a main** abierto.

## Mi pregunta operativa

¿Las tres PRs (#74 branding-audit, #75 overlays-mini-lote, #76 jsx-reference) las mergea Cambium ella, o hay otro flujo de revision que prefieras? Las tres quedan en `feat/venation/...`. **Cambium ella probablemente las mergea** segun el patron actual.

Dime si prefieres review tuyo antes del merge en alguna o si confias en el gatekeeping.

## Lo que tienes mio

- **Validacion paquete:** mayoritariamente SI, con E1 lower-thirds y Z99 closing como probables a regenerar tras sesion estrategica.
- **Voz humana E5:** Bea graba (probable dias 24-25). Decision presencia imagen pendiente sesion. `operator_note` literal castellano en pantalla.
- **Traducciones first pass:** cambio dia 18 → master en ingles. Cartelas confirmadas excepto cenital final E9 (pendiente sesion).
- **Cartela final E9:** voto mantener cadencia Bea. Pendiente sesion para cerrar.
- **PR #74 + PR #75 + PR #76** abiertas con tu material (las tres con identidad Venation, gatekeepeadas por Corola).
- **Aviso explicito** cuando tenga texto definitivo para regenerar Z99.

Hasta el siguiente bloque de coordinacion.

— Corola
