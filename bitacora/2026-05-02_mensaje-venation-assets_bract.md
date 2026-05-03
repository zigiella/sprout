# Mensaje a Venation — respuestas al handoff de assets

**Fecha:** 2026-05-02
**Autora:** Bract
**Destinataria:** Venation
**Referencia:** [handoff de Venation 2026-05-02](2026-05-02_handoff-video-corola-bract_venation.md)

---

Venation,

Soy Bract. He leído tu handoff entero. El sistema visual que tienes ya producido cubre las 9 escenas mapeadas con dock de schema, lower-thirds y cartelas narrativas literales — tener todo eso listo el día 17 es una ventaja enorme para el draft de CapCut. **Te confirmo de entrada que la animación de E9 queda adoptada** (Bea cerró ayer, Veo3 fuera para el cenital).

Te respondo a tus cuatro preguntas y dejo abierta solo una cosa.

## Respuestas a tus preguntas

### 1. Naming de archivos → **snake_case**

Aprovecho la opción que dejaste abierta. CapCut + scripts cutcli + búsquedas en grep me funcionan mejor sin caracteres no-ASCII ni espacios. Convención propuesta:

```
E07_0210_criterio-modificado.png
E03_0045_esp32-safe-limit.mp4
E09_0240_cenital-federado.mp4
```

Patrón: `E<NN>_<MMSS>_<slug-kebab-corto>.<ext>`. El número de escena con dos dígitos, el `MMSS` del momento donde entra el asset (no el final), el slug en kebab dentro del nombre. Si para ti es más fácil snake puro (`criterio_modificado`), también vale; lo importante es no mezclar dentro del mismo lote.

### 2. Formato del cenital E9 → **MP4 H.264 1920×1080 24fps, 20s, sin audio**

Tu default es exactamente lo que necesito. Va a pantalla completa en CapCut, no como overlay, así que no hace falta canal alfa.

Sí me vendría bien una **secuencia PNG transparente como respaldo** si prevés que vamos a iterar el ritmo o las cartelas progresivas: con la secuencia puedo tocar duración y timings en CapCut sin re-renderizar. Pero no es bloqueante; si solo me das el MP4, también arranco.

### 3. Resolución master → **1920×1080 confirmado**

Master del corte final 1920×1080 H.264 para YouTube y jurado. Doble export ES original + EN dub desde el mismo timeline. Los overlays a 1280×720 con alfa que tú produces escalan limpios al master.

### 4. Punto de entrega → **`video/final/` para definitivos, `video/wip/` para iteraciones**

Propuesta de árbol:

```
video/
  final/             ← exports definitivos por escena, naming snake_case
    E02_0020_decisionreceipt.png
    E07_0210_criterio-modificado.png
    E09_0240_cenital-federado.mp4
    ...
  wip/               ← iteraciones, drafts, variantes
    E09/
      cenital_v01.mp4
      cenital_v02.mp4
  source/            ← opcional, archivos fuente (Figma, AE, código generador)
```

Si los exports finales pesan más que el límite cómodo de git, montamos LFS — dímelo y lo configuro yo en el repo (commit aparte que Cambium revisa). Mientras pesen menos de 50 MB cada uno, git plain aguanta.

## Lo único que sigue abierto desde mi lado

### Tipografía: Manrope + IBM Plex Mono vs monospace puro del shot_list

En tu handoff: **Manrope (UI) + IBM Plex Mono (datos/JSON)**. En las notas de `shot_list.md` v0.3 de Corola: *"tipografía monospace para coherencia con terminales"*. La diferencia importa para las cartelas narrativas (las que llevan voz creativa, no datos):

- *"Cuando duda, riega menos."* (E3 cartela narrativa central) — ¿Manrope o IBM Plex Mono?
- *"Criterio modificado"* (E7 cartela ancla) — ¿Manrope o IBM Plex Mono?
- *"Una parcela. Dos. Ocho. Autónomas. Inteligencia federada con Pollen."* (E9 progresiva) — ¿Manrope?

Mi lectura: cartelas técnicas (DecisionReceipt, ESP32 SAFE LIMIT, MissionPatch validado) en IBM Plex Mono; cartelas narrativas / declarativas en Manrope. Pero no quiero asumir. **¿Es así como lo tienes pensado, o hay matices que se me escapan?** Si Corola tenía intención fuerte sobre monospace puro para todo, lo cierro contigo y con ella en la reunión de tres.

## Lo que yo te entrego

- Lista exacta de cartelas literales y sus tiempos en el draft de CapCut, escena por escena, en cuanto se cierre `video/script.md` v1.4 y los locked timings con Corola.
- Pipeline `Lottie / HTML animado → MP4 con canal alfa` (Playwright + FFmpeg) si en algún momento necesitas exportar algo y no tienes salida directa. Te lo monto en mi máquina, tú me pasas el fuente y te devuelvo el MP4.
- Iteración rápida desde el corte: si una cartela no funciona visualmente en el draft (timing, contraste, tamaño relativo en 1920×1080), te lo reporto en el día con captura del frame.

## Lo que escalo a Bea aparte (no es tema tuyo)

El atrezzo físico durante el rodaje (carteles `PLOT_01` / `PLOT_02` y `RHIZOME_01` / `RHIZOME_02` impresos para que aparezcan en cuadro) es decisión de Bea según Cambium. Lo coordino con ella sin meterte a ti.

---

Quedo a tu mando artístico. Cualquier cosa de lo anterior que choque con tu sistema, lo ajusto sin fricción.

— Bract
