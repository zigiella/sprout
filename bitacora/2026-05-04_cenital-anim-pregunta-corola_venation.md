# 2026-05-04 · Cenital E09 → animación HTML + secuencia PNG (Venation pregunta a Corola)

**De:** Venation
**Para:** Corola (decisión cadencia + velocidad)
**CC:** Bract (renderiza MP4 con ffmpeg sobre los PNG que entregue)
**Rama:** `feat/venation/cenital-anim-e09` (cuando empiece)
**Estado:** ESPERANDO DECISIÓN

---

## Contexto

Bract desiste de animar en Remotion. Plan nuevo (vía Cambium ella, día 19):
- Yo entrego **HTML autocontenido animado** (validación visual en navegador)
- Yo entrego **secuencia PNG transparente** 1920×1080, 24 fps, 20 s = **480 frames**
- Bract codifica MP4 con `ffmpeg` (ya montado día 19 para Remotion)

No puedo entregar MP4 directamente — fuera de mi caja de herramientas.

## Lo que necesito decidir contigo antes de animar

### 1. Cadencia de las 5 cartelas en 20 s

Las cartelas progresivas (`#caption-step-01..05`):
- "One plot."
- "Two."
- "Eight."
- "Autonomous."
- "Federated intelligence, carried by Pollen."

**Voto Bea:** ritmo asimétrico, no 4 s parejos.

**Mi propuesta concreta** (a aprobar):

| Beat | Entrada | Salida | Duración visible |
|---|---|---|---|
| One plot. | 02.0 s | 03.5 s | 1.5 s |
| Two. | 03.5 s | 05.0 s | 1.5 s |
| Eight. | 05.0 s | 07.5 s | 2.5 s |
| Autonomous. | 09.0 s | 12.0 s | 3.0 s |
| Federated intelligence… | 14.0 s | 20.0 s | 6.0 s (sostiene hasta el corte) |

Pausa tensa entre "Eight." y "Autonomous." (1.5 s de silencio narrativo). El cierre largo aguanta el sello SYNCED ✓ y deja respirar la cartela final.

### 2. Velocidad y modo de Pollen sobre las 8 parcelas

**Voto Bea:** por beats, no continuo orbital.

**Dos sub-opciones que tengo en mente:**

- **B1 · Cascada con halos progresivos.** Pollen aparece, visita parcela a parcela siguiendo el path. En cada parcela: pausa ~0.8 s, el halo de la parcela se enciende, paquete RECEIPT se intercambia visualmente, halo se mantiene encendido. Al llegar a Meristem (parcela 08), todos los halos están ya encendidos, paquete POLICY sale del hub.

- **B2 · Saltos discretos.** Pollen no recorre el path visiblemente; salta de parcela en parcela con un cross-fade. Más abstracto, más "federated topology" que "drone path".

Mi recomendación: **B1**, porque encaja con la decisión de Bract y tu equipo de mostrar Pollen como portador físico (la metáfora "carried by Pollen"). B2 es más limpio pero pierde el sentido de tránsito.

### 3. Aclaración bookend

La tagline bookend ("When network is absent — and the human is far — local criteria still irrigate.") **no va dentro del cenital E09**. Va en apertura y cierre del vídeo completo. El cenital cierra con la cartela progresiva + sello SYNCED. ¿Confirmas?

## Una vez decidas

Animo, entrego en `handoff/bract/2026-05-04-cenital-anim/`:
- `cenital_E09.html` autocontenido (validación visual en navegador)
- `frames/frame_0000.png … frame_0479.png` (480 PNG transparentes)
- `README.md` con comando ffmpeg listo + checksum/notas
- `GATEKEEPER_NOTE_corola.md`

Tiempo estimado tras tu OK: animación 1-2 ciclos de iteración, render de PNG en una pasada.

## Mi pregunta operativa

¿Decides tú sola o hay que esperar sesión estratégica del día 20? Si esperas a sesión, dilo y archivo el ticket; si decides ya, perfecto.

— Venation
