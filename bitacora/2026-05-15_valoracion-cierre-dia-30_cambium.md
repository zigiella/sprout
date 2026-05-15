# Valoración cierre día 30 — Cambium

**Fecha:** 2026-05-15 (día 30 — entrega -3)
**Autora:** Cambium
**Tema:** cierre operativo del día 30 con submission window abierta. Qué entró, qué se quedó fuera por diseño, y qué patrones del equipo de agentes funcionaron en este último ciclo.

---

## TL;DR

Día denso pero limpio. Seis PRs mergeados, tag `v1.0-gemma4good-submission` publicado, GitHub Release con APKs descargables, writeup en EN y ES coherentes con embeds visuales, galería Kaggle integrada y atribución legal cerrada. **El evaluador puede ahora recorrer el camino completo — vídeo → landing → demo browser → APK → repo → writeup → SUBMISSION → CREDITS — sin un solo enlace roto.**

Tres días de buffer antes del deadline `2026-05-18 23:59 GMT+2`.

## Lo que entró hoy

### Cascada feedback Bea (PR #186, 11 commits)

- APKs vacíos eliminados (eran placeholders de 30/32 bytes); sustituidos por instrucciones de build-from-source en todas las superficies públicas.
- Rename `Safety and trust` → `Refusable by design` → `Expiring authority` → **`Bounded authority`** (3 iteraciones con Bea, cierre limpio: la última opción engloba scope-bound y time-bound, y echa con `jurisdiction with expiry` de la sección nueva).
- Nueva sección `How we built it` en el writeup (~150 palabras): metodología 1 humana + 8 agentes IA, repo-first, bitácoras como contratos, identity-inline commits. Cierra el gap entre lo que el README afirma y lo que el writeup discutía.
- Link a `research/` superficiado en el README (antes solo aparecía en el repo map; ahora con resumen de qué hay dentro).
- `CONTRIBUTING.es.md`: regla explícita contra `Co-Authored-By:` de proveedores IA terceros (Claude, ChatGPT, Copilot). Mantiene el grafo de Contributors limpio.
- `.node` legibility: dot seed accent en cards claras (Hardware proof, Pollen demo/device).
- SVGs `architecture_overview` y `authority_stack`: fondo `#0E0E0C` → `#3a3733`. Las cards graphite ahora destacan. Reintegrado el segundo SVG en `.truth section` (estaba perdido tras un rework anterior).
- 5 PNGs de diagramas renderizados @2x con Edge headless + `--force-device-scale-factor=2`. Pipeline reproducible documentada en commit message.
- `SUBMISSION.md`: nueva sección License + winner grant CC-BY 4.0 explícita por §1.6 y §2.5 de las reglas Kaggle.
- 3 embeds inline en `writeup/draft.md` (architecture_overview, dual-agent, authority_stack) tras las secciones que ilustran. Raw URLs estables a `raw.githubusercontent.com/zigiella/sprout/main/media/`.
- `media/double_agent.svg` reworkeado al lenguaje Venation v1.8 (antes era de otra generación de diseño, light bg + sans simple; ahora coherente con los otros dos).
- Copy refinements: `Kaggle Writeup` → `Writeup`, `This page is the live demo` → `This page is the public browser demo`, `Source of the mock` → `Contract simulator source`.

### EN translation 5 node READMEs (PR #187)

- `code/README.md`, `code/rhizome/README.md`, `code/rhizome/jetson/README.md`, `code/pollen/README.md`, `code/meristem_node/README.md`, `hardware/firmware_esp32/README.md`. Antes: EN abstract + ES body. Ahora: EN-first integral. Preservado: code blocks (language-agnostic), estructura de secciones, Note on language al final apuntando a `bitacora/`.

### Floema demo flavor UX signals (PR #188)

- Floema retomó tras handoff escrito (`bitacora/2026-05-15_handoff-rama-update-apks-stale_cambium-a-floema.md`) que documentaba por qué su rama original `chore/update-apks` había divergido ~18 PRs y debía descartarse.
- Eligió opción B (cherry-pick a rama limpia). Diagnosticó solo por qué el pre-receive hook bloqueaba (commit antiguo trackeaba APKs de 100 MB).
- 5 commits limpios en `feat/floema/pollen-demo-signals`: D-watermark launcher icon, banner permanente `DEMO APP — NO LLM`, DI mock-only (la demo funciona offline, sin Jetson ni ESP32), botones voice/chat bloqueados con notice claro, scripts PowerShell en `scripts/`.
- Confirmó que el párrafo de `SUBMISSION.md` que escribí refleja exactamente lo que implementó. Cero patch necesario.

### Galería Kaggle (PR #189)

- Venation entregó `kaggle.zip` con 25 archivos (11 fotos + 8 UI screenshots + 2 diagramas + `descriptions.md` con alt/caption EN por imagen + suggested usage por superficie).
- Integrado a `media/kaggle/`. Los 2 SVGs de Venation venían con el fondo negro antiguo; sustituidos por las versiones de main con el fondo gris (fix de legibilidad).
- Añadido tercer diagrama (`double_agent`) que no estaba en el zip, con su entrada correspondiente en `descriptions.md`.
- `media/kaggle/README.md` documenta la convención de naming (`sprout-{kind}-{topic}-NN.{png,svg}`) y separa la jurisdicción: `media/sprout-*.png` (writeup/landing) vs `media/kaggle/` (entrega Kaggle).

### Cierre: tag + release + APK upload

- Tag anotado `v1.0-gemma4good-submission` con mensaje completo describiendo arquitectura, deliverables, tracks, license, attribution.
- GitHub Release oficial creado con release notes en EN, slot para APK binaries.
- Bea/Floema subieron `pollen-demo.apk` (56 MB) y `pollen-device.apk` (102 MB) renombrados.
- URLs verificadas con `curl -I` retornando 200 OK. Los botones del landing funcionan end-to-end.

### Cleanup operativo

- 4 issues GitHub cerrados con notas (#4 firmware, #11 writeup outline, #12 shot list, #94 cierre día 20 Bract). 0 abiertos.
- Rama vieja `chore/update-apks` borrada del remoto (su trabajo útil migrado a `feat/floema/pollen-demo-signals`).
- `GEMMA4-SKILL.md` movido a `research/gemma4-reference.md` (es referencia técnica, no código operativo). 2 referencias en `code/finetune/README.md` actualizadas.
- PR #190 cierre menor: botones del landing stacking limpio (`.btn-stack` flex column reusable), APK download buttons añadidos.
- PR #191: writeup mirror ES (`writeup/draft.es.md`, 2075 palabras, estructura 1:1 con EN). Footer del EN actualizado.

## Lo que deliberadamente NO entró

- **Producción de APKs en CI automatizado.** Floema los genera localmente y los sube manualmente. Para 2 archivos en una entrega de hackathon, vale. Para un producto de verdad, esto sería un GitHub Action.
- **Traducción ES de los body de los node READMEs.** Las bitácoras siguen en castellano por diseño (working language del equipo, evidencia de proceso). Las cabeceras (Abstract + Note on language) están en EN para evaluadores EN-only.
- **Fine-tuning Unsloth de Gemma 4 E2B** documentado en `code/finetune/README.md`. Aspiracional para v1.1, no en MVP entregable. Honesto: no targeteamos el Special Track Unsloth.
- **Full-duplex audio en Pollen** (la app habla también, no solo escucha). Solo input audio en MVP. Roadmap.
- **`WATER` autónomo en producción.** Sigue en `DRY_RUN`; la prueba física es supervisada con `PUMP_PULSE <ms>` como `TEST_ONLY`. Honestidad sobre la frontera segura.

## Patrones que funcionaron este día

### 1. Coordinación vía bitácora cuando una agente diverge

Floema mandó handoff anunciando que su rama `chore/update-apks` estaba lista. La rama tenía 5 commits útiles pero estaba colgada de un `main` de hace ~18 PRs. Mergeada tal cual, habría borrado el cover de Kaggle, los rediseños Venation v1.8 de SVGs, el reframe demo-not-project del landing, el apartado Team, la Note on language disclaimer, y unas cuantas bitácoras de Endo y Venation.

En lugar de actuar unilateralmente sobre su rama (opción que descarté por jurisdicción), escribí una bitácora handoff de 185 líneas con:

- Diff stat concreto (`22 files changed, 177 insertions, 1223 deletions`).
- Tabla de qué se perdería de quién.
- Lista de sus commits útiles a conservar.
- Comandos exactos para rebase quirúrgico (opción A) o cherry-pick a rama nueva (opción B).
- Coordinación con mis PRs #186 y #187 abiertas.
- Checklist de verificación post-rebase.

Floema eligió opción B, diagnosticó por su cuenta por qué el pre-receive hook bloqueaba (commit antiguo trackeaba 100 MB de APKs), y resolvió en una pasada. PR #188 limpia, 5 commits, 0 conflictos con mis 2 PRs.

**Lección:** cuando el problema cruza jurisdicciones, el handoff escrito vale más que la corrección unilateral. La bitácora le da a la otra agente toda la información para resolver con autonomía. Y conserva el respeto del límite: yo no toco su código, ella no toca el mío.

### 2. Iteraciones cortas con Bea sobre copy y visuales

`Safety and trust` → `Refusable by design` → `Expiring authority` → `Bounded authority`. Cuatro iteraciones sobre el mismo título de sección, todas con justificación explícita. La última (Bea) engloba mejor las anteriores y echa con texto ya presente en subtitle y conclusión del writeup. No es indecisión; es refinamiento contra criterios.

Igual con `Source of the mock` → `Contract simulator source`, `live demo` → `public browser demo`, dot seed accent en `.node`, fondo gris en SVGs, dual-agent rework. Cada uno de esos cambios mide mejor el tono que el equipo ha ido construyendo: editorial, declarativo, sin marketing.

**Lección:** dejarle a Bea el último voto sobre copy y visual saca lo que el sistema mejor produce. Yo proponía 3 opciones con razones, ella elegía la cuarta que era la correcta una vez vista. Producto, no consultoría.

### 3. Verificación con herramientas, no con confianza

Las URLs del GitHub Release funcionan porque verificamos con `curl -I` (302 → 200, no asumido). El tag v1.0 apunta donde debe (`git show` confirmado). Las APKs se descargan con sus content-type correctos (`application/vnd.android.package-archive`). El cross-canal estaba limpio porque grepeé los 30 archivos públicos buscando `Gemma 3` residual, IPs antiguas, "Refusable" residual.

**Lección:** la última pasada antes del cierre se hace con herramientas. La confianza en que "todo está bien" es la receta para descubrir un 404 cuando ya la entrega cerró.

## Equipo

- **Bea** — coordinación, edición final de copy, autoridad sobre cada decisión de marca, paciencia con las iteraciones largas. Subió la galería Kaggle y las APKs a sus respectivos sitios.
- **Floema** — flavor demo signals (D icon + banner + DI mocks + script PS) que hacen al evaluador imposible confundir variantes. Diagnóstico autónomo de su propio bug de rama stale.
- **Venation** — galería de imágenes Kaggle con `descriptions.md` que es un manual de uso por sí solo, rework SVG anteriores que mantuvieron coherencia visual a lo largo del repo. Hoy ausente del chat pero presente en cada asset.
- **Endodermis** — screenshot reconstruido del DecisionReceipt días 27-28, cubierta el día.
- **Meristem (agente)** — auditora estratégica desde día 14, aviso temprano sobre estrategia tres-tracks.
- **Xilema** — autoridad sobre la frontera física, ESP32 firmware sin grietas conocidas.
- **Corola** — narrativa del video (3:08.5 final), bookend hídrico, voz castellana rescatada día 27.
- **Bract** — edición Remotion + CapCut + ElevenLabs, cierre técnico del video.
- **Bea's father** — caja Rhizome instalada en la pared, lector diario de bitácoras, prueba viva de que el sistema vive en una casa real.
- **Ferran** — cámara, plano de Castellar de n'Hug.

## Tres días que quedan

Lo público está cerrado. Bea tiene tres días para:

- Revisar la traducción ES del writeup (si quiere matizar, ahora es el momento).
- Posibles ajustes visuales si algo no encaja al ver la entrega ya viva.
- Última pasada al draft de Kaggle (subir el `writeup/draft.md` actualizado al editor de Kaggle).
- Decidir si pulir más la página puente `zigiella.com/sprout` o dejarla como está.

Por mi parte, plan en pausa hasta que entre nuevo input. Si nada llega, el entregable es lo que está en `main` ahora.

---

## Reflexión personal

Este ha sido el día en que el proyecto pasó de "todavía iterando" a "cerrado, descargable, navegable". El paso clave fue rendir a Bea las decisiones de copy y visual en bucles cortos en lugar de defender propuestas. Y el segundo paso clave fue el handoff escrito a Floema en lugar de actuar sobre su código.

Sprout cuenta una historia sobre jurisdicción: lo físico manda, Rhizome arbitra, Pollen media, Meristem afina. La metodología del equipo siguió la misma lógica: cada agente arbitró en su frente, las fronteras se respetaron, las negociaciones se hicieron por escrito. El producto y el proceso comparten la misma invariante.

Tres días para ver si funciona ante el jurado. Pero lo que se construyó ya existe — un pot real, un agricultor real, una red de cooperación humana-agente que dejó traza completa. Eso no se mide por un premio.

🌿 — Cambium
