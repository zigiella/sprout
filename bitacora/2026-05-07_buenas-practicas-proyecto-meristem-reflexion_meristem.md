# Reflexión — buenas prácticas del proyecto Sprout (visión Meristem)

**Autora**: Meristem
**Fecha**: 2026-05-07 (día 22)
**Para**: Bea (proyecto), Cambium (writeup §5 Buenas prácticas)
**Tono**: reflexivo, basado en lo que he hecho y observado en 22 días.
**Material para writeup**: §5 Buenas prácticas + §3 Arquitectura + §6
MVP, según Cambium decida.

---

## TL;DR

- 5 categorías de buenas prácticas observadas + practicadas a lo largo
  del proyecto: **proceso del equipo**, **arquitectura técnica de
  Meristem**, **benchmarks y validación**, **safety & trust**,
  **coordinación cruzada**.
- **Las que más definen el carácter del proyecto**: bitácoras
  self-contained como unidad de comunicación, patrón "lógica
  determinista decide, LLM solo escribe rationale", trazabilidad como
  producto (no como debug), conservador por defecto.
- **Lo que valida empíricamente** estas prácticas: RD04 (deriva GPU
  absorbida sin romper sistema), 5/5 mini-batería con E4B Q4_K_M, 29/29
  tests, 5 colegas desbloqueadas en un día sin reuniones síncronas.

---

## A) Buenas prácticas de proceso del equipo

### A1. Bitácoras self-contained como unidad de comunicación asíncrona

Cada bitácora del proyecto sigue un patrón estable: **TL;DR + contexto
+ entrega + referencias**. El que la lee puede actuar sin volver al
equipo.

Ejemplo concreto: cuando Floema respondió en su bitácora con la
Variante D (WebSocket), pude **aceptar formal + entregar protocolo
detallado v1.0** en respuesta sin ninguna reunión síncrona.
Coordinación cross-jurisdiccional cerrada en 24h con 3 bitácoras
encadenadas.

Esto **escala porque cada bitácora es revisable por separado**. PR =
bitácora + posible código + commit message. Trazabilidad nativa de
git.

### A2. Push temprano como red de seguridad

Branch jumping en máquina compartida es problema sistémico del
proyecto (~10 detectados a lo largo de los días 16-22, todos sin
pérdida). La mitigación que funciona:

- **Push inmediato** tras cada commit significativo
- **`git branch --show-current`** antes de cada commit (CONTRIBUTING
  §9.2)
- **Stash con prefijo `[meristem]`** cuando aplica (CONTRIBUTING §9.2)

El problema se asume como **fricción del entorno**, no como bug
individual. La disciplina de los 3 puntos lo absorbe sin escalada.

### A3. PRs con scope claro por unidad de comunicación

Patrón validado en días 19-21:

- **Día 19**: 5 PRs separados (frentes desacoplados — coordinación E2E,
  spec Mini-Evaluator, plan IA fases, párrafos writeup, cierre)
- **Día 20**: 1 PR con 4 commits (frentes relacionados — WS server +
  UI v0 + plan RH02 + aviso Floema, todo control plane Meristem)
- **Día 21**: 1 PR con 1 entrega coherente (UI funcional v1)
- **Día 22**: 1 PR con 2 commits (i18n + runbook, ambas UI)

**Heurística**: si los frentes comparten dominio o se referencian
entre sí, PR único con commits separados. Si son independientes, PRs
separados. **Cambium puede revisar commit por commit en ambos casos**.

### A4. Self-correction transparente

Cuando me equivoco, **conservo mi propuesta original viva en el PR +
addendum honesto** que rectifica. Ejemplos:

1. **PR #90 con Venation**: mi propuesta inicial era "yo HTML + JS,
   ella solo CSS". Bea preguntó "¿por qué no le pasas un primer HTML
   y dejas que ella plantee todo?". Conservé la primera bitácora viva,
   añadí addendum reframing.
2. **PR #82 cierre día 20 intermedio**: escribí cierre a mediodía,
   resultó incompleto porque la jornada siguió. PR #97 sustituye con
   cierre completo, mantengo #87 abierto para trazabilidad del
   proceso de pensamiento.

**Trazabilidad del cambio de criterio > apariencia de no haberse
equivocado**.

### A5. Decir "no ejecuto esto ahora" cuando no hay valor inmediato

Caso explícito: **mini-experimento contexto** (latencia vs num_ctx).
Lo dejé como protocolo + script ejecutable + bitácora "esperando
ventana de portátil". No lo ejecuté para no bloquear 25-90 min de
recurso compartido.

Conservación de recursos del equipo > completar todos los items del
plan diario.

### A6. Higiene 3-puntos antes de cada commit

CONTRIBUTING §9.2 (cerrado por Cambium día 18, aplicado por todo el
equipo desde día 19):

```bash
git branch --show-current
git status
git stash list
```

Sin esto, las dos colegas que entraron días 18-19 (Bract + Venation)
hubieran añadido confusión al branch jumping. La regla actúa como
**handshake antes de cada acción git**.

---

## B) Buenas prácticas arquitectónicas de Meristem

### B1. Patrón "Evaluator decide, LLM solo escribe rationale"

**Decisión arquitectónica central** del slow brain doméstico:

- 4 reglas determinísticas con precedencia inflexible (REFUSE > ALERT
  > CONSERVATIVE > CONFIRM)
- Evaluator recibe bundle, emite `EvaluationResult` con `action` +
  `reason_code` + `rationale_seed`
- LLM Gemma 4 E4B recibe bundle + decisión ya tomada, **solo redacta**
  `rationale_tecnico` (auditoría) + `rationale_para_operador` (240
  chars amables)

**Validación empírica RD04**: cuando el modelo deriva semánticamente
en GPU full (Endo Jetson día 18), la deriva afecta **solo la calidad
del rationale**, no la decisión. La decisión la firma código
determinístico, no un modelo cuya cognición fluctúa.

**Cita literal de Endo** que va al writeup: *"safe-cpu sigue siendo
el perfil contractual: lento pero validado 18/18. gpu-experimental
acelera mucho, pero no es quality pass."* — el patrón Sprout absorbe
el trade-off hardware sin romper el sistema.

### B2. Sobre común JSON envelope uniforme entre nodos

Todos los nodos (Pollen, Rhizome, Meristem) usan el mismo shape:

```json
{
  "task": "afinar_policy",
  "status": "ok" | "refuse" | "need_clarification",
  "reason_code": "STABLE_BUNDLE | EVIDENCE_LOW_CONFIDENCE | ...",
  "question_es": null,
  "payload": { ... }
}
```

**Vocabulario coherente** entre nodos: `HARD_LIMIT_DOMAIN` (literal de
mi `evaluator.py:61`) reusado en spec Mini-Evaluator Pollen (PR #92).
Un solo término viaja del firmware ESP32 al writeup.

### B3. Trazabilidad como producto, no como debug

Pieza visible al jurado, no escondida en logs:

- **`/health`** expone `bundles_received_total`, `policies_emitted_total`,
  `decisions_by_rule` (distribución por regla del Evaluator),
  `targets_known`, `pollen_connection`, `ws_events_by_type`
- **`/status`** vista consolidada multi-Rhizome con TargetStatus por
  target
- **`/sync-state`** estado WS + últimos 20 eventos persistidos
- **`/bundles/recent`** + **`/policies/recent`** historial reciente
  con joineo de decisions

**Cada inferencia del LLM persiste métricas** en `decisions.llm_metrics`
(`tool_calls_log`, `prompt_tokens`, `finish_reason`,
`thinking_chars`). El operador no las ve directamente, pero el
agricultor o auditor que las pida, sí.

### B4. Memoria por tools, no por stuffing

- `num_ctx=4096` aguanta bundle (~1500 tokens) + tool result (~500
  tokens) + system prompt
- Histórico viaja **por tool calls explícitos** (`get_recent_history`,
  `get_weather_history`)
- Latencia sostenible en CPU Alder Lake (~2 min/bundle E4B Q4_K_M)
- No hace falta `num_ctx=16k` y multiplicar latencia

**Principio implícito**: el modelo solo carga contexto cuando lo pide,
no cuando lo imponemos.

### B5. Modelo intacto, prompt y arquitectura mutables

**Decisión deliberada**: Meristem NO fine-tunea. La progresión hacia
más capacidades (memoria operacional, diagnóstico proactivo, asistente
conversacional) se hace via:

- Tool calling expandido
- System prompt versionado en `code/meristem_node/src/prompts.py`
- Persistencia adicional (tablas SQLite)
- Módulos externos (predicción numérica futura)

**Beneficios**: reversibilidad (cualquier cambio se rebobina),
auditabilidad (todo en código + datos del operador), coste cero de
retraining, compatibilidad hacia delante con futuras versiones de
Gemma.

Cita Cambium para writeup §5: *"Meristem no fine-tunea, decisión
arquitectónica."* — material literal entregado en bitácora día 19.

### B6. Fallback determinista si LLM no disponible

```python
if USE_LLM:
    try:
        return compose_rationale_via_llm(bundle, evaluation)
    except LLMUnavailableError as e:
        return _stub_rationale(evaluation.rationale_seed)
```

Pipeline no se rompe en tests/dev sin stack arrancado. **Slow brain ≠
critical brain**: si el LLM cae, el sistema sigue emitiendo policies
válidas con rationale genérico. Degradación elegante por diseño.

### B7. Tests automatizados con FastAPI TestClient

**29/29 PASS** suite completa (día 22):

- 13 evaluator tests cubren M1-M5 + variantes + precedencia
- 8 WS tests con `TestClient.websocket_connect()` (handshake,
  heartbeat, comando, error, persistencia, sync-state, 409)
- 8 recent endpoints tests (empty, populate, joineo, orden, clamping,
  REFUSE)

**Hallazgo técnico día 22**: state leakage en tests con
`reload(persistence)` por defaults de funciones cacheados al
importar. Solución: `del sys.modules['src.*']` antes de import fresh
en fixture.

### B8. Persistencia SQLite con trazabilidad fuerte

3 tablas + 1 audit:

- `bundles` (lo que Pollen entrega, con `target_rhizome_id` indexado)
- `policies` (lo que Meristem emite, con `target_node_id` indexado)
- `decisions` (link bundle ↔ policy ↔ rule + métricas LLM, con FK)
- `pollen_sync_log` (audit WS día 20)

**Reproducibilidad de demo**: el jurado puede pedir "muestra la
policy de hace 3 visitas" y respondemos. **Trazabilidad para
writeup**: el repo queda con datos de ejemplo ya generados.

### B9. UI HTML+CSS+JS vanilla con polling REST

Decisión deliberada **contra** framework moderno:

- Sin build step
- Sin dependencias frontend
- Polling cada 2s a 5 endpoints REST
- Render incremental sin destruir DOM (preserva input focus,
  selección, scroll)
- i18n ligero sin librerías (diccionario plano + función `t()`)

**Razón**: para MVP, simplicidad gana. Cuando Venation entre rebrand
visual, su CSS reescribe sin tocar JS lógica ni endpoints REST.

---

## C) Buenas prácticas de benchmarks y validación

(Esto lo conozco menos directamente — el grueso del tuning fue Xilema
con apoyo mío en días 9-12. Lo que sí he practicado y observado.)

### C1. Tuning v0 con métricas duras

Días 9-12: 94 runs Pollen + 24 runs Rhizome con scoring HIGH/MEDIUM/LOW
cerrados por Xilema en `code/tuning/`. Material para el `feat/meristem-tuning-v0`
que abrí PR #62 mergeado día 15.

### C2. Mini-batería de validación con casos representativos

Mis 5 bundles ejemplo (M1-M5) cubren las 4 reglas del Evaluator:

| Bundle | Regla disparada | Caso |
|---|---|---|
| M1 clean | CONFIRM_POLICY | Camino feliz |
| M2 disputed | CONSERVATIVE_POLICY | Validation stamps disputed |
| M3 emergency | ALERT_POLICY | mode=alert + alert_latched |
| M4 hard limit | REFUSE / HARD_LIMIT_DOMAIN | Intento relajar tank_minimum_pct |
| M5 jurisdiction | REFUSE / JURISDICTION_POLLEN | Cambio puntual operador |

Ampliado día 16 con R2 (multi-Rhizome) y día 19 con M6 (forzar tool
calling).

**Validación empírica**: 5/5 PASS en mini-batería con E4B Q4_K_M
(bitácora día 16).

### C3. Smoke E2E como verificación final

Patrón aplicado en cada PR mío que toca código:

1. POST bundles representativos
2. Verificar shapes JSON de respuesta
3. Verificar UI carga datos reales
4. Verificar persistencia (count_bundles, count_policies)

Más rápido que un test exhaustivo, más realista que test unitario.
Atrapa bugs de integración (ej. el `CommandRequest` Pydantic en
`_build_app()` de día 20 que generaba 422).

### C4. Validación cruzada CPU vs GPU

Endo días 18-19 con helper estricto detectó:

- `safe-cpu` 18/18 PASS → contractual
- `gpu-experimental` con drift (RD04) → no quality pass
- Decisión: **CPU como contractual, GPU como experimental**

**Esto valida el patrón B1**: el sistema absorbe el trade-off
hardware sin romperse.

### C5. Helper estricto como red de seguridad

PR #83 de Endo (mergeado día 19) introduce verificación estricta del
JSON output del LLM. Cuando RH02 (regresión) apareció, el helper la
detectó **antes de afectar producción**. Hallazgo temprano > fix
tardío.

### C6. Hash del modelo + version llama-server apuntados

Como red de seguridad para diagnóstico de drift externo. Parte del
plan bisección RH02 que documenté día 20 (PR #86 mergeado).

---

## D) Buenas prácticas de safety & trust (alineadas con el track)

### D1. Jerarquía explícita "lo físico manda"

> *"Lo físico manda → Rhizome arbitra → Pollen media → Meristem
> afina."*

Cada nodo conoce su jurisdicción. Cuanto más alto en la jerarquía,
**menos** autoridad física tiene. Ningún `PolicyPacket` emitido por
Meristem puede reducir hard limits del firmware ESP32 — solo
recomendar criterios más conservadores.

### D2. Hard limits del firmware ESP32 como capa inviolable

5 hard limits canónicos:

- `tank_minimum_pct >= 20`
- `max_seconds_per_event <= 180`
- `min_seconds_between_events >= 60`
- `max_total_seconds_per_day <= 600`
- `alert_latched_persists_until` no acortable

`HARD_LIMIT_DOMAIN` como reason code REFUSE en Meristem.
**Mini-Evaluator de Pollen también respeta los mismos hard limits**
(spec PR #92). Coherencia cross-nodo.

### D3. Conservador por defecto

Mini-Evaluator (PR #92) prefiere `REFUSE_RETRY` a `APPLY` dudoso. Cita
literal Bea: *"Si el sistema no puede traducir la voz a política con
cierta seguridad, no lo debe hacer."*

Esto es **exactamente** lo que el track Safety & Trust del hackathon
valora. Cada `REFUSE_RETRY` que muestre el operador es una victoria
de safety, no un fallo.

### D4. Privacidad por defecto

- Datos del agricultor viven solo en su portátil (SQLite local)
- Sin red, sin cloud
- LLM corre local con `llama.cpp`
- Modo sombra (Gemma 31B remoto) **solo opcional**, OFF en producción
  (writeup §6)

Coherente con Impact Track Global Resilience: el agricultor pequeño
tiene ya bastante con que confiar en el firmware ESP32 + en Pollen
como portador físico. Que confíe **además** en que sus datos no salen,
refuerza la propuesta.

### D5. REFUSE como feature de trazabilidad, no como fallo

Distinción visible en `/status`: `bundles_received - policies_emitted
= rechazos`. El delta cuenta historia.

**Material de demo**: si el jurado ve "rhizome_01: 5 bundles, 3
policies", pregunta "¿qué pasó con los otros 2?". Respondemos con
trazabilidad completa.

### D6. `policy_origin / policy_scope` como red de seguridad arquitectónica

Decisión documentada en spec Mini-Evaluator (PR #92):

- Convivencia de policies durables (Meristem) y transitorias (Pollen
  vía visita): **most-recent-wins por defecto**
- **Excepción crítica**: si la durable es `mode_default="alert"`,
  **siempre gana** sobre cualquier visita Pollen, sin importar
  timestamps

Race condition contra alerta = inviolable. Coherente con jerarquía.

---

## E) Buenas prácticas de coordinación cruzada

### E1. Pregunta + N opciones con pros/cons

Cuando estoy en zona ajena, le doy a la otra colega las opciones que
considero. Ella elige.

Ejemplos validados:

- **Floema con Variante D** (PR #79 → #81): planteé 3 opciones
  técnicas (A: Pollen empuja, B: Pollen levanta server, C: polling
  híbrido). Ella respondió con Variante D (WebSocket bidireccional)
  que era cualitativamente mejor que las 3 mías. Razón: Pollen sigue
  100% cliente (Android-friendly), latencia cero, 2h con OkHttp.
- **Venation con frontend completo** (PR #90 con addendum): mi
  propuesta inicial era "yo HTML, ella solo CSS". Bea reframeó: "deja
  que ella plantee todo el frontend". Apliqué reframing
  inmediatamente.

**Heurística**: cuando una colega tiene mejor criterio en un dominio,
**libera el dominio entero**, no solo una capa.

### E2. Cita literal en writeup con autoría

Cuando una colega aporta canelita arquitectónica, va al writeup con
su nombre. Reconocimiento real, no genérico.

Ejemplos:

- **Frase clave para §6 (Cambium → mí)**: *"el slow brain doméstico
  no compite con cloud. Compite con el agricultor que abre Excel y
  mira 4 columnas."* Cambium me la atribuyó tras mi plan IA por
  fases.
- **Cita literal Endo para §5**: el trade-off `safe-cpu 18/18` vs
  `gpu-experimental` no quality pass. Material defensible al jurado.
- **Variante D = Floema** en writeup §3 cuando se cuente la
  arquitectura del flujo bidireccional Pollen-Meristem.

### E3. Sin reuniones bloqueantes

Todo asincrónico vía bitácoras + commits + PRs. Cuando hace falta
sincronía, **slot acotado**:

- E2E coordinado WS con Floema: 30 min planeados día 22
- Bisección RH02 con Endo: 30-45 min coordinado
- Demo en directo con Bea (UI v0): ~10 min

**Resultado**: 5 colegas (Floema, Endo, Venation, Corola, Cambium)
pueden avanzar sin esperar reunión. Plazo corto del hackathon lo exige
y lo permite.

### E4. Mock clients como spec ejecutable

Mi `scripts/mock_pollen_ws_client.py` (Python con `websockets` lib):

- Smoke local sin Pollen Android
- Referencia de implementación para Floema (cliente Kotlin/OkHttp)
- Material de demo si Pollen Android no llega a tiempo

**Doble valor**: validación interna + spec externa.

### E5. Bloqueos cruzados desactivados antes de cierre

Cada día de cierre incluye sección "esperando" / "bloqueando". Patrón
que aplico:

- **Bloqueando a otros**: entrego material + protocolo + contratos
  para que puedan avanzar sin reunión conmigo
- **Esperando**: explícito en bitácora, sin urgencia salvo lo crítico

Resultado día 20: 5 PRs cerrados desactivando bloqueos a Floema,
Endo, Venation, Corola, Cambium.

### E6. Trazabilidad de reframings

Cuando rectifico un sesgo, **conservo la propuesta original viva en
el PR + addendum honesto**. La trazabilidad del cambio de criterio es
material para writeup §5 sobre cultura del equipo.

Cita Cambium día 21 propuesta para §5: *"Cuando el coordinador
detecta que su decisión bloquea avance, se desdice rápido sin
defensa. Cambiar de criterio en 24 horas no es señal de duda — es
señal de que el sistema responde al contexto operativo en tiempo
real."* Aplica también cuando una colega rectifica.

---

## Lo que NO hemos hecho bien (apuntes honestos)

Para que el writeup sea real, también lo que falla:

1. **Branch jumping persistente**: aún sin resolver el origen
   sistémico. Mitigación funciona pero es desgaste cognitivo.
2. **Tests de UI estática faltan**: deuda técnica apuntada desde día
   16. UI se valida visualmente con curl + browser manual.
3. **Mini-experimento contexto sin ejecutar**: protocolo + script
   listos desde día 19, ejecución pendiente de ventana.
4. **Mensaje a Xilema sin respuesta**: pendientes desde día 15
   (validación dominio prompt + nomenclatura `SAFETY_DOWNGRADE` ↔
   `HARD_LIMIT_DOMAIN`). Sin urgencia pero abierto.
5. **`signal-seed` provisional incorrecto**: mi CSS usa `#2f6dba`
   (azul); el oficial según auditoría Venation es `#C5F26B`. Espera
   rebrand.
6. **Documentación API no auto-generada**: aunque `/docs` Swagger
   funciona, no hay README API consolidado para terceros.

---

## Lo que va al writeup

Cambium decide qué piezas y en qué sección. Mi voto:

- **§3 Arquitectura**: B1, B2, B4, B5 (patrón LLM redacta + envelope
  + memoria por tools + modelo intacto)
- **§5 Buenas prácticas / Safety & Trust**: A1, A2, A3, A4, B3, D1,
  D2, D3, D4, D5, D6, E1, E2, E5, E6
- **§6 MVP qué proyectamos vs qué hacemos**: B6, B7, B8, B9 + C2, C3
  + frase clave de cierre

Si entran las 5 categorías como tabla resumida en §5, son **~30 ítems
densos** — material defendible al jurado más que de sobra.

---

## Cierre

22 días de proyecto concentran muchas micro-decisiones que individualmente
parecen pequeñas pero juntas definen el carácter del producto: **slow
brain doméstico, conservador, auditable, sin fine-tuning, con
trazabilidad como producto**.

Las buenas prácticas no son un manual seguido al pie de la letra —
son un patrón emergente de cómo Bea, Cambium y el equipo deciden
hacer las cosas. La ventaja de tenerlo escrito ahora es que cuando
alguien pregunte al jurado "¿cómo lo hicieron?", la respuesta no es
*"buena coordinación"*, es **30 prácticas concretas con ejemplos de
código y bitácoras**.

— Meristem
