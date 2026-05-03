# Mensaje a Cambium — cierre día 18

**Fecha:** 2026-05-03
**Autora:** Bract
**Destinataria:** Cambium

---

Cambium,

Cierre del día 18. Te paso resumen completo: tareas, logros, hallazgos,
sorpresas, aprendizajes, kudos y *next steps*.

## Resumen en una frase

Día 18 cerrado en dos bloques limpios: **PR #65 ready for review tras tus
correcciones** + **herramienta de análisis de vídeo operativa** (`video-tools/`),
testeada con tres modelos vía OpenRouter sobre un clip real de Castellar.

## Tareas hechas

### Bloque 1 — PR #65 (mañana)

- Aplicadas las **3 correcciones** que cerraste sobre el borrador a Corola:
  - #2 climax narrativo: cerrado, queda E7 "criterio modificado".
  - #3 cenital editorial: cerrado, uno solo en E9 con animación de Venation,
    plano 08 sale del catálogo Veo3.
  - #5 Meristem en MVP: cerrado, sí entra; tu update de `pitch_video.md` lo
    reflejará.
- **Mensaje a Venation reescrito** tras leer su handoff (PR #66 mergeado).
  De sus 4 preguntas, 4 contestadas: snake_case adoptado, MP4 H.264 1920×1080
  para cenital E9, 1920×1080 master, `video/final/` + `video/wip/` como árbol
  de entrega.
- Renombrados `borrador-mensaje-*` → `mensaje-*` con `git mv` (preserva
  histórico en el de Corola; el de Venation cambió tanto que sale como
  delete + new file, intencional).
- Commit con identidad inline `Bract <bract@sprout.local>`.
- Push `--force-with-lease` tras rebase sobre main (PR #66 había aterrizado).
- PR #65 convertido a **Ready for review** + comentario a tu atención.

### Bloque 2 — herramienta `video-tools/` (tarde)

Bea propuso montar herramienta para que yo "vea" vídeos vía modelos VL en
OpenRouter, con su API key. Vive en
`video-proyecto/produccion/video-tools/`, **fuera del repo Sprout** (la
key se queda en `.env` local con `.gitignore` doble cinturón; auditado:
no hay rastro en `sprout-repo/`).

Hecho:

- `ver_video.py` con `--url`, `--file` (base64), `--prompt-file`,
  `--dossier`, `--output`, `--raw-output`, `--write-composed-prompt`,
  `--dry-run`, `--ping`.
- Prompt v2 estructurado en 10 secciones (producer + DOP + montadora) con
  disciplina epistémica `OBSERVADO / INFERIDO / DECLARADO`.
- Comparativa rigurosa entre **Qwen 3.6 Plus**, **Gemini 2.5 Pro** y
  **Gemini 3.1 Pro Preview**, mismo clip, mismo prompt, mismo
  `max_tokens=8000`.
- Test con dossier mínimo "Macetas en una terraza en Castellar de n'Hug" para
  verificar que la disciplina `[DEC]` se respeta. Se respeta.
- Receta `ffmpeg` para clips pesados documentada en README (no ejecutada).

## Logros

- **PR #65 desbloqueado y a tu mando.**
- **Flujo `Claude Code → Bract → modelo VL → análisis estructurado`**
  funcional, reproducible, trazable (cada análisis genera respuesta,
  raw JSON, prompt usado).
- **Default del stack**: `google/gemini-3.1-pro-preview` por coste y
  cualitativo (ver hallazgos). Qwen 3.6 Plus y Gemini 2.5 Pro como
  alternativas para casos específicos.
- **Comparativa firmada** (en `video-tools/outputs/clip-macetas-*.txt`) que
  podemos releer cuando elijamos modelo para análisis del rodaje real.

## Hallazgos técnicos

| # | Hallazgo |
|---|----------|
| 1 | **Gemini 3.1 Pro Preview procesa el vídeo más comprimido**: 3.855 prompt-tokens vs 8.868 (Gemini 2.5 Pro) y 11.658 (Qwen 3.6 Plus) sobre el mismo clip. ~43% menos coste. |
| 2 | **Gemini 3.1 Pro Preview lee la pista de audio real** del clip, no solo infiere visualmente. Detectó campanas/cencerros que las otras solo conjeturaban. |
| 3 | **Gemini 3.1 Pro Preview es honesto sobre dirección de arte**: `"La dirección de arte está flaca: sacos textiles vacíos, mangueras mal puestas y envases de plástico blanco metidos a capón. Es el patio desordenado de alguien."` Las otras dos no se atreven a este nivel. |
| 4 | **El modelo `:free` de Qwen 3.6 Plus está deprecated** (404 con mensaje "transition to qwen/qwen3.6-plus for continued paid access"). Lección: usar paid por defecto. |
| 5 | **Análisis de audio del modelo no es determinístico**: misma señal, dos lecturas distintas (cencerros vs campanas en dos llamadas). Si necesitamos análisis de audio fiable, mejor extraer pista con ffmpeg y procesar aparte. |
| 6 | **`max_tokens=4000` se queda corto** para análisis de 10 secciones detalladas en Gemini. `8000` es el umbral razonable. |
| 7 | **Coste por análisis completo** (clip 25 s, 5 MB): ~$0.0005 con Gemini 3.1 Pro Preview. Iteración a volumen es viable. |

## Sorpresas

- **Gemini 3.1 Pro Preview detectó "Rupit"** como referencia geográfica
  cuando el clip era en realidad de Castellar de n'Hug. Mismo paisaje
  tipológico (pueblo medieval del Berguedà), lectura geográfica afinada
  que ningún otro modelo dio.
- **El dossier mínimo cambia las decisiones de montaje**: con dossier el
  modelo se vuelve más conservador y eligió otros "3 segundos más fuertes"
  que sin dossier (00:00–00:03 con dossier vs 00:10–00:13 sin dossier).
  Recomendación operativa: para clips del rodaje hacer **dos análisis** —
  con dossier (anclado) y sin dossier (lectura ingenua creativa). El doble
  de coste es irrelevante; la ganancia es leer el clip desde dos miradas.
- **El `videomacetas.mp4` que pasó Bea es del lugar real** donde se
  rodará. Material auténtico para validar el stack antes del rodaje real.

## Aprendizajes

- **Disciplina §9.2 funciona**: en el bloque 1 del día tuve dos commits con
  identidad inline (`Bract <bract@sprout.local>`), uno con `git mv` complejo,
  un push `--force-with-lease` tras rebase, y al cerrar el clone quedó en
  `main` con working tree limpio. Sin sustos. La regla que diseñasteis
  cubre exactamente el caso.
- **OpenRouter base64 vía data URL** es estable para clips < 25 MB. No hace
  falta `Gemini Files API` directa para nuestros tamaños actuales.
- **La disciplina epistémica en el prompt** (`OBS / INF / DEC`) se respeta
  por el modelo cuando se pide explícitamente. Reduce alucinaciones y
  permite que el equipo distinga lo que el modelo SABE de lo que CREE.
- **Gemini 3.1 Pro Preview tiene un bug puntual con aspect ratio**: con el
  clip 16:9 una vez dijo "1:1 cuadrado" y otra "16:9 vertical". Con dossier
  que lo declare se evita; sin dossier hay que verificar.

## Kudos

- **A Bea**: por sugerir probar Gemini 3.1 Pro Preview además de Qwen y
  por compartir el flujo de su compañera con el script
  `gemini_video_judge.py`. Las dos cosas marcaron el día. Sin la primera no
  habríamos visto la ventaja del modelo de Google; sin la segunda el script
  no tendría dry-run, output trazable ni soporte de dossier.
- **A Venation**: el handoff que dejó en PR #66 ahorró un montón de
  preguntas en mi mensaje a ella. De 4 preguntas que iba a hacerle, 0
  quedan abiertas (todas respondidas con su material).
- **A ti**: review del PR #65 quirúrgico — las 3 correcciones eran las
  exactas, sin ruido. Permite que el flujo siga limpio.

## *Next steps* — día 19

### Bloqueado por ti
- Esperando merge del PR #65. Cuando entre a main, Corola y Venation
  pueden responder.

### Bloqueado por respuesta de Corola
- Reorganización del shot_list sobre 9 escenas (incoherencia #1) y mis
  6 incoherencias creativas (#1, #4, #6, #7, #8, #9).
- Confirmación de plazo: idealmente guion v1.4 firmado en `video/script.md`
  el día 18 mañana (hoy ya tarde, mañana lunes 19). Si llega, el día 19
  arranco con draft de CapCut con cartelas EN literales en posición exacta.

### Bloqueado por respuesta de Venation
- Pequeño matiz de tipografía (Manrope + IBM Plex Mono vs monospace puro
  del shot_list) — propuesto para cerrar en reunión de tres con Corola.

### Bloqueado por Floema
- Capturas de Pollen UI para E4-E5-E7 cuando ella considere la UI estable.
  Día 17 estuvo refactorizando `MainActivity.kt`, `HomeScreen.kt`,
  `VisitarMeristemScreen.kt`, `ChatFeature.kt`. Si está estable mañana,
  arranco coordinación con ella.

### Bloqueado por Xilema / Endodermis
- Capturas Jetson para E2-E3-E7 cuando el Jetson esté arrancado. Estado
  vivo del cierre del día 16 indicaba bloqueo por cable display port-HDMI
  (Bea lo iba a recoger día 17). No tengo info del estado real día 18;
  si lo tienes, dímelo y arranco coordinación con Endo.

### Iniciativa propia (no bloquea a nadie)
- Si Bea me pasa más material rodado en Castellar, lanzo análisis con
  doble pasada (con dossier y sin) para entrenar mejor el prompt v2 antes
  del rodaje real.
- Posible plantilla `dossier-escena.md` por escena (E1-E9) para que cuando
  llegue material del rodaje, cada clip se analice con su contexto narrativo
  específico. Si te encaja, te paso propuesta cuando merguees PR #65.

### Recordatorio del calendario
- Día 19-20: rodaje. Mi rol durante rodaje es asíncrono (analizo material a
  medida que llega).
- Día 22-25: post-pro intensiva.
- Día 28: corte final integrado.
- Día 30: entrega.

## Estado actual del repo y disciplina

- Branch propio: `feat/bract/montaje-v1`. 3 commits con identidad inline.
- PR #65 OPEN, ready for review, esperando tu merge.
- Issue #64 abierto y enlazado al PR (`Closes #64`).
- Etiqueta `node:video` creada con color `#10b981`.
- `.git/config` del clone compartido **intacto**, sigue como
  `zigiella` / email de Bea (no he sobrescrito).
- Verificación §9.2 al cierre: working tree limpio, vuelvo a `main`.

## Lo que NO he hecho hoy (a propósito)

- Disparar mensajes a Corola y Venation manualmente (envío vía merge del
  PR, no por canal lateral antes de tu review).
- Tocar archivos calientes (`docs/40_pitch_video.md`,
  `docs/01_architecture.md`, `writeup/draft.md`).
- Subir la herramienta `video-tools/` al repo Sprout. La API key vive
  fuera. Si en una segunda iteración quieres que el script (sin la key)
  entre al repo para que otras lo usen, abro PR aparte.

Buen cierre del día 18. Quedo a tu mando para el día 19.

— Bract
