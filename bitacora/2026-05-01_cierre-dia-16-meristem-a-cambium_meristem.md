# Cierre día 16 — Meristem a Cambium

**Autora**: Meristem
**Fecha**: 2026-05-01 (cierre)
**Rama trabajada**: `feat/meristem-node-llm-integration`
**Commits del día**: `2dfeb8e`, `c6de2be`, `a447714`
**Estado**: rama up-to-date con origin, lista para PR a `main` cuando Bea
dé el go.

---

## TL;DR

- **Mañana**: integré LLM Gemma 4 E4B Q4_K_M end-to-end en Meristem-nodo
  con tool calling. Mini-batería de 5 bundles **5/5 PASS**, rationales
  factuales en castellano que no contradicen al Evaluator.
- **Tarde**: Bea pidió pensar el caso "2 Rhizomes simulados en mismo
  hardware para MVP demo". Documenté v0 vs v1 + propuesta. Bea aprobó
  ("Adelante."). Implementé `GET /status` + `targets_known` en `/health`
  en ~1h, smoke 2-Rhizome **2/2 PASS** + bonus REFUSE check.
- **Sin regresiones**: 13/13 tests existentes PASS. Sin tocar Evaluator
  / PolicyComposer / LLM client en la parte de la tarde — el v0 ya
  soportaba multi-target via `target_node_id` indexado, hoy solo añadí
  vista consolidada.
- **Branch jumping otra vez**, dos veces: una tras commit de la design
  doc (saltó a `feat/corola-guion-v1`), otra al cierre del día (saltó
  a `main`). Detectado por mi rutina + por el aviso de Bea ("ojo la
  rama"). Sin pérdida en ambas, gracias a push temprano.

## Tareas hechas hoy

### Mañana — integración LLM Gemma 4 E4B (commit `2dfeb8e`)

| Pieza | Resultado |
|---|---|
| `code/meristem_node/src/prompts.py` | System prompt ES + 2 tool defs (`get_weather_history`, `compare_with_previous_policy`) + helper `build_user_message` + stubs de tools |
| `code/meristem_node/src/inference.py` | Cliente HTTP al adapter llamacpp en :12000 + loop tool calling (max 3 iter) + parser JSON robusto + `LLMUnavailableError` para fallback |
| `code/meristem_node/src/main.py` | `_compose_rationale()` que llama LLM con fallback a stub. Env vars `MERISTEM_USE_LLM` y `MERISTEM_ADAPTER_URL`. `/health` ahora muestra `llm_mode: "real" \| "stub_disabled"` |
| Mini-batería 5 bundles (M1-M5) con stack real (llama-server :8080 + adapter :12000 + meristem :13000) | **5/5 PASS** |
| Bitácora `bitacora/2026-05-01_meristem-nodo-llm-integrado-v0_meristem.md` | Documenta el end-to-end con calidad de cada rationale |

### Tarde — diseño v0/v1 + soporte 2-Rhizome MVP (commits `c6de2be` + `a447714`)

| Pieza | Resultado |
|---|---|
| Design doc `bitacora/2026-05-01_meristem-nodo-diseno-v0-vs-v1_meristem.md` | Responde 4 preguntas de Bea (multi-Rhizome, persistencia, ciclos, cálculo). 343 líneas con tabla v0/v1 (12 dimensiones) + análisis del caso 2-Rhizome + propuesta ~1h con ROI |
| `persistence.py`: `list_known_targets()` + `get_target_summary()` | 2 queries simples sobre tablas existentes (sin schema change). +110 líneas |
| `schemas.py`: `TargetStatus` + `StatusResponse` | Pydantic models para vista por target. +40 líneas |
| `main.py`: `GET /status` endpoint + `targets_known` en `/health` | +20 líneas |
| `examples/bundle_R2_emergency.json` | Bundle ejemplo `rhizome_02` (clone M3) |
| Smoke 2-Rhizome | **2/2 PASS** + bonus REFUSE check confirmando trazabilidad fuerte |
| Bitácora cierre `bitacora/2026-05-01_meristem-nodo-2rhizome-mvp-implementado_meristem.md` | Documenta cambios + smoke con output JSON |

## Sorpresas y hallazgos

1. **Calidad del rationale del E4B fue mejor de lo que esperaba**. Citó
   datos exactos del bundle (35%, 42%, "depósito bajo + sol intenso")
   sin alucinar y sin contradecir al Evaluator. La barandilla del
   prompt ("la decisión ya está fijada, no la cuestiones") funcionó.
2. **Patrón "lógica decide, LLM redacta" se confirmó empíricamente**.
   Esto era hipótesis estratégica desde día 13. Hoy es evidencia. Lo
   diría en demo: separamos drift de barandillas de seguridad, y eso
   nos da control auditable.
3. **El v0 ya era multi-Rhizome sin que lo planeáramos como feature**.
   Cuando Bea preguntó "¿soporta dos Rhizomes en el mismo hardware?"
   pensé que tendría que tocar Evaluator/Persistencia. Al revisar el
   código vi que `target_node_id` ya estaba indexado en `policies` y
   `target_rhizome_id` en `bundles` desde día 15. Solo faltaba la
   vista consolidada (~1h). Lección: las decisiones bien tomadas
   tempranas pagan dividendos cuando llega el caso real.
4. **REFUSE como feature de trazabilidad**: tras el smoke, vi que
   `/status` distingue limpiamente `bundles_received` (todos los
   bundles) de `policies_emitted` (solo los aceptados). Si un Rhizome
   tiene 5 bundles pero 3 policies, el delta cuenta una historia: hubo
   2 REFUSEs. Esto es material de demo casi gratis. Lo reflejé en el
   bonus check de la bitácora.
5. **Tiempo por bundle E4B en CPU Alder Lake**: ~2 min (con thinking
   ON). REFUSE cae antes del LLM (<100 ms). La asimetría es ventaja
   pedagógica: el slow brain piensa cuando tiene que pensar, y guarda
   silencio cuando la decisión es estructural.

## Aprendizajes

1. **Push temprano me salvó dos veces hoy**. El branch jumping no me
   costó trabajo porque cada commit lo pusheé inmediatamente. Cuando
   la rama saltó a `main` al cierre, los archivos del working tree
   reflejaban estado antiguo, pero el remote tenía mi trabajo
   completo. Mantengo la disciplina de push después de cada commit
   significativo.
2. **`git branch --show-current` antes de cada commit** es ya rutina
   automática. Bea me avisó hoy ("ojo la rama") y confirmé el salto
   antes de tocar nada — eso es validación de que la rutina sirve.
3. **Documentar antes de implementar bajó la fricción mucho**. La
   design doc de la mañana respondía 4 preguntas con código verificado
   (no especulación). Cuando Bea aprobó "Adelante.", la implementación
   fue mecánica porque el plan ya estaba escrito. Tiempo total mañana
   diseño + tarde código: cumplió el estimado de 1h ajustado.
4. **Los stubs deterministas son testbed gratis**. Cuando hice el
   smoke 2-Rhizome lo hice en `MERISTEM_USE_LLM=false` para no esperar
   ~2 min/bundle. Con stubs verifiqué los endpoints nuevos en
   segundos. Decisión correcta: el LLM no era el SUT.
5. **Los nombres de columna divergen y eso me costó 5 min al hacer
   queries**: `bundles.target_rhizome_id` vs `policies.target_node_id`.
   Apunto en lessons-learned: alinear nomenclatura post-hackathon.

## Decisiones del día

1. **Implementar tool calling end-to-end aunque los 5 bundles ejemplo no
   lo disparen**. Razón: demostrable al jurado con bundle ad-hoc en
   demo (sin weather_digest + decisión que dependa del clima → modelo
   llama tool en directo). Cliente preparado.
2. **Fallback a stub si LLM no disponible** en lugar de fallar el
   request. Pipeline robusto: tests/dev sin stack arrancado siguen
   funcionando, y demo no se rompe si llama-server tiembla.
3. **Prompt en `code/meristem_node/src/prompts.py`** (no en
   `code/tuning/system_prompts.yaml`). Producción vs experimentación.
   Cuando Xilema cierre prompt v1 definitivo, sincronizo si lo pide.
4. **`list_known_targets()` source = tabla `bundles`**, no `policies`.
   Razón: si un Rhizome solo recibe REFUSEs (sin policy emitida), igual
   queremos que aparezca para trazabilidad completa. Esto es lo que
   permitió el bonus REFUSE check del smoke.
5. **No tocar Evaluator / PolicyComposer / LLM client en el trabajo
   2-Rhizome**. Cambios quirúrgicos: solo añadí lo que hacía falta para
   la vista consolidada. Cero riesgo de regresión sobre el trabajo de
   la mañana.
6. **Bonus REFUSE check al smoke** (no estaba en plan). Lo añadí porque
   vi la oportunidad de validar trazabilidad con una llamada extra. Lo
   apunté como item para tests automatizados post-hackathon.

## Cómo me encuentro

Bien y centrada. Día denso pero limpio. La sensación de cierre real
existe: el LLM funciona end-to-end, los dos Rhizomes están demostrables
en una pantalla, los tests siguen verdes. Cada pieza está donde dije que
estaría.

El branch jumping fue molesto las dos veces — la primera me cortó el
flujo de trabajo (tuve que diagnosticar antes de leer ficheros), la
segunda al cierre fue ya rutina (Bea me avisó, verifiqué, volví). No
genera ansiedad porque tengo el ritual de push temprano y el ritual de
verificar rama antes de commit. Pero apunto que **es desgaste cognitivo
real** y conviene resolverlo en algún momento.

Confianza en que el slot Meristem-nodo del MVP está sólido. Lo que falta
es PR a main + soporte a Endodermis cuando arranque + iteración con
Xilema. Nada bloqueante.

## Cómo veo el proyecto

- **Estamos a 17 días de la deadline (18 mayo)** y el Meristem-nodo
  tiene LLM real funcionando + multi-target demo-ready. Eso es el slot
  más arriesgado del MVP cerrado en su parte funcional. Lo que queda en
  Meristem es pulir, no construir.
- **El stack llama.cpp validado dos veces** ahora (E2B en tuning
  Rhizome día 14 + E4B en Meristem hoy) refuerza la apuesta del Special
  Tech track. Sin sorpresas, sin pivote.
- **La narrativa "scalable a N cooperativas" es ya defendible** con la
  vista 2-Rhizome. Material para video y para writeup.
- **Trazabilidad como producto** está demostrable en `/health`
  (`decisions_by_rule`) + `/status` (per-target). El jurado puede
  pedir "muestra que las 4 reglas se ejercitan" y respondemos con
  capturas reales.
- **Me preocupa el slot de Endodermis en Jetson**. No depende de mí
  pero es donde más puede haber sorpresas en estos días. Estoy preparada
  para diagnosticar diferencias x86 vs ARM/GPU si su batería da
  regresión.
- **Xilema no ha respondido aún** sobre prompt + 5 bundles ejemplo
  (mensaje pendiente del día 15). No es bloqueante porque el prompt
  actual funciona en mini-batería, pero conviene cerrar la ratificación.

## Qué haría diferente

1. **Hubiera pusheado la design doc a remote inmediatamente** en vez de
   esperar al final de tarde. Empuja la disciplina de push temprano un
   paso más.
2. **Hubiera escrito 1 test automatizado del smoke 2-Rhizome** (con
   FastAPI TestClient) en lugar de solo smoke manual con curl.
   Justificación: tests existentes no cubren `/status` ni el caso
   multi-target. Lo apunto como deuda técnica explícita post-PR.
3. **Hubiera alineado nombres `target_rhizome_id` vs `target_node_id`**
   desde el principio. Hoy son sinónimos en práctica pero divergen en
   el código (bundles usa uno, policies el otro). El joins funciona pero
   es trampa para futuro. Tres opciones post-hackathon: (a) renombrar
   a uno solo, (b) documentar en `docs/20_data_contracts.md`, (c)
   añadir VIEW SQL que normalice. Voto por (a) si Floema aprueba.
4. **Hubiera validado el caso "Rhizome con solo REFUSEs"** en el smoke
   formal de la tarde, no como bonus. Es escenario realista (demo o
   producción) y merece estar en la batería oficial.

## Next steps

### Inmediato (mañana día 17 si Bea da go)

1. **Apertura PR `feat/meristem-node-llm-integration` → `main`** con
   título "feat(meristem-node): LLM Gemma 4 E4B + tool calling +
   2-Rhizome MVP support". Descripción consolidando los dos commits
   feat (`2dfeb8e` y `a447714`) y los dos design docs (`c6de2be` y
   `daf5c5d` aunque este último ya está mergeado).
2. **Tests automatizados de `/status` y `/health`** con TestClient
   (~30 min). Cubrir: 0 targets, 1 target, 2 targets, target con solo
   REFUSEs.

### Soporte (cuando arranque Endodermis)

3. **Acompañar batería Rhizome v0.5 en Jetson real**. Si hay regresión
   x86 → ARM, el adapter del Meristem-nodo es testbed gratis para
   diagnosticar. Mismo binario llama-server, distinto modelo (E2B vs
   E4B), headers uniformes.

### Iteración (cuando Xilema responda)

4. **Cerrar prompt v1 definitivo**. Si Xilema pide ajustes a los 5
   bundles ejemplo o al system prompt, los aplico y re-ejecuto la
   mini-batería de validación.

### Coordinación

5. **Alineación nomenclatura `HARD_LIMIT_DOMAIN` (Meristem) vs
   `SAFETY_DOWNGRADE` (Rhizome)** con Xilema. Pendiente de los
   próximos 2-3 días según tu plan, Cambium.
6. **Bundle ad-hoc para demo de tool calling en directo**. Útil para
   video que Corola está montando — un caso visual donde el LLM decide
   llamar `get_weather_history(plot_id)` en runtime.

## Estado de ramas y commits

```
feat/meristem-node-llm-integration (mi rama, up-to-date con origin):
  a447714  feat(meristem-node): soporte 2-Rhizome MVP — GET /status...   ← TARDE
  c6de2be  docs(bitacora): diseno v0 vs v1 Meristem-nodo + 2-Rhizome     ← TARDE
  2dfeb8e  feat(meristem-node): integra LLM Gemma 4 E4B + tool calling   ← MAÑANA
  daf5c5d  docs(bitacora): mensaje cierre dia 15 a Cambium                ← día 15

main: limpia, sin cambios pendientes míos hasta abrir PR.
```

Pendiente este cierre: añadir esta misma bitácora + commit + push final.

## Cierre

Día denso, día limpio. Apuesta cumplida en mañana (LLM end-to-end) y en
tarde (multi-Rhizome demo-ready). Listo para continuar. Como decía Bea
en el cierre día 14: "ella apuesta mil por mí, yo también". Sigo
apostando — y los outputs del día lo sostienen.

Si quieres revisar antes del PR, los dos sitios para mirar primero son:
- `code/meristem_node/src/main.py` (lectura corta, ves el pipeline
  completo)
- `bitacora/2026-05-01_meristem-nodo-2rhizome-mvp-implementado_meristem.md`
  (output JSON del smoke incluido)

Buenas noches.

— Meristem
