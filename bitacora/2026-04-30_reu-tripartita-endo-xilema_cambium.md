# Reu tripartita Endo + Xilema + Cambium — día 15

**Fecha:** 2026-04-30 (día 15)
**Modera:** Cambium
**Participan:** Endodermis (entra al equipo, primer trabajo concreto sobre Jetson), Xilema (dueña Rhizome físico + ESP32, supervisora técnica de Endo)
**Formato:** síncrona, ~45 min máximo
**Materiales en mano:**
- `docs/52_endodermis_jetson_bringup_brief.md` (briefing técnico de Xilema, mergeado hace minutos en PR #61)
- `code/tuning/` y bitácoras de Meristem ya en main (PR #62 mergeado hace minutos)
- Carta motivacional de Endodermis (`CAJON/carta_motivacional_endodermis_a_cambium.md`)
- Bitácora de onboarding repo vivo de Endodermis (`bitacora/2026-04-30_endodermis-onboarding-repo-vivo_endodermis.md`)
- Briefing de Endodermis sobre el bloqueo BME280 de Xilema (`bitacora/2026-04-30_endodermis-briefing-y-bme280-bloqueo_xilema.md`)

---

## Estado de partida (lo que las tres ya saben)

- **Endodermis** se incorpora al equipo. Trabajará bajo supervisión técnica de Xilema en frontera física. Su primer frente concreto: re-ejecutar batería Rhizome v0.5 en Jetson real días 16-17 + apoyar consolidación Jetson + ESP32. Horizonte condicional: doble agente días 25-30 si MVP estable día 24.
- **Xilema** preparó briefing técnico (PR #61) antes incluso de la conversación — anticipa frontera, stack, checklist y smoke cases. Tiene además bloqueo físico BME280 (sensor crudo sin presoldar) que no afecta directamente a Endo pero es contexto.
- **Cambium** modera. Bea aprueba decisiones por mensaje cuando proceda.

---

## Agenda (45 min máximo)

| Bloque | Tiempo | Output |
|--------|--------|--------|
| 0. Arranque | 2 min | Confirmación de que las tres han leído briefing + onboarding bitácora |
| 1. Estado del MVP al día 15 (Xilema explica) | 5 min | Endo entiende dónde encajan sus días 16-17 |
| 2. Frontera entre frentes (casos límite) | 10 min | Endo y Xilema acuerdan qué toca cada una |
| 3. Preguntas de Endo sobre briefing + `code/tuning/` + smoke cases | 15 min | Dudas resueltas o convertidas en parking lot |
| 4. Plan operativo concreto días 16-17 | 10 min | Tareas con dueña + plazo escritas en bitácora |
| 5. Cadencia de check-ins durante semana | 3 min | Quién avisa a quién y cuándo |

---

## Bloque 0 — Arranque (2 min)

*[Cambium pregunta: las tres han leído? Endodermis confirma haber leído briefing de Xilema y tener acceso a `code/tuning/`. Xilema confirma haber leído onboarding bitácora de Endo y briefing tripartita.]*

**Resultado:** *[pendiente]*

---

## Bloque 1 — Estado del MVP al día 15 desde Rhizome físico (5 min)

*[Xilema explica brevemente:]*

- Estado del firmware ESP32 (cinco reglas + SAFETY_DOWNGRADE en placa real, códigos en inglés tras cascada).
- Estado del host harness (`hardware/host_tools/esp32_host_harness.py`, escenarios `guardian_demo` + `telemetry_stub_roundtrip` reproducibles).
- Bloqueo BME280 (sensor crudo, no afecta a Endo).
- Lo que falta antes de Jetson en mesa: cableado físico + montaje eléctrico (fusibles, masa común, flyback).

**Resultado / decisiones:** *[pendiente]*

---

## Bloque 2 — Frontera entre frentes (10 min)

Casos límite que conviene cerrar por escrito:

**Lo que toca Xilema (no Endo):**
- Firmware ESP32 (sources C en `hardware/firmware_esp32/main/`).
- Reglas duras (`docs/30_safety_rules.md`).
- Sensores físicos + actuadores + cableado físico.
- Host harness ESP32-side.

**Lo que toca Endo (no Xilema):**
- Servicio Rhizome lado Jetson (Python + llama.cpp + Gemma 4 E2B Q4_K_M).
- Re-ejecución batería Rhizome v0.5 desde `code/tuning/` contra `llama-server` en Jetson.
- Comparación tok/s + latencia + estabilidad envelope vs baseline x86 de Meristem.
- Validación operativa de `docs/51_rhizome_gemma4_e2b_jetson_guide.md` en hardware real.

**Frontera compartida (decisión por escrito):**
- ¿Quién lanza el primer ping ESP32 ↔ Jetson via USB-CDC nativo? Probable: Xilema, con Endo como observadora.
- ¿Quién expone el endpoint `/explain/decision/{id}` en el servicio Rhizome lado Jetson (contrato JSON envelope cerrado en PR #58)? Probable: Endo, con validación de Xilema sobre el contrato.
- ¿Quién es responsable del bundle mínimo de visita que Meristem-nodo va a ingerir (FieldVisit + receipts + snapshot)? Probable: Xilema define el shape (es contrato del nodo Rhizome), Endo lo emite operativamente desde el servicio.

**Resultado / decisiones:** *[pendiente — escribir aquí lo acordado]*

---

## Bloque 3 — Preguntas de Endo (15 min)

Las tres preguntas operativas que dejó en su bitácora del día 14 + cualquier nueva tras leer el briefing y `code/tuning/`:

**Pregunta 1 — Rama base:** Resuelta. `main`. Trabajo nuevo en `feat/endodermis/[descripción]`. Verificar `git branch --show-current` antes de cada commit.

**Pregunta 2 — Harness exacto Rhizome v0.5:** Ahora ya en main tras PR #62. `code/tuning/harness.py` + `code/tuning/system_prompts.yaml` (entry `rhizome_balanced_es_v05`) + `code/tuning/prompt_pack_rhizome_es.yaml` + `code/tuning/matrix_rhizome_v0.yaml`. Smoke cases obligatorios: RA04, RD03, RD08, RD01.

**Pregunta 3 — Protocolo DRY_RUN ESP32:** `docs/13_esp32_spec.md` + briefing `docs/52_endodermis_jetson_bringup_brief.md` (Xilema). Si quedan dudas tras lectura, este es el momento.

**Preguntas nuevas que probablemente plantee Endo:**
- ¿Qué versión exacta de `llama.cpp` se va a usar en Jetson? ¿Build precompilado para Jetson Orin Nano Super o compilado desde fuente?
- ¿Q4_K_M o Q5_K_M para Gemma 4 E2B en Jetson? Meristem validó Q4_K_M en x86 CPU; Jetson tiene GPU offload.
- ¿`pytest` y otras dependencias se instalan en venv del Jetson o en sistema?
- ¿Cómo se versionan los transcripts de las pruebas en Jetson (carpeta git-ignored o committed)?

**Resultado / decisiones:** *[pendiente]*

---

## Bloque 4 — Plan operativo concreto días 16-17 (10 min)

Plantilla a rellenar en directo:

| # | Tarea | Dueña | Plazo |
|---|-------|-------|-------|
| 1 | Setup entorno Jetson (JetPack 6.x + MAXN SUPER + NVMe SSD + swap + Docker NVIDIA runtime) | *[pendiente]* | *[pendiente]* |
| 2 | Arrancar `llama-server` en Jetson con Gemma 4 E2B Q4_K_M | *[pendiente]* | *[pendiente]* |
| 3 | Smoke test inicial (1 prompt) verificando endpoint OK + `Sprout-Inference-*` headers correctos | *[pendiente]* | *[pendiente]* |
| 4 | Re-ejecutar batería Rhizome v0.5 completa (18 prompts) contra Jetson real | *[pendiente]* | *[pendiente]* |
| 5 | Comparación tok/s + latencia p50/p95 + estabilidad envelope vs baseline x86 de Meristem | *[pendiente]* | *[pendiente]* |
| 6 | Documentar regresiones (si las hay) en bitácora + abrir PR pequeño con análisis | *[pendiente]* | *[pendiente]* |
| 7 | Primer ping ESP32 ↔ Jetson via USB-CDC | *[pendiente]* | *[pendiente]* |
| 8 | Validación operativa de docs/51 contra Jetson real + actualizar guía si hace falta | *[pendiente]* | *[pendiente]* |

**Resultado / decisiones:** *[pendiente]*

---

## Bloque 5 — Cadencia de check-ins (3 min)

Propuestas para que las tres acordemos:

- **Diario (cada cierre del día)**: cada miembra escribe bitácora corta de progreso. Cambium relayea a Bea si hay decisión pendiente.
- **Síncrono opcional**: 15-30 min al día si Endo o Xilema lo piden. Cambium agenda.
- **Bloqueos**: si Endo bloquea en algo de Xilema (frontera física, contrato, sensor), Endo escribe en bitácora con tag `[bloqueado]`. Xilema responde en ≤2 horas.
- **Decisiones de scope**: si surge cosa nueva (regresión seria, propuesta de cambio en frontera), Cambium decide si va a Bea inmediatamente o a bitácora con label `escalable`.

**Resultado / decisiones:** *[pendiente]*

---

## Cierre

*[Cambium: recap rápido de las decisiones cerradas + recordatorio de quién hace qué + plazo. Si hay parking lot abierto, lo apunta abajo.]*

### Acciones derivadas con dueña + plazo

*[pendiente — rellenar en directo durante la reu]*

### Parking lot

*[pendiente]*

---

*Bitácora abierta el 2026-04-30, día 15. Modo síncrono en directo. Cambium edita durante la reu y al cierre. Resto del equipo lee post-reu si quiere contexto.*
