<!-- Bilingual document · Spanish first, English below · See CONTRIBUTING §4 for language policy -->

🇪🇸 **[Español](#sprout-es)** · 🇬🇧 **[English](#sprout-en)**

---

<a id="sprout-es"></a>

# Sprout

> Red agricola local-first para parcelas remotas con agua limitada y presencia humana intermitente. Funciona en todo el espectro de conectividad — WiFi, 4G intermitente, o nada.

**Rhizome ejecuta, Meristem aprende y reparte, Pollen transporta inteligencia cruzada.**

Cada parcela puede seguir viva sola con un nodo Rhizome. El sistema se vuelve mas inteligente cuando Meristem consolida evidencia de varias parcelas y Pollen transporta inteligencia cruzada entre ellas, auditando sobre el terreno las decisiones de Rhizome.

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

Tres nodos alineados con los tres tiers oficiales de la familia Gemma 4, con roles inspirados en biologia vegetal:

- **Rhizome** — nodo edge en parcela. Ejecuta decisiones locales seguras. Si la red cae, sigue decidiendo solo. (Jetson Orin Nano Super + microcontrolador ESP32 acoplado + Gemma 4 E2B)
- **Meristem** — nodo estrategico. Consolida evidencia de multiples parcelas, detecta contradicciones, emite politicas con rationale. (Gemma 4 26B MoE; en el MVP via proxy Ollama-compatible hacia la nube — hardware local como objetivo post-hackathon)
- **Pollen** — nodo movil agnostico al portador. Transporta inteligencia cruzada entre parcelas y audita decisiones sobre el terreno. Lo que viaja es el movil con Gemma; quien lo lleva (persona a pie, en bici, en tractor, o un dron agricola autonomo) es decision de despliegue. (Pixel 10 Pro + Gemma 4 E4B via LiteRT)

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
| Meristem | 26B MoE objetivo; demo via proxy Ollama-compatible hacia la nube en MVP; decision de hardware local pendiente dia 18-20 |

Ultima actualizacion en [bitacora/](bitacora/).

---

## Principios no negociables

1. **Funciona en todo el espectro de conectividad** — la desconexion es condicion normal, no excepcion
2. **La IA propone, la seguridad dispone** — capa fisica valida o bloquea
3. **No enviamos ordenes, enviamos politicas** — con caducidad
4. **Toda decision importante deja trazabilidad**
5. **Pollen transporta inteligencia cruzada con caducidad, no "todo"**
6. **Toda politica o contexto util tiene caducidad**
7. **El prototipo debe ser filmable y entendible en menos de un minuto**
8. **Cada nodo declara su modelo objetivo y su modelo andamio** — la demo es honesta sobre en que modo corre cada uno

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

> A local-first agricultural network for remote plots with limited water and intermittent human presence. Runs across the full connectivity spectrum — WiFi, patchy 4G, or none.

**Rhizome executes, Meristem learns and dispatches, Pollen carries cross-field intelligence.**

A single Rhizome node keeps a plot alive on its own. The system becomes smarter when Meristem consolidates evidence from multiple plots and Pollen carries cross-field intelligence between them, auditing Rhizome's on-the-ground decisions.

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

Three nodes aligned with the three official tiers of the Gemma 4 family, with roles inspired by plant biology:

- **Rhizome** — edge node on the plot. Executes safe local decisions. If the network drops, it keeps deciding on its own. (Jetson Orin Nano Super + companion ESP32 microcontroller + Gemma 4 E2B)
- **Meristem** — strategic node. Consolidates evidence from multiple plots, detects contradictions, issues policies with rationale. (Gemma 4 26B MoE; in the MVP via an Ollama-compatible proxy to the cloud — local hardware is the post-hackathon target)
- **Pollen** — mobile node, carrier-agnostic by design. Ferries cross-field intelligence between plots and audits decisions on the ground. What travels is the phone carrying Gemma; who carries it (person walking, on a bike, in a tractor, or an autonomous agricultural drone) is a deployment decision. (Pixel 10 Pro + Gemma 4 E4B via LiteRT)

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
| Meristem | 26B MoE target; MVP demo via Ollama-compatible cloud proxy; local hardware decision pending day 18-20 |

Latest updates in [bitacora/](bitacora/) (Spanish).

---

## Non-negotiable principles

1. **Works across the full connectivity spectrum** — being disconnected is normal, not an exception
2. **The AI proposes, safety decides** — a physical layer validates or blocks
3. **We send policies, not orders** — every policy has an expiry
4. **Every meaningful decision leaves a trace**
5. **Pollen carries cross-field intelligence with expiry, not "everything"**
6. **Every useful policy or context has an expiry**
7. **The prototype must be filmable and understandable in under a minute**
8. **Every node declares its target model and its scaffold model** — the demo is honest about which mode each runs in

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
