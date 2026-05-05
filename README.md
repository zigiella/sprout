<!-- Bilingual document · Spanish first, English below · See CONTRIBUTING §4 for language policy -->

🇪🇸 **[Español](#sprout-es)** · 🇬🇧 **[English](#sprout-en)**

---

<a id="sprout-es"></a>

# Sprout

> Arquitectura local-first para decisiones de riego en parcelas aisladas, con agua limitada, visitas humanas intermitentes y conectividad incierta.

**Rhizome mantiene viva la parcela cuando nadie esta. Pollen convierte la visita en inteligencia util.**

La promesa de Sprout no es automatizar una bomba. Es **reducir la latencia de decision** cuando la parcela, la persona y la red no coinciden en el tiempo.

---

## Por que Sprout

La agricultura aislada no sufre solo por falta de agua. Sufre porque la decision correcta suele llegar tarde.

Si no hay buena conectividad y solo visitas la parcela cada cierto tiempo:
- riegas demasiado tarde
- riegas demasiado pronto
- o riegas con el criterio equivocado

**Cuando el campo, la persona y la red no coinciden en el tiempo, Sprout reduce la latencia de decision sin renunciar a soberania local, seguridad fisica y explicabilidad.**

---

## Arquitectura en una frase

Tres nodos con jurisdicciones distintas, inspirados en biologia vegetal:

- **Rhizome** — nodo autonomo de parcela. Lee estado local, decide dentro de un sobre seguro, ejecuta o bloquea a traves del ESP32. Gemma 4 E2B sobre Jetson Orin Nano Super. **Jurisdiccion: minutos.**
- **Pollen** — nodo itinerante movil. Compilador de intencion humana, auditor itinerante, federador de parcelas, interfaz conversacional de Rhizome. Gemma 4 E4B sobre Pixel 10 Pro via LiteRT-LM. **Jurisdiccion: visita con TTL corto.**
- **Meristem** — cerebro lento. Consolida bundles de varias visitas, evalua desempeno de politicas, emite `PolicyPacket`. **Jurisdiccion: dias. No esta en la demo del hackathon; queda especificado como trabajo en curso post-hackathon.**

Separadamente, y criticamente: un **ESP32** como coprocesador de seguridad. Dueno de sensores criticos, dueno de actuadores, arbitro de seguridad fisica, guardian del failsafe. **Si Jetson se cae, el sistema no se vuelve peligroso.**

Detalle completo en [docs/01_architecture.md](docs/01_architecture.md).

---

## Estructura del repositorio

```
.
├── docs/           Documentacion del producto y arquitectura v2 (ES)
├── bitacora/       Diario del proyecto (ES, todo el equipo escribe)
├── research/       Investigacion no-codigo (metricas, referencias)
├── writeup/        Documento de presentacion del proyecto
├── video/          Storyboard, guion, shot list
├── code/           Todo el software
│   ├── rhizome/    Jetson + Python
│   ├── pollen/     Android + LiteRT-LM
│   ├── meristem/   Python + adapter Ollama-compatible (post-hackathon)
│   ├── simulator/  Visualizacion de red
│   ├── shared/     Schemas JSON compartidos
│   └── finetune/   Unsloth: dataset, notebooks, evals (post-hackathon)
├── hardware/       Firmware ESP32, wiring, fotos
└── demo/           Assets de live demo
```

---

## Estado del proyecto

| Area | Estado |
|------|--------|
| Arquitectura | Cerrada v2 (2026-04-22) |
| BOM | Cerrado |
| Hardware Jetson | Comprado |
| Pollen (Pixel 10 Pro) | Confirmado; pendiente verificacion oficial LiteRT-LM + E4B + Android 16 |
| Firmware ESP32 | En curso (pieza bloqueante para demo) |
| Meristem | Fuera de demo. Adapter Ollama-compatible disponible como infraestructura v2 |

Ultima actualizacion en [bitacora/](bitacora/).

---

## Principios no negociables

1. **Offline-first real** — el sistema debe seguir sirviendo aunque no haya internet
2. **La IA propone, la seguridad dispone** — ningun modelo toca bomba o valvulas sin pasar por reglas duras del ESP32
3. **La visita humana es parte de la computacion** — la persona que recorre la parcela es evento del sistema, no "usuario periferico"
4. **Cada nodo tiene jurisdiccion** — Rhizome minutos, Pollen visita con TTL, Meristem dias
5. **Toda inteligencia caduca** — toda politica, digest o enmienda lleva tiempo de validez

---

## Licencia

Apache 2.0. Igual que Gemma 4.

## Atribucion

Sprout usa modelos Gemma 4 de Google. Gemma is a trademark of Google LLC.
Este proyecto no esta afiliado ni respaldado por Google.

## Autoria

Mantenido por **equipo zigiella**.

## Como participar

Ver [CONTRIBUTING.md](CONTRIBUTING.md).

---
---

<a id="sprout-en"></a>

# Sprout — English

> A local-first architecture for irrigation decisions in isolated plots with limited water, intermittent human visits, and uncertain connectivity.

**Rhizome keeps the plot alive when no one is there. Pollen turns the visit into useful intelligence.**

Sprout's promise is not to automate a pump. It is to **reduce decision latency** when the plot, the person, and the network don't coincide in time.

---

## Why Sprout

Isolated agriculture doesn't suffer only from water scarcity. It suffers because the right decision usually arrives late.

If connectivity is poor and you only visit the plot periodically:
- you water too late
- you water too early
- or you water with the wrong criterion

**When the field, the person, and the network don't coincide in time, Sprout reduces decision latency without giving up local sovereignty, physical safety, and explainability.**

---

## Architecture in one sentence

Three nodes with distinct jurisdictions, inspired by plant biology:

- **Rhizome** — autonomous plot node. Reads local state, decides inside a safe envelope, executes or blocks through the ESP32. Gemma 4 E2B on Jetson Orin Nano Super. **Jurisdiction: minutes.**
- **Pollen** — roaming mobile node. Compiler of human intent, itinerant auditor, plot federator, conversational interface for Rhizome. Gemma 4 E4B on Pixel 10 Pro via LiteRT-LM. **Jurisdiction: visit with short TTL.**
- **Meristem** — slow brain. Consolidates visit bundles, evaluates policy performance, issues `PolicyPacket`. **Jurisdiction: days. Not in the hackathon demo; specified as post-hackathon work in progress.**

Separately, and critically: an **ESP32** as safety coprocessor. Owner of critical sensors, owner of actuators, physical-safety arbiter, failsafe guardian. **If Jetson goes down, the system does not become dangerous.**

Full detail in [docs/01_architecture.md](docs/01_architecture.md) (Spanish only).

---

## Repository layout

```
.
├── docs/           Product & architecture v2 docs (Spanish)
├── bitacora/       Project journal (Spanish, whole team writes)
├── research/       Non-code research (metrics, references)
├── writeup/        Project presentation document
├── video/          Storyboard, script, shot list
├── code/           All software
│   ├── rhizome/    Jetson + Python
│   ├── pollen/     Android + LiteRT-LM
│   ├── meristem/   Python + Ollama-compatible adapter (post-hackathon)
│   ├── simulator/  Network visualization
│   ├── shared/     Shared JSON schemas
│   └── finetune/   Unsloth: dataset, notebooks, evals (post-hackathon)
├── hardware/       ESP32 firmware, wiring, photos
└── demo/           Live-demo assets
```

---

## Project status

| Area | Status |
|------|--------|
| Architecture | Closed v2 (2026-04-22) |
| BOM | Closed |
| Jetson hardware | Purchased |
| Pollen (Pixel 10 Pro) | Confirmed; pending official LiteRT-LM + E4B + Android 16 verification |
| ESP32 firmware | In progress (blocking piece for demo) |
| Meristem | Out of demo. Ollama-compatible adapter available as v2 infrastructure |

Latest updates in [bitacora/](bitacora/) (Spanish).

---

## Non-negotiable principles

1. **Offline-first, for real** — the system must keep serving even without internet
2. **The AI proposes, safety decides** — no model touches pump or valves without passing the ESP32's hard rules
3. **The human visit is part of the computation** — the person walking the plot is a system event, not a "peripheral user"
4. **Each node has jurisdiction** — Rhizome minutes, Pollen visit with TTL, Meristem days
5. **All intelligence expires** — every policy, digest, or amendment carries validity time

---

## License

Apache 2.0. Same as Gemma 4.

## Attribution

Sprout uses Gemma 4 models by Google. Gemma is a trademark of Google LLC.
This project is not affiliated with or endorsed by Google.

## Maintained by

**equipo zigiella**.

## How to contribute

See [CONTRIBUTING.md](CONTRIBUTING.md) — also bilingual.

---

### Language policy

- `README.md` and `CONTRIBUTING.md` are **bilingual** (Spanish + English).
- Product specs (`docs/`) and the project journal (`bitacora/`) are **Spanish-only** to keep maintenance cost low.
- Code identifiers, commit messages, and issue titles can be written in either language, author's choice — clarity over consistency.
