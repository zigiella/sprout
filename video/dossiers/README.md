# video/dossiers/

Dossiers por escena para alimentar al modelo VL (Gemini 3.1 Pro Preview por
defecto vía la herramienta `video-tools/`) cuando analizamos clips de prueba
o material del rodaje.

## Para qué sirven

Cada `Eнн.md` es contexto compacto que ancla al modelo en hechos verificados
sobre la escena: tiempos, VO literal, cartelas EN, origen del material,
riesgos a evitar. El modelo lo recibe como **dossier adjunto** y lo etiqueta
como `[DEC]` (declarado) en su análisis. Reduce especulación y permite cruzar
guion ↔ material.

## Patrón de uso

```bash
# Análisis con dossier de la escena
.venv/Scripts/python.exe ver_video.py \
  --file plano_E2_take03.mp4 \
  --prompt-file prompts/analisis-completo-v2.txt \
  --dossier video/dossiers/E2.md \
  --output outputs/E2_take03.txt \
  --max-tokens 8000

# Doble análisis (con + sin dossier) para tener lectura ingenua creativa
.venv/Scripts/python.exe ver_video.py \
  --file plano_E2_take03.mp4 \
  --prompt-file prompts/analisis-completo-v2.txt \
  --output outputs/E2_take03_ingenuo.txt \
  --max-tokens 8000
```

## Estructura

- `_template.md` — plantilla vacía, copiar y adaptar.
- `E1.md ... E9.md` — dossiers cerrados (compatibles con guion `v2.1` actual).
- `E9b.md` — pendiente, se cerrará tras sesión conjunta cuando E9b se
  apruebe formalmente.

## Versión del guion

Estos dossiers están alineados con `docs/40_pitch_video.md` v2.1 + las
decisiones del día 17-18 (cartela Sprout inicial, apertura E1 con 4 datos
globales, VO en inglés master + dub ES, tagline bookend). Cuando Cambium
actualice `pitch_video.md` con la nueva versión consolidada, **hay que
regenerar los dossiers afectados**. La cabecera de cada uno indica con qué
versión es compatible.

## Convención de nombres

- `Eнн.md` — escena principal con dos dígitos (E01, E02, …).
- `Eннx.md` — sub-escena (E09b, etc.).
- Todo en español para coherencia con el resto de `docs/` y `bitacora/`,
  aunque las cartelas EN del vídeo se citen literales en inglés.

## Convención narrativa: parcelas vs macetas

**El vídeo habla de parcelas, pero filmamos macetas.** Es una simulación
honesta asumida por el equipo (apuntada por Bea día 19):

- **"Parcela"** = escala de la solución diseñada. Lo dicen VO, cartelas EN
  y writeup. La solución se piensa para parcelas reales (almendros remotos,
  cultivos de secano, etc.).
- **"Maceta" o "jardinera"** = material físico filmable. **Sprout escala 1
  está plantado en la terraza de Bea en Castellar de n'Hug** (tomate, fresa,
  pimientos, aromáticas) con garrafa-depósito y sensores ESP32. El sistema
  funciona a escala doméstica — no es metáfora.

`pitch_video.md` v2.1 lo formaliza: *"dos parcelas lógicas (`rhizome_01`
con estación meteo + `rhizome_02` sin meteo) se filman con un solo Rhizome
físico — distinto ángulo, distinta maceta, distinta zona de terraza. Los
IDs en pantalla hacen el trabajo lógico."*

### Implicación para análisis con dossier

Cuando analicemos un clip con su dossier de escena vía `ver_video.py`, el
modelo VL puede flagear como contradicción que el VO hable de parcela y la
imagen muestre maceta. **Ese flag es falso positivo salvo que el guion
explícitamente prohíba la simulación**. El equipo asumió la simulación con
conciencia.

Cuando un dossier mencione "parcela" en VO o cartelas, en la sección de
"Visual / planos previstos" indicar siempre que el sujeto visual será maceta
o jardinera y que los IDs `rhizome_01`/`rhizome_02` hacen el trabajo lógico.

## Mantenimiento

- Los dossiers son responsabilidad de **Bract**.
- Si Corola cambia algo del guion, Bract regenera los dossiers afectados.
- Si Venation cambia algún asset (cartela, overlay, cenital), Bract
  actualiza la sección correspondiente.
- Si una decisión grande del frente vídeo aterriza en `pitch_video.md`,
  Bract actualiza la cabecera de cada dossier afectado y commitea.
