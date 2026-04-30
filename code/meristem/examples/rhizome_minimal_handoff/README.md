# Rhizome minimal handoff for Meristem MVP

Fixtures prepared by Xilema on day 15 so Meristem can exercise the minimum
end-to-end path without waiting for live Rhizome APIs.

This package is intentionally pragmatic: current Meristem code accepts evidence
as individual `/ingest` envelopes plus policy/delta payloads. The future
`FieldVisit` / `SyncBundle` v2 shape is documented in `docs/20_data_contracts.md`
but is not implemented in shared Pydantic schemas yet.

## Files

- `active_policy_seed.json`: safe baseline `PolicyPacket` for `rhizome_01`.
- `ingest_rhizome_snapshot_tank_low.json`: `/ingest` envelope with local state.
- `ingest_decision_receipt_tank_low.json`: `/ingest` envelope with physical block.
- `ra04_safety_downgrade_delta.json`: unsafe policy delta that lowers
  `rules.tank_minimum_pct` below the ESP32 hard limit.

## Expected flow

1. Seed `active_policy_seed.json` into Meristem persistence as active policy.
2. POST the two `ingest_*.json` envelopes to `/ingest`.
3. POST `ra04_safety_downgrade_delta.json` to `/deltas/propose`.
4. Expected result: HTTP 422 with `reason=violates_safety_rule` and a violation
   on `rules.tank_minimum_pct`.

## Architectural invariant

Meristem may recommend stricter policy, but it must never reduce hard limits
owned by ESP32 firmware. Pattern:

`lo fisico manda, Rhizome arbitra, Pollen media, Meristem afina`.
