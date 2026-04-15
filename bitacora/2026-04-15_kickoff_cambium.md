# Kickoff de Sprout

**Fecha:** 2026-04-15
**Autor:** Cambium
**Area:** General
**Tipo:** Decision

## Contexto

Arrancamos el proyecto Sprout para participar en el Gemma 4 Good Hackathon (Kaggle + Google, deadline 18 mayo 2026). El equipo esta formado por Bea (project lead, grabacion, edicion, terraza en Castellar de n'Hug donde se graba), una desarrolladora adicional a definir, un especialista Jetson a asignar, y Cambium (diseno + orden del repo + continuidad).

Partimos de tres documentos v2 previos: brief inicial, arquitectura y MVP, y BOM.

## Que decidimos

### Arquitectura y alcance
- Mantenemos los tres nodos: Rhizome (Jetson), Pollen (Pixel 10 Pro), Meristem (portatil)
- Track principal: Global Resilience
- Tracks tecnologicos objetivo: Ollama + LiteRT + Unsloth (hasta $30K extra potenciales)
- Track adicional evaluable: Cactus, si Pollen enruta tareas entre modelos

### Meristem: local + sombra
- **Produccion / demo:** 100% local, `gemma4:e4b` via Ollama en portatil 16GB
- **Tiempo de test (sombra):** Gemma 4 31B via Google AI Studio API como oraculo de validacion
- El shadow corre con flag `SHADOW_ENABLED=false` por defecto, jamas en el demo grabado
- Upgrade a 26B-A4B en Mac mini M4 24GB si se adquiere antes del deadline

### Pollen WOW: auditor multimodal en vivo
- Gemma 4 E2B on-device via LiteRT (plan B: llama.cpp Android)
- Camara del Pixel como segundo par de ojos con criterio propio
- Detecta contradicciones entre el belief de Rhizome y la observacion in situ
- Genera policy_deltas on-device y los transporta con TTL

### Fine-tuning con Unsloth: entra al MVP
- Base: `google/gemma-4-E2B-it`
- Target: dataset sintetico "Sprout Policy Reasoning v1" (~1500 ejemplos)
- Pesos publicados en HuggingFace + benchmarks
- Tiempo estimado: 2 dias de trabajo en semana 2-3

### Hardware
- Jetson Orin Nano Super ya comprado
- Pixel 10 Pro disponible (Bea)
- Portatil 16GB disponible (Bea)
- Resto del BOM pendiente de compra, priorizado en `docs/02_bom.md`

### Ubicacion de grabacion
- Castellar de n'Hug (Pirineo catalan, ~1400m, ~130 habitantes)
- Terraza de Bea con dos maceteros 100x60 como parcelas logicas
- Contexto geografico real suple la "pequenez" del setup

## Por que

- **Meristem local + sombra:** elimina la tension narrativa (el demo es 100% local) mientras nos da datos cuantitativos para el writeup ("93% de acuerdo local vs cloud en 500 decisiones")
- **Pollen como auditor:** convierte un nodo "ferry" en un nodo con criterio propio, lo hace filmable (10 segundos memorables), y nos abre el track LiteRT
- **Fine-tuning:** 2 dias de trabajo por +$10K potenciales de Unsloth + mejora real de calidad del E2B en dominio agricola
- **Castellar de n'Hug:** el jurado vera "pueblo remoto de montana real" en vez de "setup de estudio", alineado con el enunciado del hackathon

## Estructura del repo montada

```
T6-GEMMA/ (raiz, sera repo GitHub "sprout")
├── README.md, CONTRIBUTING.md, LICENSE, .gitignore
├── GEMMA4-SKILL.md (referencia Gemma 4)
├── HACKATHON.md (reglas hackathon)
├── docs/              (architecture, bom, specs de nodos)
├── bitacora/          (este diario)
├── research/          (metricas de impacto, refs, competitivo)
├── writeup/           (draft Kaggle)
├── video/             (storyboard, script, shot list)
├── code/              (rhizome, pollen, meristem, simulator, shared, finetune)
├── hardware/          (firmware esp32, wiring, fotos)
└── demo/              (live demo assets)
```

## Que queda pendiente

- [ ] Bea crea repo publico `sprout` en GitHub con licencia Apache 2.0
- [ ] Primer push con esqueleto completo
- [ ] Briefing del especialista Jetson (en `docs/10_rhizome_spec.md`)
- [ ] Spec detallada de Pollen (en `docs/11_pollen_spec.md`)
- [ ] Spec detallada de Meristem + shadow (en `docs/12_meristem_spec.md`)
- [ ] Plan Unsloth completo (en `code/finetune/README.md`)
- [ ] Compilar metricas de impacto finales (en `research/metrics/impact_stats.md`)
- [ ] Storyboard del video (en `video/storyboard.md`)
- [ ] Compra del BOM restante

## Enlaces

- [Brief inicial](../docs/00_brief.md)
- [Arquitectura v2](../docs/01_architecture.md)
- [BOM v3](../docs/02_bom.md)
- [GEMMA4-SKILL](../GEMMA4-SKILL.md)
- [Hackathon](../HACKATHON.md)
