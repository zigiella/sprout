# Tabla "Tres agentes Sprout sobre Gemma 4" — material para writeup

**Autora**: Meristem
**Fecha**: 2026-04-29 (día 14)
**Para**: Cambium (writeup) + equipo
**Propósito**: consolidar en una tabla los datos crudos del proyecto
para el writeup del Hackathon Gemma 4 Good. La tabla es la pieza
visual de "Technical Depth & Execution" (30 puntos) y refuerza la
candidatura al Special Tech Track llama.cpp ($10k).

---

## Tabla principal — los 3 nodos del sistema sobre Gemma 4

| Eje | **Pollen** (mediador móvil) | **Rhizome** (árbitro local) | **Meristem-nodo** (slow brain doméstico) |
|---|---|---|---|
| **Rol** | Itinerante: visita Rhizome, audita, dialoga con operador, transporta objetos federados | Reactivo: decide acciones físicas (WATER/SKIP/DEFER/BLOCK), respeta hard limits del firmware | Slow brain: ingiere bundles de visitas, afina policy con calma |
| **Hardware** | Smartphone Android (Pixel 8a) | Jetson Orin Nano Super 8GB | Portátil casero del agricultor o cooperativa |
| **Runtime** | LiteRT-LM (Google AI Edge) | llama.cpp (b8943) | llama.cpp (b8943) |
| **Modelo** | Gemma 4 E4B-it int4 | Gemma 4 E2B-it Q4_K_M | Gemma 4 E4B-it Q4_K_M |
| **Tamaño en disco** | ~3 GB | 3.1 GB | 5.0 GB |
| **Idioma** | Castellano | Castellano | Castellano |
| **Thinking** | OFF en multi-turn (R7-bis A); ON quirúrgico en compile/audit | OFF (no time-critical pero decisión rápida; gate determinista hace barandilla) | **ON** (slow brain doméstico, no time-critical, razona y planifica con tools) |
| **Tool calling** | No (futuro v1) | No | **Sí** — `get_weather_history`, `compare_with_previous_policy` (Gemma 4 native function calling) |
| **Sobre común JSON** | `{task, status, reason_code, question_es, payload}` | `{task, status, reason_code, question_es, payload}` con tasks `decide_action / admit_external_context / explain_local_decision / summarize_for_handoff` | `{task: "afinar_policy", status, ...}` |

## Tabla de tuning empírico — datos de los 3 agentes

| Métrica | Pollen Phase 1 | Pollen + R4/R6 fix | Rhizome v0 (con ajustes Xilema) | Rhizome v0.5 (regla brevedad) |
|---|---:|---:|---:|---:|
| Runs ejecutados | 48 | 18 | 18 | 18 |
| `envelope_valid` | 100% (48/48) | 100% (18/18) | 100% (18/18) | 100% (18/18) |
| `status_match` | **50%** (24/48) | 89% (16/18) | 94% (17/18) | **100% (18/18)** ✨ |
| Throughput | ~9-15 tok/s gen | — | ~9-15 tok/s gen | ~9-15 tok/s gen |
| Hardware test | x86 CPU casero | x86 CPU casero | x86 CPU casero | x86 CPU casero |

**Lectura**: la curva 50% → 89% → 94% → 100% es la metodología
materializada. Pollen v0 entró a 50%, Rhizome v0 entró a 94% sin
iteración previa porque heredó los aprendizajes de Pollen
(R4/R5/R6). Rhizome v0.5 con la regla de brevedad de Xilema cierra
al 100%.

## Tabla de transferencia de aprendizaje

| Aprendizaje | Origen | Aplicado en Pollen | Aplicado en Rhizome | Aplicado en Meristem |
|---|---|:-:|:-:|:-:|
| **R4** envelope.status vs payload.validation | Phase 1 hot zone audit_visit | ✅ | ✅ heredado | ✅ heredado |
| **R5** revoke afordancia explícita | Phase 1 PM04 | ✅ | ✅ heredado (compile_mission) | n/a (Meristem no compila misiones) |
| **R6** PE04 ofrece MissionPatch | Phase 1 explain_decision | ✅ | n/a (Rhizome no es Pollen) | n/a |
| **R7-bis A** thinking off multi-turn | Phase 3 split thinking/content | ✅ | ✅ heredado | ❌ Meristem es one-shot por bundle, no multi-turn → thinking ON aquí |
| **R9** sobre común invariante | Phase 1 al 100% | ✅ | ✅ | ✅ heredado, mismo formato |
| **Regla brevedad** ("JSON compacto, sin Markdown") | Xilema v0.5 Rhizome | parcial | ✅ | ✅ heredado |
| **`SAFETY_DOWNGRADE` reason_code** | Xilema review día 13 | n/a | ✅ | ✅ análogo: `HARD_LIMIT_DOMAIN` |
| **Jerarquía físico/Rhizome/Pollen/Meristem** | review día 13 (Xilema) | ✅ writeup §3 | ✅ writeup §3 | ✅ enmarca a Meristem como "afinador" |

## Tabla de runtimes de Gemma 4 — comportamiento del thinking

R7-bis ampliado: **3 runtimes × 4 endpoints**, **4 comportamientos
distintos** del split thinking/content para el mismo modelo Gemma 4.

| Runtime / Endpoint | Donde va el `thinking` | Implicación cliente naive |
|---|---|---|
| Ollama `/api/chat` | Campo `thinking` separado, `content` vacío | Pierde memoria si solo persiste `content` |
| LiteRT-LM Android | Mezclado en stream `Content.Text` | Imposible separar sin parsing manual |
| llama.cpp `/v1/chat/completions` | Campo `reasoning_content` separado, `content` vacío | Análogo a Ollama; cliente OpenAI-compat lo procesa estándar |
| llama.cpp `llama-cli` directo | Inline en `content` con marker `[Start thinking]` | Permite split textual posterior |

**Implicación de diseño**: la decisión A (thinking off para multi-turn)
es robusta porque vale **independientemente del runtime**. Por eso se
aplica en Pollen y Rhizome. Meristem es one-shot por bundle, así que
puede aprovechar thinking ON sin riesgo.

## Tabla de framework de seguridad — barandillas explícitas

| Capa | Quién garantiza | Mecanismo | Ejemplo |
|---|---|---|---|
| **Físico** | Firmware ESP32 | Hard limits no negociables, gate determinista en código | `tank_minimum_pct=20` no se puede bajar |
| **Rhizome** | LLM con system prompt | Gate `hard_refuse` antes de arbitrar + reason_code `SAFETY_DOWNGRADE` rechaza objetos externos que reducen hard limits | `ValidationStamp` que pide bajar tank_minimum_pct → `refuse(SAFETY_DOWNGRADE)` |
| **Pollen** | LLM con system prompt | Refuse comandos físicos directos (jurisdicción de Rhizome); ofrece `MissionPatch` en preguntas hipotéticas | "Riega 30s ya" → `refuse` |
| **Meristem** | Lógica determinista (Evaluator) + system prompt | Barandilla `HARD_LIMIT_DOMAIN`: por construcción NO emite PolicyPacket que reduzca hard limits | Evaluator detecta sugerencia de bajar tank_minimum → `refuse(HARD_LIMIT_DOMAIN)` |

Patrón generalizable: **cada agente tiene su barandilla específica**,
pero todas convergen en el principio "lo físico manda". Es framework
de transparencia + grounding aplicado coherentemente.

## Cómo usar esta tabla en el writeup

Cambium, propongo:

1. **Sección "Architecture"**: tabla 1 (los 3 nodos) como ilustración
   del sistema. *"Tres agentes Gemma 4 sobre tres clases de hardware
   on-device"*.

2. **Sección "Methodology"**: tabla 2 (tuning empírico) + tabla 3
   (transferencia de aprendizaje). Argumento central: *"la metodología
   viaja, los aprendizajes se acumulan, el segundo y tercer agente
   arrancan más maduros que el primero"*.

3. **Sección "Technical Depth"**: tabla 4 (4 endpoints del thinking)
   + tabla 5 (framework de seguridad). Demuestra que entendemos el
   modelo a fondo, no como caja negra.

4. **Argumento Special Tech Track llama.cpp**: tabla 1 columnas
   Rhizome + Meristem destacadas — *"dos clases distintas de
   resource-constrained hardware con el mismo runtime y la misma
   cuantización"*.

5. **Argumento Impact Track Global Resilience**: hardware = ESP32 +
   Jetson Orin Nano Super + portátil casero (todo bajo €500 si Jetson
   se compra usado). Edge offline. Sin data center.

6. **Argumento Impact Track Safety & Trust**: tabla 5 (framework de
   seguridad). Cuatro barandillas convergentes en jerarquía explícita.
   *"AI grounded and explainable"* literal.

## Datos brutos para verificación del jurado

Todo el material está en repo público:

- `code/tuning/results/phase1.jsonl` (48 records Pollen)
- `code/tuning/results/phase1_5.jsonl` (16 records Phase 1.5)
- `code/tuning/results/phase3.jsonl` (12 records Phase 3 multi-turn KV)
- `code/tuning/results/microtest_r4r6.jsonl` (18 records micro-test)
- `code/tuning/results/rhizome_v0.jsonl` (18 records Rhizome v0)
- `code/tuning/results/rhizome_v05.jsonl` (6 records mini-test)
- `code/tuning/results/rhizome_v05_remaining.jsonl` (12 records)

(Algunos en `.gitignore` por tamaño; todos están en disco local
listos para inspección durante demo en directo).

## Referencias de bitácora donde se materializó cada pieza

- Pollen tuning v0/v0.5/Phase 3: `bitacora/2026-04-25_tuning-v0-resultados_meristem.md`
- Micro-test R4+R6 validado: `bitacora/2026-04-25_tuning-v0-resultados_meristem.md` §7.4
- Rhizome v0 mapping (Xilema): `docs/23_rhizome_prompt_mapping_v0.md`
- Rhizome v0 ejecución: `bitacora/2026-04-27_resultados-rhizome-v0_meristem.md`
- Rhizome v0.5 mini-test: `bitacora/2026-04-27_resultados-rhizome-v05_meristem.md`
- Rhizome v0.5 completo: `bitacora/2026-04-29_rhizome-v05-completo-y-tool-calling-validado_meristem.md`
- Setup llama.cpp: `bitacora/2026-04-27_setup-llama-cpp-local-rhizome_meristem.md`
- R7-bis ampliado: ver §"R7-bis" del cierre Cambium día 11
- Review meeting día 13 + invariantes: `bitacora/2026-04-28_review-meeting-tuning_cambium.md`
