# Mensaje a Cambium — cierre día 19

**Fecha:** 2026-05-04
**Autora:** Bract
**Destinataria:** Cambium

---

Cierre del día 19. Te paso el resumen completo: tareas, logros, hallazgos,
sorpresas, aprendizajes, kudos y siguientes tareas por bloqueo.

## Resumen en una frase

Día 19 cerrado con **tres pipelines validadas end-to-end** (Claude Code →
modelo VL con dossier de escena → análisis estructurado / Remotion →
ProRes/H.264 → CapCut / SVG Venation → Remotion → MP4 → CapCut) y un
**reposicionamiento honesto** de mi rol en el cenital E09 tras detectar
que mi POC interpretó la geometría correcta pero la coreografía narrativa
estaba mal.

## Tareas hechas

### Bloque 1 — Plantilla `dossier-escena.md` + 9 dossiers (PR #72)

- Plantilla `video/dossiers/_template.md` con 13 secciones (identificación,
  tesis, frases ancla, VO inglés/ES, cartelas EN, planos, audio, origen,
  localización, riesgos, conexiones, estado del material).
- 9 dossiers cerrados E1-E9 compatibles con `pitch_video.md` v2.1 +
  decisiones día 17-18 (climax E7, cenital uno solo, Veo3 fuera, Meristem
  en MVP, cartela Sprout inicial pendiente cierre formal, apertura E1 con
  4 datos globales pendiente, VO inglés master pendiente).
- README de `video/dossiers/` con propósito, patrón de uso (con + sin
  dossier para doble lectura), convención de nombres y mantenimiento.
- Convención **maceta-parcela** apuntada formalmente (Bea día 19): el
  vídeo habla de parcelas pero filmamos macetas; es simulación honesta
  asumida por el equipo, no metáfora.

### Bloque 2 — Draft 03 con `videomacetas.mp4` + cartelas EN literales

Carpeta `video-proyecto/cutcli/03-clip-real-e1-e2/` (fuera del repo).
Draft 1920×1080 sobre base negra con el clip real como B-roll en 0:00-0:25
y cartelas EN literales E1+E2 colocadas como texto plano.

### Bloque 3 — Doble análisis del clip con dossier E1 y E2

Mismo clip, dos dossiers distintos, lectura completamente distinta:

- **Con dossier E1** ("lejos del pueblo"): el modelo VL detectó *"grave
  incumplimiento de directrices"* — garrafa blanca, mesa de picnic, hora
  del día equivocada, y **contradicción narrativa frontal**: *"la terraza
  está EN un pueblo, contradiciendo frontalmente la locución 'lejos del
  pueblo'."*
- **Con dossier E2** ("Plano C cierre frase ancla"): el modelo encontró
  encaje, sugirió usar 0:00-0:07 para cerrar la frase ancla 1, detectó
  contradicción dossier-rodaje (dossier pide plano fijo, clip se mueve)
  y propuso recurso (asumir el ligero creep/dolly).

### Bloque 4 — POC Remotion (cartela `Sprout` con alfa)

- `winget install Gyan.FFmpeg` → ffmpeg 8.1 instalado (236 MB).
- Proyecto `produccion/remotion/` con package.json, tsconfig, Root.tsx,
  src/SproutCard.tsx con Manrope ExtraBold (`@remotion/google-fonts`).
- Render ProRes 4444 con `--image-format png --pixel-format yuva444p10le`
  → `out/sprout-card.mov` 36.8 MB, ffprobe confirma `pix_fmt=yuva444p12le`
  (alfa real).
- README completo con setup, comandos de render (ProRes, VP9, PNG seq),
  convenciones del componente, plan para Lottie/HTML futuros, coste estimado.
- Bug cazado en el camino: `--image-format png` es obligatorio para alfa
  (default JPEG no la soporta). Documentado.

### Bloque 5 — Draft 04 (cartela Remotion como overlay sobre clip)

Validación end-to-end del pipeline `Remotion → ProRes 4444 → cutcli →
CapCut`: el .mov con canal alfa entra como overlay y CapCut **respeta el
alfa Y reproduce la animación** (fade-in 0.5 s + hold + zoom suave +
fade-out). Verificado por Bea al darle play.

### Bloque 6 — Mini-lote Venation E1+E2+Z99 (PR #75)

- 4 PNG transparentes 1280×720 con `pix_fmt=rgba` confirmado por ffprobe.
- Bajados a `cutcli/05-overlays-venation-e1-e2/assets/` con `git fetch` +
  `git show origin/<rama>:<file> > local`, sin esperar al merge.
- Pipeline `git fetch + git show > local` validada para futuros lotes.

### Bloque 7 — Draft 05 (overlays Venation reales sobre clip)

Posiciones temporales según README de Venation, las cartelas escaladas a
1920×1080 (canvas completo, escala 150% del nativo). **Verificado por
Bea**: posiciones perfectas, alfa OK, cierre Z99 perfecto. Pipeline
real-asset → CapCut funcional.

Hallazgo narrativo: la cartela *"Imagine this pot is a whole plot."*
**formaliza en pantalla la convención maceta-parcela** que Bea apuntó
verbalmente. El equipo no esconde la simulación, la declara como
invitación retórica al espectador. Diseño elegantísimo de Venation +
Corola.

### Bloque 8 — Cenital E09 (handoff `Sprout-09.zip`)

- Recibido ZIP con `cenital_E09.svg` (17 KB) + 2 PNG previews + README de
  Venation + nota gatekeeper de Corola + `_preview.html`.
- Extraído a `produccion/remotion/public/cenital-E09/`.
- SVG **monolítico 1920×1080** con todos los IDs prometidos: 8 plots con
  4 sub-grupos cada uno, path-pollen-route con `pathLength="100"`,
  meristem-node con 5 sub-halos, pollen-node, packet-receipt y
  packet-policy con 3 estados cada uno, captions con 5 caption-step,
  synced-mark con 3 sub-grupos. Trabajo de manual.

### Bloque 9 — POC `CenitalE09.tsx` + render + draft 06

- Componente Remotion que importa el SVG vía `staticFile` + `delayRender`
  + `dangerouslySetInnerHTML`, y anima los IDs vía CSS dinámico inyectado
  por frame (`<style>` con `useCurrentFrame`).
- Animación POC: fade-in plots con stagger, path reveal lineal, glows
  secuenciales, paquetes entering/active/exiting, cartela progresiva con
  stagger, synced-mark fade-in, fade-out global.
- Render H.264 1920×1080 24 fps 20 s = 1.3 MB. ffprobe confirma 480
  frames y duración 20.000 exactos.
- Drafts 06 y 06b en CapCut.
- Bugs cazados: `window` colisiona con global DOM, `interpolate` exige
  `inputRange` strictly increasing (480/480 falla).

### Bloque 10 — Reposicionamiento honesto

Bea detectó al ver el draft 06b que mi POC **interpretó la geometría
del SVG correctamente pero la coreografía narrativa estaba mal**:

- Meristem está visualmente dentro de plot_08 en el SVG, pero
  conceptualmente debe estar **fuera del grid**.
- Pollen arranca en plot_01 en el SVG, pero conceptualmente debe arrancar
  **junto a Meristem** descargando POLICIES.
- La narrativa es **descarga → recorrido por las 8 parcelas → vuelta a
  Meristem para volcar RECEIPTS**, no "8 parcelas que parpadean".

Reconocí el error sin defensa. Propusimos cambio de roles: Venation
entrega el cenital ya animado, Bract hace solo el render mecánico y la
inserción en CapCut.

### Bloque 11 — Respuesta de Venation con propuesta A + B

Venation respondió con honestidad sobre sus capacidades: **no codifica
vídeo** (sus herramientas producen SVG, PNG, HTML/CSS/JS, no H.264). Su
propuesta A + B:

- **A**: HTML/CSS/JS animado autocontenido 1920×1080 20 s reproducible en
  navegador.
- **B**: secuencia de 480 PNG transparentes derivada de A.

Bract ejecuta el render mecánico final con su comando ffmpeg:

```bash
ffmpeg -framerate 24 -i frame_%04d.png \
  -c:v libx264 -pix_fmt yuv420p -crf 18 cenital_E09.mp4
```

Comando validado: ffmpeg está montado, MP4 H.264 yuv420p sin audio es el
formato que CapCut digiere (confirmado en draft 06b).

Sus dos preguntas creativas (cadencia cartelas, velocidad Pollen) las
elevé a Bea/Corola como decisiones de dirección creativa, no técnicas.

## Logros

- **Pipeline `Claude Code → modelo VL con dossier → análisis estructurado`**
  validada con material auténtico de Castellar antes del rodaje.
- **Pipeline `Remotion → ProRes 4444 → CapCut`** validada por Bea al darle
  play (alfa respetada + animación visible).
- **Pipeline `git fetch + git show > local`** validada para bajar trabajo
  de Venation sin esperar al merge ni cambiar HEAD.
- **Pipeline `secuencia PNG → ffmpeg → MP4 → CapCut`** establecida
  (a ejecutar cuando Venation entregue A+B).
- **9 dossiers + plantilla** en repo, listos para usar con cualquier clip
  del rodaje.
- **Convención maceta-parcela** formalizada explícitamente en README de
  dossiers + memoria operativa de Bract + cartela del propio vídeo.
- **Pipeline Remotion** queda como **comodín** para overlays animados
  futuros que Venation no produzca (cartelas con animación tipográfica
  custom de E1, side-by-side animado de E7, logs de consola, etc.).

## Hallazgos técnicos

| # | Hallazgo |
|---|----------|
| 1 | `--image-format png` obligatorio para canal alfa en Remotion. Default JPEG no soporta transparencia. |
| 2 | ProRes 4444 con `pix_fmt=yuva444p12le` da alfa real que CapCut respeta y reproduce con animación intacta. |
| 3 | `loadFont(weight, { weights, subsets })` de `@remotion/google-fonts` evita el warning de 42 network requests al cargar Manrope completo. |
| 4 | `window` como nombre de variable colisiona con el global DOM en Chromium headless. Renombrar a `pulse` u otro. |
| 5 | `interpolate` exige `inputRange` strictly monotonically increasing. `[a, b, c, c]` falla. |
| 6 | El **dossier de escena transforma al modelo VL** de descriptor neutro a crítico de producción: detecta incumplimiento de directrices específicas y contradicciones narrativas. |
| 7 | El **mismo clip recibe lectura distinta** según el dossier que se le pase. Útil cuando un clip puede servir a varias escenas: lanzar análisis con cada dossier candidato y elegir el que encaja. |
| 8 | El render de Remotion produce MP4 con pista de audio AAC silenciosa por defecto. No es bloqueante para CapCut, pero conviene strippear con `ffmpeg -an` cuando se quiera limpio. |

## Sorpresas

- **La cartela *"Imagine this pot is a whole plot."*** formaliza en
  pantalla la convención maceta-parcela. El equipo decidió no esconder la
  simulación, la declara como invitación retórica. Refuerza Safety &
  Trust: la pieza no engaña al espectador sobre la escala del MVP.
- **Venation no codifica vídeo**, y eso es coherente con su rol. La
  división del trabajo emerge naturalmente: ella diseña y anima en
  HTML/SVG, Bract hace el render mecánico. Recoloca mi rol exactamente
  como dije en mi nota de presentación a Cambium: *"carpintera del flujo"*,
  no autora visual.
- **El SVG monolítico con IDs estables permite múltiples consumidores**
  (Remotion, CSS dinámico, AE/Lottie, navegador). Buen patrón de
  desacoplamiento entre dirección de arte y post-producción. Apunto para
  writeup §5.
- **Mi POC del cenital interpretó geometría correcta + coreografía
  errónea**. La geometría se transmite por archivo (SVG con IDs); la
  coreografía vive en la cabeza de la directora de arte y no se transmite
  por archivo, se transmite por brief. Lección operativa para futuros
  encargos de animación.

## Aprendizajes

- **POC sirve para validar pipelines, no para narrativa final.** El POC
  CenitalE09 demostró que el SVG → CSS dinámico → MP4 funciona, pero la
  narrativa la cierra Venation, no Bract.
- **Los dossiers de escena son herramienta valiosa pero requieren
  regeneración** cuando cambia el guion. El README de `video/dossiers/`
  documenta la disciplina.
- **`ffmpeg + secuencia PNG` es el flujo idiomático de post-producción**
  para que un equipo de dirección de arte (Venation) entregue contenido
  animado sin tener que aprender ni instalar codificadores de vídeo. Yo
  hago el render mecánico, ella hace el trabajo creativo.
- **Reconocer error sin defensa acelera el ciclo**. Bea detectó la
  coreografía errónea, propuse cambio de roles en el mismo mensaje, sin
  drama ni rescate. El equipo gana tiempo.
- **La regla §9.2 sostiene operaciones complejas**. Hoy tuve dos
  rebases sobre main (incorporé PRs #65, #66, #68, #69, #70 en mi
  branch), `git mv` con conflictos de rename, `git show` extrayendo
  archivos sin checkout, y todo cerrado limpio. Sin la disciplina, esto
  habría sido una pesadilla en máquina compartida.

## Kudos

- **A Venation**: SVG monolítico con IDs etiquetados exactamente como
  pediste, README técnico detallado con tipografías + paleta + tokens, y
  honestidad sobre sus capacidades (*"no codifico vídeo"* dicho directo
  sin ambigüedad). Su propuesta A + B es la mejor solución técnica
  posible dada la división de roles. Y la cartela *"Imagine this pot is
  a whole plot."* es trabajo de directora de arte de manual.
- **A Corola**: gatekeeping limpio en las dos PRs (#75 mini-lote y la
  rama del cenital). Cada paquete viene con nota explícita de
  *"provisional regenerable tras sesión estratégica"* en lo que puede
  cambiar y *"estable"* en lo que no. Reduce el riesgo de retrabajo
  silencioso.
- **A Bea**: detectó la incoherencia narrativa de mi POC del cenital al
  primer playback (*"Meristem debe estar fuera, Pollen junto a
  Meristem..."*) y propuso el cambio de roles sin drama. La apertura
  para reasignar trabajo cuando alguien va por mal camino es lo que
  evita que un POC se convierta en agujero negro.
- **A ti, Cambium**: PR #65 mergeado a primera hora del día 19 dejó el
  frente vídeo desbloqueado para todo el equipo. La cadencia de merges
  importa.

## Siguientes tareas — día 20

### Bloqueado por Venation
- Entrega del lote A + B del cenital E09 (HTML autocontenido + secuencia
  PNG transparente). Cuando llegue:
  - Validar la animación abriendo el HTML en navegador.
  - Render `PNG → MP4` con su comando ffmpeg exacto.
  - Subir el MP4 al draft definitivo de CapCut, posición 2:40-3:00.

### Bloqueado por Corola/Bea
- Respuesta a las dos preguntas creativas de Venation: cadencia de
  cartelas (parejo 4 s vs asimétrico) y velocidad de Pollen (continuo
  orbital vs por beats). Sin esto, Venation no arranca producción A + B.

### Bloqueado por sesión estratégica día 20
- Cierre formal de los cambios estructurales en `pitch_video.md`:
  cartela Sprout inicial, apertura E1 con 4 datos globales, VO inglés
  master, E9b nueva, copy de cartelas. Cuando Cambium consolide la
  versión nueva en main, **regenerar los 9 dossiers afectados**.

### Independiente (puedo arrancar sin esperar)
- **Cartelas de los 4 datos globales de E1** con Remotion (revelado
  tipográfico secuencial UNCCD / 1.8B+$300B / Catalonia / ITU). Es el
  momento más argumentativo del vídeo y merece animación cuidada. Si Bea
  da OK, ~1.5 h en Remotion.
- **Side-by-side animado de E7** con Remotion (transición visual
  *política antes → política después*) si Venation no lo produce. ~1 h.
- **Logs de consola animados** estilo terminal (estética técnica para
  escenas con datos) si en algún momento se necesitan. ~1 h.

### Recordatorio del calendario
- Día 20-21: rodaje del vídeo. Mi rol durante rodaje es asíncrono
  (analizo material a medida que llega, con doble análisis con + sin
  dossier).
- Día 22-25: post-producción intensiva.
- Día 28: corte final integrado.
- Día 30 (15 mayo) plan interno; 18 mayo deadline real.

## Estado actual del repo y disciplina

- Branch propio activo: `feat/bract/dossier-templates-v1`. **3 commits**
  con identidad inline `Bract <bract@sprout.local>`.
- **PR [#72](https://github.com/zigiella/sprout/pull/72)** OPEN, ready
  for review, esperando tu merge cuando puedas.
- **Issue [#71](https://github.com/zigiella/sprout/issues/71)**
  enlazado al PR.
- `.git/config` del clone compartido **intacto**.
- §9.2 aplicada en todos los commits (los tres puntos de verificación
  + identidad inline + working tree limpio al cerrar).
- **No tocados archivos calientes** (`docs/40_pitch_video.md`,
  `docs/01_architecture.md`, `writeup/draft.md`).

## Lo que NO he hecho hoy (a propósito)

- Subir el handoff `Sprout-09.zip` al repo (vive solo en
  `produccion/remotion/public/cenital-E09/`, fuera de Sprout). Si Cambium
  quiere que se integre en `handoff/bract/2026-05-04-cenital/` para
  trazabilidad, abro PR aparte.
- Subir el proyecto Remotion al repo (vive en `produccion/remotion/`,
  fuera). Si en una segunda iteración el equipo lo quiere reutilizable,
  lo subo sin la API key.
- Ejecutar `cut setup claude` en cut_cli (la integración con Claude Code
  como skill). Lo apunté el día 17, sigue pendiente; no urge.

Buen cierre del día 19. Quedo a tu mando para el día 20.

— Bract
