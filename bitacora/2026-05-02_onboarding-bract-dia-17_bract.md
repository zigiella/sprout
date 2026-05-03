# Onboarding Bract — día 17

**Fecha:** 2026-05-02
**Autora:** Bract
**Rol:** Montadora de vídeo (frente vídeo, junto a Corola y Venation)
**Mando técnico:** Cambium
**Identidad git:** `Bract` / `bract@sprout.local` (modo inline §11.1)
**Nodo:** `node:video`
**Branch propio:** `feat/bract/montaje-v1`

## Lo hecho en esta sesión

### Lecturas completas

- `docs/00_estado_vivo.md` (cierre día 16)
- `docs/00_positioning.md`
- `docs/40_pitch_video.md` (pitch + 9 escenas + 5 frases fuertes)
- `video/shot_list.md` en branch `feat/corola-shot-list-v0` (15 planos, v0.3, autora Corola)
- `CONTRIBUTING.md` entero, incluida §9.2 nueva (operaciones git seguras en máquina compartida)
- Lectura parcial de specs: `01_architecture.md`, `10_rhizome_spec.md`, `11_pollen_spec.md`, `12_meristem_spec.md`, `13_esp32_spec.md`, `30_safety_rules.md` — pendiente segunda pasada profunda.

### Trabajo previo en `video-proyecto/` (fuera del repo, días 15-16)

Carpeta de trabajo personal de Bract en la máquina de Bea, no parte del repo:

- Stack `Claude Code → cutcli → CapCut` verificado y funcionando.
- Esqueleto de draft de CapCut con las 9 escenas del `pitch_video.md` colocadas en sus tiempos exactos (1920×1080, 30 fps, base casi-negra de 3:00).
- Plan de pistas para doble export (ES original + EN dub) con la voz cruda de E5 manteniendo castellano en ambas versiones.
- Borrador de prompts Veo (`produccion/veo-prompts.md`) limitado a planos 08 y 14, alineado con la doctrina de Corola.
- Repo `sprout-repo/` clonado en lectura.

### Disciplina §9.2 adoptada

- Tres puntos de verificación antes de cada commit: `git status`, `git branch --show-current`, `git stash list`.
- Stash con prefijo: `[bract] WIP descripción`.
- Una operación atómica por sesión (cierre con working tree limpio).
- Identidad git inline (no persistente) para no pisar la del clon compartido.

## Riesgos detectados (apuntados en mensajes a Corola y Cambium)

1. **Incoherencias entre `video/shot_list.md` y `docs/40_pitch_video.md`** — climax narrativo, posición del cenital editorial, presencia de Meristem en MVP. Detalle en borrador a Corola.
2. **3 minutos es justo** para la arquitectura cubierta. E5 (voz cruda) y E9 (cierre editorial) son las primeras candidatas a recorte si toca hacer hueco.
3. **Doble export ES / EN-dub** añade fricción si no se planifica desde el inicio. Previsto en la estructura de pistas del draft.

## Pendientes inmediatos día 17

- Mandar mensaje a Corola sobre incoherencias (borrador en `bitacora/2026-05-02_borrador-mensaje-corola-incoherencias_bract.md`).
- Mandar mensaje a Venation sobre assets necesarios (borrador en `bitacora/2026-05-02_borrador-mensaje-venation-assets_bract.md`).
- Esperar respuesta de Floema sobre estabilidad UI Pollen (capturas E4-E5-E7).
- Esperar respuesta de Xilema sobre disponibilidad de capturas Jetson (E2-E3-E7).

## Pendientes para próximas sesiones

- Segunda pasada profunda a specs Rhizome / Pollen / Meristem / ESP32 para cazar incoherencias entre lo que diga el vídeo y lo que dicen los specs.
- Cuando el guion v1.4 esté firmado en `video/script.md`, regenerar el draft de CapCut con cartelas EN literales en posición exacta (capa de texto separada de los marcadores actuales).
- Ensayar pipeline `HTML animado → MP4 con alfa` (Playwright + FFmpeg) por si Venation lo necesita para overlays con movimiento.

## Decisiones que adopto desde hoy

- Los archivos calientes (`docs/40_pitch_video.md`, `docs/01_architecture.md`, `writeup/draft.md`) **no los toco directamente**: si necesito cambio, mensaje a Cambium.
- Trabajo siempre en `feat/bract/<descripcion>` con slash, no en main.
- Cualquier decisión grande se eleva a Bea o Cambium. Coordinación lateral con Corola y Venation es directa.
