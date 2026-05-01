# Meristem-nodo — diseño v0 (MVP demo) vs v1 (post-hackathon)

**Autora**: Meristem
**Fecha**: 2026-05-01 (día 16, tarde)
**Para**: Bea (decisiones), Cambium (writeup), Floema (integración),
Xilema (validación dominio), Endodermis (referencia tuning)
**Trigger**: Bea preguntó por scope de Meristem-nodo (multi-Rhizome,
persistencia, ciclos, cálculo de policies). Documentación honesta de
qué hay hoy vs qué iría a v1, con caso especial **MVP demo con 2
Rhizomes simulados sobre el mismo ESP32**.

---

## TL;DR

| Pregunta | Hoy v0 | v1 post-demo |
|---|---|---|
| ¿Multi-Rhizome simultáneo? | ✅ **base preparada** (per-Rhizome processing); ❌ vista conjunta + batch endpoint | Endpoint batch `POST /visits` + consolidación cross-target |
| Persistencia | SQLite file-based con 3 tablas + índices | Compresión raw_json + backup automático + multi-proceso |
| Gestión de ciclos | Emergente (Pollen dicta el ritmo); sin agendamiento | Alertas si pasan N días sin visita + cronología |
| Cálculo de policies | Determinístico stateless con 4 reglas | Consolidación histórica + ajuste por arquetipo + forecast meteo |

**Para el caso demo MVP (2 Rhizomes simulados)**: con un ajuste pequeño
(añadir `GET /status` que muestre estado consolidado de los nodos
conocidos), v0 cubre el caso. **No es refactor**, es adición visible
útil para demo. **~30-60 min de trabajo.** Detalle en sección 5.

---

## 1. Estado actual del Meristem-nodo (v0 día 16)

### Pipeline funcional

```
POST /visit
   ↓ Pydantic validation (Bundle)
   ↓ IngestService → SQLite bundles
   ↓ Evaluator (4 reglas determinísticas, stateless)
   ↓
   ├── REFUSE → respuesta envelope sin policy
   │
   └── ok → LLM Gemma 4 E4B Q4_K_M (rationale)
            ↓ PolicyComposer → PolicyPacket
            ↓ SQLite policies + decisions
            ↓
VisitResponse con sobre común JSON
```

### 4 reglas determinísticas (en `evaluator.py`)

| Regla | reason_code | Mode | Rules generadas |
|---|---|---|---|
| 1. REFUSE | `HARD_LIMIT_DOMAIN` o `JURISDICTION_POLLEN` | - | (no emite policy) |
| 2. ALERT | `PERSISTENT_EMERGENCY` | alert | `alert_until_human_review`, `skip_routine_watering` |
| 3. CONSERVATIVE | `EVIDENCE_LOW_CONFIDENCE` | conservative | `soil_dry_threshold_pct_bump: 5`, `extra_caution_on_disputed_evidence` |
| 4. CONFIRM | `STABLE_BUNDLE` | normal | `{}` (confirma policy activa con `valid_until +7d`) |

**Limitación clave**: el Evaluator es **stateless respecto a histórico**.
Solo mira el bundle actual. No lee bundles previos del mismo Rhizome.

### Persistencia SQLite (`persistence.py`)

3 tablas con FOREIGN KEYs:

- `bundles`: `bundle_id`, `received_at`, `source_pollen_id`,
  `target_rhizome_id`, `active_policy_id`, `raw_json` (Bundle completo)
- `policies`: `policy_id`, `emitted_at`, `target_node_id`, `raw_json`
  (PolicyPacket completo), `evidence_refs` (JSON list de bundle_ids)
- `decisions`: `decision_id`, `bundle_id` (FK), `policy_id` (FK),
  `rule_applied`, `reason_code`, `llm_metrics` (JSON con tokens/finish/tools)

**Índices útiles**:
- `idx_bundles_target` por `(target_rhizome_id, received_at DESC)`
- `idx_policies_target` por `(target_node_id, emitted_at DESC)`
- `idx_decisions_bundle` por `(bundle_id, created_at DESC)`

**Queries disponibles**: `get_latest_policy_for(target_node_id)`,
`get_latest_policy_global()`, `get_policy_by_id`, counts para
`/health`, `count_decisions_by_rule()`.

**Limitaciones v0**:
- SQLite mono-proceso (file lock)
- Sin compresión `raw_json` (el JSON completo del Bundle se guarda
  serializado, puede crecer)
- Sin backup automático

## 2. Las 4 preguntas de Bea respondidas con código

### Q1 — ¿Multi-Rhizome en una iteración?

**Hoy**:
- ✅ El código **soporta múltiples Rhizomes**: `Bundle.target_rhizome_id`
  distingue nodos, persistencia indexa por target, `GET /policy/by-target/{id}`
  filtra correctamente.
- ✅ Pollen puede hacer **N POSTs separados** (uno por Rhizome) y
  recibir N policies separadas.
- ❌ No hay endpoint batch (`POST /visits` con lista).
- ❌ No hay vista consolidada (`GET /status` con estado de N nodos).
- ❌ El Evaluator NO consolida cross-target (cada bundle se evalúa
  aislado).

**Para "2 Rhizomes en MVP" — análisis específico en sección 5**.

### Q2 — ¿Cómo y dónde guardamos los datos?

**SQLite file-based** en `meristem_node.db` (cwd, configurable vía env
`MERISTEM_DB_PATH`).

Trazabilidad fuerte por diseño:
- Bundle se persiste **antes** del Evaluator (incluso si después es
  REFUSE — para auditoría)
- Cada Policy linkea a `evidence_refs[bundle_ids]`
- Cada Decision linkea Bundle ↔ Policy con regla aplicada + métricas
  LLM (tokens, finish_reason, tool_calls log)

Sobrevive reinicios. Cualquiera puede inspeccionar el `.db` con
`sqlite3` CLI.

### Q3 — ¿Cómo se gestiona un ciclo nuevo?

**El "ciclo" es emergente, no orquestado por Meristem**:

1. Pollen visita Rhizome (cuándo, depende del operador)
2. Pollen vuelve a Wi-Fi → POST `/visit` con bundle
3. Meristem ingiere → evalúa → emite PolicyPacket
4. Esa policy queda en `/policy/by-target/{rhizome_id}` para la
   **siguiente** visita
5. Pollen consulta antes de salir, recoge policy, entrega a Rhizome

**Meristem no agenda nada**. Si el operador hace 1 visita/semana,
Meristem emite 1 policy/semana por Rhizome. Si 2/semana, 2/semana. El
ritmo lo dicta Pollen.

**Hoy NO hay**:
- Alertas si pasan N días sin visita
- Cronología consultable (`GET /history/by-target/{id}`)
- Caducidad activa (el `valid_until +7d` se emite pero Meristem no
  hace nada al expirar — confía en que Pollen vuelva)

### Q4 — ¿Cómo se calculan las policies nuevas?

**Determinístico stateless**:
1. Evaluator aplica 4 reglas en orden de precedencia → devuelve
   `Action`, `reason_code`, `suggested_mode`, `suggested_rules`
2. PolicyComposer construye PolicyPacket con `valid_until = now + 7d`,
   `mode_default`, `rules` (las del Evaluator + metadata trazabilidad),
   `signature: "<placeholder-meristem-v0>"` (firma criptográfica
   diferida a v1)
3. LLM Gemma 4 E4B Q4_K_M escribe `rationale` técnico + prosa al
   operador, **sin contradecir al Evaluator** (la decisión ya está
   fijada)

**Hoy NO hay**:
- Aprendizaje histórico (cada bundle se evalúa aislado)
- ML clasificadores
- Ajuste fino por arquetipo (las "rules" generadas son las mismas
  para todo CONSERVATIVE / ALERT)
- Forecast meteo (el `weather_digest` solo se mira para `isStale=true`)

## 3. Tabla v0 vs v1 — qué iría dónde

| Pieza | v0 (MVP demo) | v1 (post-hackathon) |
|---|---|---|
| **Multi-Rhizome processing** | ✅ via N POSTs separados | Endpoint batch `POST /visits` |
| **Vista conjunta multi-Rhizome** | ❌ falta | `GET /status` con estado de N nodos |
| **Persistencia SQLite** | ✅ 3 tablas + índices | Compresión raw_json, backup automático |
| **Trazabilidad** | ✅ bundle ↔ policy ↔ decision con FKs | Endpoint `/history/by-target/{id}` con cronología |
| **Pipeline determinístico** | ✅ 4 reglas + 13 tests | Más reglas según patrones que aparezcan |
| **LLM rationale** | ✅ Gemma 4 E4B + tool calling | Tools reales (no stubs); fine-tuning v1 |
| **Aprendizaje histórico** | ❌ stateless | Evaluator lee últimos N bundles → detecta tendencias |
| **Ajuste por arquetipo** | ❌ rules genéricas | Reglas distintas por tipo de plot/región/estación |
| **Forecast meteo** | ❌ solo `isStale` | Tool `get_weather_forecast(plot, days=7)` con ajuste activo |
| **Personalización operador** | ❌ no | `Bundle.operator_preferences` (más conservador, prioriza X) |
| **Agendamiento** | ❌ ritmo emergente | Alertas tras N días sin visita |
| **Caducidad activa** | ❌ pasiva (confía en Pollen) | Detección activa al expirar `valid_until` |

## 4. Recomendaciones priorizadas para post-hackathon

Por ROI estimado:

1. **Consolidación histórica simple** (1-2 días). El Evaluator lee
   últimos N bundles del mismo target y detecta tendencias ("disputas
   crecientes 3 semanas seguidas → más conservador"). Es lo que
   distingue "Meristem registra" de "Meristem aprende".

2. **Endpoint `/history/by-target/{rhizome_id}`** (medio día). Útil al
   operador y al jurado en demo en directo.

3. **Tools reales**: `get_weather_history` ya está, falta sustituir
   stubs por servicio meteo real. Y añadir `get_weather_forecast`. ~1
   día.

4. **Endpoint batch `POST /visits`** (medio día). Pollen envía N
   bundles de golpe en lugar de N POSTs. Optimización, no urgente.

5. **Multi-proceso** (incierto): si en algún momento un agricultor
   monta una cooperativa con 50+ Rhizomes y un único Meristem, SQLite
   monoproceso puede ser cuello. Migración a Postgres o WAL mode de
   SQLite.

## 5. Caso especial — MVP demo con 2 Rhizomes simulados

### Contexto

Bea confirmó (día 16): **el demo simulará 2 Rhizomes (`rhizome_01` y
`rhizome_02`) sobre el mismo ESP32 físico, con 2 parcelas distintas**.
Es decir, 1 hardware ESP32 expone (vía firmware o vía mock) los datos
de las dos parcelas como si fuesen dos nodos Rhizome separados, cada
uno con su contexto.

Esto activa la pregunta: **¿v0 actual cubre 2 Rhizomes, o requiere
ajuste?**

### Análisis

**Lo que ya funciona sin cambios**:

✅ **Persistencia separada por target**. Si Pollen hace dos POSTs:

```bash
POST /visit  body: {target_rhizome_id: "rhizome_01", ...bundle_R1...}
POST /visit  body: {target_rhizome_id: "rhizome_02", ...bundle_R2...}
```

→ Meristem persiste 2 bundles distintos (con `bundle_id` único cada
uno), evalúa cada uno por separado, emite 2 policies distintas, y
las queries `/policy/by-target/rhizome_01` vs `/policy/by-target/rhizome_02`
devuelven la policy correcta para cada nodo.

✅ **Decisiones independientes por nodo**. Si Rhizome_01 está en
emergencia y Rhizome_02 limpio, el Evaluator emite ALERT para R1 y
CONFIRM para R2. Cada nodo tiene su propio rationale, su propio
`valid_until`, su propia trazabilidad.

✅ **Trazabilidad cruzada disponible**. Las queries SQL ya soportan
filtrar por target. Si alguien pregunta "muéstrame la cronología del
nodo R2", la query es trivial (`SELECT * FROM bundles WHERE
target_rhizome_id='rhizome_02' ORDER BY received_at DESC`).

**Lo que faltaría añadir** (para que el demo sea visualmente fuerte):

❌ **`GET /status`** o `GET /policies/all`: endpoint que devuelva
**estado consolidado** de los N Rhizomes conocidos. Útil para que el
jurado vea de un vistazo "Meristem maneja 2 nodos a la vez".

Forma propuesta:
```json
GET /status
{
  "targets_known": ["rhizome_01", "rhizome_02"],
  "by_target": {
    "rhizome_01": {
      "latest_policy_id": "pkt_meristem_...",
      "latest_policy_emitted_at": "2026-05-01T...",
      "latest_policy_mode": "alert",
      "last_bundle_received_at": "2026-05-01T...",
      "bundles_total": 5,
      "decisions_total": 5,
      "decisions_by_rule": {"alert_policy": 3, "confirm_policy": 2}
    },
    "rhizome_02": {
      "latest_policy_id": "pkt_meristem_...",
      "latest_policy_emitted_at": "2026-05-01T...",
      "latest_policy_mode": "normal",
      "last_bundle_received_at": "2026-05-01T...",
      "bundles_total": 4,
      "decisions_total": 4,
      "decisions_by_rule": {"confirm_policy": 4}
    }
  }
}
```

❌ **Update `/health`** para que el `decisions_by_rule` agregado
existente se complemente con un breakdown por target. Mejora menor.

❌ **(Opcional)** `POST /visits` batch: aceptar lista de bundles en
un POST. Comodidad para Pollen pero no esencial — Pollen puede hacer
2 POSTs separados sin problema.

### Coste de los cambios necesarios

| Cambio | Coste | Bloquea demo si no se hace? |
|---|---:|---|
| `GET /status` con vista consolidada | 30-60 min | No bloquea pero **mejora demo significativamente** |
| Update `/health` con breakdown por target | 15 min | No bloquea (`/status` lo cubre) |
| `POST /visits` batch | 30 min | No bloquea (Pollen puede hacer 2 POSTs) |
| **Total recomendado** | **~1 hora** | mejora visible, no bloquea |

### Mi propuesta concreta

**Para v0 / MVP demo**:

1. ✅ **Sin cambios al Evaluator ni al pipeline**: cada Rhizome se
   procesa independientemente, como ya hace.
2. ✅ **Sin cambios a la persistencia**: las 3 tablas + índices ya
   soportan multi-target.
3. ➕ **Añadir `GET /status`** que muestre estado consolidado de
   los N Rhizomes conocidos. **30-60 min**.
4. ➕ **Update `/health`** con `targets_known: list[str]` para que
   sea visible incluso sin entrar a `/status`. **15 min**.
5. ➖ **Saltar `POST /visits` batch** por ahora — Pollen hace 2 POSTs
   y listo. Si Floema lo pide explícitamente, lo añadimos.

**Demo del flujo con 2 Rhizomes**:

1. Pollen visita Rhizome_01 → POST `/visit` con bundle_R1 (parcela A
   limpia) → Meristem emite policy CONFIRM para R1
2. Pollen visita Rhizome_02 → POST `/visit` con bundle_R2 (parcela B
   con disputa) → Meristem emite policy CONSERVATIVE para R2
3. Demo muestra `GET /status` → jurado ve **2 nodos manejados, 2
   policies distintas, 2 modes distintos en pantalla**
4. Pollen consulta `GET /policy/by-target/rhizome_01` y
   `GET /policy/by-target/rhizome_02` → recoge ambas policies para
   entregar en próxima visita

**Todo esto se demo en directo o en grabación de video** sin tocar
arquitectura. Solo añadir un endpoint visible.

### Pregunta para Bea

¿Adelante con la propuesta?

- **Si sí**: implemento `GET /status` + actualizo `/health` esta tarde
  (~1h), smoke con bundles de R1 y R2, commit + push.
- **Si prefieres otro alcance** (ej. también `POST /visits` batch, o
  `GET /history/by-target/{id}` para cronología): dilo y replanteo.
- **Si dices "v0 actual basta, el demo enseña 1 Rhizome a la vez sin
  vista conjunta"**: cero cambios, el código ya soporta el caso.

Mi voto: **adelante con la propuesta**. La vista consolidada en demo
refuerza la narrativa "scalable a N cooperativas" sin coste real.

## Referencias

- `code/meristem_node/src/main.py` — pipeline + endpoints actuales
- `code/meristem_node/src/persistence.py` — queries por target
- `code/meristem_node/src/evaluator.py` — 4 reglas
- `code/meristem_node/src/policy_composer.py` — PolicyPacket con
  `valid_until +7d`
- `code/meristem_node/ARCHITECTURE.md` — diseño por capas
- `bitacora/2026-05-01_meristem-nodo-llm-integrado-v0_meristem.md` —
  resultados smoke 5/5 PASS con LLM real
