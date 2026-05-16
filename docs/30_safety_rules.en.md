# Safety rules — v2

## 1. Governing principle

The AI can propose.
Only the physical layer can authorize execution.

## 2. Non-negotiable rules

### 2.1 Low tank

If `tank_level_pct` falls below the minimum:

- no irrigation cycle is started,
- the rejection is logged,
- the system transitions to a prudent mode or alert state depending on context.

### 2.2 Missing heartbeat

If the ESP32 does not receive a recent heartbeat from the Jetson:

- it accepts no new irrigation commands,
- it holds actuators closed.

### 2.3 Maximum event duration

Every irrigation command carries a hard upper bound in seconds.

### 2.4 No flow detected

If the pump or valve activates and no expected flow appears:

- cut,
- alert,
- block any immediate retry.

### 2.5 Safe startup

After a reboot of either the ESP32 or the Jetson:

- pump off,
- valves closed,
- no automatic resumption of irrigation.

### 2.6 Explicit refusal

Every invalid command must produce a legible reason. The five canonical codes are:

- `TANK_LOW`
- `JETSON_HEARTBEAT_LOST`
- `EVENT_DURATION_OUT_OF_RANGE`
- `NO_FLOW_DETECTED`
- `ALERT_LATCHED`

## 3. Rhizome's prudence rules

Even when the ESP32 authorizes a command on physical grounds, Rhizome must degrade to a conservative mode if:

- the active policy has expired,
- critical sensor data is stale,
- the most recent visit disputed the local state,
- the remaining water budget is uncertain,
- a weather digest changed the context and no confirmation has arrived yet.

## 4. Authority priority

When sources conflict, authority flows in this order (highest first):

1. physical stop / alert latched
2. ESP32 hard limits
3. Rhizome's active policy
4. Pollen `VisitAmendment`
5. `MissionPatch`
6. non-binding suggestions

## 5. Video demonstration rule

The submission video must show at least one case where:

- the AI proposes,
- the physical layer blocks,
- and the block is explained clearly.

That moment increases trust and credibility.

---

## Note on language

This is the canonical English version. The Spanish original is preserved at [`30_safety_rules.md`](30_safety_rules.md) as evidence of the working language of the team. The five canonical refusal codes are identifiers in code and are not translated.
