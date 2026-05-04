# Propuesta prueba E2E Pollen ↔ Meristem-nodo

**De**: Meristem
**Para**: Floema (con CC Bract para flavors device/demo)
**Fecha**: 2026-05-04 (día 19)
**Pre-requisito de lectura**: ninguno; esta bitácora es self-contained.
**Antecede**: `bitacora/2026-05-01_meristem-nodo-llm-integrado-v0_meristem.md`,
`bitacora/2026-05-01_meristem-nodo-2rhizome-mvp-implementado_meristem.md`

---

## TL;DR

- **Meristem-nodo está listo** para recibir POSTs de Pollen real:
  endpoint `POST /visit` validado con 5/5 bundles ejemplo en mini-batería
  + 2/2 bundles multi-Rhizome en smoke. Sobre común JSON envelope
  alineado con `docs/20_data_contracts.md`.
- **Falta una sola cosa**: probar Pollen Android (demo flavor de Bract)
  contra Meristem en mi portátil vía Wi-Fi local. Todo lo demás está
  validado entre máquinas separadas vía `curl`.
- **Pido 30-60 min coordinados** contigo + Bract en una ventana de hoy
  o mañana. Yo levanto el stack, tú/Bract apuntáis Pollen demo a mi
  IP, hacemos 3 escenarios concretos. Si funciona, lo grabamos para
  el video.
- **Bea aprobó la prueba en chat** ("Para el 3..."). Esta bitácora es
  para que tengas el detalle antes de coordinar.

## Estado actual de Meristem-nodo

Endpoints expuestos en `:13000`:

| Endpoint | Método | Qué hace |
|---|---|---|
| `/health` | GET | Status + `targets_known` + `decisions_by_rule` + `llm_mode` |
| `/status` | GET | Vista consolidada multi-Rhizome (lista `TargetStatus` por target) |
| `/visit` | POST | **Pollen llama aquí** con `Bundle` JSON. Devuelve `VisitResponse` envelope |
| `/policy/latest` | GET | Última policy emitida (debug) |
| `/policy/{policy_id}` | GET | Policy concreta por id (trazabilidad) |
| `/policy/by-target/{target_node_id}` | GET | **Pollen llama aquí** para retirar última policy de un Rhizome |
| `/docs` | GET | OpenAPI/Swagger |

Schema esperado en `POST /visit` (resumen, ver `code/meristem_node/src/schemas.py` para detalle Pydantic):

```json
{
  "source_pollen_id": "string",
  "target_rhizome_id": "string",
  "active_policy_id": "string",
  "rhizome_snapshot": { "...": "..." },
  "decision_receipts": [ { "...": "..." } ],
  "weather_digest": { "...": "..." },
  "validation_stamps": []
}
```

(`bundle_id` y `received_at` son auto-generados si Pollen no los envía;
si los envía Meristem los respeta.)

Schema de la respuesta `VisitResponse` (sobre común alineado con
Pollen+Rhizome, mismo formato `task/status/reason_code/question_es/payload`):

```json
{
  "task": "afinar_policy",
  "status": "ok" | "refuse" | "need_clarification",
  "reason_code": "STABLE_BUNDLE | EVIDENCE_LOW_CONFIDENCE | PERSISTENT_EMERGENCY | HARD_LIMIT_DOMAIN | JURISDICTION_POLLEN",
  "question_es": null,
  "payload": {
    "policy_packet": { "policy_id": "...", "target_node_id": "...", "valid_until": "...", "mode_default": "normal|conservative|alert", "rules": {...}, "rationale": "...", "signature": "..." },
    "rationale_for_operator": "máx 240 chars en castellano",
    "evidence_refs": ["bundle_id_1"]
  }
}
```

Si `status="refuse"`, `payload` es `null` y `reason_code` es uno de los
dos REFUSE codes (`HARD_LIMIT_DOMAIN`, `JURISDICTION_POLLEN`).

## Lo que NO está probado todavía

| Punto | Severidad | Mitigación propuesta |
|---|---|---|
| Pollen Android (demo flavor de Bract) → POST /visit real vía Wi-Fi | Alta — bloqueante para demo | **Esta prueba** |
| Discovery de Meristem desde Pollen | Media | IP estática manual primera versión; mDNS post-MVP |
| Latencia E2E desde Pollen-Android | Media | Instrumentar headers `Sprout-Latency-*` (infra ya existe para `Sprout-Inference-*`) |
| Auth/security | Baja para demo, alta para producción | v0 sin auth deliberadamente; out-of-scope hackathon |
| Wi-Fi mismo segmento Android↔portátil | Baja | Verificar en setup de la prueba |

## Propuesta de prueba E2E — 3 escenarios

### Setup (10 min)

1. **Yo levanto** stack en mi portátil (mismo Wi-Fi que el Android):
   - `llama-server :8080` con E4B Q4_K_M (o stub mode `MERISTEM_USE_LLM=false` si queremos rapidez)
   - `meristem_inference_adapter :12000`
   - `meristem_node :13000` con `host="0.0.0.0"`
2. **Yo te paso** mi IP local (ej. `192.168.1.42:13000`).
3. **Tú/Bract** lanza Pollen Android demo flavor apuntando a mi IP.

### Escenario 1: visita normal (camino feliz)

- Pollen envía POST /visit con `bundle_M1_clean.json` modificado
  (`source_pollen_id` real de la app).
- **Esperado**: `status="ok"`, `reason_code="STABLE_BUNDLE"`,
  `payload.rationale_for_operator` en castellano amable.
- **Latencia esperada**: ~2 min con LLM real, <100 ms en stub mode.

### Escenario 2: REFUSE (camino estructural)

- Pollen envía bundle con `source_pollen_id="pollen_unauthorized_999"`
  o equivalente que dispare `JURISDICTION_POLLEN`.
- **Esperado**: `status="refuse"`, `payload=null`. Pollen lo gestiona
  sin esperar policy.
- **Latencia esperada**: <100 ms (REFUSE corta antes del LLM).

### Escenario 3: retirada de policy

- Pollen llama `GET /policy/by-target/rhizome_01` después del Escenario 1.
- **Esperado**: PolicyPacket recién emitida. Pollen la transporta a
  Rhizome.
- **Latencia esperada**: <50 ms (solo SQLite query).

### Criterios de éxito

- [ ] Los 3 escenarios completan sin errores HTTP (no 500, no timeouts)
- [ ] Schema de la respuesta valida en el lado Pollen (Floema/Bract
      confirman que `VisitResponse` deserializa limpio en Kotlin)
- [ ] Tiempo total de cada escenario dentro del rango esperado
- [ ] Logs de Meristem (`/health` post-prueba) muestran
      `bundles_received_total` y `decisions_by_rule` actualizados
- [ ] Si todo OK: grabamos un screencast de los 3 escenarios para
      video de Corola (E5 procesamiento Pollen)

## Lo que necesito de ti (Floema) y de Bract

**De Floema**:
1. **Confirmar schema Bundle alineado** (Kotlin `Bundle.kt` ↔ Pydantic
   `Bundle`). Si hay drift, lo cerramos antes de la prueba —
   mejor 5 min ahora que descubrirlo en directo.
2. **Documentar campos opcionales vs obligatorios** desde el lado
   Pollen. Mi `Bundle` Pydantic acepta `weather_digest=None` y
   `validation_stamps=[]`; confirmar que Pollen real puede enviar así.
3. **Ventana de 30-60 min** entre hoy tarde y mañana. Estoy disponible
   en cualquier momento que te encaje.

**De Bract** (vía Floema o directa):
1. **Demo flavor de Pollen apuntando a IP configurable** desde la
   app (no hardcoded). Si ya está, perfecto; si no, ~15 min de
   ajuste antes de la prueba.
2. **Build .apk de demo flavor** instalable en un Android de prueba
   (el suyo, el de Floema, o el mío si haga falta).

**De ambas si se anima**:
- Asistir a la prueba para ver en directo. Material para video si
  capturamos screencast del Android + portátil.

## Riesgos conocidos y mitigaciones

| Riesgo | Probabilidad | Mitigación |
|---|---|---|
| Wi-Fi del local con AP isolation (Android no ve portátil) | Media | Hotspot del móvil de Floema/mío como red común |
| Schema drift Pollen-Kotlin ↔ Meristem-Pydantic | Baja | Alineación previa con Floema (paso 1 arriba) |
| LLM E4B tarda >2 min en CPU Alder Lake | Cierta | Usar stub mode (`MERISTEM_USE_LLM=false`) en primera prueba; si pasa, segunda prueba con LLM real |
| Pollen Android demo flavor no compila | Media | Bract avisa antes; usar curl-from-Android (Termux) como fallback |
| Discovery por IP fija no funciona (firewall) | Media | Probar con `python -m http.server 9999` primero como sanity check |

## Materiales para video si la prueba va bien

- Screencast del Android + portátil dual (capturable con OBS).
  Mostrar:
  1. Pollen UI con botón "Visitar Rhizome"
  2. Click → loading → respuesta del Meristem visible en logs
  3. Cambio en `/health` y `/status` reflejado tras la visita
- Cita en castellano para escena 5 ("Pollen recoge bundle, Meristem
  afina policy, Pollen lo lleva de vuelta — todo offline").

## Calendario propuesto

- **Hoy día 19 tarde** (preferido) o **mañana día 20 cualquier hora**.
- 30-60 min coordinados. Yo me adapto.
- Tú/Bract me decís cuándo. Yo aviso 10 min antes para levantar stack.

## Después de la prueba

- Bitácora de cierre con resultados + screencast + decisiones (mínimo
  esfuerzo para Floema o yo, según vayan los pulsos del día).
- Si funciona: PR a `main` con cualquier ajuste de schema necesario
  + cita al video.
- Si falla parcial: issue específico con repro + plan de fix coordinado.

## Referencias técnicas

- `code/meristem_node/src/main.py` — endpoints
- `code/meristem_node/src/schemas.py` — Pydantic models
- `code/meristem_node/examples/bundle_M*.json` y `bundle_R2_emergency.json`
  — bundles de referencia
- `docs/20_data_contracts.md` — contratos de datos (origen del envelope)
- `bitacora/2026-05-01_meristem-nodo-llm-integrado-v0_meristem.md` —
  cómo funciona el LLM cuando está activo
- PR #63 (`feat/meristem-node-llm-integration`) — pendiente de merge,
  contiene todo lo descrito aquí

---

Avísame cuando tengas hueco, Floema. Esto va rápido si nos coordinamos.

— Meristem
