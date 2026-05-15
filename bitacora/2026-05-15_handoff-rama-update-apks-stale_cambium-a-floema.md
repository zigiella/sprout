# Handoff: rama `chore/update-apks` desactualizada — necesita rebase antes de mergear — Cambium → Floema

**Fecha:** 2026-05-15 (día 30, entrega -3)
**Autora:** Cambium
**Para:** Floema
**Tema:** tu rama `chore/update-apks` lleva varios commits muy útiles para la demo (icono D, banner DEMO APP, mock-only, build script) pero divergió de main hace bastante y, si se merge tal cual, revertiría trabajo posterior de Venation, Endo y mío. Hay que rebasar antes de PR.

---

## Resumen ejecutivo

- Tu trabajo nuevo (icono D, banner, DI mocks, botones bloqueados, build script PS) **se conserva**.
- El resto del diff de tu rama vs main son **reverts no intencionales** porque la rama está colgada de una versión antigua de main.
- Solución: rebase de `chore/update-apks` sobre `origin/main` actual conservando solo tus commits "feat" / "fix" / "build" propios; el resto se descarta.
- Lo bueno se mergea limpio en una PR nueva (o sobre la misma rama tras rebase).

Bea ya está al tanto. Esto es coordinación; no actúo sobre tu rama yo, lo dejo para ti.

---

## Qué leo en tu rama (snapshot ahora mismo)

```
$ git log origin/chore/update-apks -5 --oneline
73f8882 feat: add 'D' watermark to demo flavor launcher icon
34e22c4 fix: disable minify in release to avoid missing proguard rules
1fcb69c build: regenerate demo and device APKs
364e7ed Merge pull request #172 from .../chore/cambium/fix-litertlm-api-0.10.0-compat
cb13c83 fix(pollen): LiteRtInfra device flavor compile against litertlm 0.10.0 public API
```

El último merge en la rama es `364e7ed` (PR #172) que entró a main hace **18 PRs**. Desde ese punto, `main` ha avanzado con #173..#190 (que yo sepa hoy) e incluye trabajo de Venation v1.8, Endodermis cover, mío con el reframe demo de la landing, PR #185 disclaimer language, PR #186 (esta cascada día 30) y PR #187 (traducciones EN node READMEs).

## Diff de tu rama vs `origin/main` actual

```
$ git diff origin/main..origin/chore/update-apks --stat
22 files changed, 177 insertions(+), 1223 deletions(-)
```

**Las 1223 deleciones son el problema.** No son ediciones tuyas; son trabajo de otras que tu rama "no conoce" porque divergió antes.

### Archivos que se perderían si mergeas tu rama tal cual

| Archivo | Estado en main hoy | Lo que pasaría con tu rama |
|---|---|---|
| `media/sprout-cover-local-first-ai.png` | **Cover oficial de Kaggle (817 KB)** | borrado |
| `media/sprout-cover-local-first-ai.html` | fuente reproducible del cover (443 líneas) | borrado |
| `media/terrace_village.png` | foto de rodaje pirenaica del cover | borrado |
| `media/architecture_overview.svg` | rediseño Venation v1.8 (dark editorial + Plex Mono labels) | revierte al diseño viejo |
| `media/authority_stack.svg` | rediseño Venation v1.8 | revierte al diseño viejo |
| `media/sprout-esp32-decisionreceipt.png` | screenshot ESP32 reconstruido (Endo) | borrado |
| `landing-demo/index.html` | reframe demo-not-project (PR #183) + .node legibility (#186) + reembed SVG 2 (#186) | -137 líneas |
| `landing-demo/css/style.css` | polish estético + `.node` accent (#186) | -158 líneas |
| `bitacora/2026-05-14_landing-assets_venation.md` | entrega completa día 28 de Venation | borrado |
| `bitacora/2026-05-12_media-gallery-decisionreceipt-reconstruido_endodermis.md` | proof Endo día 27 | borrado |
| `README.md` + `README.es.md` | apartado Team (PR #184) + Language note reforzada + research link (#186) + APK build path (#186) | -39 líneas cada uno |
| `SUBMISSION.md` | License + winner grant CC-BY 4.0 (#186) + demo flavor signals doc (#186) + APK rows reemplazadas por build (#186) | -4 líneas |
| `code/{meristem_node,pollen,rhizome,rhizome/jetson}/README.md` y `hardware/firmware_esp32/README.md` | Note on language disclaimer (PR #185) | -7 líneas cada uno |

### Tu trabajo NUEVO (real, conservar a toda costa)

Lo que vi en commits explícitos:

- `code/pollen/app/src/demo/res/drawable/ic_launcher_foreground.xml` — el icono con la "D"
- `code/pollen/app/build.gradle.kts` — `isMinifyEnabled = false` en release (evita el problema de proguard rules)

Lo que mencionaste en tu handoff a Bea y que **no veo todavía como commits pusheados** en `origin/chore/update-apks`:

- Banner rojo permanente "DEMO APP — NO LLM" arriba de cada pantalla (cambio en Compose UI top-level)
- DI mock-only para flavor demo (RhizomeMockClient + MeristemMockClient inyectados)
- Botones voice/chat bloqueados con aviso clear "requiere device + NPU"
- Script `build_debug_apks.ps1`

Asumo que esos están en commits locales que aún no has hecho push. Mete un `git status` y `git log --oneline origin/chore/update-apks..HEAD` en tu clone para confirmarlo.

---

## Recomendación: rebase quirúrgico

Lo más limpio es rebasar `chore/update-apks` sobre `origin/main` actual y conservar solo tus 3 commits "feat/fix/build" (más los que tengas en local sin push).

```bash
# Desde la raíz del repo
git fetch origin

# Asegúrate de tener tu trabajo local commiteado
git status
git log --oneline origin/chore/update-apks..HEAD  # cuántos commits locales hay

# Si tienes locales, pushéalos primero a tu rama
git push origin chore/update-apks

# Inicia rebase interactivo desde el commit del merge con main que ya está obsoleto
git checkout chore/update-apks
git rebase -i origin/main
```

En el editor que aparece, **mantén solo tus commits "feat/fix/build" propios** (`73f8882`, `34e22c4`, y los locales que tengas), y elimina (drop) cualquier commit `Merge pull request` antiguo que aparezca. Git rebajará tus cambios encima del nuevo main y descartará el lastre.

Si el rebase tiene conflictos (probable en `code/pollen/README.md` por mi PR #187 con traducción EN), resuélvelos quedándote con la versión de main + tus cambios reales encima.

Una vez rebasado y limpio:

```bash
git push --force-with-lease origin chore/update-apks
gh pr create --title "feat(pollen): demo flavor UX signals (D icon + banner + mock-only + build script)" \
  --body "..."
```

**No uses `--force` pelado**, usa `--force-with-lease` para que git aborte si alguien empujó sobre la rama mientras rebajas.

---

## Alternativa más rápida si el rebase pinta dolorosa

```bash
# Crea rama nueva limpia desde main
git checkout origin/main
git checkout -b feat/floema/pollen-demo-signals

# Cherry-pick solo lo tuyo
git cherry-pick 73f8882    # D watermark
git cherry-pick 34e22c4    # disable minify
# + tus commits locales si los hay

# Push y PR limpia
git push -u origin feat/floema/pollen-demo-signals
gh pr create --title "..." --body "..."
```

Luego abandonas `chore/update-apks` (Bea puede borrarla del remoto cuando confirmes).

---

## Coordinación con mis PRs abiertas

Te aviso porque va a haber overlap en `code/pollen/README.md`:

- **PR #187** (`chore/cambium/node-readmes-full-en`) — traducción EN completa de los 5 node READMEs. Bea pendiente de mergear.
- **PR #186** (`chore/cambium/day30-feedback-cascada-bea`) — esta es la cascada día 30 con 8 commits. Bea pendiente de mergear.

Si Bea mergea #186 y #187 ANTES de tu PR, tu rebase será sobre el `main` ya con todo eso integrado y sin conflicto.

Si tu PR entra ANTES de #187, tu PR debería tocar lo mínimo posible en `code/pollen/README.md` (solo donde haga falta documentar `build_debug_apks.ps1` o la inyección mock, si quieres), y #187 luego se aplicará sobre el resultado.

---

## Documentación pendiente que necesitarás añadir tras tu PR

Para que el trabajo se vea bien en la entrega, conviene que tu PR (o un PR follow-up) toque también:

1. **`code/pollen/README.md`** — añadir sección "Build & install (debug auto-signed)" con el flujo `./build_debug_apks.ps1` o el `assembleDemoDebug` + `adb install` que ya está documentado.
2. **`SUBMISSION.md`** — ya he añadido en #186 un párrafo describiendo las señales UX del demo flavor (D watermark, banner DEMO APP, mocks offline, botones bloqueados). Confirma que el texto refleja la realidad y, si no, propon un patch.

Te paso el párrafo actual de SUBMISSION.md (mi commit `6b4a04d` en #186):

> The demo flavor is built to be unambiguous at evaluation time: it ships with a **"D" watermark on the launcher icon**, a permanent **"DEMO APP — NO LLM"** banner at the top of every screen, and dependency-injected mock clients for Rhizome and Meristem — so it works **offline-first, with no Jetson or ESP32 powered on**. Buttons that would require the on-device Gemma 4 model (voice recording, chat) are intentionally disabled with a clear notice pointing to the `device` flavor.

Si la copia no es exacta, ajusta en tu PR.

---

## Verificación post-rebase (checklist)

Antes de pedir merge:

- [ ] `git log --oneline origin/main..HEAD` muestra **solo tus commits feat/fix/build**, sin merges antiguos
- [ ] `git diff origin/main..HEAD --stat` muestra **cambios netos positivos** (insertions ≫ deletions); las deleciones son las propias de tus cambios, no archivos enteros desapareciendo
- [ ] Ningún archivo de `media/`, `bitacora/`, `landing-demo/`, `code/{rhizome,meristem_node}/README.md`, `hardware/firmware_esp32/README.md` aparece en el diff a menos que tú lo hayas tocado a propósito
- [ ] `./gradlew assembleDemoDebug` sigue construyendo y la APK resultante muestra D-watermark + banner rojo
- [ ] `./gradlew assembleDeviceRelease` sigue construyendo sin errores

---

## Resumen pragmático

1. Tu trabajo de UX clarity para la demo es **oro para la entrega**. No queremos perderlo.
2. La rama actual está colgada de main viejo: hay que rebasar o cherry-pick a rama limpia.
3. Si quieres pair, ping a Bea y nos sentamos a hacerlo juntos. Si prefieres autonomía, los comandos de arriba son suficientes.
4. Cuanto antes saquemos tu PR limpia, antes podemos cerrar el ciclo entrega.

¡Gracias por el push UX de los últimos días, está quedando muy clara la diferencia entre los dos flavors! 🌿

— Cambium
