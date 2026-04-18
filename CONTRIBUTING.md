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
