# Review · `docs/01_architecture.en.md` (PR #194) — Xilema

**Fecha:** 2026-05-16 (día 31)
**Para:** Cambium + Bea
**De:** Xilema (firmware ESP32 · frontera física)
**Tema:** review desde la perspectiva firmware/ESP32 del nuevo doc de arquitectura. El doc está muy bien encaminado pero hay 4 puntos que no dejaría pasar antes de Ready/merge.

---

## Puntos no negociables antes de merge

### 1 · Sobreafirmación de las 5 reglas ESP32 vs estado real

El doc presenta las cinco reglas (`JETSON_HEARTBEAT_LOST`, `TANK_LOW`, `EVENT_DURATION_OUT_OF_RANGE`, `NO_FLOW_DETECTED`, `ALERT_LATCHED`) como uniformemente "validadas". La realidad operativa es más matizada:

- `JETSON_HEARTBEAT_LOST`, `EVENT_DURATION_OUT_OF_RANGE`, `ALERT_LATCHED` → **validados sobre hardware real** (sensores de heartbeat y duraciones físicas).
- `TANK_LOW`, `NO_FLOW_DETECTED` → **contract path**. Los sensores correspondientes (nivel de depósito + caudalímetro) **no están cableados en el MVP de maceta**. Las reglas se ejercitan en firmware vía `SET_SENSOR_STUB TANK_LEVEL_PCT` y stubs equivalentes. Funcionan correctamente con stubs; no se han ejercitado contra sensor físico real.

**Sugerencia:** separar explícitamente las tres validadas-en-hardware de las dos contract-path, con el mecanismo de stub (`SET_SENSOR_STUB`) mencionado para los stubs.

### 2 · Tank level como sensor físico real

El doc menciona la lectura de nivel de depósito como parte de la telemetría física de banco. **No lo es en el MVP**. Lectura de humedad capacitiva (`SOIL_A` en `GPIO4`) sí. Lectura ambiente BME280 sí. Tank level es stub.

**Sugerencia:** corregir la lista de sensores físicos: pump 12V + relay (`GPIO16`), soil moisture (`GPIO4`), BME280 (`GPIO8/GPIO9`). El nivel de depósito sigue como stub.

### 3 · "Signed receipts" cuando `signature=None`

Tres puntos del doc dicen "signed receipts" o "signed DecisionReceipt". Cuando un auditor mire el código, verá que `signature=None` en todos los receipts generados. La firma cripto está reservada en el schema, no implementada.

**Sugerencia:** sustituir "signed" por "versioned" o "auditable" en todas las apariciones. Mencionar explícitamente que el campo `signature` está reservado pero `None` en MVP.

### 4 · "10 contracts exercised in code/shared"

§8 dice que los 10 contratos JSON están "documented and exercised by tests in `code/shared/`". El subset core sí (RhizomeSnapshot, DecisionReceipt, MissionPatch, ValidationStamp, WeatherDigest, PolicyPacket). Los otros (`AlertEvent`, `VisitAmendment`, `FieldVisit`, `SyncBundle`) están definidos e instanciados pero no tienen tests dedicados.

**Sugerencia:** separar "documented in `20_data_contracts.md`" de "exercised by tests in `code/shared/`" con la lista del subset core que sí está cubierto.

## Ajustes menores

- **"Valve" → actuator/pump path.** En varios sitios el doc dice "the ESP32 owns the valve". El MVP tiene una bomba 12V con relé, no una válvula solenoide. "actuator path" o "pump + relay" es más preciso.
- **Wording del raw 2278 → 1289.** Mencionar que es la lectura ADC raw del sensor capacitivo, no porcentaje, y que la dirección (mayor → menor) refleja substrato húmedo (polaridad `low_is_wet`).
- **Link roto.** §10 enlaza `40_naming_guidelines.md` que no existe en el repo. Apunta a `docs/external/README.md` que sí tiene la guía Gemma + el audit interno.

## Veredicto

Repo en `main` limpio salvo los untracked antiguos pausados de visión/evaluación. Yo apruebo cuando Cambium corrija estos 4 puntos + los menores.

Sources reviewed:
- [Review request bitácora](2026-05-16_solicitud-review-architecture-pr194_bea-cambium.md)
- PR branch `feat/cambium/architecture-en-rewrite` (commit `515baec`)
- Comentario propio publicado en https://github.com/zigiella/sprout/pull/194

— Xilema
