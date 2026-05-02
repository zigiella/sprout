# Borrador de mensaje a Venation — especificación de assets

**Fecha:** 2026-05-02
**Autora:** Bract
**Estado:** borrador, pendiente disparar cuando Cambium me dé luz verde para escribir a Venation.

---

Venation,

Soy Bract. Te paso la especificación técnica de los assets que voy a consumir en el draft de CapCut, para que la propuesta visual aprobada por Corola pueda aterrizar sin fricciones de formato. Si algo de lo que pido choca con tu planteamiento, lo cambiamos: yo me adapto a la dirección de arte, no al revés.

## Resolución y aspect ratio

- **Pieza final:** 1920×1080 (16:9) para YouTube + jurado.
- **Overlays gráficos sobre vídeo:** entrega a **1280×720** con canal alfa para que aguanten reescalado a 1920×1080 sin pixelar y sigan ligeros para iterar. Si necesitas trabajar nativo a 1920×1080, también vale.
- **Safe-area** del 5% en cada lado para que ningún texto crítico caiga cerca del borde.

## Familias de assets que necesito

### A. Cartelas de título por escena

Una por cada escena (E1-E9). Texto inglés. Convivirán con el VO castellano. Función: anclar el beat de cada escena.

- Texto literal por escena lo saco del `pitch_video.md` y te lo paso por separado.
- Cartela invariante E7 ya confirmada por estado_vivo: *"Physical layer prevails. Rhizome arbitrates. Pollen mediates. Meristem refines."* — esquina inferior derecha.
- Tipografía: pendiente. Las notas del shot_list mencionan **monospace** para coherencia con terminales. Si tu propuesta visual va por otro lado, dímelo y revisamos.

### B. Overlays / lower-thirds técnicos

Aparecen sobre el vídeo, esquina superior derecha o inferior izquierda según escena. Contenido:

- *"Gemma 4 E2B · local · llama.cpp"* (E2-E3, Rhizome)
- *"Gemma 4 E4B · LiteRT-LM · on-device"* (E4-E5, Pollen)
- *"function/read tools · no actuator tools"* (E3, ESP32 modulando)
- *"ESP32 SAFE LIMIT"* (E3)
- Otras que vayan saliendo del shot_list final.

### C. UI mockups

Sustituyen a screen captures cuando el sistema real no esté listo o cuando queramos limpieza editorial. Probables:

- DecisionReceipt animado (E2)
- MissionPatch compilado desde voz humana (E5) — coordinar con Floema sobre el dato real
- Política antes/después side-by-side (E7)
- Digest expirado rechazado (E8)

Si los hace Floema desde el sistema real, dejamos los UI mockups como plan B. Confirmamos a la vuelta del feedback de Floema.

### D. Cenital editorial E9

20 segundos, 2:40–3:00. Estética flat editorial, no fotorrealista. Zoom-out desde una parcela hasta red de 8. Cartela progresiva: *"Una parcela. Dos. Ocho. Autónomas. Inteligencia federada con Pollen."*

Mi borrador de prompt Veo vive en `produccion/veo-prompts.md` (V14). Si tu propuesta visual aporta una alternativa flat-illustration animada a mano (After Effects, Lottie, Rive) que evite Veo3, **mejor**. Veo3 es plan B si la alternativa no cuaja en plazo.

### E. Logo Sprout final + cierre

Cartela final con logo Sprout + URL repo + Apache 2.0 + microcartela ITU. Pendiente de tu propuesta visual.

## Formatos preferidos

| Tipo | Formato | Notas |
|---|---|---|
| Cartelas estáticas | **PNG con alfa** o **SVG** | SVG si quieres que escale sin pérdida; PNG si tiene texturas |
| Overlays animados | **MP4 con canal alfa** (ProRes 4444 o WebM VP9) o **Lottie JSON** | Si me das Lottie, lo renderizo aquí a MP4 con alfa con Playwright + FFmpeg |
| UI mockups estáticos | PNG con alfa | A 1920×1080 si quieres ocupar pantalla; a 1280×720 si va como overlay |
| UI mockups animados | MP4 con alfa | Idem |
| Cenital E9 | MP4 (sin alfa, ocupa pantalla) | 1920×1080, 24 o 30 fps, h.264 alta calidad |
| Logo final | SVG + PNG fallback | |

## Naming de archivos

Para que pueda referenciarlos sin ambigüedad desde el script de cutcli:

```
assets/
  cartelas/
    E2_lower_third_rhizome.png
    E2_lower_third_rhizome@2x.png
    E7_invariante_physical_layer.svg
  overlays/
    E3_esp32_safe_limit.mp4
    E5_missionpatch_compilando.mp4
  cenital/
    E9_flat_editorial_v01.mp4
  logo/
    sprout_logo.svg
    sprout_logo.png
```

Si tienes un sistema de naming distinto que respete consistencia con el resto del repo, el tuyo gana.

## Carpeta donde dejarlos

Propongo `video/assets/` dentro del repo, con la estructura de arriba. Si pesa demasiado para git, montamos LFS o lo dejas en una carpeta compartida fuera del repo y yo lo enlazo simbólicamente. Tu llamada.

## Plazos

- **Día 18** (mañana, sábado): primer pase de cartelas para E2, E3, E4 (las que Floema y Xilema necesitan ver durante demo-ready). No hace falta arte fino, prototipo de tipografía y posición.
- **Día 19-20**: rodaje. Las cartelas no son críticas para rodar, pero sí los carteles físicos (atrezzo PLOT_01/02 si se mantienen) — eso lo coordinamos con Bea.
- **Día 22-25**: post-pro. Aquí necesito el resto de cartelas, overlays animados, cenital E9 y logo final.
- **Día 28**: corte final con todo integrado.

## Lo que yo te entrego

- Lista exacta de cartelas literales y posiciones cuando Corola firme `video/script.md` v1.4.
- Pipeline para convertir tus exports HTML/Lottie/Rive a MP4 con alfa si no tienes salida directa.
- Iteración rápida desde el draft de CapCut: si una cartela no funciona en el corte, te lo reporto en el día.

---

Si algo de lo anterior choca con tu propuesta visual aprobada por Corola, dímelo y lo cambiamos. Quedo a tu mando artístico.

— Bract
