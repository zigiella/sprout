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

## Contexto: Gemma 4 Good Hackathon

Sprout es la entrega de este equipo para [The Gemma 4 Good Hackathon](https://www.kaggle.com/competitions/gemma-4-good-hackathon) (Kaggle + Google).

- **Track principal:** Global Resilience
- **Tracks tecnologicos objetivo:** Ollama, LiteRT, Unsloth
- **Deadline:** 18 mayo 2026

Reglas y estrategia en [HACKATHON.md](HACKATHON.md).

---

## Estructura del repositorio

```
.
├── docs/           Documentacion del producto y arquitectura
├── bitacora/       Diario del proyecto (todo el equipo escribe)
├── research/       Investigacion no-codigo (metricas, referencias)
├── writeup/        Draft de la entrega Kaggle (max 1500 palabras)
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
| Fine-tuning Unsloth | Entra al MVP |
| Vide
o | Localizacion: Castellar de n'Hug |
| Fecha kickoff | 2026-04-15 |

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

## Como participar

Ver [CONTRIBUTING.md](CONTRIBUTING.md).
