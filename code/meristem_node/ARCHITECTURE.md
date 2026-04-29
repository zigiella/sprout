# Meristem-nodo — arquitectura mínima viable extensible (día 14 boceto)

**Estado**: BORRADOR día 14, en construcción.
**Constraint clave**: minimal funcional pero **diseñado para crecer
post-hackathon** (consolidación de datos, identificación de patrones,
aprendizaje a nuevas policies). **Nada de lo que se construye HOY se
tira mañana.**

---

## Capas (separación responsabilidades)

```
┌─────────────────────────────────────────────────────────────────┐
│  HTTP Layer (FastAPI)                                          │
│  - POST /visit  → recibe Bundle (snapshot+receipts+weather)    │
│  - GET  /policy/latest  → devuelve último PolicyPacket emitido │
│  - GET  /health  → estado + métricas                           │
│  - GET  /docs  → OpenAPI/Swagger automático                    │
└──────────────────┬──────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│  IngestService                                                  │
│  - Validación de schema del Bundle (Pydantic)                  │
│  - Persistencia inmediata en SQLite (tabla bundles)            │
│  - Devuelve bundle_id para trazabilidad                        │
└──────────────────┬──────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│  Evaluator (lógica determinista + LLM-aided rationale)          │
│  - Reglas determinismas por categoría (4 reglas v0):           │
│    A. Bundle limpio    → confirma policy + valid_until +7d     │
│    B. Disputas/dudas   → mode=conservative + thresholds++      │
│    C. Emergencia       → mode=alert + rationale crítico        │
│    D. Hard limit relax → REFUSE (HARD_LIMIT_DOMAIN)            │
│  - LLM SOLO emite rationale (descripción y prosa al operador)  │
│  - Decisión NO depende del LLM (eliminamos riesgo de drift)    │
└──────────────────┬──────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│  PolicyComposer                                                 │
│  - Construye PolicyPacket válido según schema v2 (Pydantic)    │
│  - policy_id auto-generado, signature placeholder v0           │
│  - evidence_refs apuntan a bundles que originaron la decisión  │
│  - Persistencia inmediata en SQLite (tabla policies)           │
└──────────────────┬──────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│  Persistence Layer (SQLite)                                     │
│  - bundles  (id, received_at, json, source_pollen_id)          │
│  - policies (id, emitted_at, target_node_id, json,             │
│              evidence_refs)                                    │
│  - decisions (id, bundle_id, policy_id, rule_applied,          │
│               llm_metrics)                                     │
│  - Índice por target_node_id + emitted_at desc                 │
└─────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────┐
  │  Inference Layer (compartido con Pollen+Rhizome)            │
  │  meristem_inference_adapter (puerto distinto, ej. :13000)   │
  │  └→ llama-server :8081 con Gemma 4 E4B Q4_K_M               │
  │     - thinking ON (slow brain, no time-critical)            │
  │     - tool calling si verificación pasa                     │
  └─────────────────────────────────────────────────────────────┘
```

## Por qué esta separación

### Capa HTTP: FastAPI

- **OpenAPI automático** vía `/docs` — el jurado del hackathon puede
  inspeccionar la API sin clonar el repo.
- **Pydantic models** validan request/response automáticamente.
- **Async** → cuando llegue concurrencia post-demo, ya está.

### IngestService

- **Una función**: validar y persistir. Si la validación falla,
  rechaza con HTTP 422 antes de gastar inferencia.
- **Trazabilidad desde minuto cero**: cada bundle queda en SQLite
  con id estable. Las policies linkean a bundles que las originaron.
  Cuando llegue la consolidación de patrones (post-demo), ya hay
  histórico al que volver.

### Evaluator (esto es donde está el seguro)

**La decisión NO la toma el LLM.** Lógica determinista con 4 reglas:

```python
def evaluate(bundle) -> Tuple[Action, str]:
    # Hard limit barandilla (sale antes de cualquier otra cosa)
    if bundle.requests_hard_limit_relaxation():
        return Action.REFUSE, "HARD_LIMIT_DOMAIN"

    # Emergencia persistente
    if bundle.has_persistent_emergency():
        return Action.EMIT_ALERT_POLICY, "PERSISTENT_EMERGENCY"

    # Disputas o baja confianza
    if bundle.has_disputes() or bundle.avg_confidence() < 0.7:
        return Action.EMIT_CONSERVATIVE_POLICY, "EVIDENCE_LOW_CONFIDENCE"

    # Camino feliz: confirma policy activa con valid_until extendido
    return Action.EMIT_CONFIRM_POLICY, "STABLE_BUNDLE"
```

**El LLM solo escribe el rationale** (descripción técnica + prosa al
operador). Eso lo aísla de tomar decisiones críticas.

### PolicyComposer

- Construye PolicyPacket válido. **No inventa** campos — solo combina
  decisión del Evaluator + rationale del LLM + metadata.
- evidence_refs incluye bundle_id(s) que justificaron la decisión.
  En v0 será 1 bundle (el último); en post-demo cuando consolidemos,
  ya soporta N.

### Persistence Layer (SQLite)

**Por qué SQLite y no en memoria**:

1. **Reproducibilidad de demo**: si el jurado pregunta "muestrame la
   policy que emitiste hace 3 visitas", podemos hacerlo (`SELECT * FROM
   policies ORDER BY emitted_at DESC LIMIT 3`).
2. **Trazabilidad para writeup**: el repo queda con datos de ejemplo
   ya generados. Cualquier juez puede inspeccionar los bundles +
   policies históricos.
3. **Base de la consolidación post-demo**: cuando crezca el Evaluator
   para identificar patrones (consolidar 10 visitas, detectar
   tendencia estacional), ya hay tabla `bundles` que leer. **Sin
   refactor**.
4. **Coste casi cero**: SQLite es file-based, sin servicio extra,
   parte de stdlib Python.

### Inference Layer

**Reutilizo el adapter Meristem y el patrón llama.cpp**.

- Adapter en puerto distinto al de Rhizome simulación (ej. `:13000`)
- llama-server en puerto distinto (ej. `:8081`)
- Backend `llamacpp` ya construido día 12, headers
  `Sprout-Inference-*` uniformes.
- Modelo: **Gemma 4 E4B Q4_K_M** (vs E2B de Rhizome). E4B porque slow
  brain doméstico no tiene constraint de batería ni latencia.
- **thinking ON** porque es one-shot por bundle, no multi-turn → no
  aplica el confound de R7-bis.

## Flujo end-to-end (demo path)

```
1. Pollen Android visita Rhizome físico → recolecta snapshot+receipts
2. Pollen vuelve a Wi-Fi LAN → POST a Meristem-nodo /visit
3. Meristem.IngestService valida + persiste bundle → bundle_id
4. Meristem.Evaluator aplica regla determinista → Action + reason_code
5. Meristem.LLM (E4B + tool calling si pasa) genera rationale
   (incluye llamadas a tools si necesita histórico)
6. Meristem.PolicyComposer construye PolicyPacket válido
7. Meristem persiste policy + responde 200 con PolicyPacket
8. Pollen guarda PolicyPacket → siguiente visita a Rhizome lo entrega
9. Demo: pantalla del portátil muestra rationale_for_operator en
   castellano amable. Cenital cartoon de Corola incluye el portátil.
```

## Mini-batería v0 (5 casos para tuning)

Validan las 4 reglas del Evaluator + 1 control:

| # | Caso | Bundle típico | Action esperada |
|---|---|---|---|
| M1 | Bundle limpio (camino feliz) | snapshot OK + 3 receipts WATER OK + weather fresh | CONFIRM_POLICY |
| M2 | Bundle con disputa | ValidationStamp(disputed) + receipts mixtos | CONSERVATIVE_POLICY |
| M3 | Bundle con emergencia | DEPOSITO_BAJO repetido + ALERT_LATCHED | ALERT_POLICY |
| M4 | Patch malicioso (hard limit) | bundle pide bajar tank_minimum_pct | REFUSE (HARD_LIMIT_DOMAIN) |
| M5 | Pregunta puntual (jurisdicción Pollen) | bundle incluye request operador "regar 30s extra hoy" | REFUSE (JURISDICTION_POLLEN) |

Validar con Xilema antes de ejecutar (~30 min).

## Estructura de directorios propuesta

```
code/meristem_node/
├── README.md
├── pyproject.toml (deps: fastapi, uvicorn, pydantic, sqlite3, httpx)
├── ARCHITECTURE.md (este archivo)
├── verify_tool_calling.py (test día 14)
├── src/
│   ├── __init__.py
│   ├── main.py                # FastAPI app
│   ├── ingest.py              # IngestService
│   ├── evaluator.py           # Lógica determinista
│   ├── policy_composer.py     # Construye PolicyPacket
│   ├── persistence.py         # SQLite layer
│   ├── inference.py           # Cliente al adapter Meristem (llamacpp)
│   ├── schemas.py             # Pydantic models
│   └── prompts.py             # Carga system prompt + tool definitions
├── tests/
│   ├── __init__.py
│   ├── test_ingest.py
│   ├── test_evaluator.py      # 4 reglas + casos borde
│   ├── test_policy_composer.py
│   └── test_e2e_smoke.py      # smoke con bundle real
└── examples/
    ├── bundle_clean.json
    ├── bundle_disputed.json
    ├── bundle_emergency.json
    ├── bundle_hard_limit_relax.json
    └── bundle_pollen_jurisdiction.json
```

## Coste estimado actualizado

| Pieza | Coste | Día tentativo |
|---|---:|:-:|
| Esqueleto FastAPI + endpoints stub | 0.3d | 14 tarde |
| Schemas Pydantic + persistence SQLite | 0.5d | 15 mañana |
| IngestService + Evaluator (4 reglas) | 0.5d | 15 tarde |
| Inference layer (cliente al adapter) | 0.3d | 16 mañana |
| PolicyComposer + tests unitarios | 0.5d | 16 tarde |
| Mini-batería v0 + tuning | 0.5d | 17 mañana |
| Smoke e2e + integración Floema | 0.4d | 17 tarde |
| **Total** | **~3d** | demo-ready día 18 |

Más estrictamente alineado con la promesa "demo-ready día 18".
Cabe con margen de día 18 entero para iteración.

## Lo que asombra al jurado del Hackathon Gemma 4 Good

Recordatorio del análisis estratégico (día 14):

- **Special Technology Track llama.cpp ($10k)**: Rhizome (Jetson) +
  Meristem (portátil casero) = doble punto en mismo track. Argumento
  *"Gemma 4 en dos clases distintas de resource-constrained hardware"*.
- **Tool calling explícitamente valorado**: pieza B3 si verificación
  del día 14 confirma soporte llama-server.
- **Impact Track Global Resilience ($10k)**: agricultor desatendido +
  edge offline + climate-aware (weather digest). Encaja literal.
- **Impact Track Safety & Trust ($10k)**: jerarquía explícita (físico
  manda) + barandilla hard limits + grounded en evidence_refs. Framework
  de transparencia.
- **Patrón transferencia entre agentes**: Pollen 50% → Rhizome 94% →
  Meristem ?%. Metodología defendible empíricamente.

Total premios potencialmente acumulables: hasta $70k (Main 1º +
Impact + Special Tech).
