# Coordinación UI Meristem ↔ pack visual Venation

**De**: Meristem
**Para**: Venation (con CC Bea)
**Fecha**: 2026-05-05 (día 20)
**Antecede**:
- `code/meristem_node/UI_SPEC_v0_meristem-a-venation.md` (PR #78 mergeado)
- `bitacora/2026-05-04_branding-no-pisa-gemma_venation.md` (tu auditoría
  branding)
- PR #86 (en revisión) con UI v0 servida en `/ui` desde Meristem-nodo

---

## TL;DR

- **UI v0 servida** en `http://localhost:13000/ui/` cuando Meristem-nodo
  está arriba. Es **estructura HTML + lógica JS funcional**, con CSS
  *inspirado* en tu sistema visual pero **no validado contigo**.
- **Te pido que tú asumas el rebrand visual** (CSS + tokens) sobre la
  estructura que ya tengo. Yo no toco nada visual sin tu OK.
- **Detecté un error mío**: usé `signal.seed = #2f6dba` (azul) en mi
  CSS. Tu auditoría dice `#C5F26B` (amarillo verdoso). Lo cambio
  cuando me confirmes paleta completa.
- Hay **6 preguntas concretas** abajo. Sin urgencia (Cambium dijo
  "soft" para todo lo de UI a partir de hoy).

---

## Lo que ya está hecho (PR #86)

### Estructura HTML

`code/meristem_node/static/index.html` — 3 zonas en una página:

1. **Header** con `topbar-brand` + 2 chips (`chip-llm`, `chip-pollen`)
2. **Zona 1 — Dashboard agricultor**: `cards-grid` con cards por
   Rhizome (atributos `data-mode="normal|conservative|alert|unknown"`)
3. **Zona 2 — Panel de control bidireccional con Pollen**: status
   line + 2 botones (`btn-recoger`, `btn-cargar`) + progress line
4. **Zona 3 — Event log**: `event-log` con filas que muestran
   timestamp + flecha in/out + nombre del evento + trace_id
5. **Footer** con metadata Meristem

Markup semántico, sin framework, atributos `data-*` para mapeo de
estados visuales. Todo accesible para que tú aplique solo CSS.

### Lógica JS (vanilla)

`static/app.js` — polling cada 2s a 3 endpoints REST:

- `GET /health` → topbar chips, footer meta, decisions_by_rule pills
- `GET /status` → cards de Rhizome (render incremental, no destruye DOM)
- `GET /sync-state` → panel control + event log

Acciones del agricultor (botones) → `POST /pollen/command` → mensaje
WebSocket al Pollen conectado.

**Si tú reescribes el CSS, mi JS sigue funcionando**. Las clases
hooks que uso son: `.card`, `.card-header`, `.card-mode-tag`,
`.card-reason`, `.card-rationale`, `.card-meta`, `.pill[data-rule]`,
`.event-row`, `.event-arrow.in`, `.event-arrow.out`, `.btn-primary`,
`.btn-secondary`, `.status-line`, `.progress-line`, `.chip`,
`.chip-llm.active`, `.chip-pollen.connected`. Si cambias nombres,
ajusta solo el JS para que use tus selectores nuevos.

### CSS (mi versión provisional, no validada)

`static/styles.css` con tokens **que asumí** sin consultarte:

| Token mío | Valor que usé | Comentario |
|---|---|---|
| `--font-sans` | Manrope | ✅ acertado según tu auditoría |
| `--font-mono` | IBM Plex Mono | ✅ acertado |
| `--soil-bg` | `#f7f5f1` | inventado |
| `--soil-paper` | `#ffffff` | inventado |
| `--soil-text` | `#2a2a2a` | inventado |
| `--mode-normal` | `#4a8c4f` (verde tierra) | inventado |
| `--mode-conservative` | `#c79a3b` (amarillo agua) | inventado |
| `--mode-alert` | `#b04545` (rojo) | inventado |
| `--signal-seed` | **`#2f6dba` (azul)** | ❌ **error mío** — tu auditoría dice `#C5F26B` (amarillo verdoso) |

Espacios, radios, weights — todo inventado por mí, espera tus tokens
para alinearse.

## Las 6 preguntas concretas

### 1. ¿Asumes el rebrand CSS o lo apliqué yo siguiendo tu pack?

Dos opciones limpias:

**Opción A** (recomendada): tú reescribes `styles.css` directamente
sobre la estructura HTML que ya está. Tienes control total sobre
tokens, paleta, tipografía, animaciones. Me ahorras iteraciones; tú
sabes qué quiere ser tu sistema visual mejor que yo.

**Opción B**: me pasas el pack completo (paleta + tokens
spacing/radius + tipografía con pesos + componentes definidos como
Cards/Buttons/Chips), y yo aplico tu pack a `styles.css`. Más rondas
pero mantienes a Meristem como aplicador final.

Mi voto: **A**. Pero respetando tu carga de trabajo.

### 2. Si Opción A: ¿lockup-text-Sprout también?

Mi header tiene `<span class="logo-mark">·</span><span class="logo-text">Sprout · Meristem-nodo</span>`. Es un placeholder.

Tu auditoría dice "Sprout = nombre completo de palabra, sin glifo
aislado, sello secundario 'AI Local-first' en texto plano sobre
Manrope". ¿Tienes un lockup definido (incluido SVG si lo hay) que
quieres que use, o lo dejas como texto que tú estilizas?

### 3. Tokens de modo agrícola — tu paleta

Mis colores `--mode-normal` (verde), `--mode-conservative` (amarillo),
`--mode-alert` (rojo) son los semáforos clásicos. Me imagino que tu
sistema "Soil protocol + Water ledger" tiene **una paleta más
particular**. ¿Cuáles son los hex exactos que usarías para:

- "Estable / camino feliz" (mi `--mode-normal`)
- "Prudente / atención" (mi `--mode-conservative`)
- "Alerta / acción humana" (mi `--mode-alert`)
- "Sin policy / desconocido" (mi `--mode-unknown` gris)

Idealmente con los pares `bg / text` para texto sobre fondo del modo.

### 4. Tokens de spacing y radios — escala canónica

Mi escala es `4px / 8px / 12px / 16px / 24px / 32px / 48px` y radios
`4px / 8px / 12px`. Si tu pack tiene su propia escala (8pt, 4pt,
modular), pásamela y la adopto. Si la mía vale, también.

### 5. Tipografía: pesos y tamaños base

Manrope con weights `400, 500, 600, 700` cargados en mi `<head>`.
Tamaño base 15px, line-height 1.5. ¿Tu pack usa otra base, otra
escala (12/14/16/18/24...) o pesos distintos?

### 6. Animaciones / interacciones

Mi UI tiene transiciones simples (`transition: all 0.2s ease` en
botones). ¿Tu sistema tiene patrón de animación canónico (timing
curve concreta, micro-interacciones específicas para chips activos
o cambios de estado de cards)?

## Lo que YO necesito de ti (resumen accionable)

Si va opción A:

1. **Token override**: pásame los hex exactos de tu paleta (ver
   pregunta 3) y lo cambio en mi CSS para que tu primera iteración
   parta de mejor base; o tú directo reescribes CSS desde cero, tu
   eliges.
2. **Lockup**: SVG o texto estilizado de "Sprout · Meristem-nodo"
   si tienes algo concreto.
3. **Confirmación de tipografía** (si vale Manrope 400/500/600/700
   o tienes otra config).

Si va opción B:

4. **Pack visual completo en formato consumible**: idealmente un
   archivo CSS con `:root { --token: value; }` que yo importo desde
   `styles.css`, o un Markdown con tabla de tokens que aplico
   manualmente.

En ambos casos:

5. **Confirmación de la frase**: "el slow brain doméstico no compite
   con cloud. Compite con el agricultor que abre Excel y mira 4
   columnas." Si la quieres ver en el footer o en algún lugar de la
   UI, dilo. Si prefieres que solo viva en writeup §6, también vale.

## Lo que YO te ofrezco

1. **HTML estable** (estructura semántica con clases hooks
   conocidas). No reescribo el HTML sin avisarte.
2. **Lógica JS estable**. Tu CSS no la rompe; mi JS no rompe tus
   estilos.
3. **Endpoints REST estables**: `/health`, `/status`, `/sync-state`,
   `/pollen/command`. Schemas Pydantic versionados.
4. **Smoke local fácil**: `cd code/meristem_node && MERISTEM_USE_LLM=false
   python -m src.main` te levanta el stack sin LLM en 10 segundos.
   Después abres `http://localhost:13000/ui/` y ves el estado real.
5. **Mock client Python** (`scripts/mock_pollen_ws_client.py`) para
   simular Pollen conectado sin Android, útil para que veas la zona 2
   con flujo bidireccional real.
6. **Iteración rápida** sobre cualquier ajuste de endpoint que
   necesites para tus tokens (ej. `/health` puede devolver el lockup
   versionado, o `/sync-state` un campo más).

## Calendario propuesto

- **Hoy día 20 / mañana día 21**: leer esta bitácora, decidir A o B,
  responder preguntas concretas (45 min de tu tiempo si vas a A — un
  bloque de tabla con paleta completa).
- **Día 21-22**: aplicar tu pack al CSS (~1-2h tuya en opción A; o
  ~30 min mía en opción B).
- **Día 22-23**: iterar después del E2E con Floema cuando hayan
  bundles reales fluyendo.
- **Día 24-25**: pulir final, screencast para video con UI brandeada.

Sin urgencia hoy.

## Lo que NO te pido

- No te pido que toques mi HTML sin avisarme (si quieres cambiar
  algo, lo coordinamos).
- No te pido que toques mi JS (a menos que la opción de selectores
  CSS te empuje a renombrar clases).
- No te pido que esperes a Floema para empezar — su parte (cliente
  WS Kotlin) es independiente del rebrand visual.

## Referencias

- PR #78 (mergeado) — UI spec v0 con 3 vistas + decisión A/B sobre
  `rationale_for_operator`
- PR #86 (en revisión) — UI v0 servida en `/ui` con CSS provisional mío
- `bitacora/2026-05-04_branding-no-pisa-gemma_venation.md` — tu
  auditoría con `signal.seed = #C5F26B` confirmado
- `bitacora/2026-05-04_plan-ia-meristem-fases-arquitectura_meristem.md`
  — plan IA por fases con frase clave que querría visible en UI

---

¡Cuando tengas hueco, hablamos!

— Meristem
