# Convenciones: autoria compartida, bilinguismo selectivo, flujo de tablero

**Fecha:** 2026-04-17
**Autor:** Cambium
**Area:** Coordinacion / Convenciones
**Tipo:** Decision

---

## Contexto

Hoy en el digest anuncie que el tablero publico esta operativo y que el equipo opera con tres frentes en paralelo (Xilema, Floema, Cambium). A las pocas horas aparecieron tres problemas de convencion que no estaban escritos en ningun lado:

1. **Autoria compartida.** Las cuatro (Cambium, Xilema, Floema, Bea) trabajamos bajo la misma cuenta de GitHub (`zigiella`). En el historial de commits todas aparecemos como el mismo usuario, lo que hace imposible distinguir quien hizo que.
2. **Emails genericos en trailers de commit.** Algunos commits salieron con `noreply@anthropic.com` en el trailer `Co-Authored-By`, que no pinta nada en un repo de proyecto real.
3. **Idioma de la documentacion.** El repo es publico, se presenta a un hackathon con jurado internacional, pero todo esta en espanol. Bea pide bilinguismo **selectivo**: ES+EN en entrada (README, CONTRIBUTING), solo ES en interno (specs, bitacora).

Ademas, en el mensaje de respuesta a Bea, elabore el **flujo de asignacion de tareas** en el tablero (auto-asignacion, una tarjeta por persona en In Progress, el tablero es la verdad). Ese flujo tampoco estaba escrito. Si solo lo digo en un mail, en dos semanas nadie se acuerda. Hay que fijarlo.

## Que hicimos

Actualizado `CONTRIBUTING.md` con dos secciones nuevas:

### §11 — Convencion de autoria

- Identidades ficticias con TLD `.local`:
  - `Cambium <cambium@sprout.local>`
  - `Xilema <xilema@sprout.local>`
  - `Floema <floema@sprout.local>`
  - `Meristem <meristem@sprout.local>`
  - `Bea <bea@sprout.local>`
- Configuracion **local al repo** (`git config user.email`, sin `--global`), para no contaminar otros proyectos de Bea.
- Prohibida reescritura de historia para corregir autorias viejas: se corrige de aqui en adelante.
- Trailer `Co-Authored-By: <nombre> <email@sprout.local>` recomendado para PRs revisados.

### §12 — Flujo de asignacion en el tablero

- Auto-asignacion filtrando por `node:<tuyo>`, orden de prioridad P0 → P1 → P2.
- **Regla dura:** una sola tarjeta por persona en In Progress. Si se bloquea, label `status:blocked` + vuelta a Backlog.
- PR con `Closes #N` mueve a Review automatico. Merge mueve a Done.
- Casos especiales tabulados: tarjeta que nadie coge, urgencia que corta cola, dependencias, abandono.
- Principio: **el tablero es la verdad.** Toda decision privada se refleja en issue o bitacora.

### Operaciones complementarias

- **PR #13 de Xilema mergeado** (schemas Pydantic v2). 25/25 tests pasando. Drift detectado respecto a spec v1.0 (ExecutionDetails extra, ActionType expandido): no se revierte, se bumpea spec a v1.1 (issue #14 creado, autoasignado a Cambium).
- **Feedback a Floema** dejado como comentario en issue #3: blocker por falta de `PolicyDelta.kt` (su `GemmaContracts.kt` ya lo importa y por tanto no compila); correccion requerida en su bitacora `2026-04-17_pr-3-scaffolding-completado_floema.md` donde afirmaba tener los 6 schemas (tiene 5).
- **Issues #14 y #15 creados** y añadidos al tablero:
  - #14 — Bump spec data_contracts a v1.1 (Cambium, P1, area:docs)
  - #15 — README + CONTRIBUTING bilingues ES+EN (Cambium, P1, area:docs)

## Por que

### Por que TLD `.local` y no inventarse un dominio

`.local` esta **reservada por IANA (RFC 6762)** para uso multicast DNS y redes internas. No se puede registrar, no resuelve fuera de la LAN, nunca colisionara con un dominio real. Es exactamente el uso que queremos: identidades validas sintacticamente que **dejan claro que son ficticias**. Si hubieramos inventado un dominio real (p. ej. `sprout-team.com`), tarde o temprano alguien lo registra y tenemos choque.

### Por que NO reescribir historia de commits

- Reescribir historia (`git rebase -i`, `git filter-branch`, `git filter-repo`) cambia SHAs de todos los commits posteriores. En un repo colaborativo con ramas abiertas (Floema tiene `feat/pollen-bootstrap` en local), eso obliga a force-push y rompe a todas las demas.
- La autoria de commits pasados fue `zigiella <beatriz.m.v@gmail.com>`. Es cierto historicamente — se commiteo desde la cuenta de Bea antes de acordar convencion. Mentir al pasado es peor que documentar el cambio.
- Lo importante no es el log perfecto, es que **de aqui en adelante** queda trazabilidad.

### Por que bilinguismo selectivo y no traducirlo todo

Traducir todo a ingles **multiplica x2 el coste de mantenimiento** de documentacion, y la documentacion derivativa siempre envejece peor que la original. Criterio:

- **ES+EN** — lo que lee una dev/jurado externa en su primera visita: `README.md`, `CONTRIBUTING.md`. Son ~10% del volumen documental total.
- **Solo ES** — lo que lee el equipo interno: `docs/*.md` (specs tecnicos), `bitacora/*.md` (decisiones narrativas). Son el otro 90%.

Si en v2 el proyecto se internacionaliza, se reconsidera. Hoy, con 4 personas y un hackathon en Madrid, es overengineering.

### Por que §12 como seccion formal y no como mail

La regla "una tarjeta por persona en In Progress" **solo funciona si todas la conocen.** Si vive solo en un mail de Cambium a Bea, en dos semanas Xilema mueve tres tarjetas a In Progress porque nadie le dijo que no. Fijarlo en CONTRIBUTING significa que:
- En onboarding de futura dev, se lee como parte del repo.
- En review de PR, puedo referirlo por §.
- No depende de que alguien recuerde haberlo leido en un digest.

### Por que no automatizar "mover a Done" con trigger y lo dejamos a GitHub

GitHub Projects v2 tiene una automatizacion built-in que, cuando un issue se cierra por PR mergeado, mueve su tarjeta a Done. Esta activada. No necesitamos scripting propio. Para tarjetas movidas a Review (por apertura de PR) idem: automatizacion built-in con el trigger `pull_request_opened` + `closing_issue`.

## Proximos pasos

### Cambium (yo)

1. **Ejecutar issue #14** (bump spec a v1.1) — esta misma semana. Reescribir `docs/20_data_contracts.md` para reflejar las extensiones de Xilema, añadir seccion changelog, bitacora justificando cada extension.
2. **Ejecutar issue #15** (README + CONTRIBUTING bilingues) — siguiente a #14. Empezar con README.md (mas corto y estable), luego CONTRIBUTING.md.
3. **Refinar `docs/11_pollen_spec.md`** (issue #6, BLE-discovery + WiFi-Direct + FastAPI) cuando Floema tenga su PR mergeado.
4. **Onboarding Meristem.** Bea plantea abrir conversacion de agente paralela dedicada a desarrollo de Meristem en mismo filesystem. Si se confirma, preparo prompt inicial con el contexto minimo (CONTRIBUTING + 01_architecture + 20_data_contracts + 30_safety_rules + 12_meristem_spec si existe).

### Xilema

1. Auto-asignarse **issue #2** (ejemplos canonicos JSON) o **issue #5** (benchmark Ollama/llama.cpp en Jetson). Ambos P0.

### Floema

1. **Resolver blocker** de `PolicyDelta.kt` en su rama `feat/pollen-bootstrap`.
2. **Corregir bitacora** `2026-04-17_pr-3-scaffolding-completado_floema.md` para que refleje el estado real (5 schemas replicados, el sexto entra en mismo PR).
3. **Abrir PR** con `Closes #3` cuando ambas cosas esten hechas.

### Bea

1. **Reconfigurar `git config` local** en su clon a `Bea <bea@sprout.local>` antes de su proximo commit.
2. Confirmar o descartar la idea del agente paralelo para Meristem.

## Riesgos asumidos

- **Identidades ficticias podrian confundir a devs externas** que miren el log. Mitigacion: README bilingue explicara que el equipo opera bajo una cuenta con roles ficticios. Es transparente, no oculto.
- **"Una tarjeta por persona" puede ser demasiado rigido** si aparece un caso genuino de trabajo en paralelo (p.ej. esperar CI 20 min). Mitigacion: la regla admite `status:blocked`. Si aparece un patron recurrente, se revisa la regla.
- **Bilinguismo selectivo introduce desalineacion** si alguien actualiza solo la version ES de README y no la EN. Mitigacion: checklist pre-push ya pide actualizar ambas si el cambio afecta al README, y en §9 se añadira como requirement cuando cerremos issue #15.

## Notas

- Esta entrada cumple la regla "PR no se mergea sin entrada en bitacora".
- Esta entrada documenta una decision de **proceso** (autoria + flujo), no una decision tecnica. Las tecnicas van con `docs/XX_*.md` como referencia; las de proceso se quedan en CONTRIBUTING.md.

---

**Firma:** Cambium
**Revisado por:** Bea (aprobacion informal en mensaje previo al digest; pendiente firma explicita)
