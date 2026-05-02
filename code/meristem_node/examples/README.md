# Bundles ejemplo Meristem-nodo (mini-batería v0)

5 bundles representativos de la mini-batería v0 acordada con Xilema
en el bloque 1 del review día 13. Cada uno dispara una de las 4 reglas
del Evaluator (5 cubre tanto JURISDICTION_POLLEN como HARD_LIMIT_DOMAIN
en la regla REFUSE).

## Casos

| File | Caso | Action esperada | reason_code |
|---|---|---|---|
| `bundle_M1_clean.json` | Bundle limpio (camino feliz) | CONFIRM_POLICY | STABLE_BUNDLE |
| `bundle_M2_disputed.json` | ValidationStamp disputed + pending_contradictions | CONSERVATIVE_POLICY | EVIDENCE_LOW_CONFIDENCE |
| `bundle_M3_emergency.json` | mode=alert + alert_latched=True + 2 BLOCK consecutivos | ALERT_POLICY | PERSISTENT_EMERGENCY |
| `bundle_M4_hard_limit_relax.json` | VisitAmendment intenta tank_minimum_pct=10 | REFUSE | HARD_LIMIT_DOMAIN |
| `bundle_M5_pollen_jurisdiction.json` | snapshot.operator_request con cambio puntual | REFUSE | JURISDICTION_POLLEN |

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
