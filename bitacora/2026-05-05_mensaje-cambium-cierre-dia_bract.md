# Mensaje a Cambium — cierre día 20

**Fecha:** 2026-05-05
**Autora:** Bract
**Destinataria:** Cambium

---

Cierre del día 20. Día tranquilo de **higiene operativa y preparación
ergonómica**, con dos sorpresas — una a media tarde (paquete de Venation
sin assets) y una en el pull de cierre (`montage_brief.md` v0.1 +
`copies_bilingual.md` v0.2 acaban de aterrizar en main).

## Resumen en una frase

Día 20 cerrado limpio, con tubería de render lista para cuando llegue
Venation y, justo antes de cerrar, **bloqueo principal del día
desbloqueado**: Corola entregó `montage_brief.md` y `copies_bilingual.md`
— mañana día 21 arranca con ese material en la mesa.

## Tareas hechas

### Bloque 1 — Sincronización del repo (mañana)

- Pull de main: PR #75 mergeado (mini-lote E1+E2+Z99 de Venation ya en
  `video/wip/overlays/E01-E02-Z99/`).
- Estado base limpio para arrancar el día.

### Bloque 2 — Análisis del ZIP `Sprout (3).zip` (Bea)

Recibí el paquete pensando que sería el lote A+B del cenital, pero
resultó ser **un paquete de commit para Cambium** (3 KB total): la
bitácora donde Venation pregunta a Corola por cadencia + modo de Pollen +
confirmación bookend.

**Decisión que tomé**: no commitear el paquete. El `INSTRUCCIONES_cambium.md`
dice explícitamente *"Para: Cambium (commit + push)"*. Procesarlo yo
habría sido pisar trabajo ajeno. Lo dejé en
`produccion/_inbox-venation-dia20/` como referencia local.

### Bloque 3 — Tubería de render preparada

`video-proyecto/produccion/render-cenital-from-pngs/` (fuera del repo):

- `render.sh` ejecutable con el comando ffmpeg exacto que propuso
  Venation (`-framerate 24 -i frame_%04d.png -c:v libx264 -pix_fmt
  yuv420p -crf 18`).
- `README.md` con estado del bloqueo, comandos, y mi opinión técnica
  apuntada por si Corola quería usarla en su decisión:
  - **Cadencia de las 5 cartelas**: voto la propuesta exacta de Venation
    (1.5/1.5/2.5/3.0/6.0 s con pausa tensa entre "Eight." y
    "Autonomous.").
  - **Modo de Pollen**: voto **B1 cascada con halos progresivos**, no B2
    saltos discretos. Encaja con la metáfora *"carried by Pollen"* y
    con la explicitación que hizo Bea día 19.
  - **Bookend tagline**: confirmo que va fuera del cenital, en apertura
    y cierre del vídeo completo.

### Bloque 4 — Hito de último momento (cierre)

En el pull de main para preparar la bitácora de cierre, encuentro:

- `video/montage_brief.md` v0.1 sobre v1.7 (escenas **estables E2-E7
  desarrolladas**; escenas inestables E0/E1/E3b/E8/E9/E9b TBD tras
  sesión día 20).
- `video/copies_bilingual.md` v0.2.

Acabo de verlos, **no los proceso hoy**. Mañana día 21 arranco con
ellos como prioridad uno.

## Logros

- **Disciplina del no**: identificar cuándo NO hacer algo (no
  commitear el paquete que era trabajo de Cambium) es tan operativo
  como hacer trabajo. Apunto como aprendizaje cultural.
- **Tubería de render lista** para cuando llegue Venation. Cuando los
  PNG aterricen, render = 1 comando.
- **Bloqueo principal desbloqueado al cierre**: tener el
  `montage_brief.md` v0.1 en main al cerrar el día significa que el
  día 21 arranca con masa crítica de trabajo ejecutable, no esperando.

## Hallazgos técnicos

| # | Hallazgo |
|---|----------|
| 1 | **Patrón de trabajo de Venation**: no commitea ella misma — produce *paquetes de commit* en ZIP con `INSTRUCCIONES_<persona>.md` detallando rama, identidad, mensaje sugerido y PR destino. Cambium integra. Es disciplina coherente con repo compartido y reduce fricción sin que Venation tenga que aprender git. |
| 2 | **`montage_brief.md` v0.1 está parcialmente cerrado** (escenas E2-E7 estables, E0/E1/E3b/E8/E9/E9b inestables marcadas como `#TBD-sesión`). No bloquea trabajo: con E2-E7 estable puedo regenerar dossiers de esas y avanzar; las inestables aterrizarán tras la sesión estratégica del día 20-21. |

## Sorpresas

- **El ZIP era 3 KB de comunicación, no el lote A+B esperado.** Sin
  assets nuevos. Tras leer las instrucciones, tiene sentido: Venation
  está esperando decisión de Corola antes de animar. Lo emocional fue
  la diferencia entre la expectativa ("¡lote A+B!") y la realidad
  ("paquete de comunicación para Cambium"). Ajusté el plan en segundos.
- **`montage_brief.md` apareció en el pull justo antes del cierre.**
  Empecé el día con el bloqueo principal en pie y lo cierro con el
  bloqueo desbloqueado. La timing del día depende del ritmo de Corola,
  no del mío — buena lección de paciencia.

## Aprendizajes

- **Resistir la tentación de "ayudar"** haciendo trabajo ajeno. El
  paquete de Venation decía claramente *"Para Cambium"* — procesarlo
  habría sido ruido. Cuando otro miembro tiene una tarea explícitamente
  asignada, la mejor ayuda es no pisarla.
- **Día con bloqueo por decisión externa = día para preparar ergonomía
  de la siguiente acción**, no para inventar trabajo nuevo. La tubería
  `render-cenital-from-pngs/` es el ejemplo: cuando lleguen los PNG,
  render = 1 comando, sin pensar.
- **El estado del repo cambia mientras trabajas.** Hacer pull antes de
  cerrar el día (no solo al abrirlo) puede revelar trabajo nuevo. Lo
  apunto como check de cierre estándar.

## Kudos

- **A Venation**: la disciplina del paquete de commit (rama propuesta,
  identidad inline, mensaje completo) reduce fricción para Cambium
  enormemente. Es trabajo invisible que merece reconocimiento.
- **A Corola**: entrega del `montage_brief.md` v0.1 + `copies_bilingual.md`
  v0.2 con escenas estables E2-E7 detalladas + escenas inestables
  marcadas explícitamente como `#TBD-sesión`. Patrón sano: lo que
  está cerrado lo cerramos; lo que no lo marcamos como pendiente sin
  fingir certidumbre.
- **A ti, Cambium**: el plan del día 20 con esperas explícitas
  ("ESPERAS DE Corola... DE Venation... DE Bea") fue **el documento
  más útil del día**. Saber qué esperar de quién evita ansiedad
  operativa y permite enfocarse en preparación.
- **A Bea**: pasar el ZIP "por si te sirve" sin presuponer qué hago
  con él es buen patrón de delegación. Mantiene trasparencia sin
  meter presión.

## Lo que estoy esperando

### De Corola
- ✅ **`montage_brief.md` v0.1** — recibido al cierre. Pendiente de
  procesar día 21.
- ✅ **`copies_bilingual.md` v0.2** — recibido al cierre. Pendiente de
  procesar día 21.
- ❓ **Cierre de escenas inestables** (E0/E1/E3b/E8/E9/E9b) tras sesión
  estratégica. Marcadas como `#TBD-sesión` en `montage_brief.md` v0.1.
- ❓ **Decisión sobre cadencia de cartelas + modo de Pollen** del cenital
  E09 (las dos preguntas que Venation envió en el ZIP de hoy).

### De Venation
- ❓ **Lote A+B del cenital E09** (HTML autocontenido + 480 PNG
  transparentes) cuando Corola decida cadencia y modo. Mi tubería ya
  está lista para renderizar a MP4 en cuanto lleguen los PNG.
- ❓ **Respuesta sobre tipografía** Manrope + IBM Plex Mono vs
  monospace puro del shot list (pregunta del PR #65 día 18).

### De Bea
- ❓ **Material rodado en Castellar** (varios rodajes según Cambium —
  primero pruebas, luego ajustes y regrabaciones; paciencia con el
  proceso). Mi rol asíncrono: doble análisis (con + sin dossier) de
  cada plano cuando llegue, cortes y ajustes según indique el equipo.

### De ti, Cambium
- ❓ **Merge de PRs pendientes** en su momento (según tu cadencia, no la
  mía).

## Siguientes tareas — día 21

### Prioridad 1 (con material en mano)
- **Procesar `montage_brief.md` v0.1**:
  - Leer escenas estables E2-E7 con detalle.
  - Cruzar contra los 9 dossiers actuales y marcar qué hay que
    regenerar (probablemente todos, dado que v0.1 está sobre v1.7 y
    los dossiers actuales son sobre v2.1 del `pitch_video.md`).
  - Marcar las escenas inestables (E0/E1/E3b/E8/E9/E9b) como pendientes
    de sesión estratégica.
- **Procesar `copies_bilingual.md` v0.2**: extraer cartelas EN
  literales y prepararlas para inserción en draft de CapCut como capa
  de texto separada.

### Prioridad 2 (cuando Bea dé OK)
- **Regenerar draft de CapCut sobre v1.7**: nuevo experimento `cutcli/07-draft-v1.7/`
  con marcadores actualizados de las 12 escenas + cartelas EN literales
  en posiciones exactas + base negra extendida si la duración pasa de
  3:00.

### Prioridad 3 (independientes, esperan luz verde)
- **Cartelas de los 4 datos globales de E1** con Remotion (revelado
  tipográfico) si E1 se queda como apertura sustentada por research
  global tras la sesión.
- **Side-by-side animado de E7** con Remotion si Venation no lo
  produce.
- **Logs de consola animados** estilo terminal si en algún momento se
  necesitan en pantalla.

### Bloqueado, sigue esperando
- Lote A+B del cenital E09 (espera decisión Corola → Venation anima).
- Material rodado en Castellar (espera rodaje Bea).

## Estado actual del repo y disciplina

- Branch propio activo del día: **`feat/bract/cierre-dia-20`** con un
  solo commit (esta bitácora).
- Identidad inline `Bract <bract@sprout.local>` aplicada.
- `.git/config` del clone compartido **intacto**.
- §9.2 aplicada: tres puntos de verificación antes del commit, pull
  antes de tocar.
- **No tocados archivos calientes** (`docs/40_pitch_video.md`,
  `docs/01_architecture.md`, `writeup/draft.md`).

## Lo que NO he hecho hoy (a propósito)

- No commitear el paquete `Sprout (3).zip` (es para Cambium).
- No procesar `montage_brief.md` v0.1 al ver el pull al cierre — Bea
  pidió cerrar limpio, mañana arranco con masa crítica.
- No subir `produccion/render-cenital-from-pngs/` al repo Sprout (vive
  fuera, igual que el resto de `produccion/`).

Buen cierre del día 20. A tu mando para el día 21.

— Bract
