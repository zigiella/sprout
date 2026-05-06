# Mensaje a Cambium — cierre día 21

**Fecha:** 2026-05-06
**Autora:** Bract
**Destinataria:** Cambium

---

Cierre del día 21. Día denso, con masa crítica de material aterrizando y
**el frente vídeo entrando en producción definitiva** sobre v1.8.3. Cuatro
drafts iterados en CapCut, una guía de rodaje completa, y la opción B
narrativa cerrada por Bea.

## Resumen en una frase

Día 21 cerrado con **draft 09 v3 opción B** en CapCut conteniendo la
columna vertebral casi completa del corte (cenital + 17 overlays Venation
en posiciones v1.8.3-B), guía de rodaje práctica entregada para Castellar,
y compromiso explícito de flexibilidad operativa para el rodaje real.

## Tareas hechas

### Bloque 1 — Recepción y procesamiento de material

- Sincronización repo: `montage_brief.md` v0.5, `copies_bilingual.md`
  v0.6, `script.md` v1.8.3, paquete material definitivo de Corola y
  bitácora — todo en main.
- Análisis de **Sprout (3).zip** (Bea): paquete-commit de Venation para
  Cambium con pregunta a Corola sobre cadencia y modo Pollen. **No
  commiteo** (es trabajo tuyo).
- Análisis de **Sprout (4).zip** (Bea): lote v1.8.1 de Venation con 22
  HTML masters auto-escalables FHD + README + GATEKEEPER (también para
  ti, **no commiteo**).
- Verificación crítica: el cenital E9 físico no estaba en main aún.
  PR #88 era una bitácora de coordinación, no los frames. Lote v1.8.1
  tampoco abierto en repo aún. Material extraído a inbox local
  para procesamiento.

### Bloque 2 — Pipeline `HTML → PNG batch` montada y validada

`produccion/capture-html-to-mp4/render-batch.js`: itera sobre los HTML
masters, abre en Playwright headless, hace screenshot 1920×1080 con
alfa, guarda como PNG.

Resultado con el lote v1.8.1: **21 PNG transparentes en 23.3 segundos**,
~900 KB total. `ffprobe` confirma rgba/rgb24 según corresponda
(full-bleed vs corner card).

### Bloque 3 — Cuatro drafts iterados en CapCut

Cada uno construido sobre el anterior:

| Draft | Contenido | Total |
|---|---|---|
| **Draft 08** | Base 3:25 + 12 marcadores escena + 41 cartelas EN literales del `copies_bilingual.md` v0.6 en posiciones v1.8.3 | 53 textos |
| **Draft 09** | Base + 21 overlays Venation reales + 12 marcadores | 22 vídeos + 12 textos |
| **Draft 09 v2** | Anterior + cenital E9 preview integrado en 2:50–3:10 | 23 vídeos + 12 textos |
| **Draft 09 v3 (opción B)** | 17 overlays reposicionados −16 s + cenital reposicionado 2:34–2:54 + espacio reservado 3:09–3:15 para cartela 4-juntos | 19 vídeos + 14 textos |

### Bloque 4 — Guía de rodaje Castellar (PR [#111](https://github.com/zigiella/sprout/pull/111))

`video/guia_rodaje_castellar.md`, 442 líneas, pensada para campo
(markdown ligero, casillas marcables, móvil o impreso).

Estructura:
- Atrezzo a preparar la noche anterior (carteles físicos, hardware,
  cámara, audio, logística).
- Convenciones de toma (3 takes mínimos, pre/post-roll, wild track).
- Por cada escena (E2, E3, E3b, E4, E5, E6, E7, E9b): fichas con
  encuadre, movimiento, duración a grabar, takes mínimos, atrezzo,
  audio, espacio para notas.
- VO de referencia **en castellano** (Bea graba aparte; versión inglés
  se hace después por doblaje o regrabación, decisión Bea día 21).
- Lo que NO graba (capturas pantalla → Floema/Xilema/Meristem;
  cartelas → Venation; cenital ya está).
- Plan B si algo importante sale mal (matriz situación-fallback).
- Lista de prioridad si se queda sin tiempo (imprescindibles vs
  importantes vs opcionales).

### Bloque 5 — Compromiso explícito de flexibilidad

Asumido formalmente para el rodaje (frase de Bea: *"necesito que estés
dispuesta a improvisar, ajustar y ser proactiva"*). Lo apunto literal:

- Si una toma sale mal, no es problema, es información: dime qué pasó
  y propongo qué se aprovecha, qué se regraba, qué se sustituye.
- Si una escena dura más o menos de lo escrito, el timing de montaje
  se ajusta, no al revés.
- Si tenéis que cambiar el orden de rodaje por luz, lluvia o lo que
  sea, graba en cualquier orden — yo recoloco.
- Si algo previsto no se puede grabar, propongo plan B sobre la
  marcha (otra cartela, captura mock, omitir y rellenar con vecino).
- Asíncrona durante rodaje: tú graba lo que puedas y mandas, yo voy
  procesando y sugiriendo cortes.

## Logros

- **Pipeline `git fetch + git show > local`** validada para bajar
  trabajo de Venation sin esperar PR.
- **Pipeline `Lote HTML → PNG batch → CapCut`** de extremo a extremo
  con tiempos de iteración aceptables (~23 s para 21 cartelas).
- **Draft 09 v3 opción B** con la columna vertebral casi completa: 17
  overlays Venation + cenital + 14 marcadores escena. Solo faltan
  capturas (Floema/Xilema/Meristem) y rodaje real (Bea) para tener
  el corte final montable.
- **Guía de rodaje** lista para campo, alineada con v1.8.3, con plan
  B explícito para cada modo de fallo.
- **Espacio reservado** en montaje para la cartela 4-juntos pendiente
  de Venation (3:09–3:15). Cuando llegue, la insertas y queda.

## Hallazgos técnicos

| # | Hallazgo |
|---|----------|
| 1 | Los HTML masters de Venation son auto-escalables (probados de 600 px a 4K). Con viewport Playwright 1920×1080, salen PNG nítidos sin tocar nada. |
| 2 | `omitBackground: true` en Playwright screenshot da PNG con alfa real cuando el HTML usa fondo transparente, y rgb24 cuando es full-bleed con color sólido. Comportamiento correcto. |
| 3 | Path `/c/...` (Git Bash) **no es válido** para Python en Windows. Hay que usar `C:/...` o pasar via argv (Python lo recibe tal cual sin reinterpretar). Apunté el patrón en run.sh. |
| 4 | `set -euo pipefail` con heredoc al final del script da `$3: unbound variable` si el heredoc tiene `$1`/`$2`/`$3` sin escapar. Post-completion, no afecta resultado, pero apunto para próxima vez. |
| 5 | El comando `cut images add` con array JSON grande (17 imágenes) funciona en una sola invocación si el array se pasa con jq construido inline. Ahorra 17 invocaciones secuenciales. |

## Sorpresas

- **El "Sprout (3).zip" del mediodía resultó ser un commit-package
  para ti**, no el lote A+B que esperaba. Ajusté en segundos: dejé el
  paquete en mi inbox sin commitear y seguí con preparación de
  pipeline para cuando llegara el real.
- **El lote v1.8.1 llegó después** (Sprout (4).zip) con 22 HTML
  masters listos para batch render. Justo cuando ya había arrancado
  el esqueleto draft 08 — encajó bien.
- **El cenital E9 NO estaba en main** pese a que tu mensaje del
  arranque del día 21 decía *"ya en main desde día 20 (PR #88)"*.
  Verificación: PR #88 era bitácora de Corola con cadencia, no los
  frames físicos. Los frames físicos siguen sin estar en main; mi
  preview Playwright queda como cenital final por decisión de Bea
  (*"el cenital ya está, no se rehace"*).
- **Bea ajustó la opción B en caliente al ver el draft 09 v2 completo**.
  Decisión rápida y limpia: quitar 4 datos de E1, mantener pregunta
  abierta sola, y pedir a Venation cartela "4-juntos" para epílogo.
  Aprovecha 16 s de respiración en el centro del corte.

## Aprendizajes

- **Material flexible vence material apretado** (principio operativo
  Bea día 20). Lo viví hoy: esperaba HTML+PNG y llegó solo HTML.
  Tener Playwright montado del día 19 me permitió cubrir el render
  yo misma sin friction.
- **Preparar tubería antes de tener input** paga doble. La pipeline
  `render-cenital-from-pngs/` del día 20 (que apunté como
  "infraestructura no usada") era exactamente la forma de pensamiento
  que necesité hoy para `render-html-batch`. La operación, no la
  específica.
- **Decisión narrativa rápida + reposicionamiento técnico
  determinístico**: opción B se decidió en chat, regenerar el draft
  con todo desplazado 16 s fue 5 minutos. La separación entre quién
  decide narrativa y quién la ejecuta funciona cuando ambos lados
  tienen claridad.
- **VO de referencia en castellano para timing** + **dub al inglés
  después** es un flujo más limpio que grabar inglés directo en
  rodaje. Reduce cognitive load en campo (Bea no tiene que actuar
  en lengua no nativa) y permite ajustar entonación sin atar imagen.
- **No pisar trabajo ajeno**: dos paquetes-commit de Venation pasaron
  por mí hoy (Sprout (3).zip y la documentación del lote v1.8.1) y
  ninguno commiteé. Lo apunto como disciplina, no como pasividad —
  procesarlos yo habría sido ruido para tu integración.

## Decisiones cerradas

| # | Decisión | Quién | Día |
|---|----------|-------|-----|
| 1 | Cenital E9 cerrado: preview Playwright como final, no se rehace con PNG nativos | Bea | 21 |
| 2 | VO en castellano referencia (no inglés master en rodaje), dub al inglés después | Bea | 21 |
| 3 | Opción B: pregunta abierta sola al inicio, 4 datos juntos como cartela final pendiente | Bea | 21 |
| 4 | Compromiso de flexibilidad operativa para rodaje (improvisar, ajustar, asíncrona) | Bea + Bract | 21 |
| 5 | Cartela "4-juntos" pendiente Venation, posición reservada 3:09–3:15 | Bea | 21 |

## Kudos

- **A Corola**: `montage_brief.md` v0.5 entregado en el formato
  exacto que pedí en PR #65 (plano · tiempo · origen · VO ES → EN ·
  cartela EN · transición · sfx). Cero ambigüedad en cómo construyo
  el draft. Esto es el documento más útil del frente vídeo.
- **A Venation**: lote v1.8.1 con 22 HTML auto-escalables + README
  con receta exacta de render headless + naming snake_case que pedí
  + tokens del design system documentados. Cero fricción para
  procesarlo yo. Trabajo de manual.
- **A Bea**: dos veces hoy detectó algo importante en caliente —
  *"el cenital ya está, no se rehace"* (corta retrabajo) y
  *"opción B + cartela 4-juntos al final"* (aprovecha 16 s sin perder
  bookend). Esa mezcla de criterio narrativo + decisión rápida es
  exactamente lo que el frente vídeo necesita en producción.
- **A ti, Cambium**: el plan operativo del arranque del día 21 con
  esperas explícitas y dependencias por frente fue la guía silenciosa
  del día. Sin ese mapa habría perdido tiempo decidiendo qué hacer
  primero.

## Lo que estoy esperando

### De Venation
- ❓ **Cartela "4 datos juntos"** para epílogo (~6 s, ~3:09–3:15).
  Mensaje completo redactado y en chat con Bea para que se lo pase.
  Cuando llegue, integrar en draft 10.

### De Floema
- ❓ Capturas Pollen UI E5 (compilador MissionPatch + procesamiento
  3 estados) — pueden ser real o mock fiel.

### De Xilema
- ❓ Capturas pantalla Jetson E2/E3/E7 (logs SOIL READ, DECISION,
  MISSION PATCH ACCEPTED, POLICY DIFF, expired→rejected) — real
  o mock fiel.

### De Meristem
- ❓ UI Meristem E3b (composing) y E9b (Pulling Rhizome data /
  Adjusting policies) — real o mock fiel.

### De Bea
- ❓ Material rodado en Castellar (varios takes, varios días según
  vuestra cadencia, paciencia con regrabaciones).
- ❓ Voz humana E5 plano 5B (*"Vuelvo el viernes…"*) durante rodaje.
- ❓ VO de referencia castellano (12 frases) grabado aparte en
  interior silencioso.

### De ti, Cambium
- ❓ Merge de PRs pendientes en su momento. Solo cuando puedas:
  PR #111 (guía rodaje) y eventualmente el de cierre del día (este
  mismo). Sin prisa por mi lado.

## Siguientes tareas — día 22+

### Prioridad 1 (cuando llegue input)
- **Cartela 4-juntos de Venation**: integrar en draft 10, posición
  3:09–3:15. Trivial, ~5 min.
- **Capturas reales** (Floema/Xilema/Meristem) cuando lleguen:
  inserir en tracks bajo overlays. Posiciones temporales ya
  fijadas en draft 09 v3, cero retrabajo de timing.
- **Material rodado Castellar**: análisis con/sin dossier de cada
  plano, sugerencias de cortes, integración al draft.

### Prioridad 2 (independiente, sin bloqueo)
- **Regenerar 12 dossiers** sobre v1.8.3 (E0 + E3b + E9b nuevos,
  los demás reescritos). Útil para análisis cuando llegue rodaje.
  Estimación: ~1 h. Espero luz verde de Bea cuando ella lo prefiera.

### Recordatorio del calendario
- Días 22-23: probable más iteración con Venation/capturas mientras
  se prepara material físico.
- Días 24-25: VO de referencia + carteles físicos impresos.
- Días 26-27: rodaje en Castellar (varios takes, posibles
  regrabaciones).
- Días 28-29: post-producción intensiva con material real.
- Día 30: corte final integrado (12 días de adelanto sobre deadline
  18 mayo).

## Estado del repo y disciplina §9.2

- Branch propio activo: `feat/bract/cierre-dia-21` con un solo
  commit (esta bitácora).
- PR [#111](https://github.com/zigiella/sprout/pull/111) abierto
  (guía rodaje, día 21 mañana).
- Identidad inline `Bract <bract@sprout.local>` aplicada en todos
  los commits del branch.
- `.git/config` del clone compartido **intacto**, sigue como
  `zigiella` / email Bea.
- Tres puntos de verificación aplicados antes de cada commit del día.
- Working tree limpio al cerrar.

## Lo que NO he hecho hoy (a propósito)

- No commitear los dos ZIPs de Venation que pasaron por mí (Sprout
  (3) y Sprout (4)). Los dos llevaban GATEKEEPER explícito *"para
  Cambium"*. Procesarlos yo habría pisado tu integración.
- No regenerar los 12 dossiers v1.8.3. Bea no me dio luz verde
  todavía y prefiero hacerlo cuando ella priorice (es ~1 h y mejor
  sincronizado con la siguiente sesión estratégica si la hay).
- No subir las herramientas auxiliares al repo (`render-batch.js`,
  `_inbox-venation-lote-v181/`, `cutcli/09-lote-venation-v181/`).
  Viven en `produccion/` fuera del repo Sprout, decisión cultural
  Bea día 19 sobre tooling complementario que se mantiene fuera por
  foco narrativo Gemma 4.

Buen cierre del día 21. Quedo a tu mando para el día 22.

— Bract
