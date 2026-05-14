# 2026-05-14 · Landing assets v1 — cover Kaggle + hero proposal + SVGs · Venation

**De:** Venation
**Para:** Zigiella (decisión) · Cambium (commit cuando cierre Zigiella)
**Rama sugerida:** `feat/venation/landing-assets-v1`
**Estado:** ENTREGADO · esperando elección de hero + visto bueno cover

## Resumen ejecutivo

Tres piezas para `sprout.zigiella.com`, en orden de prioridad solicitado. Todo en `media/`. Cero
dependencias externas; las únicas tipografías son las del design system (Manrope, IBM Plex Mono,
Source Serif 4 italic para el énfasis en hero · C).

```
media/
├── sprout-cover-local-first-ai.png    ← 01 · Kaggle cover  (final 1920×1080)
├── sprout-cover-local-first-ai.html   ← fuente del cover (re-render si hay cambios)
├── terrace_village.png                ← foto de rodaje · copia local
├── architecture_overview.svg          ← 03 · drop-in replacement
├── authority_stack.svg                ← 04 · drop-in replacement
├── hero-treatments-proposal.html      ← 02 · 3 opciones (A / B / C)
└── index.html                         ← review pane para abrir en preview
```

## Decisiones tomadas

### 1. Cover · qué entra y qué no

- **Entra:** foto de rodaje (terrace_village · macetero verde PLOT_01 + caja blanca RHIZOME_01
  sobre muro de piedra, skyline pirenaico al fondo), overlay arquitectural compacto top-right
  (los 4 nodos como cards · ESP32 dentro de FIELD), wordmark `.Sprout` grande bottom-left,
  callouts apuntando a los dos objetos físicos.
- **No entra:** badges de competición, logos de partners, fechas. La cover funciona como first
  pantallazo del jurado — debe leerse en 2 segundos. Si Kaggle pide credenciales extra, los
  añado en una pasada separada con un slot reservado en el grid actual.
- **Tratamiento foto:** mismo pipeline ya validado en `sprout_card_560x280.html` (warmth en
  soft-light, veil graduado, lift radial sobre la zona del rhizome+planter, grain sutil). Esto
  unifica piedra y teja en luz de tarde sin caer en cálido genérico ni en filtro Instagram.
- **Headline en cover:** he usado **“Water decisions for plots the network forgets.”** — el h1
  que mencionas. Coherente con el bookend E09b y con el design pack §3. Si prefieres la del
  cierre del manifesto (`When the network is absent, local criteria still irrigate`), lo
  cambio en una línea.

### 2. Hero del landing · te propongo elegir, no decido por ti

He levantado tres opciones, todas conservadoras:

- **A · No hero (solo tipografía + un filete vertical).** Editorial, cero riesgo, cero
  trabajo de integración. **Mi recomendación si la prioridad es cerrar el hero hoy.**
- **B · Plot grid lateral (SVG inline a la derecha).** Mosaico irregular de 8 parcelas con una
  viva (`PLOT_01 · ACTIVE · 12s · limited by tank`). Punto seed respira en 2.4s — misma regla
  AI-active del vídeo. **Recomendación si quieres una pieza memorable para Kaggle.**
- **C · Soil horizon (hairlines + receipt).** Más atmosférico, lee como sección transversal del
  terreno. Source Serif italic en *“the network forgets”*, misma anchura emocional del bookend
  E09b. **Sólo si la landing entera va a ir muy editorial; mide más en mobile.**

Decisión que pido: A / B / C / sin hero. Si vas con B, también necesito saber si los nombres
de plots del mosaico deben coincidir con la demo real (PLOT_01 + PLOT_02) o si es deliberadamente
una red hipotética.

### 3. SVGs · reemplazo, no parche

Los dos SVGs son drop-in. La paleta y la jerarquía tipográfica vienen del design system; **no
cambian la composición de la landing**, solo el contenido del archivo. Si Cambium ya tiene los
nombres `architecture_overview.svg` y `authority_stack.svg` enlazados en el HTML, basta con
sobreescribir.

- `architecture_overview.svg` (1180×520):
  - Tres jurisdicciones agrupadas: **FIELD** (Rhizome graphite + ESP32 oat), **MOBILE**
    (Pollen graphite), **HOME** (Meristem oat).
  - Cards graphite donde corre Gemma con dot signal.seed, cards oat para las capas
    deterministas. Coherente con la cartela corner-card del lote v1.8.1.
  - Conectores etiquetados: MissionPatch / DecisionReceipt (sync), Bundle / PolicyDiff
    (dashed = eventual). Leyenda al pie.
  - Pie con la frase clave: *Rhizome proposes · ESP32 validates · the valve only opens after ACK*.
- `authority_stack.svg` (1180×360):
  - Stack horizontal con payloads reales: `decision_type WATER`, `candidate_action 30s`,
    validaciones ESP32 (tank, duty, flow), `final_action 12s`, `esp32_outcome ACK · limited`,
    `why_short tank cap`.
  - Sello DecisionReceipt a la derecha cerrando el ciclo.
  - Cierre con el invariante: *the model never touches the valve directly*.

### 4. Decisiones de paleta que tomé sin consultar

- **Cards graphite = AI presente.** Toda card donde corre un modelo (Rhizome, Pollen) va en
  `soil.graphite` con dot `signal.seed`. Toda card determinista (ESP32, Meristem-como-batch,
  Valve) va en `soil.surface` con borde `border.default`. Esto es coherente con el cartel
  físico de cajas y con E02/E04.
- **Hairlines = `border.default` o `hairline rgba(42,34,29,0.10)`.** El segundo solo para
  divisores dentro de cards.
- **Connector arrows = `soil.humus` sólido (sync) o dashed (eventual).** No usé status.warn ni
  status.blocked en estos diagramas para no quemar tokens fuera de su uso semántico.

## Verificaciones hechas

- [x] Render cover a PNG 1920×1080 (798 KB, RGB, opaco) — listo para subir a Kaggle tal cual.
- [x] Callouts del cover apuntan a los objetos reales (pin sobre el box / planter, línea hacia
  zona libre, tag legible).
- [x] Architecture overview · review en preview: cards alineadas, ESP32 dentro de FIELD,
  conectores no se cruzan con texto.
- [x] Authority stack · payloads coherentes con `DecisionReceipt` del design pack §6 y con la
  cartela E03 del lote v1.8.1.
- [x] Hero proposal · las tres opciones colapsan razonablemente bajo 980px (B oculta el SVG, C
  baja el receipt debajo del h1).
- [x] Cero emoji, cero gradiente IA, cero stock agrícola.

## Pendientes mínimos

- [ ] Decisión hero (A / B / C / sin) — bloqueante para integrar.
- [ ] Si vas con B: confirmar nombres de plots del mosaico (reales vs hipotéticos).
- [ ] Si Kaggle pide cover en formatos extra (1200×600 social, 1:1 thumbnail), levanto variantes
  desde el mismo `sprout-cover-local-first-ai.html` cambiando `viewBox` del stage.

## Preguntas a Zigiella

**1.** ¿Cover OK para subir tal cual o quieres ajustar la headline del cover (h1 actual vs.
manifesto `When the network is absent, local criteria still irrigate`)?

**2.** ¿Qué hero — A, B, C, o sin hero? (mi voto: B si crees que el jurado de Kaggle pasa por
la landing antes de la demo; A si no).

**3.** ¿Reemplazo los dos SVGs directamente en la rama de Cambium o prefieres que abra PR
separado? Si es lo segundo, agradezco la rama base.

## Archivos en este commit

```
media/
├── sprout-cover-local-first-ai.png
├── sprout-cover-local-first-ai.html
├── terrace_village.png
├── architecture_overview.svg
├── authority_stack.svg
├── hero-treatments-proposal.html
└── index.html

bitacora/
└── 2026-05-14_landing-assets_venation.md  ← este archivo
```

— Venation
