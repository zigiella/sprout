<!-- Bilingual document · Spanish first, English below · See CONTRIBUTING §4 for language policy -->

🇪🇸 **[Español](#sprout-es)** · 🇬🇧 **[English](#sprout-en)**

---

<a id="sprout-es"></a>

# Sprout

> Red agricola local-first para parcelas remotas con agua limitada, presencia humana intermitente y conectividad incierta.

**Rhizome ejecuta, Pollen transporta y revisa, Meristem aprende y reajusta.**

Cada parcela puede seguir viva sola con un nodo Rhizome. El sistema se vuelve mas inteligente cuando Pollen y Meristem transforman sensores, vision, memoria operativa y meteo compartida en criterio local, politicas seguras distribuidas y accion offline.

---

## Por que Sprout

Los pequenos cultivos remotos no fallan solo por falta de agua. Fallan por falta de presencia.

Cuando la visita humana es semanal y la conectividad es irregular, casi toda decision llega tarde:
- tarde para detectar estres hidrico
- tarde para corregir una mala politica
- tarde para aprovechar la lluvia
- tarde para evitar gastar un agua que no volvera

**El agua ya no se pierde solo por escasez. Tambien se pierde porque la decision llega tarde.**

---

## Arquitectura en una frase

Tres nodos con roles inspirados en biologia vegetal:

- **Rhizome** — nodo edge en parcela. Ejecuta decisiones locales seguras. (Jetson Orin Nano Super + Gemma 4 E2B)
- **Pollen** — nodo itinerante. Ferry de inteligencia contextual con caducidad. (Pixel 10 Pro + Gemma 4 E2B via LiteRT)
- **Meristem** — nodo estrategico local. Consolida, revisa politicas, emite criterio mas duradero. (Portatil + Gemma 4 E4B via Ollama)

Detalle completo en [docs/01_architecture.md](docs/01_architecture.md).

---

## Estructura del repositorio

```
.
├── docs/           Documentacion del producto y arquitectura (ES)
├── bitacora/       Diario del proyecto (ES, todo el equipo escribe)
├── research/       Investigacion no-codigo (metricas, referencias)
├── writeup/        Documento de presentacion del proyecto
├── video/          Storyboard, guion, shot list
├── code/           Todo el software
│   ├── rhizome/    Jetson + Python
│   ├── pollen/     Android + LiteRT
│   ├── meristem/   Python + Ollama
│   ├── simulator/  Visualizacion de red
│   ├── shared/     Schemas JSON compartidos
│   └── finetune/   Unsloth: dataset, notebooks, evals
├── hardware/       Firmware ESP32, wiring, fotos
└── demo/           Assets de live demo
```

---

## Estado del proyecto

| Area | Estado |
|------|--------|
| Arquitectura | Cerrada v2 |
| BOM | Cerrado, pendiente de compra final |
| Hardware Jetson | Comprado |
| Pollen (Pixel 10 Pro) | Confirmado |
| Meristem local | E4B en portatil 16GB decidido |

Ultima actualizacion en [bitacora/](bitacora/).

---

## Principios no negociables

1. **Offline-first real** — la desconexion es condicion normal, no excepcion
2. **La IA propone, la seguridad dispone** — capa fisica valida o bloquea
3. **No enviamos ordenes, enviamos politicas** — con caducidad
4. **Toda decision importante deja trazabilidad**
5. **Pollen transporta deltas, no "todo"**
6. **Toda politica o contexto util tiene caducidad**
7. **El prototipo debe ser filmable y entendible en menos de un minuto**

---

## Licencia

Apache 2.0. Igual que Gemma 4.

## Autoria

Mantenido por **equipo zigiella**.

## Como participar

Ver [CONTRIBUTING.md](CONTRIBUTING.md).

---
---

<a id="sprout-en"></a>

# Sprout — English

> A local-first agricultural network for remote plots with limited water, intermittent human presence, and uncertain connectivity.

**Rhizome executes, Pollen carries and audits, Meristem learns and adjusts.**

A single Rhizome node keeps a plot alive on its own. The system becomes smarter when Pollen and Meristem turn sensor data, vision, operational memory, and shared weather into local judgment, safely distributed policies, and offline action.

---

## Why Sprout

Small remote plots don't fail from water scarcity alone. They fail from lack of presence.

When human visits are weekly and connectivity is unreliable, almost every decision arrives too late:
- too late to detect water stress
- too late to correct a bad policy
- too late to take advantage of rainfall
- too late to avoid spending water that won't come back

**Water is no longer lost only to scarcity. It is also lost because the decision arrives late.**

---

## Architecture in one sentence

Three nodes with roles inspired by plant biology:

- **Rhizome** — edge node on the plot. Executes safe local decisions. (Jetson Orin Nano Super + Gemma 4 E2B)
- **Pollen** — itinerant node. Ferries contextual intelligence with an expiry date. (Pixel 10 Pro + Gemma 4 E2B via LiteRT)
- **Meristem** — local strategic node. Consolidates, reviews policies, issues longer-lived judgment. (Laptop + Gemma 4 E4B via Ollama)

Full detail in [docs/01_architecture.md](docs/01_architecture.md) (Spanish only).

---

## Repository layout

```
.
├── docs/           Product & architecture docs (Spanish)
├── bitacora/       Project journal (Spanish, whole team writes)
├── research/       Non-code research (metrics, references)
├── writeup/        Project presentation document
├── video/          Storyboard, script, shot list
├── code/           All software
│   ├── rhizome/    Jetson + Python
│   ├── pollen/     Android + LiteRT
│   ├── meristem/   Python + Ollama
│   ├── simulator/  Network visualization
│   ├── shared/     Shared JSON schemas
│   └── finetune/   Unsloth: dataset, notebooks, evals
├── hardware/       ESP32 firmware, wiring, photos
└── demo/           Live-demo assets
```

---

## Project status

| Area | Status |
|------|--------|
| Architecture | Closed, v2 |
| BOM | Closed, final purchase pending |
| Jetson hardware | Purchased |
| Pollen (Pixel 10 Pro) | Confirmed |
| Meristem (local) | E4B on a 16 GB laptop decided |

Latest updates in [bitacora/](bitacora/) (Spanish).

---

## Non-negotiable principles

1. **Offline-first for real** — being disconnected is the default, not an exception
2. **The AI proposes, safety decides** — a physical layer validates or blocks
3. **We send policies, not orders** — every policy has an expiry
4. **Every meaningful decision leaves a trace**
5. **Pollen ferries deltas, not "everything"**
6. **Every useful policy or context has an expiry**
7. **The prototype must be filmable and understandable in under a minute**

---

## License

Apache 2.0. Same as Gemma 4.

## Maintained by

**equipo zigiella**.

## How to contribute

See [CONTRIBUTING.md](CONTRIBUTING.md) — also bilingual.

---

### Language policy

- `README.md` and `CONTRIBUTING.md` are **bilingual** (Spanish + English).
- Product specs (`docs/`) and the project journal (`bitacora/`) are **Spanish-only** to keep maintenance cost low.
- Code identifiers, commit messages, and issue titles can be written in either language, author's choice — clarity over consistency.
