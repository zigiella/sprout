# Bundles ejemplo Meristem-nodo (mini-batería v0)

5 bundles representativos de la mini-batería v0 acordada con Xilema
en el bloque 1 del review día 13. Cada uno dispara una de las 4 reglas
del Evaluator (5 cubre tanto JURISDICTION_POLLEN como HARD_LIMIT_DOMAIN
en la regla REFUSE).

Bundle adicional `R2` (día 16, cierre 2-Rhizome MVP) y `M6` (día 19,
demo tool calling) ampliando la batería sin sustituirla.

## Casos

| File | Caso | Action esperada | reason_code |
|---|---|---|---|
| `bundle_M1_clean.json` | Bundle limpio (camino feliz) | CONFIRM_POLICY | STABLE_BUNDLE |
| `bundle_M2_disputed.json` | ValidationStamp disputed + pending_contradictions | CONSERVATIVE_POLICY | EVIDENCE_LOW_CONFIDENCE |
| `bundle_M3_emergency.json` | mode=alert + alert_latched=True + 2 BLOCK consecutivos | ALERT_POLICY | PERSISTENT_EMERGENCY |
| `bundle_M4_hard_limit_relax.json` | VisitAmendment intenta tank_minimum_pct=10 | REFUSE | HARD_LIMIT_DOMAIN |
| `bundle_M5_pollen_jurisdiction.json` | snapshot.operator_request con cambio puntual | REFUSE | JURISDICTION_POLLEN |
| `bundle_R2_emergency.json` | Igual que M3 pero `target_rhizome_id="rhizome_02"` | ALERT_POLICY | PERSISTENT_EMERGENCY |
| `bundle_M6_tool_calling_demo.json` | ALERT con `weather_digest=null` → fuerza al modelo a llamar `get_weather_history` y opcionalmente `get_recent_history` para tener material que escribir | ALERT_POLICY | PERSISTENT_EMERGENCY |
| `bundle_M7_compare_targets_demo.json` | ALERT en `rhizome_01` con hint multi-Rhizome → invita al modelo a llamar `compare_targets(rhizome_01, rhizome_02)` y emitir hipótesis "problema local, no global" con marcador de confianza explícito | ALERT_POLICY | PERSISTENT_EMERGENCY |

## M6 — propósito específico

`bundle_M6_tool_calling_demo.json` está diseñado para **forzar tool
calling en directo en demo**. Estado del bundle:

- `mode=alert`, `alert_latched=true`, `tank_pct=15` → Evaluator dispara
  ALERT_POLICY (PERSISTENT_EMERGENCY) sin ambigüedad.
- 3 `decision_receipts` BLOCK seguidos (2 por DEPOSITO_BAJO + 1 por
  ALERTA_LATCHED) → emergencia persistente clara.
- **`weather_digest: null`** → el modelo no tiene contexto meteorológico
  y para escribir un rationale completo *necesita* llamar
  `get_weather_history(plot_id)`.
- Idealmente también llama `get_recent_history(target_node_id, last_n=5)`
  para situar la ALERT en secuencia temporal y construir narrativa
  ("la situación viene degradándose desde T-5d").

Esto es **valor estratégico de demo**: muestra al jurado que el LLM
no solo redacta — sabe pedir datos cuando le faltan, y los stubs
deterministas devuelven info plausible al instante. Tool calling
ejercitado en runtime, no como capacidad latente.

## Verificación rápida

Con `meristem_node` corriendo en `:13000`:

```bash
for f in examples/bundle_*.json; do
  echo "=== $f ==="
  curl -s -X POST http://localhost:13000/visit \
    -H "Content-Type: application/json" \
    -d @"$f" | python -c "import sys,json;d=json.loads(sys.stdin.read());print('status:',d['status'],'reason:',d.get('reason_code'),'mode:',d.get('payload',{}).get('policy_packet',{}).get('mode_default') if d.get('payload') else 'n/a')"
done
```

Resultado esperado del smoke completo:

```
=== M1 ===
status: ok    reason: STABLE_BUNDLE              mode: normal
=== M2 ===
status: ok    reason: EVIDENCE_LOW_CONFIDENCE    mode: conservative
=== M3 ===
status: ok    reason: PERSISTENT_EMERGENCY       mode: alert
=== M4 ===
status: refuse reason: HARD_LIMIT_DOMAIN          mode: n/a
=== M5 ===
status: refuse reason: JURISDICTION_POLLEN        mode: n/a
```

## Para Xilema

Estos bundles son **borrador de intención** de cómo se ven los datos
de cada caso. Si crees que algún campo del snapshot/receipt/stamp
debería ser distinto para representar bien el caso desde dominio
Rhizome, dilo y ajusto. Especialmente:

- ¿Los `decision_receipts` capturan la información que Rhizome
  realmente persistiría?
- ¿La estructura del `validation_stamp` con `visit_amendment.policy_override`
  como string ("tank_minimum_pct=10") es la que vais a transportar
  desde Pollen, o prefieres dict tipado?
- ¿`pending_contradictions` lleva strings tipo "sensor_vs_observation"
  o ids de contradiction objects?

Cualquier ajuste tuyo, lo aplico en los 5 bundles + en el Evaluator
+ en los tests, sin coste.
