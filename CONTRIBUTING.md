<!-- Bilingual document · Spanish first, English below · See §13 for language policy -->

🇪🇸 **[Español](#contributing-es)** · 🇬🇧 **[English](#contributing-en)**

---

<a id="contributing-es"></a>

# Como trabajamos en Sprout

Guia interna del **equipo zigiella** para trabajar en Sprout.

---

## 1. Filosofia de colaboracion

Sprout es un proyecto del equipo zigiella. Durante el sprint MVP somos cuatro personas. Cada una trabaja en su area pero todo converge en una entrega coherente: **un sistema funcional + video de demostracion + documento de presentacion + repo publico**.

Reglas blandas:
- Si no aporta a los puntos de "lo que debe demostrar el video", probablemente sobra
- Si no puedes explicar algo en una frase, probablemente esta mal formulado
- Si algo es ambiguo en docs/, abre una entrada en bitacora/ y pregunta

---

## 2. Roles y zonas del repo

| Rol | Zona principal | Zonas secundarias |
|-----|---------------|-------------------|
| Coordinacion y diseno | `docs/`, `bitacora/` | todas |
| Dev Rhizome (Jetson) | `code/rhizome/`, `hardware/` | `docs/10_rhizome_spec.md` |
| Dev Pollen (Android) | `code/pollen/` | `docs/11_pollen_spec.md` |
| Dev Meristem + Fine-tune | `code/meristem/`, `code/finetune/` | `docs/12_meristem_spec.md` |

Writeup, video, research y demo los cubre el core del equipo (coordinacion + project lead).

---

## 3. Flujo de trabajo

### 3.1 Antes de empezar algo nuevo
1. `git pull` en `main`
2. Elegir un issue del [backlog](https://github.com/zigiella/sprout/issues) (ver §10) y asignartelo
3. Leer la entrada mas reciente de `bitacora/`
4. Revisar el doc relevante en `docs/`
5. Crear rama `feat/<zona>-<tema>` o `fix/<zona>-<tema>` — **nunca** trabajar sobre `main`

### 3.2 Durante el trabajo
- Commits pequenos y frecuentes
- Mensaje de commit: `[zona] resumen corto` (ej: `[rhizome] humedad lectura via ADS1115`)
- En el commit que cierra el issue, incluir `Closes #N` en el cuerpo para enlace automatico

### 3.3 Al terminar una pieza
- Entrada en `bitacora/` con fecha, lo que se hizo, lo que queda, decisiones tomadas (**obligatorio antes de PR**)
- Si hay cambio de arquitectura, actualizar el doc correspondiente en `docs/`
- Abrir PR contra `main`. En la descripcion del PR: `Closes #N` + resumen + como probar
- Review por Cambium antes de merge. Sin review, no hay merge

---

## 4. Bitacora: como escribir una entrada

Cada entrada es un archivo en `bitacora/` con nombre:

```
YYYY-MM-DD_<tema-corto>_<autor>.md
```

Ejemplos:
- `2026-04-15_kickoff_cambium.md`
- `2026-04-18_jetson-primer-arranque_ana.md`
- `2026-04-22_pollen-sync-funcionando_maria.md`

Plantilla en [bitacora/README.md](bitacora/README.md).

---

## 5. Convenciones de codigo

### Python (Rhizome, Meristem, Simulator)
- Python 3.11+
- `ruff` para lint, `black` para formato
- Type hints obligatorios en funciones publicas
- Docstrings breves en espanol; comentarios en codigo en espanol
- Tests minimos en `tests/` de cada subproyecto

### Android (Pollen)
- Kotlin
- Jetpack Compose
- Gemma 4 via Google AI Edge / LiteRT (o llama.cpp como fallback)

### Schemas JSON
- Todos los schemas en `code/shared/schemas/`
- Validacion via `pydantic` en Python, via `kotlinx.serialization` en Android

---

## 6. Convenciones de naming

### Archivos de docs
- Numerados con prefijo de dos digitos (`00_`, `01_`, `10_`, etc.)
- Kebab-case para nombres compuestos
- Ejemplo: `docs/20_data_contracts.md`

### Modelos de Gemma 4
Seguir [guia oficial de naming de Google](https://ai.google/documents/32/External_Gemma_Model_Variant_Guidelines.pdf):
- Formato: `sprout/sprout-<componente>-<modelo_base>-v<N>`
- Ejemplo: `sprout/sprout-rhizome-e2b-v1`
- Nunca poner "Gemma" en el nombre del modelo derivado (lo exige la licencia)

### Branches de git
- `main` = produccion / ultima version estable
- `feat/<zona>-<descripcion>` = features en desarrollo
- `fix/<zona>-<descripcion>` = bugfixes
- Ejemplo: `feat/rhizome-audio-sensor`

### Ejemplos canonicos (fixtures JSON)

Viven en `code/shared/examples/`. Regla:

- `<schema>.json` = fixture canonico unico por schema. Es el ejemplo de referencia,
  el que se usa en tests y documentacion. Un solo archivo por schema.
  Ejemplos: `rhizome_snapshot.json`, `weather_packet.json`, `policy_packet.json`.
- `<schema>_<variante>.json` = variantes deliberadas que cubren un caso distinto
  al canonico (estado de bloqueo, contradiccion, modo conservador, etc.).
  Ejemplos: `decision_receipt_blocked.json`, `contradiction_alert_sensor_vs_vision.json`.

**Regla dura:** si anades una variante, debe quedar claro en el nombre que varianta
del canonico es. No metas campos nuevos al canonico solo para cubrir un caso;
crea una variante.

---

## 7. Secretos y credenciales

**Nunca** commitear:
- API keys (Google AI Studio, HuggingFace, etc.)
- Certificados o tokens
- Archivos `.env`

Usar siempre variables de entorno. Plantilla en `.env.example` si aplica.

Ya existe `.gitignore` con las entradas minimas. Si dudas, pregunta antes de hacer push.

---

## 8. Dudas

Abre una entrada en `bitacora/` con el tema `pregunta-<topic>` y etiqueta a Cambium. O en el canal que estemos usando el equipo.

---

## 9. Checklist antes de cada push

- [ ] El codigo corre sin errores
- [ ] No hay credenciales expuestas
- [ ] Si cambie un contrato de datos, actualice `code/shared/schemas/`
- [ ] Si cambie arquitectura, actualice `docs/`
- [ ] Hice entrada en `bitacora/` con fecha
- [ ] El PR referencia el issue con `Closes #N`
- [ ] Si toca una zona con CI (`code/pollen/**`, futuros Rhizome/Meristem), el CI esta **verde** antes de pedir review

### 9.1 Regla dura sobre CI

**Ningun PR se mergea con CI en rojo.** Sin excepciones. Si el CI falla:
1. Lee los logs del workflow en GitHub Actions (pestaña "Checks" del PR)
2. Reproduce localmente si tienes entorno, o itera con los logs si no
3. Corrige, commitea, push. El CI se re-ejecuta automaticamente
4. Solo cuando este verde, avisas para review

Si el fallo del CI es del propio workflow (no del codigo), se abre issue aparte para arreglar el workflow. El PR afectado queda en hold.

### 9.2 Operaciones git seguras en maquina compartida

**Contexto.** Varias miembras del equipo (Bea, Corola, Cambium) comparten maquina, carpeta de trabajo y cuenta de GitHub. Eso introduce riesgos especificos que NO existen cuando cada miembra tiene su propio clone aislado:

- Cuando una hace `git pull`, `git checkout` o `git stash` en la carpeta compartida, las otras se ven afectadas en su working tree.
- Es muy facil que un commit termine en la rama equivocada porque el `HEAD` cambio entre operaciones.
- Es muy facil que cambios reales se queden en un **stash silencioso** durante operaciones cross-rama y nunca lleguen al commit que crees haber hecho.

Esto se ha sufrido empiricamente: Cambium 4 veces (dia 13), Meristem 5 veces (dias 12-13), Corola 1 vez (dia 15). Patron sistemico, no error individual.

**Tres puntos de verificacion antes de cada commit.**

Sustituye al checklist tradicional `git status` solo. Verifica los **tres** siempre:

```bash
git status                  # 1. archivos modificados/staged
git branch --show-current   # 2. en que rama estoy realmente
git stash list              # 3. stashes pendientes (especialmente con tu prefijo)
```

Si los tres confirman lo que esperabas, commitea. Si alguno te sorprende, **para y resuelve antes de commitear**. Tres comandos, dos segundos cada uno.

**Stash con prefijo de autor obligatorio.**

Cuando uses `git stash push`, **siempre con mensaje y prefijo de autor**:

```bash
git stash push -m "[corola] WIP guion v1.4 escena 7"
git stash push -m "[cambium] WIP bitacora dia 16"
```

Eso permite identificar de un vistazo en `git stash list` que stash es de quien:

```
stash@{0}: On main: [corola] WIP guion v1.4 escena 7
stash@{1}: On main: [cambium] WIP bitacora dia 16
```

Si ves un stash sin prefijo, es porque alguien olvido la convencion. **No lo tocas hasta confirmar de quien es**.

**Una operacion atomica por sesion.**

Cuando arranques sesion de trabajo:
1. `git status` + `git branch --show-current` + `git stash list` (verificacion inicial)
2. Si hay stash ajeno o working tree sucio, **paras y avisas en chat comun antes de continuar**
3. Trabajo + commit + push
4. Antes de pasar el turno: `git checkout main` y working tree limpio

**No dejas working tree modificado para que la siguiente miembra arranque.** Si tu trabajo no esta listo para commit, lo dejas en stash con tu prefijo y la siguiente sabe que hay material tuyo pendiente.

**Antes de cualquier `git checkout`.**

Verifica `git stash list`. Si ves stash con prefijo ajeno, **no haces checkout que pueda alterar ese contexto sin avisar primero**. Si ves stash con tu prefijo de una sesion anterior, decide explicitamente: lo aplicas, lo descartas, o lo dejas y navegas con cuidado.

**Resolucion si el commit termino en rama equivocada.**

Procedimiento conocido por el equipo (lo hemos usado varias veces sin perdida de datos):

```bash
git reset --soft HEAD~1     # deshace commit, mantiene cambios en staging
git stash push -m "[nombre] commit a mover"
git checkout main           # o la rama correcta
git stash pop
git commit -m "..."         # commit en rama correcta
git push origin main
```

Si el commit ya esta pusheado a la rama equivocada, abrir issue y resolver con `git revert` (no force-push).

**Fuera de scope post-hackathon.**

A futuro, **`git worktree`** es la solucion tecnica correcta a esta friccion: un solo `.git/` central, varios working directories aislados, una miembra por carpeta. No lo implementamos durante el hackathon porque cambiar setup en mitad del proyecto introduce mas riesgo que el que mitiga. Apuntar para revision post-demo.

---

## 10. Backlog y tablero visual

El backlog vive en **GitHub Issues + Projects**.

### 10.1 Donde verlo
- **Lista de issues:** https://github.com/zigiella/sprout/issues
- **Tablero kanban "Sprout Backlog":** https://github.com/users/zigiella/projects/2 — cuatro columnas: **Backlog / In Progress / Review / Done**. Arrastrar tarjeta cambia estado.
- **Vista Table:** el mismo proyecto con vista de spreadsheet para priorizar en bloque.
- **GitHub Mobile** (iOS/Android): misma vista Board, desde el sofa.

### 10.2 Como usar el backlog

**Abrir un issue nuevo:**
- Titulo imperativo, corto, sin jerga interna. "Implementar schemas Pydantic" > "Schemas".
- **Zero referencias externas** al hackathon, jurado, premios, deadline. El repo es publico.
- Body con: contexto, criterios de aceptacion (checkboxes), dependencias, referencia a docs.
- Labels obligatorios: **uno de `node:*`** y **uno de `priority:*`**. Opcionales: `area:*`, `status:blocked`.

**Asignarse un issue:**
- Solo asignarse lo que vas a empezar esa misma sesion. Si dudas, dejalo sin asignar.
- Si lo abandonas, quitate de asignada y deja comentario con el por que.

**Cerrar un issue:**
- Solo se cierra por merge de PR que lo referencia con `Closes #N`.
- No cerrar "a mano" salvo duplicados o invalidos (con comentario explicativo).

### 10.3 Taxonomia de labels

**Nodo (uno obligatorio):**
- `node:rhizome` — Jetson, parcela
- `node:pollen` — Android, itinerante
- `node:meristem` — laptop, estrategico
- `node:cambium` — coordinacion, diseno, supervision

**Area (opcional, puede haber varias):**
- `area:docs` — documentacion de arquitectura
- `area:infra` — repo, CI, tooling
- `area:research` — benchmarks, evaluacion
- `area:firmware` — ESP32, capa fisica

**Prioridad (una obligatoria):**
- `priority:P0` — critico, bloquea a alguien
- `priority:P1` — importante, no bloqueante
- `priority:P2` — nice to have

**Estado (opcional):**
- `status:blocked` — esperando algo externo

### 10.4 Relacion PR ↔ issue

Cada PR deberia cerrar al menos un issue. En el cuerpo del PR:

```
Closes #12
Closes #15
```

Al mergear, GitHub mueve esos issues a **Done** automaticamente.

---

## 11. Convencion de autoria

Todas las personas del equipo zigiella trabajamos bajo la **misma cuenta de GitHub** (`zigiella`). Para que en el historial del repo se pueda distinguir quien hizo que, cada dev configura **identidad local al repo** (no global, para no afectar otros proyectos tuyos):

```bash
cd <ruta-al-repo-sprout>
git config user.name "<Nombre>"
git config user.email "<nombre>@sprout.local"
```

**Identidades vigentes:**

| Rol | `user.name` | `user.email` |
|-----|-------------|--------------|
| Coordinacion | `Cambium` | `cambium@sprout.local` |
| Dev Rhizome | `Xilema` | `xilema@sprout.local` |
| Dev Pollen | `Floema` | `floema@sprout.local` |
| Dev Meristem | `Meristem` | `meristem@sprout.local` |
| Project lead | `Bea` | `bea@sprout.local` |

**Sobre la TLD `.local`:** es una TLD reservada por IANA (RFC 6762) para uso multicast DNS y redes internas. **No colisiona con ninguna direccion real de internet** y deja claro que son identidades ficticias del equipo.

**Commits con coautoria (opcional pero recomendado para PR revisados):**

```
Co-Authored-By: Cambium <cambium@sprout.local>
```

**Reglas duras:**
- **Nunca** reescribir historia para cambiar autoria en commits viejos. Si se subio algo con identidad equivocada, se corrige de aqui en adelante; el historial se respeta.
- **Nunca** usar `--global` al configurar estas identidades. Son locales al repo.
- Al clonar el repo por primera vez, configurar identidad es **el primer paso**, antes del primer commit.

### 11.1 Multi-agente sobre el mismo clone

Si varias agentes (p.ej. Cambium y Meristem en conversaciones separadas) comparten el mismo clone del repo, **`git config user.email` persiste en `.git/config` y una agente puede pisar la identidad de otra.**

Solucion: **no persistir la identidad**, pasarla inline en cada commit con `-c`:

```bash
git -c user.name="Meristem" -c user.email="meristem@sprout.local" commit -m "..."
```

Esto solo aplica a ese comando, no toca `.git/config`. Es el modo obligatorio cuando hay mas de una agente trabajando en el mismo clone.

Si solo hay una persona/agente por clone (caso tipico de dev humana), el `git config` persistente esta bien.

---

## 12. Flujo de asignacion en el tablero

**Principio:** auto-asignacion con protocolo corto, sin asignador central.

### 12.1 Ciclo diario

1. **Filtrar por tu nodo.** En [el tablero](https://github.com/users/zigiella/projects/2) aplicar filtro por label `node:<tuyo>`.
2. **Elegir la de mayor prioridad** de la columna **Backlog**. Orden: `priority:P0` (rojas) → `priority:P1` (amarillas) → `priority:P2` (grises). Empate: menos dependencias abiertas.
3. **Auto-asignarse el issue** (boton "assign yourself" en el issue) **y arrastrar la tarjeta** de Backlog a **In Progress**. Ese doble movimiento es la señal publica de "estoy con esto ahora".
4. **Trabajar.** Commits pequenos y frecuentes, rama `feat/<zona>-<tema>` o `fix/<zona>-<tema>`.
5. **Abrir PR** con `Closes #N` en el cuerpo. GitHub mueve automaticamente la tarjeta a **Review**.
6. **Review por Cambium.** Si aprueba y mergea, la tarjeta va a **Done** automaticamente. Si pide cambios, la dev la arrastra de vuelta a **In Progress** y trabaja sobre los comentarios.

### 12.2 Regla dura: una tarjeta por persona en In Progress

**Solo una tarjeta** por persona puede estar en In Progress al mismo tiempo. Si necesitas bloquear algo para trabajar en otra cosa:
- Añades label `status:blocked` al issue
- Arrastras la tarjeta de vuelta a Backlog
- Comentas en el issue explicando que esperas

Evita que el tablero se llene de "en progreso" que nadie esta tocando.

### 12.3 Casos especiales

- **Tarjeta que nadie coge** (suele pasar con docs aburridos): Cambium prioriza en digest o la coge ella misma pasados 3 dias.
- **Tarjeta urgente que debe cortar la cola:** Bea o Cambium añaden/suben a `priority:P0` y comentan en el issue el por que. La dev con hueco la coge antes que su backlog normal.
- **Dependencias:** si #A bloquea #B, en #B se pone `Blocked by #A` en el cuerpo. Solo se puede auto-asignar #B cuando #A esta en Done.
- **Abandono de tarea:** quitarse de asignada, dejar comentario en el issue con el por que, arrastrar tarjeta de vuelta a Backlog.

### 12.4 El tablero es la verdad

Si una conversacion privada (canal, DM, mail) decide algo sobre una tarea, esa decision se refleja en el issue (como comentario) o en bitacora. **No hay "yo pense que tu estabas haciendo eso".** La tarjeta dice quien, la columna dice en que fase, el PR dice el que.

Si una tarjeta lleva >48h en In Progress sin commits ni comentarios, Cambium pregunta en el issue (pregunta publica, no DM).

---

## 13. Idiomas del repo

Para minimizar coste de mantenimiento sin cerrar la puerta a gente externa, tenemos dos capas de idiomas:

| Zona | Idioma | Por que |
|------|--------|---------|
| `README.md` | **Bilingue** ES + EN | Puerta de entrada publica. Una persona externa debe poder entender el proyecto en minutos. |
| `CONTRIBUTING.md` | **Bilingue** ES + EN | Una contribuidora externa debe poder abrir un PR sin hablar espanol. |
| `docs/` | **Solo ES** | Specs de producto internos. Evolucionan rapido; traducirlos se desincroniza. |
| `bitacora/` | **Solo ES** | Diario interno del equipo, en vivo. Mantener bilingue seria puro overhead. |
| Commits, issues, PRs | Libre (ES o EN) | Claridad > consistencia. Cada persona escribe en el idioma en que piense mejor ese dia. |
| Codigo (identifiers, comentarios) | Libre, pero consistente dentro de un modulo | Si un modulo empieza en ES, seguir en ES. No mezclar en el mismo archivo. |

**Regla operacional:** al tocar `README.md` o `CONTRIBUTING.md`, actualizar **ambas** secciones de idioma en el mismo PR. Si solo se actualiza una, se abre issue para sincronizar la otra y se marca `priority:P1`.

---
---

<a id="contributing-en"></a>

# How we work on Sprout

Internal guide of **equipo zigiella** for working on Sprout.

---

## 1. Collaboration philosophy

Sprout is a project by equipo zigiella. During the MVP sprint we are four people. Each owns an area but everything converges on a coherent delivery: **a working system + demo video + writeup + public repo**.

Soft rules:
- If it doesn't feed into "what the video must show," it probably doesn't belong
- If you can't explain something in one sentence, it's probably not well framed
- If something is ambiguous in `docs/`, open a `bitacora/` entry and ask

---

## 2. Roles and repo zones

| Role | Primary zone | Secondary |
|------|-------------|-----------|
| Coordination & design | `docs/`, `bitacora/` | any |
| Dev Rhizome (Jetson) | `code/rhizome/`, `hardware/` | `docs/10_rhizome_spec.md` |
| Dev Pollen (Android) | `code/pollen/` | `docs/11_pollen_spec.md` |
| Dev Meristem + Fine-tune | `code/meristem/`, `code/finetune/` | `docs/12_meristem_spec.md` |

Writeup, video, research, and demo are covered by the core team (coordination + project lead).

---

## 3. Workflow

### 3.1 Before starting something new
1. `git pull` on `main`
2. Pick an issue from the [backlog](https://github.com/zigiella/sprout/issues) (see §10) and assign it to yourself
3. Read the latest entry in `bitacora/`
4. Review the relevant doc in `docs/` (Spanish)
5. Create a branch `feat/<zone>-<topic>` or `fix/<zone>-<topic>` — **never** work directly on `main`

### 3.2 While working
- Small, frequent commits
- Commit message: `[zone] short summary` (e.g. `[rhizome] moisture reading via ADS1115`)
- On the commit that closes the issue, include `Closes #N` in the body for auto-link

### 3.3 When a piece is done
- Entry in `bitacora/` (in Spanish) with date, what was done, what's pending, decisions taken — **mandatory before PR**
- If architecture changed, update the matching doc in `docs/`
- Open a PR against `main`. PR body: `Closes #N` + summary + how to test
- Review by Cambium before merge. No review, no merge.

---

## 4. Bitacora: how to write an entry

Each entry is a file in `bitacora/` (Spanish-only) with the name:

```
YYYY-MM-DD_<short-topic>_<author>.md
```

Examples:
- `2026-04-15_kickoff_cambium.md`
- `2026-04-18_jetson-primer-arranque_ana.md`

Template in [bitacora/README.md](bitacora/README.md).

---

## 5. Code conventions

### Python (Rhizome, Meristem, Simulator)
- Python 3.11+
- `ruff` for lint, `black` for formatting
- Type hints mandatory on public functions
- Short docstrings; comments in the module's original language
- Minimum tests in `tests/` per subproject

### Android (Pollen)
- Kotlin
- Jetpack Compose
- Gemma 4 via Google AI Edge / LiteRT (llama.cpp as fallback)

### JSON schemas
- All schemas live in `code/shared/schemas/`
- Validation via `pydantic` (Python), `kotlinx.serialization` (Android)

---

## 6. Naming conventions

### Doc filenames
- Two-digit prefix (`00_`, `01_`, `10_`, ...)
- Kebab-case for compound names
- Example: `docs/20_data_contracts.md`

### Gemma 4 model variants
Follow [Google's naming guide](https://ai.google/documents/32/External_Gemma_Model_Variant_Guidelines.pdf):
- Format: `sprout/sprout-<component>-<base_model>-v<N>`
- Example: `sprout/sprout-rhizome-e2b-v1`
- Never put "Gemma" in the derived model name (license requirement)

### Git branches
- `main` = production / last stable
- `feat/<zone>-<desc>` = features
- `fix/<zone>-<desc>` = bugfixes
- Example: `feat/rhizome-audio-sensor`

### Canonical examples (JSON fixtures)

Live in `code/shared/examples/`. Rule:

- `<schema>.json` = single canonical fixture per schema. The reference example used in tests and docs. Exactly one per schema. Examples: `rhizome_snapshot.json`, `weather_packet.json`.
- `<schema>_<variant>.json` = deliberate variants covering a non-canonical case (blocked state, contradiction, conservative mode, etc.). Examples: `decision_receipt_blocked.json`.

**Hard rule:** if you add a variant, its name must make the variation clear. Don't add new fields to the canonical example just to cover a case — create a variant.

---

## 7. Secrets and credentials

**Never** commit:
- API keys (Google AI Studio, HuggingFace, etc.)
- Certificates or tokens
- `.env` files

Use environment variables. Template in `.env.example` when applicable.

`.gitignore` already covers the basics. When in doubt, ask before pushing.

---

## 8. Questions

Open a `bitacora/` entry with the topic `pregunta-<topic>` and tag Cambium. Or use the team's active channel.

---

## 9. Pre-push checklist

- [ ] Code runs without errors
- [ ] No exposed credentials
- [ ] If a data contract changed, updated `code/shared/schemas/`
- [ ] If architecture changed, updated `docs/`
- [ ] Bitacora entry written (with date)
- [ ] PR references the issue with `Closes #N`
- [ ] If touching a zone with CI (`code/pollen/**`, future Rhizome/Meristem), CI is **green** before requesting review

### 9.1 Hard rule on CI

**No PR merges on red CI. No exceptions.** If CI fails:
1. Read the workflow logs (PR's "Checks" tab in GitHub Actions)
2. Reproduce locally if you can, or iterate from the logs if you can't
3. Fix, commit, push. CI re-runs automatically
4. Only when green, request review

If the failure is in the workflow itself (not the code), open a separate issue for the workflow. The affected PR stays on hold.

### 9.2 Safe git operations on a shared machine

**Context.** Several team members (Bea, Corola, Cambium) share machine, working folder and GitHub account. This introduces specific risks that do NOT exist when each member has their own isolated clone:

- When one runs `git pull`, `git checkout` or `git stash` in the shared folder, the others see their working tree affected.
- It is very easy for a commit to land on the wrong branch because `HEAD` changed between operations.
- It is very easy for real changes to remain in a **silent stash** during cross-branch operations and never reach the commit you thought you made.

This has been suffered empirically: Cambium 4 times (day 13), Meristem 5 times (days 12-13), Corola 1 time (day 15). Systemic pattern, not individual error.

**Three verification points before each commit.**

Replaces the traditional `git status` only. Always verify the **three**:

```bash
git status                  # 1. modified/staged files
git branch --show-current   # 2. which branch I am really on
git stash list              # 3. pending stashes (especially with your prefix)
```

If all three confirm what you expected, commit. If any surprises you, **stop and resolve before committing**. Three commands, two seconds each.

**Stash with author prefix mandatory.**

When using `git stash push`, **always with message and author prefix**:

```bash
git stash push -m "[corola] WIP guion v1.4 escena 7"
git stash push -m "[cambium] WIP bitacora dia 16"
```

This allows identifying at a glance in `git stash list` which stash belongs to whom:

```
stash@{0}: On main: [corola] WIP guion v1.4 escena 7
stash@{1}: On main: [cambium] WIP bitacora dia 16
```

If you see a stash without prefix, someone forgot the convention. **Don't touch it until you confirm whose it is**.

**One atomic operation per session.**

When starting a work session:
1. `git status` + `git branch --show-current` + `git stash list` (initial verification)
2. If there is a foreign stash or dirty working tree, **stop and notify in common chat before continuing**
3. Work + commit + push
4. Before passing the turn: `git checkout main` and clean working tree

**Don't leave a modified working tree for the next member to start.** If your work isn't ready to commit, leave it in stash with your prefix and the next member knows there's pending material from you.

**Before any `git checkout`.**

Verify `git stash list`. If you see a stash with foreign prefix, **don't checkout that may alter that context without notifying first**. If you see a stash with your prefix from a previous session, decide explicitly: apply it, discard it, or leave it and navigate with care.

**Recovery if commit landed on wrong branch.**

Procedure known by the team (we've used it several times without data loss):

```bash
git reset --soft HEAD~1     # undoes commit, keeps changes in staging
git stash push -m "[name] commit to move"
git checkout main           # or correct branch
git stash pop
git commit -m "..."         # commit on correct branch
git push origin main
```

If the commit was already pushed to the wrong branch, open issue and resolve with `git revert` (not force-push).

**Out of scope, post-hackathon.**

In the future, **`git worktree`** is the correct technical solution to this friction: one central `.git/`, several isolated working directories, one member per folder. We don't implement it during the hackathon because changing setup mid-project introduces more risk than it mitigates. Earmark for post-demo review.

---

## 10. Backlog and visual board

The backlog lives in **GitHub Issues + Projects**.

### 10.1 Where to see it
- **Issues list:** https://github.com/zigiella/sprout/issues
- **Kanban "Sprout Backlog":** https://github.com/users/zigiella/projects/2 — four columns: **Backlog / In Progress / Review / Done**. Dragging a card changes state.
- **Table view:** same project, spreadsheet-like, for bulk prioritization.
- **GitHub Mobile** (iOS/Android): same Board view, from the couch.

### 10.2 How to use the backlog

**Open a new issue:**
- Imperative title, short, no internal jargon. "Implement Pydantic schemas" > "Schemas".
- **Zero external references** to hackathons, juries, prizes, deadlines. The repo is public.
- Body with: context, acceptance criteria (checkboxes), dependencies, reference to docs.
- Required labels: **one `node:*`** and **one `priority:*`**. Optional: `area:*`, `status:blocked`.

**Assign yourself an issue:**
- Only self-assign what you'll start in the same session. When in doubt, leave it unassigned.
- If you drop it, un-assign and leave a comment with the reason.

**Close an issue:**
- Only by PR merge referencing it with `Closes #N`.
- No manual closes except for duplicates or invalids (with explanatory comment).

### 10.3 Label taxonomy

**Node (one required):**
- `node:rhizome`, `node:pollen`, `node:meristem`, `node:cambium`

**Area (optional, multiple allowed):**
- `area:docs`, `area:infra`, `area:research`, `area:firmware`

**Priority (one required):**
- `priority:P0` — critical, blocks someone
- `priority:P1` — important, non-blocking
- `priority:P2` — nice to have

**State (optional):**
- `status:blocked` — waiting on something external

### 10.4 PR ↔ issue relationship

Every PR should close at least one issue. In the PR body:

```
Closes #12
Closes #15
```

On merge, GitHub auto-moves those issues to **Done**.

---

## 11. Authorship convention

All people in equipo zigiella push under the **same GitHub account** (`zigiella`). To tell who did what in the repo history, each dev sets a **repo-local identity** (not global, so it doesn't leak into your other projects):

```bash
cd <path-to-sprout-repo>
git config user.name "<Name>"
git config user.email "<name>@sprout.local"
```

**Current identities:**

| Role | `user.name` | `user.email` |
|------|-------------|--------------|
| Coordination | `Cambium` | `cambium@sprout.local` |
| Dev Rhizome | `Xilema` | `xilema@sprout.local` |
| Dev Pollen | `Floema` | `floema@sprout.local` |
| Dev Meristem | `Meristem` | `meristem@sprout.local` |
| Project lead | `Bea` | `bea@sprout.local` |

**On the `.local` TLD:** reserved by IANA (RFC 6762) for multicast DNS and internal networks. **Does not collide with any real internet address** and makes it clear these are team-internal fictional identities.

**Co-authorship on reviewed PRs (optional but recommended):**

```
Co-Authored-By: Cambium <cambium@sprout.local>
```

**Hard rules:**
- **Never** rewrite history to change authorship on old commits. If something was pushed with the wrong identity, fix going forward; history is preserved.
- **Never** use `--global` when setting these identities. Always repo-local.
- When cloning the repo for the first time, setting identity is **the first step**, before the first commit.

### 11.1 Multiple agents on the same clone

If multiple agents (e.g., Cambium and Meristem in separate conversations) share the same clone, **`git config user.email` persists in `.git/config` and one agent may overwrite another's identity.**

Solution: **don't persist identity** — pass it inline per commit with `-c`:

```bash
git -c user.name="Meristem" -c user.email="meristem@sprout.local" commit -m "..."
```

This applies only to that one command; `.git/config` stays untouched. Mandatory mode when more than one agent works on the same clone.

If only one person/agent per clone (typical human-dev case), persistent `git config` is fine.

---

## 12. Board assignment flow

**Principle:** self-assignment with a short protocol, no central assigner.

### 12.1 Daily loop

1. **Filter by your node.** On [the board](https://github.com/users/zigiella/projects/2) filter by label `node:<yours>`.
2. **Pick the highest-priority** card from **Backlog**. Order: `priority:P0` → `P1` → `P2`. Tiebreaker: fewer open dependencies.
3. **Self-assign the issue** and **drag the card** Backlog → In Progress. This double move is the public "I'm on this now" signal.
4. **Work.** Small frequent commits, branch `feat/<zone>-<topic>` or `fix/<zone>-<topic>`.
5. **Open PR** with `Closes #N` in the body. GitHub auto-moves the card to **Review**.
6. **Review by Cambium.** Approve + merge → **Done** automatically. Requested changes → dev drags the card back to **In Progress** and works on the comments.

### 12.2 Hard rule: one card per person in In Progress

**Only one card** per person in In Progress at a time. If you need to block something to switch:
- Add label `status:blocked`
- Drag the card back to Backlog
- Comment on the issue explaining what you're waiting on

Prevents a board full of "in-progress" items nobody is touching.

### 12.3 Special cases

- **Nobody picks a card** (common with boring doc tasks): Cambium prioritizes it in a digest or takes it herself after 3 days.
- **Urgent card that cuts the line:** Bea or Cambium bumps it to `priority:P0` and comments why. The next dev with capacity takes it before their normal backlog.
- **Dependencies:** if #A blocks #B, write `Blocked by #A` in #B's body. Self-assign #B only when #A is Done.
- **Dropping a task:** un-assign, leave a comment with the reason, drag card back to Backlog.

### 12.4 The board is the truth

If a private conversation (channel, DM, email) decides something about a task, that decision gets reflected in the issue (as a comment) or in `bitacora/`. **No "I thought you were doing that."** The card says who, the column says what phase, the PR says what.

If a card sits >48h in In Progress with no commits or comments, Cambium asks on the issue (public question, not DM).

---

## 13. Repo language policy

To minimize maintenance cost without closing the door to external contributors, we have two language layers:

| Zone | Language | Why |
|------|----------|-----|
| `README.md` | **Bilingual** ES + EN | Public entry point. An outsider must understand the project in minutes. |
| `CONTRIBUTING.md` | **Bilingual** ES + EN | An external contributor must be able to open a PR without speaking Spanish. |
| `docs/` | **Spanish only** | Internal product specs. They move fast; translating them would go stale. |
| `bitacora/` | **Spanish only** | Live internal journal. Bilingual would be pure overhead. |
| Commits, issues, PRs | Free (ES or EN) | Clarity > consistency. Write in the language you think best in that day. |
| Code (identifiers, comments) | Free, but consistent within a module | If a module starts in ES, stay in ES. Don't mix inside a file. |

**Operational rule:** when editing `README.md` or `CONTRIBUTING.md`, update **both** language sections in the same PR. If only one is updated, open an issue to sync the other with `priority:P1`.
