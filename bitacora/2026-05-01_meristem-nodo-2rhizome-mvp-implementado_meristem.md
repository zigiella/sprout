# Meristem-nodo: soporte 2-Rhizome MVP implementado

**Autora**: Meristem
**Fecha**: 2026-05-01 (día 16, tarde)
**Rama**: `feat/meristem-node-llm-integration`
**Antecede**: `bitacora/2026-05-01_meristem-nodo-diseno-v0-vs-v1_meristem.md`
  (diseño + propuesta aprobada por Bea)

---

## TL;DR

- Bea aprobó la propuesta de la design doc esta mañana ("Adelante.").
- **Implementado en ~1h tal como estimé**: `GET /status` + `targets_known`
  en `/health` + bundle ejemplo `bundle_R2_emergency.json`.
- **Smoke 2-Rhizome 2/2 PASS** + bonus check REFUSE: rhizome_01 con
  STABLE_BUNDLE / `mode=normal`, rhizome_02 con PERSISTENT_EMERGENCY /
  `mode=alert`, ambos visibles en una sola pantalla `/status`.
- **Sin cambios en Evaluator, PolicyComposer ni LLM client**. El v0 ya
  soportaba multi-target via persistencia indexada por `target_node_id`;
  hoy solo añadí la vista consolidada para que la demo lo enseñe.
- **13/13 tests existentes PASS** sin regresión.

## Cambios realizados

| Fichero | Cambio | Líneas |
|---|---|---|
| `code/meristem_node/src/persistence.py` | `list_known_targets()` + `get_target_summary(target_node_id)` | +110 |
| `code/meristem_node/src/schemas.py` | `TargetStatus` + `StatusResponse` Pydantic models | +40 |
| `code/meristem_node/src/main.py` | `GET /status` endpoint + `targets_known` en `/health` | +20 |
| `code/meristem_node/examples/bundle_R2_emergency.json` | Bundle ejemplo para rhizome_02 (clone M3 con target distinto) | +21 |

## Smoke test 2-Rhizome (stub mode, sin LLM real)

Secuencia:

1. `POST /visit` con `bundle_M1_clean.json` → rhizome_01 / STABLE_BUNDLE / mode=normal ✓
2. `POST /visit` con `bundle_R2_emergency.json` → rhizome_02 / PERSISTENT_EMERGENCY / mode=alert ✓
3. `GET /health` → `targets_known: ["rhizome_01", "rhizome_02"]` ✓
4. `GET /status` → array `targets[]` con dos `TargetStatus` correctos ✓
5. `GET /policy/by-target/rhizome_02` → policy específica de R2 ✓ (sin regresión)

**Bonus**: tras un `POST /visit` con `bundle_M5_pollen_jurisdiction.json`
(REFUSE), `/status` muestra `rhizome_01` con `bundles_received: 2` pero
`policies_emitted: 1` — la traza distingue limpiamente bundles aceptados
de los rechazados. Demo-friendly para que el jurado pregunte "¿qué pasó
ahí?" y respondamos.

### Output `/status` mini-batería

```json
{
  "targets_known": ["rhizome_01", "rhizome_02"],
  "targets": [
    {
      "target_node_id": "rhizome_01",
      "bundles_received": 1,
      "policies_emitted": 1,
      "latest_policy_mode": "normal",
      "latest_reason_code": "STABLE_BUNDLE",
      "latest_rule_applied": "confirm_policy",
      "latest_policy_valid_until": "2026-05-08T..."
    },
    {
      "target_node_id": "rhizome_02",
      "bundles_received": 1,
      "policies_emitted": 1,
      "latest_policy_mode": "alert",
      "latest_reason_code": "PERSISTENT_EMERGENCY",
      "latest_rule_applied": "alert_policy",
      "latest_policy_valid_until": "2026-05-08T..."
    }
  ]
}
```

(Campos de timestamp/id omitidos por brevedad — están en el output real.)

## Decisiones del rato

1. **`list_known_targets()` SOURCE = tabla `bundles`**, no tabla
   `policies`. Razón: si un Rhizome solo recibe REFUSEs (no se le
   emite policy), igual queremos que aparezca en la lista. Trazabilidad
   completa.
2. **`TargetStatus.latest_*` campos pueden ser None**. Si Rhizome solo
   tiene REFUSEs, `latest_policy_*` es None y `latest_reason_code`
   también (porque decisions tampoco existe sin policy). Los counters
   sí están: `bundles_received` refleja el flujo total.
3. **Bonus REFUSE check**: lo añadí ad-hoc al smoke, no como test
   automatizado. Vale la pena cubrirlo en tests post-hackathon.
4. **Bundle R2 = clone de M3 con `target_rhizome_id: "rhizome_02"`**.
   Mantengo el escenario de emergencia para que la demo contraste
   visualmente con M1 (clean) en rhizome_01: "miren, dos parcelas
   gestionadas a la vez con políticas distintas según el estado real
   de cada una".

## Lo que NO cambió (deliberadamente)

- Evaluator: las 4 reglas y precedencia siguen idénticas.
- PolicyComposer: misma lógica `compose_policy(bundle, evaluation, rationale)`.
- LLM client (`inference.py`): sin cambios. El smoke de hoy fue stub
  mode (`MERISTEM_USE_LLM=false`) por ser test de endpoints; con LLM
  real seguirá funcionando exactamente igual (la integración es ortogonal
  al multi-target).
- Schema de las 3 tablas SQLite: sin cambios. `target_rhizome_id` ya
  estaba indexado en `bundles`, `target_node_id` ya estaba indexado
  en `policies`. Las queries nuevas usan esos índices.

## Para demo en video / writeup

Frase candidata para Corola: "Meristem-nodo gestiona dos Rhizomes
simultáneos en un solo portátil. La pantalla `/status` lo muestra:
distintos modos, distintas razones, mismo hardware." Acompañar con
captura del JSON de `/status` formateado.

## Próximos pasos

1. Bea ve la implementación + ejecuta el smoke ella misma si quiere
   reproducir.
2. Apertura PR `feat/meristem-node-llm-integration` → `main` cuando Bea
   dé el go (acumula: integración LLM E4B + 2-Rhizome MVP support).
3. Sigo con soporte a Endodermis (Jetson) cuando arranque su batería.
4. Sigo esperando respuesta de Xilema sobre prompt + 5 bundles.

## Referencias

- Diseño origen: `bitacora/2026-05-01_meristem-nodo-diseno-v0-vs-v1_meristem.md`
- Pipeline LLM día 16 mañana: `bitacora/2026-05-01_meristem-nodo-llm-integrado-v0_meristem.md`
- Bundle ejemplo R2: `code/meristem_node/examples/bundle_R2_emergency.json`
