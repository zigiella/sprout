# Handoff video — assets disponibles para Corola y Bract

**Fecha:** 2026-05-02
**Autor:** Venation
**Area:** Video
**Tipo:** Avance

## Contexto

Entrada conjunta para Corola (direccion creativa, duena del guion v1.4) y
Bract (montaje en CapCut). El primer encuentro presencial entre las tres lo
agenda Bea cuando cuadre. Mientras tanto dejo aqui inventario completo de lo
que ya tengo producido y como encaja con `docs/40_pitch_video.md`.

Esto es un **handoff de materiales**, no una propuesta de cambios al guion.
El guion v1.4 es de Corola; las decisiones creativas son suyas. Mi trabajo es
servir el frente visual al ritmo que Bract necesite y a la voz que Corola fije.

## Que hice / decidi

### Sistema visual ya producido

- **Paleta** soil/water con `signal.seed` (#C5F26B) reservado a
  inteligencia activa.
- **Tipografia** Manrope (UI) + IBM Plex Mono (datos/JSON).
- **Cartelas y overlays** 1280×720, fondos transparentes, safe-area al 5%.
- **Lower-third** con dock de schema + linea de TTL/jurisdiccion.
- **Bordes dobles** para estados bloqueados/expirados.
- **Cuadriculado** para overlays semi-transparentes (lectura de transparencia).
- **Sello de marca "AI Local-first"** aplicado consistentemente.
- **Subtitulo logo (EN):** *"Local-first irrigation decisions. Safe ·
  explainable · open-source."* (ajustado tras feedback Corola dia 16).

### Mapeo a las 9 escenas del guion v1.4

| Escena | Asset disponible | Estado |
|--------|------------------|--------|
| E2 0:20-0:45 | Overlay `DecisionReceipt` con `final_action`, `why_short`, `policy_id` resaltados; cartela esquina *"Gemma 4 E2B · local · llama.cpp"* + sub *"LLM called only when ambiguous"* | Listo |
| E3 0:45-1:00 | Overlay **`ESP32 SAFE LIMIT`** mostrando `candidate_action.seconds=30 → final_action.seconds=12`; cartela narrativa central ***"Cuando duda, riega menos."***; cartela esquina *"function/read tools · no actuator tools"* | Listo |
| E4 1:00-1:30 | Cartela esquina *"Gemma 4 E4B · LiteRT-LM · on-device"*; pantalla Pollen "Ask" con `DecisionExplanationResponse` renderizada | Listo |
| E5 1:30-1:50 | Overlay `MissionPatch validado` con `horizon_h`, `priority_plot`, `budget_cap_ml`, `operator_note` literal | Listo |
| E6 1:50-2:10 | Overlay `WeatherDigest ferry` rhizome_01 → rhizome_02; pantalla Pollen "Context ferry" | Listo |
| E7 2:10-2:30 | Side-by-side antes/despues `soil_thresholds.dry: 35→25` y `daily_budget_ml: 1500→900`; cartela ancla **"Criterio modificado"**; cartela invariante esquina inferior derecha *"Physical layer prevails. Rhizome arbitrates. Pollen mediates. Meristem refines."* | Listo |
| E8 2:30-2:40 | Overlay `expired → rejected` con borde doble de bloqueo | Listo |
| E9 2:40-3:00 | **Cenital animado** 1920×1080, 20s, paquetes tangibles `POLICIES` y `RECEIPTS` viajando entre Meristem y Pollen, recorrido por las 8 parcelas con iluminacion progresiva, cierre con `SYNCED ✓` y cartela progresiva *"Una parcela. Dos. Ocho. Autonomas. Inteligencia federada con Pollen."* | Listo |

### Sobre el cenital E9 (reduce dependencia de Veo3)

La escena 9 estaba como **prompt Veo3 final** pendiente en el plan. La tengo
animada en HTML/CSS/SVG, ya sin generacion externa. Eso significa:

- Bract puede integrar la escena 9 desde su primer corte sin esperar Veo3.
- Si por estilo Corola decide volver a Veo3, mi version queda como fallback
  estable.
- Puedo exportarla como **MP4 / WebM** a la longitud exacta que Bract pida
  (20s segun guion), o como **secuencia PNG** si le viene mejor para CapCut.

### Pollen UX para tomas de pantalla

Prototipo bilingue EN/ES con todas las pantallas que aparecen en E4/E5/E6/E7:
Home, Rhizome status, Visit console, Mission compiler con
waveform→listening→compiling→ACK, Ask, Audit, Context ferry, Decision log,
Meristem sync. **Outdoor mode high-contrast** disponible si se filma en
exterior con luz fuerte. Tweaks expuestos para que Corola pueda comparar
variantes sin tocar codigo.

## Por que

El guion v1.4 esta cerrado conceptualmente desde el dia 14, con feedback DEV
externa integrado. Las cartelas y overlays no son decoracion: son parte de
la prueba de la tesis (frase 2 "Cada visita puede cambiar el criterio local"
se demuestra en E4-E5; frase 4 "Toda inteligencia tiene jurisdiccion y fecha
de caducidad" se demuestra en E8 con `expired → rejected`). Los assets ya
estan hechos para reforzar exactamente eso.

## Que necesito de Corola

- [ ] **Validacion del paquete**. Si algo del inventario no encaja con el
      guion v1.4 o con la voz creativa, lo ajusto en una pasada.
- [ ] **Voz humana real escena 5** — pendiente segun estado vivo. ¿Quieres
      que adapte el overlay de E5 a la entonacion final cuando este grabada?
- [ ] **Traducciones first pass** — pendiente segun estado vivo. ¿Las llevas
      tu o las preparo y tu las modulas?
- [ ] **Cartela final con el nombre Sprout justo antes del fundido**
      (E9 final). ¿La quieres como la propuse o prefieres tratamiento
      distinto del logo?

## Que necesito de Bract

- [ ] **Convencion de naming de archivos** que prefieras. Yo los tengo
      como `E07 · 02-10 · criterio-modificado.png` (middle-dot). Si CapCut
      te trabaja mejor con snake_case (`E07_0210_criterio_modificado.png`)
      o kebab-case, los renombro antes de pasar el lote.
- [ ] **Formato del cenital E9.** Por defecto exporto MP4 H.264 1920×1080
      24fps, 20s, sin audio. Si prefieres WebM, ProRes o secuencia PNG
      transparente, dimelo.
- [ ] **Resolucion final del corte.** Tengo todo a 1920×1080 pero tus
      overlays los disenare a 1280×720 (segun standard que vi en mi pack).
      ¿Confirmas resolucion master del montaje?
- [ ] **Punto de entrega.** ¿`video/final/` para exports definitivos?
      ¿Carpeta intermedia para drafts? Sigo lo que digas.

## Que queda pendiente (mio)

- [ ] Esperar a la reunion de tres que agenda Bea.
- [ ] Una vez con feedback de Corola y de Bract, abrir issue de
      handoff de assets en el tablero, asignarmela y mover a "In Progress".
- [ ] Producir lote final con naming acordado y commitear en `video/final/`
      en commits pequenos por escena.

## Enlaces

- [docs/40_pitch_video.md](../docs/40_pitch_video.md)
- [video/README.md](../video/README.md)
- [bitacora/2026-05-02_onboarding_venation.md](2026-05-02_onboarding_venation.md)
