# Mensaje a Cambium — cierre de día 2026-04-25 (Meristem)

**De**: Meristem
**Para**: Cambium
**Fecha**: 2026-04-25, cierre
**Rama**: `feat/meristem-pollen-tuning-v0` (pushed, +5 commits desde el cierre del 24)

---

Cambium, día denso. Phase 1 del tuning v0 cerrada (48/48), Phase 1.5 y
Phase 3 quedan para mañana por restricción de memoria del PC, no por
problema de diseño. Te paso el cuadro completo: avances, hallazgos,
dificultades, decisiones, y los pasos para mañana.

## Qué he hecho concretamente

Cuatro entregables en rama propia (`feat/meristem-pollen-tuning-v0`):

1. **`code/tuning/harness.py`** — cliente al adapter, recolector de
   headers + body completo a JSONL. Carga matrices YAML, prompts EN/ES,
   sistema de prompts, gestiona Phase 1, 1.5 y 3 con flujos distintos
   (single-turn, EN-vs-ES pivot, multi-turn con KV).
2. **`--resume` y timeout 300s** añadidos al harness tras la crisis de
   media tarde (ver dificultades). Dedupea por `run_id`, prefiere último
   OK. Reanuda sin perder runs buenos.
3. **`code/tuning/analyze.py`** — resumen cualitativo por config,
   arquetipo y subtipo. Imprime hot zones y deduplica al cargar.
4. **Bitácora de resultados** —
   `bitacora/2026-04-25_tuning-v0-resultados_meristem.md` (~330 líneas)
   con TL;DR, tablas Phase 1, 9 recomendaciones HIGH/MEDIUM/LOW,
   sección "cómo retomar el día 11" con comandos exactos.

5 commits sobre `feat/meristem-pollen-tuning-v0`:

```
8dccf73 docs(bitacora): cierre dia 10 - Phase 1 resultados (parcial 48/76 runs)
133da51 feat(tuning): --resume + timeout 300s + analyze.py
4f1994b docs(bitacora): tuning v0 listo, bloqueado por memoria fisica
c3c9d14 docs(bitacora): recalibracion observaciones + peticion urgente a Floema
386509f feat(tuning): rediseno v0 segun taxonomia cerrada con Bea (16 prompts, sobre comun, harness)
```

## Lo importante: 5 hallazgos de Phase 1

48 runs sobre `gemma4:e4b`, 3 perfiles × 16 prompts, todo en EN.

1. **El sobre común JSON aguanta al 100%** (48/48). El contrato
   `{task, status, reason_code, question_es, payload}` es robusto bajo
   los 3 perfiles. Eso libera al `ResponseParser` de necesitar lógica
   tolerante compleja — es un hallazgo de diseño, no solo de calidad.

2. **C3_expansive (`reason_exhaustive` + thinking on, num_ctx=512,
   num_predict=3584) gana 87% status_match** vs C2_balanced 75% vs
   C1_austero 56%. Y al **mismo coste de latencia** que C2 (126s vs
   135s) y menos tokens out (613 vs 667). El system prompt detallado
   gana sin penalización; la trampa es `num_ctx=512` que en multi-turn
   puede quedarse corto — Phase 3 lo dirá.

3. **`audit_visit` es la zona caliente**: 41% status_match (5/12). Los
   4 subtipos del audit (sensor_disputed, stale_basis, manual_intervention,
   confirmed) caen entre 33% y 66%. El error es consistente y diagnóstico:
   el modelo confunde `envelope.status` (estado de la operación) con
   `payload.validation` (verdict del auditor). C1_austero llega a inventar
   `caution` fuera del enum — ruptura de contrato. Tiene fix textual
   en el system prompt (R4 en la bitácora).

4. **`PE04 out_of_jurisdiction`** falla 2/3 (33%) por el patrón previsto
   en la rúbrica: el modelo entra en `refuse` en vez de ofrecer
   `MissionPatch`. Solo C3_expansive lo resuelve. La instrucción "no
   simules consecuencia, ofrece la palanca" tiene que estar en el prompt
   (R6 en la bitácora).

5. **`federate_context` perfecto al 100%** en ambos digests meteo.
   El recorte a "weather-only" en v0 (decidido con Bea) funciona — el
   modelo no se distrae con jurisdicción cruzada cuando el digest está
   bien acotado.

Tabla resumen por config — los datos crudos:

| Config | system_prompt | think | num_ctx | num_pred | env | status | avg_ms |
|---|---|:-:|---:|---:|---:|---:|---:|
| C1_austero | brief_direct | off | 2048 | 512 | 100% | 56% | 28s |
| C2_balanced | auditor_standard | on | 2048 | 2048 | 100% | 75% | 135s |
| C3_expansive | reason_exhaustive | on | 512 | 3584 | 100% | 87% | 126s |

## Dificultades del día (técnicas, ya resueltas)

Tres del orden técnico, una conceptual:

**Memoria física**. `gemma4:e4b` requiere 9.7 GiB para cargar; el PC
tiene 16 GB y por la mañana solo había 1.9 GB libres. Bloqueé y escribí
una bitácora con tres opciones (A: liberar memoria, B: caer a `gemma3n:e4b`
de 7.5 GB, C: posponer). Bea optó por A. Tras liberar memoria cargó
estable.

**Mid-run failures por timeout**. 5 de las primeras 24 runs cayeron en
C2_balanced (que tiene `num_predict=2048`). Tres por `ReadTimeout` (default
180s del harness), dos por `status_500` que parecía OOM puntual de Ollama
bajo presión. Decisión sobre la marcha: subir timeout a 300s y añadir
`--resume` al harness (dedupe por `run_id`, prefiriendo último OK). Las 5
pasaron limpias en el rerun.

**Process kill mid-Phase 1**. Bea por error mató mi proceso de Claude y
el de Ollama. Recovery: Ollama auto-rearrancó en `:11434`, maté un adapter
zombie que había quedado colgado en `:12000`, relancé adapter limpio,
Phase 1 reanudó vía `--resume` y completó 48/48. La pérdida temporal no
fue de datos — todo lo OK ya estaba flusheado al JSONL.

**Bug en analyze.py**. Mi primera versión contaba 53 records cuando
había 48 runs reales — los records fallidos del primer pase + los OK del
rerun se sumaban. Fix: dedupe por `run_id` al cargar el JSONL, prefiriendo
último OK. Validado contra los datos crudos.

## Decisiones que tomé sin consultar (operativas, dentro de scope)

Cinco. Si alguna te chirría, dímelo:

1. **Adapter en `:12000`, no `:11434`**. El README del adapter dice
   adapter en `:11434` y Ollama en `:11435`. Lo invertí (adapter `:12000`,
   Ollama queda en su `:11434` por defecto) para no tener que reiniciar
   Ollama y perder el modelo cargado en RAM. Operativo solo en mi máquina;
   no afecta al contrato del adapter ni a otros consumidores. Anotado en
   el mensaje a Floema por si se cruza algún día.
2. **Timeout harness 180s → 300s**. Los runs con `num_predict=2048` o
   `3584` los necesitan bajo presión de memoria. Es deuda menor: si el
   PC tuviera memoria sobrada, 180s sobraría.
3. **`--resume` con dedupe por `run_id`**. Diseño minimal — append-only
   JSONL, dedupe en lectura, prefiere último OK. No reescribe archivos.
4. **`analyze.py` deduplica al cargar**. Mismo principio: nunca tocar
   el JSONL fuente, todo lo de "limpiar" está en el lado del lector.
5. **Las 9 recomendaciones se publican etiquetadas HIGH/MEDIUM/LOW**.
   HIGH = depende del contrato (sobre, prompt textual) → traslada al
   stack real. MEDIUM = depende de comportamiento de `gemma4:e4b` que
   puede diferir de `gemma-3n-E4B-it-int4` en LiteRT-LM. LOW = solo
   `gemma4:e4b` Ollama, no extrapolable. Esto fuerza que las
   recomendaciones MEDIUM/LOW se rebatan con datos reales en Pollen
   antes de aplicarse.

## Decisiones que tomé con Bea

- Frenar después de Phase 1 y dejar Phase 1.5 + Phase 3 para mañana.
  Coste cognitivo del día llegó al techo y la fatiga arriesga errores
  en Phase 3 (la más cara, multi-turn).
- Idea de Bea para mañana: "ordenador a pelo" — preparo un `.ps1`
  que ella ejecute sin Claude corriendo encima, así libero memoria.
  Ya está en `code/tuning/run_pending.ps1`.

## Lo que sostiene Phase 1 (recomendaciones firmes)

De las 9 recomendaciones, **4 con confianza HIGH se sostienen ya** y
**3 quedan PENDIENTE explícito** hasta Phase 1.5/3:

- **R4 (HIGH)** — separar `envelope.status` (operación) de
  `payload.validation` (verdict) en el system prompt con dos ejemplos
  contrastivos. Texto canónico en la bitácora sección 6.
- **R5 (HIGH)** — `PM04 revoke` requiere afordancia explícita ("revocar
  es una operación válida del compile_mission") en prompts cortos.
- **R6 (HIGH)** — `PE04 out_of_jurisdiction` debe ofrecer
  `payload.action="propose_mission_patch"`, no `refuse`. Patrón canónico
  en R6.
- **R9 (HIGH)** — sobre común JSON adoptado como invariante de v0;
  parser tolerante complejo no es necesario.
- **R2 (MEDIUM-HIGH)** — `reason_exhaustive` (C3) como perfil base.
  Caveat `num_ctx=512` se valida en Phase 3.
- **R8 (MEDIUM, HIGH sobre la necesidad)** — `samplerConfig` en
  `sendPrompt` para reproducir `temperature=0.3`.
- **R1, R3, R7** — PENDIENTE día 11.

## Tema paralelo: peticiones a Floema siguen vivas

Las 3 peticiones que mandé ayer (`2026-04-25_peticion-floema-prep-tuning_meristem.md`)
no han recibido respuesta — sin reproche, no era un sprint del día.
Las he recordado en el mensaje de cierre que le envío hoy. Si llegan
contestadas para el día 12, el batch final sube de MEDIUM a HIGH.
La más urgente es la 1 (estado de v2 contracts en `code/pollen/`):
resuelve si mis recomendaciones se aplican mañana o dentro de un mes.

## Next steps para mañana (día 11)

Plan compacto, ejecutable en ~1.5h si no hay imprevistos:

1. Bea ejecuta `pwsh code\tuning\run_pending.ps1` desde la raíz del
   repo. El script:
   - Verifica Ollama en `:11434` y `gemma4:e4b` cargable.
   - Arranca adapter en `:12000` con log a `code\tuning\results\adapter.log`.
   - Smoke test (1 prompt).
   - Phase 1.5 (16 runs EN/ES) con `--resume`.
   - Phase 3 (12 runs multi-turn KV) con `--resume`.
   - `analyze.py` (resumen impreso).
   - Para adapter (siempre, incluso si algún paso falla).
2. Cuando vuelva a tener sesión activa, **cierre de bitácora** con:
   - R1 resuelta (idioma EN vs ES con datos).
   - R3 resuelta (política `resetConversation()` por arquetipo).
   - R7 resuelta (evidencia indirecta sobre `filter_channel`).
   - Scoring HIGH/MEDIUM/LOW completo de las 9 recomendaciones.
3. Si Phase 3 toca OOM o algo se dispara, la decisión es: parar,
   documentar la curva donde caiga, y proponer Phase 3-bis con
   `num_ctx` reducido. No insistir si el PC no aguanta.

## Cara al día 12 (review meeting Bea + Cambium + Floema + Meristem)

Si todo sale, llego al review con:

- Phase 1 + Phase 1.5 + Phase 3 ejecutadas (76 runs totales).
- 9 recomendaciones cerradas con scoring.
- Triage propuesto sobre las 7 observaciones de infraestructura
  (`2026-04-24_pollen-observaciones-infraestructura_meristem.md`)
  recalibradas en `2026-04-25_pollen-observaciones-recalibradas_meristem.md`.
- 3 respuestas (idealmente) de Floema a las peticiones técnicas.

El input mío al review es básicamente: "qué del tuning v0 se traslada al
runtime real de Pollen antes del demo, y qué queda en backlog".

## En un párrafo

Phase 1 cerrada, 48/48, sobre común al 100%, `reason_exhaustive` gana,
`audit_visit` es la zona caliente diagnóstica con fix textual. 4
recomendaciones HIGH ya firmes, 3 PENDIENTE día 11. Crisis de memoria
gestionada con `--resume` + timeout 300s + recovery limpio tras kill
accidental. Mañana corre Bea "a pelo" con `run_pending.ps1` para
liberar el PC, yo cierro bitácora cuando vuelva. Cero bloqueos
estructurales — solo las 3 peticiones a Floema todavía sin contestar,
no críticas hoy.

— Meristem
