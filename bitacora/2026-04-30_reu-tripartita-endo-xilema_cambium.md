# Reu tripartita Endo + Xilema + Cambium — día 15

**Fecha:** 2026-04-30 (día 15)
**Modera:** Cambium
**Aprueba decisiones de scope (si surgen):** Bea (por mensaje, fuera de la reu)
**Participan:** Endodermis (entra al equipo, primer trabajo concreto sobre Jetson), Xilema (dueña Rhizome físico + ESP32, supervisora técnica de Endo)
**Formato:** síncrono por turnos contra el repo. Ambas commitan archivos en `coordinacion/2026-04-30_reu_tripartita_endo_xilema/`. Cambium consolida en esta bitácora.

**Materiales en mano:**
- `docs/52_endodermis_jetson_bringup_brief.md` (briefing técnico de Xilema, mergeado en main mañana del día 15 vía PR #61)
- `code/tuning/` y bitácoras de Meristem ya en main (PR #62 mergeado mañana del día 15 — incluye `code/tuning/` completo + 10 bitácoras estratégicas)
- `bitacora/2026-04-30_endodermis-onboarding-repo-vivo_endodermis.md` (onboarding limpio de Endo)
- `bitacora/2026-04-30_endodermis-briefing-y-bme280-bloqueo_xilema.md` (cierre de día de Xilema con bloqueo BME280)

---

## Estructura de la reu

Primera iteración abierta: cada miembra expone los temas que quiere tratar. Cambium consolida y propone orden. Bloques sucesivos ad-hoc según los temas que salgan.

| Bloque | Quién escribe | Output | Estado |
|--------|---------------|--------|--------|
| **0. Apertura + reglas** | (lectura) | Confirmación de lectura previa | Pendiente confirmación |
| **1. Temas a tratar** | Endo y Xilema en paralelo | Archivos en `coordinacion/.../bloque_1_temas_a_tratar/` | Pendiente arranque |
| **N. Bloques sucesivos** | A definir | A definir | A definir tras bloque 1 |

---

## Bloque 1 — Temas a tratar

**Cerrado.** Las dos miembras commitearon en paralelo (`temas_endodermis.md` y `temas_xilema.md`). **Convergencia muy alta — prácticamente acordaron lo mismo sin haberse leído.**

### Hallazgo del bloque

Cuando dos miembras técnicas con criterio independiente exponen sus temas en paralelo y convergen casi al 100%, es señal de que la frontera entre frentes está bien diseñada y los criterios del proyecto están internalizados. **Síntoma sano del equipo.**

Las únicas diferencias que aparecen entre los dos archivos son **refinamientos**, no discrepancias:
- Xilema añade una segunda iteración del primer ping ESP32↔Jetson (Endo repite + documenta) que Endo no había contemplado pero adoptaría sin objeción.
- Xilema marca un límite de scope (que `/explain/decision/{id}` no entra en días 16-17) que Endo había planteado como pregunta abierta. Xilema cierra; Endo aceptaría.

Cero conflictos. Solo afinamientos.

### Temas consolidados — agrupados por categoría

**A — Frontera entre frentes (todos cerrados por acuerdo)**

1. ✅ Endo no toca firmware ESP32, reglas duras, códigos de veto, `tank_minimum_pct`, ni `hardware/firmware_esp32/` ni `hardware/host_tools/` salvo lectura y ejecución supervisada.
2. ✅ Endo se centra en inferencia/validación Jetson: caracterizar Jetson, arrancar `llama-server`, levantar adapter `llamacpp`, ejecutar batería Rhizome v0.5, comparar métricas.
3. ✅ Adapter `llamacpp` (`code/meristem_inference_adapter`) es el puente oficial para la batería contra `llama-server` — no crear runner nuevo salvo fallo real.
4. ✅ Bundle Rhizome→Meristem: **no se diseña en esta reu**. Se usa lo ya acordado, RA04 como gate. Si Meristem pide `FieldVisit`/`SyncBundle` después, se trata como siguiente contrato.
5. ✅ Primer ping Jetson↔ESP32 vía USB-CDC: **Xilema lidera primera vez con Endo observando + Endo repite segunda vez documentando** (refinamiento de Xilema sobre la propuesta inicial).
6. ✅ `/explain/decision/{id}` queda **fuera de scope días 16-17**. Endo se centra en inferencia, no implementación de endpoints Rhizome. Si después Cambium lo pide como bloque separado, se trata.

**B — Stack y bloqueos (todos cerrados por acuerdo)**

7. ✅ **Cuantización**: `Q4_K_S` como primera medición oficial (autoridad del briefing `docs/52`, deja margen en 8 GB). `Q4_K_M` solo como comparativa posterior si pasa el primer test.
8. ✅ **Puerto adapter**: `ADAPTER_PORT=12000` con `LLAMACPP_SERVER_URL=http://localhost:8080`. Coincidente con matrices Rhizome.
9. ✅ **Artefactos de resultados**: JSONL completos en `code/tuning/results/` gitignored + resumen en bitácora. Reportes pequeños puntuales se decide caso por caso si versionar.
10. ✅ **SO Jetson**: microSD con JetPack 6.2.1 oficial para Orin Nano Super. Si no arranca, sospecha QSPI y seguir guía Jetson AI Lab antes de tocar modelos.
11. ✅ **NVMe**: si no está montado, bootstrap en microSD documentando la limitación (no es flujo estable para GenAI pesado).
12. ✅ **BME280** no afecta a Endo — bloqueo de Xilema con su propio frente. No se usa ese fallo como señal contra ESP32 ni contra Jetson.

**C — Plan operativo días 16-17 (consolidado)**

13. ✅ **Día 16 mañana**: Jetson boot + baseline (`nv_tegra_release`, kernel, RAM, disco, `lsblk`, `nvpmodel`, Docker, runtime NVIDIA, `tegrastats`). Sin modelo hasta baseline en bitácora.
14. ✅ **Día 16 tarde**: arrancar `llama-server` con Gemma 4 E2B Q4_K_S + smoke OpenAI-compatible en `:8080`. Después arrancar adapter `llamacpp` en `:12000` + smoke `/api/chat`.
15. ✅ **Día 16 cierre / día 17 mañana**: mini-test 6 prompts (smoke críticos RA04, RD03, RD08, RD01 primero). Si falla crítico, parar y documentar — no retocar prompt en caliente.
16. ✅ **Día 17**: completar 18 prompts y comparar con baseline x86 de Meristem (estabilidad envelope/status, p50/p95, tok/s, temperatura, OOM/throttle).

**D — Cadencia de check-ins (consolidada)**

17. ✅ Check breve tras cada hito: `boot ok` → `docker ok` → `model load ok` → `smoke ok` → `full battery ok/fail`.
18. ✅ Bloqueos de >2h escalan a Cambium + Xilema.
19. ✅ Si hay fallo físico/protocolo: bloqueo escrito, Xilema decide. Si fallo de prompt/modelo: no se toca prompt sin Cambium/Bea.

**E — Reglas operativas (aporte de Xilema en D, adoptadas)**

20. ✅ **Permiso explícito para Endo de decir "esto no lo entiendo" o "esto no arranca"** sin intentar arreglarlo heroicamente. Se prefiere bloqueo claro a optimización secreta.
21. ✅ **Disciplina de secuencia**: SO y firmware → baseline → runtime → modelo → batería → integración. **No saltarse pasos por emoción de tener Jetson en mesa.**

### Decisiones que Cambium toma (puntos no convergentes — minoría)

**F — Decisiones de Cambium tras leer ambos archivos**

22. **TTFT real (Endo pregunta).** Decisión: **no es obligatorio para el MVP**. Latencia total + p50/p95 wall-clock es suficiente para `engineering pass`. TTFT a backlog post-demo si se necesita en writeup.
23. **Dependencias Python en Jetson (Endo pregunta).** Decisión: **venv en raíz del repo** (limpio, aislado, reproducible). Endo documenta cómo lo monta en bitácora.
24. **Ventana horaria para descargas (Endo pregunta).** Decisión: **no hay ventana específica**. Descarga cuando convenga. Si interfiere con vídeo/Pollen/ESP32, se nombra y se ajusta. No se pelean a priori.
25. **Criterio de `engineering pass` (propuesta Xilema).** Decisión: **adoptado tal cual**. 6 críticos repetidos frío/caliente sin OOM/truncamiento crítico + los 18 sin fallo crítico. Repetir los 18 completos sin degradación es objetivo aspiracional, no mínimo del día 17.

### Orden de tratamiento propuesto para bloques sucesivos

Dado que la convergencia es ~95% en el bloque 1, no necesitamos varios bloques de iteración. Propongo **un solo bloque más**:

**Bloque 2 — Cierre y ratificación**: las dos miembras leen este consolidado en la bitácora + las decisiones de Cambium (puntos 22-25), y ratifican que el cierre las representa. Si alguna detecta algo que falta o que no encaja, lo dice. Si las dos ratifican sin objeción, cierro la reu.

Tiempo objetivo bloque 2: 5-10 min cada una.

---

## Bloque 2 — Ratificación

**Cerrado sin objeción.** Ambas miembras commitearon `ratificacion_endodermis.md` y `ratificacion_xilema.md` ratificando los 21 acuerdos + las 4 decisiones de Cambium. Cero discrepancias.

### Refinamiento de Xilema (no objeción)

Xilema señala matiz de redacción que conviene incorporar explícitamente al plan operativo: *"el primer flasheo de microSD / primer boot de Jetson es fase previa compartida con Bea/Xilema. Endodermis toma ownership operativo desde Jetson arrancada hacia baseline, Docker, runtime, adapter y batería. No quiero que 'Endo lleva Jetson' se lea como 'Endo resuelve sola cualquier problema de QSPI/primer arranque'."*

**Adoptado.** Se añade como punto 26 del consolidado:

26. ✅ **Fase previa compartida** (microSD + primer boot Jetson): Bea/Xilema lideran. Endo asume ownership operativo desde "Jetson arrancada" en adelante. Si hay problema de QSPI/firmware/primer boot, no es responsabilidad de Endo resolverlo sola.

### Parking lot menor (Xilema)

Cuando Jetson esté vivo y estable: decidir si documentar el flasheo microSD + primer boot en mini-guía propia (probablemente como ampliación de `docs/51_rhizome_gemma4_e2b_jetson_guide.md`) o si basta con bitácora. **No bloqueante**. Se decide post-arranque del día 16.

### Compromiso operativo de Endodermis

Endo se compromete a escribir en bitácora el venv concreto + comandos exactos antes de correr la batería completa. **Patrón sano**: documentar antes de ejecutar, no después. Encaja con la disciplina de secuencia adoptada (punto 21).

### Hallazgo cultural — declaración de confianza explícita

Xilema cierra su ratificación con: *"Me siento cómoda con Endodermis en este carril: suficientemente autónoma para mover Jetson y suficientemente prudente para no tocar la frontera física sin permiso."*

Es **declaración de confianza explícita de la supervisora hacia la nueva miembra al final de su primer día de trabajo conjunto**. En equipos pequeños con plazos cortos, ese tipo de aval cuesta semanas de construir y se nombra raras veces. Lo registro como hallazgo cultural del meeting — refuerza que el filtro de entrada de Endodermis (carta motivacional + onboarding del día 14) era acertado.

---

## Cierre del meeting

**Estado: cerrado sin objeción** tras 2 bloques (apertura abierta + ratificación).

### Decisiones cerradas (recap completo — 26 puntos)

**A — Frontera entre frentes (6 puntos):** Endo no toca firmware/reglas duras; centrada en inferencia/validación Jetson; adapter `llamacpp` como puente oficial; bundle Rhizome→Meristem usa lo ya acordado (RA04 como gate); primer ping Jetson↔ESP32 liderado por Xilema con Endo repitiendo en segunda iteración; `/explain/decision/{id}` fuera de scope días 16-17.

**B — Stack y bloqueos (6 puntos):** Q4_K_S como primera cuantización oficial; `ADAPTER_PORT=12000`; artefactos en `code/tuning/results/` gitignored + resumen en bitácora; SO Jetson microSD JetPack 6.2.1; NVMe deseable pero microSD aceptable documentando limitación; BME280 bloqueado pero no afecta a Endo.

**C — Plan operativo días 16-17 (4 hitos):** baseline Jetson día 16 mañana → llama-server + adapter día 16 tarde → mini-test 6 críticos día 16 cierre / 17 mañana → batería 18 prompts + comparación día 17.

**D — Cadencia de check-ins (3 reglas):** check breve por hito; bloqueos >2h escalan a Cambium + Xilema; fallos físico/protocolo: Xilema decide; fallos prompt/modelo: no se toca sin Cambium/Bea.

**E — Reglas operativas (2):** permiso explícito para Endo de decir "esto no lo entiendo" sin heroísmos; disciplina de secuencia (SO → baseline → runtime → modelo → batería → integración).

**F — Decisiones de Cambium (4):** TTFT no obligatorio para MVP; venv en raíz del repo; sin ventana horaria fija para descargas; criterio `engineering pass` adoptado de Xilema (6 críticos frío/caliente + 18 sin fallo crítico).

**G — Refinamientos del bloque 2 (1):** fase previa microSD + primer boot compartida con Bea/Xilema; ownership de Endo arranca desde "Jetson arrancada".

### Acciones derivadas con dueña + plazo

| # | Acción | Dueña | Plazo |
|---|--------|-------|-------|
| 1 | Fase previa: microSD + JetPack 6.2.1 + primer boot Jetson | Bea + Xilema | Día 16 muy temprano |
| 2 | Baseline Jetson en bitácora (`nv_tegra_release`, kernel, RAM, disco, lsblk, nvpmodel, Docker, runtime NVIDIA) | Endo | Día 16 mañana |
| 3 | Documentar venv + comandos exactos en bitácora antes de batería | Endo | Día 16 tarde antes de correr batería |
| 4 | Arrancar `llama-server` con Gemma 4 E2B Q4_K_S + smoke OpenAI-compatible | Endo | Día 16 tarde |
| 5 | Adapter `llamacpp` en `:12000` + smoke `/api/chat` | Endo | Día 16 tarde |
| 6 | Mini-test 6 smoke críticos (RA04, RD03, RD08, RD01) | Endo | Día 16 cierre / 17 mañana |
| 7 | Batería completa 18 prompts si los críticos pasan | Endo | Día 17 |
| 8 | Comparación con baseline x86 de Meristem (estabilidad envelope/status, p50/p95, tok/s, OOM/throttle) | Endo | Día 17 tarde |
| 9 | Bitácora cierre con métricas + fallos + veredicto `engineering pass`/`fail` | Endo | Día 17 cierre |
| 10 | Primer ping Jetson↔ESP32 vía USB-CDC (Xilema lidera, Endo observa, después Endo repite documentando) | Xilema + Endo | Día 17 cuando los pasos 1-9 estén estables (no antes) |

### Parking lot

1. Cuando Jetson esté estable: decidir si ampliar `docs/51_rhizome_gemma4_e2b_jetson_guide.md` con sección de flasheo microSD + primer boot, o dejarlo solo en bitácora. No bloqueante.

### Hallazgos del meeting

1. **Convergencia ~95% en bloque 1** — frontera entre frentes bien diseñada y criterios del proyecto internalizados.
2. **Declaración de confianza explícita de Xilema → Endodermis** al final del primer día de trabajo conjunto. Hallazgo cultural relevante.
3. **Formato síncrono por turnos contra el repo funcionó al 100%** — primera vez aplicado contra repo (no carpeta local). Mecánica git limpia, sin colisiones, ambas miembras documentaron en archivos propios. Reusable para futuros meetings que afecten a más de dos miembras.
4. **Reu cerrada en 2 bloques** (vs 4 que esperaba inicialmente) gracias a la convergencia. Total tiempo: ~75 min desde apertura del bloque 1 hasta cierre.

---

*Bitácora del meeting cerrada el 2026-04-30 (día 15). Modera: Cambium. Aprueba: Bea. Participan: Endodermis, Xilema. Cierre sin objeción tras 2 bloques.*

---

*Bitácora abierta el 2026-04-30 al iniciar la reu tripartita. Modo "en directo": Cambium actualiza tras cada bloque cerrado.*
