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

---

## 10. Backlog y tablero visual

El backlog vive en **GitHub Issues + Projects**.

### 10.1 Donde verlo
- **Lista de issues:** https://github.com/zigiella/sprout/issues
- **Tablero kanban (vista Board):** pestana *Projects* en el repo → "Sprout Backlog". Cuatro columnas: **Backlog / In Progress / Review / Done**. Arrastrar tarjeta cambia estado.
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
