# Cierre día 16 — refuerzo nombres nodos + nuevos miembros + copies bilingües

**Fecha:** 2026-05-01 (día 16)
**Autora:** Corola
**Estado:** anclaje histórico de la jornada
**Rama:** `feat/corola-guion-v1`

---

## Resumen

Día 16 denso en gestión + apilado. Cinco decisiones aplicadas al guion (script + shot list v1.4 → v1.5), nuevo documento creado (`copies_bilingual.md` v0.1), tres incorporaciones nuevas al equipo registradas (Xylem montadora, Venation directora de arte, Floema confirmando opción A para escena 5).

## Decisiones recibidas y aplicadas

### Aplicadas hoy en código

1. **Swap "commands" → "prevails"** en cartela invariante de E7 (voto Bea día 16). Texto final: *"Physical layer prevails. Rhizome arbitrates. Pollen mediates. Meristem refines."*

2. **Carteles físicos extendidos a 4** (decisión Bea día 16):
   - Maceta: `PLOT_01 with RHIZOME_01` / `PLOT_02 with RHIZOME_02`
   - Caja electrónica: `RHIZOME_01` / `RHIZOME_02` (intercambiables sobre la misma cajita Jetson+ESP32 entre tomas)
   - Bea los prepara (Helvetica, mayúsculas, fondo neutro, inglés).

3. **Refuerzo de nombres de nodos** en planos 04a, 06a, 06d, sección decisión rodaje. Los nodos (Rhizome) aparecen visualmente nombrados durante todo el rodaje en plano físico.

4. **Contingencia "sin meteo"** anotada en E6 (no firme). Si Bea decide prescindir, las dos parcelas se distinguen por cartel + planta + ángulo. Frase fuerte 5 se sostiene — federación de contexto en general.

5. **Copies bilingües ES/EN** — nuevo documento `video/copies_bilingual.md` v0.1 con escenas 1-3 completas. Convenciones documentadas: VO castellano grabado por Bea, cartelas inglés en pantalla, voz humana E5 excepción única (castellano literal, no se traduce).

### Pendientes del día (para apilar día 17+)

- Continuar `copies_bilingual.md` con escenas 4-9.
- Crear `video/montage_brief.md` en formato Xylem (escena · plano · tiempo · origen · VO ES · cartela EN · transición · sfx).
- Refinar traducciones first pass restantes (cartela ancla E7, cartela progresiva E9, subtítulo logo final).
- Pedir adjuntos de ideas de Venation (Bea los mencionó pero no aparecieron en el mensaje).

## Equipo zigiella — actualización del día 16

**Tres incorporaciones nuevas:**

1. **Xylem (montadora con Capcut).** Trabaja en formato concreto que Bea me pasó. Lee repo en modo lectura. Bea me pondrá en contacto con ella pronto. Necesito producir `montage_brief.md` en su formato.

2. **Venation (directora de arte).** Trabajará sistema de diseño para app móvil + landing + cartelería física + cartelas vídeo + todo lo que se produzca. Bea preguntó qué me parece — respuesta: sí, gana coherencia visual entre todo el material. Pendiente ver sus ideas (adjuntos no llegados aún).

3. **Endodermis** (registrado día 15) — sin cambios. Solo afecta si día 24+ MVP funciona y arrancamos doble agente días 25-30.

**Bea trabaja con Floema en UX app móvil** (información de paralelo, no me afecta directamente).

## Floema confirmó opción A para escena 5

Captura real de Pollen procesando voz humana en rodaje 26-27. Mitigación: cache de pesos para TTFT inmediato. `operator_note` se queda literal castellano. Mensaje completo no relayeado por Bea — confirmado oralmente vía Cambium ella.

## Cambium ella formaliza regla "tres puntos de verificación git"

Mi aprendizaje del día 15 (verificar `git status` + `git branch --show-current` + `git stash list` antes de cada commit) escala a convención del proyecto. Cambium la formaliza mañana en `CONTRIBUTING.md` o `docs/conventions/git_safety.md`. Hallazgo cultural anotado para writeup.

## Cuestiones pendientes para Bea

1. **Pitch doc §4 actualización** con E9 final — Cambium ella escribió "Tu turno cuando tengas hueco". Ambiguo: ¿mi scope o de Cambium? Bea aclara.

2. **Timing Slack MCP** — Bea quiere probarlo conmigo para comunicarse durante rodaje. ¿Lo hacemos antes del rodaje 26-27 o post-hackathon? Pasos accionables documentados día 15. Decisión pendiente.

3. **Adjuntos Venation** — Bea mencionó "te adjunto las ideas que ha trabajado" pero no se vieron en el mensaje. Pedir.

4. **Voto Bea sobre Slack MCP** — yo recomiendo post-hackathon (riesgo distracción técnica), pero ella quiere probarlo durante rodaje. Decisión final suya.

## Pendientes activos día 17+

1. **`copies_bilingual.md` escenas 4-9.** (Plazo: día 17 mañana.)
2. **`montage_brief.md` escenas 1-3 en formato Xylem.** (Plazo: día 17 tarde.)
3. **`montage_brief.md` escenas 4-9.** (Plazo: día 18.)
4. **Refinar traducciones first pass** — sesión corta con Bea cuando cuadre.
5. **Coordinación con Xylem** cuando Bea me ponga en contacto.
6. **Coordinación con Venation** cuando lleguen los adjuntos.
7. **Ensayo capturas pantalla Jetson** E2/E3/E7 con Xilema.
8. **Prompt Veo3 final E9** con Bea cuando tenga hueco.
9. **Slack MCP** — pendiente decisión de Bea sobre timing.

## Patrón observado del día

Día 16 introduce **dos miembros nuevos del equipo creativo del video** (Xylem montadora, Venation directora de arte). Esto es señal de que el frente video pasa de **diseño** (escritura del guion) a **producción** (rodaje + montaje + diseño visual de todo). Mi rol como directora creativa se integra ahora con un equipo más amplio:

- **Yo (Corola):** dirección creativa de guion + shot list + relación con Cambium / Bea / Floema / Xilema / Meristem.
- **Bea:** dirección general + voz + relación con Floema (UX app) + producción carteles físicos.
- **Xylem:** montaje en Capcut. Lee repo en modo lectura. Trabajaré con ella en formato montaje.
- **Venation:** sistema de diseño visual. Coherencia entre app, landing, cartelería, cartelas vídeo.

Este equipo extendido implica producir **más documentos para coordinación cruzada** que documentos para mí. El `copies_bilingual.md` es para Xylem (montadora EN/ES), el futuro `montage_brief.md` es para Xylem en su formato, las cartelas finales son para Venation. El `script.md` y `shot_list.md` siguen siendo míos + del equipo interno (Cambium, Bea).

## Estado git

Verificación triple antes de commit (regla del día 15):
- `git status`: cambios en `video/script.md`, `video/shot_list.md`, `video/copies_bilingual.md` (nuevo).
- `git branch --show-current`: `feat/corola-guion-v1` ✓
- `git stash list`: vacío ✓

Sin sorpresas operativas hoy. La regla funciona.
