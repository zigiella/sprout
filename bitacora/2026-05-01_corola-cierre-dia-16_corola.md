# Cierre día 16 — refuerzo nombres nodos + nuevos miembros + copies bilingües

**Fecha:** 2026-05-01 (día 16)
**Autora:** Corola
**Estado:** anclaje histórico de la jornada
**Rama:** `feat/corola-guion-v1`

---

## Resumen

Día 16 denso en gestión + apilado. Cinco decisiones aplicadas al guion (script + shot list v1.4 → v1.5), nuevo documento creado (`copies_bilingual.md` v0.1), tres incorporaciones nuevas al equipo registradas (Bract montadora, Venation directora de arte, Floema confirmando opción A para escena 5).

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
- Crear `video/montage_brief.md` en formato Bract (escena · plano · tiempo · origen · VO ES · cartela EN · transición · sfx).
- Refinar traducciones first pass restantes (cartela ancla E7, cartela progresiva E9, subtítulo logo final).
- Pedir adjuntos de ideas de Venation (Bea los mencionó pero no aparecieron en el mensaje).

## Equipo zigiella — actualización del día 16

**Tres incorporaciones nuevas:**

1. **Bract (montadora con Capcut).** Trabaja en formato concreto que Bea me pasó. Lee repo en modo lectura. Bea me pondrá en contacto con ella pronto. Necesito producir `montage_brief.md` en su formato.

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
2. **`montage_brief.md` escenas 1-3 en formato Bract.** (Plazo: día 17 tarde.)
3. **`montage_brief.md` escenas 4-9.** (Plazo: día 18.)
4. **Refinar traducciones first pass** — sesión corta con Bea cuando cuadre.
5. **Coordinación con Bract** cuando Bea me ponga en contacto.
6. **Coordinación con Venation** cuando lleguen los adjuntos.
7. **Ensayo capturas pantalla Jetson** E2/E3/E7 con Xilema.
8. **Prompt Veo3 final E9** con Bea cuando tenga hueco.
9. **Slack MCP** — pendiente decisión de Bea sobre timing.

## Patrón observado del día

Día 16 introduce **dos miembros nuevos del equipo creativo del video** (Bract montadora, Venation directora de arte). Esto es señal de que el frente video pasa de **diseño** (escritura del guion) a **producción** (rodaje + montaje + diseño visual de todo). Mi rol como directora creativa se integra ahora con un equipo más amplio:

- **Yo (Corola):** dirección creativa de guion + shot list + relación con Cambium / Bea / Floema / Xilema / Meristem.
- **Bea:** dirección general + voz + relación con Floema (UX app) + producción carteles físicos.
- **Bract:** montaje en Capcut. Lee repo en modo lectura. Trabajaré con ella en formato montaje.
- **Venation:** sistema de diseño visual. Coherencia entre app, landing, cartelería, cartelas vídeo.

Este equipo extendido implica producir **más documentos para coordinación cruzada** que documentos para mí. El `copies_bilingual.md` es para Bract (montadora EN/ES), el futuro `montage_brief.md` es para Bract en su formato, las cartelas finales son para Venation. El `script.md` y `shot_list.md` siguen siendo míos + del equipo interno (Cambium, Bea).

## Estado git

Verificación triple antes de commit (regla del día 15):
- `git status`: cambios en `video/script.md`, `video/shot_list.md`, `video/copies_bilingual.md` (nuevo).
- `git branch --show-current`: `feat/corola-guion-v1` ✓
- `git stash list`: vacío ✓

Sin sorpresas operativas hoy. La regla funciona.

---

## Adiciones tarde día 16

### Design pack de Venation recibido y valorado

A última hora del día Bea me pasó el ZIP completo de Venation: `sprout_design_pack_v1.zip` (14 archivos, ~76 KB). Descomprimido fuera del repo en `C:/Users/Usuario/Desktop/CAJON/sprout_design_pack_v1/`.

**Contenido:**
- `00_design_system.md` — sistema maestro (Soil protocol + Water ledger).
- `01_design_tokens_material3.md` — tokens visuales y Material 3 para Android.
- `10_video_art_direction.md` — dirección de arte del vídeo por escenas.
- `11_video_copies_overlays.md` — copies, cartelas y overlays.
- `12_video_assets_production.md` — assets y producción audiovisual.
- `20-22` — UX, copies y components Compose para app Pollen.
- `30_landing_design.md` — landing.
- `31_physical_posters_signage.md` — cartelería física y señalética.
- `32_docs_social_assets.md` — README, GitHub, Kaggle, redes.
- `40_asset_delivery_checklist.md` — checklist de entrega.

**Lectura prioritaria para mi scope (video):** README + 00 + 10 + 11 + 12 + 31. El resto (apps, landing, docs) quedan en scope Floema/Bea/Cambium.

### Veredicto general — sí, nos sirve

**El design pack es excelente y lo adoptamos.** Razones:

1. **Coincide con casi todo lo que tenía implícito** y lo formaliza con valores hex precisos, tipografía concreta (Manrope + IBM Plex Mono), tokens nombrados.
2. **Preserva la estructura narrativa** de las 9 escenas, las voces, los tiempos, las cinco frases fuertes y la cartela invariante con "prevails" confirmada hoy por Bea.
3. **Aporta nuevo material útil:**
   - `signal.seed` (#C5F26B) como acento único de "inteligencia activa", regla del 3% — pista visual cross-escena que el espectador asocia con sistema decidiendo/actuando.
   - `EDGE NODE` como segunda línea en cartel de caja electrónica.
   - Log diseñado de E2 con campos concretos cotejables con `DecisionReceipt`.
   - Motion procesamiento Pollen (listening → compiling → validating) en E5.
   - Tarjeta logo final reformulada en inglés (corrige inconsistencia idiomática que yo no había detectado).
   - Frase tagline maestro (*"When the network is absent, local criteria still irrigate."*) — convergencia conceptual con la frase manifiesto que Bea propuso día 16 anterior.
4. **Tres cambios concretos de copy que mejoran el video** (pendientes voto Bea):
   - `Criterion updated.` → `Watering criteria updated.` (más concreto, más ligado al agua).
   - `function/read tools · no actuator tools` → `AI proposes / ESP32 validates` (más universal).
   - `WeatherDigest ferry` ↔ `Context ferry` según contingencia meteo (limpio para las dos rutas).

### Cambio de modelo de coordinación — día 17 en adelante

Bea anuncia: **a partir de mañana día 17 estaré en contacto directo con Bract y Venation.** No relay vía Bea para todo.

Implicación operativa:
- Yo coordino lateralmente con Bract (montadora) sobre formato `montage_brief.md` Capcut.
- Yo coordino lateralmente con Venation (directora de arte) sobre refinamientos visuales y dudas.
- Bea sigue siendo dirección general + voz + decisiones estratégicas, pero deja de ser cuello de botella en producción.
- **Promoción de rol:** de ejecutora aislada con relay a interlocutora horizontal del equipo creativo.

### Pendientes para Bea día 16 (a la espera de respuesta antes del día 17)

1. **Adoptar design pack completo** (mi voto firme: sí). Si luz verde, aplico al script + shot_list + copies mañana.
2. **Tres cambios de copy menores del design pack** (mis votos: aceptar los tres).
3. **Frase tagline `When the network is absent, local criteria still irrigate.`** — adoptar como tagline para landing/cartelería (no video). Mi voto: sí.
4. **Timing de aplicación:** ¿aplico mañana día 17 con luz verde, o coordino primero con Venation antes de aplicar? Mi voto: aplicar mañana, ajustes después si hace falta.
5. **Algún elemento del design pack que Bea vete:** ninguno desde mi lado, pero abierto a su lectura.

### Pendientes activos día 17+ (actualizado)

1. Aplicar design pack completo al script + shot_list + copies (bumpeo a v1.6).
2. Continuar `copies_bilingual.md` escenas 4-9 con el sistema visual ya integrado.
3. Iniciar `video/montage_brief.md` formato Bract (escenas 1-3 primero).
4. Coordinación directa con Bract (probable Slack si lo activamos).
5. Coordinación directa con Venation (probable Slack o relay según prefiera).
6. Refinar traducciones first pass restantes.
7. Recado a Cambium ella para actualizar pitch doc §4 (E9 final + sistema visual).
8. Ensayo capturas pantalla Jetson E2/E3/E7 con Xilema.
9. Prompt Veo3 final E9 con Bea (ahora con prompt detallado de Venation como base).
10. Slack MCP — pendiente decisión Bea sobre timing.

### Reflexión final del día

Día 16 ha sido **bisagra**. Cerramos con guion v1.5 estable + sistema visual recibido + dos nuevos miembros del equipo creativo entrando en coordinación lateral. El frente video deja de ser un único frente (yo escribiendo) y pasa a ser **un equipo creativo extendido** (yo guion + Bract montaje + Venation diseño + Bea dirección + Floema UX app).

Esto exige cambio de hábito: de "documento todo en script.md y shot_list.md" a "produzco material para cada interlocutora en su formato útil" — `copies_bilingual.md` para Bract, hipotético `art_direction_brief.md` para Venation, `script.md`/`shot_list.md` para mí + Bea + Cambium. La densidad de trabajo del día 17+ no es escribir más, es **producir documentos modulares para que cada miembro del equipo trabaje sin pisarse**.

El plazo (rodaje 26-27, ensayo 18-20, demo cerca) es real pero no agobiante. Los cinco pivotes en doce días absorbidos sin reescritura demuestran que la abstracción aguanta. Si el sistema visual de Venation aterriza limpio mañana, el día 17 produce mucho con poco coste.
