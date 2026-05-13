package net.sprout.pollen.schemas

import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Test

class RoundTripTest {

    private val format = Json { 
        ignoreUnknownKeys = true 
        encodeDefaults = true
        prettyPrint = false
        classDiscriminator = "type" // if we needed polymorphism later
    }

    @Test
    fun testRhizomeSnapshotRoundTrip() {
        val rawJson = """
            {
              "schema_version": "1.0",
              "created_at": "2026-04-16T14:32:05Z",
              "origin_node_id": "rhizome_01",
              "signature": null,
              "snapshot_id": "snap_rhizome_01_20260416T143205_a3f2",
              "mode": "normal",
              "active_policy_id": "pkt_rhizome_01_20260416T083015_d5e7",
              "active_policy_expires_at": "2026-04-17T08:30:15Z",
              "sensors": {
                "soil_moisture_a_pct": 38.2,
                "soil_moisture_b_pct": 41.7,
                "tank_level_pct": 72.0,
                "flow_rate_lpm": 0.0,
                "last_reading_at": "2026-04-16T14:31:58Z"
              },
              "vision": {
                "last_capture_at": "2026-04-16T14:25:00Z",
                "parcel_a_status": "healthy",
                "parcel_b_status": "healthy",
                "visual_notes": "hojas firmes, color normal en ambas parcelas"
              },
              "health": {
                "cpu_temp_c": 58.4,
                "cpu_load_pct": 41.0,
                "ram_used_gb": 4.8,
                "ram_total_gb": 7.4,
                "esp32_heartbeat_ok": true,
                "last_esp32_ack_at": "2026-04-16T14:32:00Z"
              },
              "last_decision_id": "rec_rhizome_01_20260416T143000_91ba",
              "pending_contradictions": []
            }
        """.trimIndent()

        // Test Deserialization
        val obj = format.decodeFromString<RhizomeSnapshot>(rawJson)
        assertNotNull(obj)
        assertEquals("snap_rhizome_01_20260416T143205_a3f2", obj.snapshotId)
        assertEquals(Mode.NORMAL, obj.mode)

        // Test Serialization
        val encoded = format.encodeToString(obj)
        val obj2 = format.decodeFromString<RhizomeSnapshot>(encoded)
        assertEquals(obj, obj2)
    }

    @Test
    fun testWeatherPacketRoundTrip() {
        val rawJson = """
            {
              "schema_version": "1.0",
              "created_at": "2026-04-16T12:15:00Z",
              "origin_node_id": "pollen_01",
              "signature": null,
              "packet_id": "pkt_weather_pollen_01_20260416T121500_e7a2",
              "observed_at": "2026-04-16T11:45:00Z",
              "observed_by_node_id": "rhizome_02",
              "provenance": "ferried",
              "valid_until": "2026-04-16T17:45:00Z",
              "location": {
                "lat": 42.1828,
                "lon": 1.9931,
                "altitude_m": 1100,
                "label": "Castellar de n'Hug, parcela A"
              },
              "measurements": {
                "temperature_c": 18.4,
                "humidity_rel_pct": 62.0,
                "pressure_hpa": 1013.5,
                "rain_last_1h_mm": 0.0,
                "rain_last_24h_mm": 2.4,
                "wind_speed_kmh": 8.2,
                "wind_direction_deg": 220,
                "solar_radiation_wm2": 485,
                "uv_index": 4.8
              },
              "confidence": 0.85,
              "notes": "Estacion WS90 en rhizome_02. Ultima calibracion hace 3 semanas."
            }
        """.trimIndent()

        val obj = format.decodeFromString<WeatherPacket>(rawJson)
        assertNotNull(obj)
        assertEquals(WeatherProvenance.FERRIED, obj.provenance)
        assertEquals(62.0f, obj.measurements.humidityRelPct)

        val encoded = format.encodeToString(obj)
        val obj2 = format.decodeFromString<WeatherPacket>(encoded)
        assertEquals(obj, obj2)
    }

    @Test
    fun testPolicyDeltaRoundTrip() {
        val rawJson = """
            {
              "schema_version": "1.0",
              "created_at": "2026-04-16T15:00:00Z",
              "origin_node_id": "meristem_01",
              "signature": null,
              "delta_id": "delta_meristem_01_20260416T150000_c92d",
              "target_node_id": "rhizome_01",
              "base_policy_id": "pkt_rhizome_01_20260416T083015_d5e7",
              "patches": [
                {
                  "op": "replace",
                  "path": "rules.soil_moisture_thresholds.parcel_b.min_pct",
                  "value": 32.0
                },
                {
                  "op": "replace",
                  "path": "rules.daily_water_budget_liters",
                  "value": 10.0
                },
                {
                  "op": "add",
                  "path": "rules.conservative_triggers",
                  "value": "humidity_below_25_forecast"
                }
              ],
              "rationale": "Forecast Pollen trae humedad baja esperada en 24h. Subir budget y anadir trigger.",
              "ttl_seconds": 86400,
              "priority": "normal"
            }
        """.trimIndent()

        val obj = format.decodeFromString<PolicyDelta>(rawJson)
        assertNotNull(obj)
        assertEquals("replace", obj.patches[0].op)

        val encoded = format.encodeToString(obj)
        val obj2 = format.decodeFromString<PolicyDelta>(encoded)
        assertEquals(obj, obj2)
    }

    @Test
    fun testV2SchemasRoundTrip() {
        val missionPatchJson = """
            {
                "schema_version": "2.0",
                "patch_op": "apply",
                "horizon_h": 24,
                "priority_plot": "parcel_a",
                "budget_cap_ml": 500,
                "avoid_hours": ["12:00", "13:00"],
                "goal_mode": "conservative",
                "operator_note": "Ahorrar agua"
            }
        """.trimIndent()
        val missionPatch = format.decodeFromString<MissionPatch>(missionPatchJson)
        assertEquals("apply", missionPatch.patchOp)
        assertEquals(500, missionPatch.budgetCapMl)

        val validationStampJson = """
            {
                "status": "caution",
                "evidence": ["sensor_a is dry"],
                "visit_amendment": {
                    "policy_override": "force_water",
                    "duration_h": 2
                }
            }
        """.trimIndent()
        val validationStamp = format.decodeFromString<ValidationStamp>(validationStampJson)
        assertEquals("caution", validationStamp.status)
        assertEquals(2, validationStamp.visitAmendment?.durationH)

        val weatherDigestJson = """
            {
                "is_stale": false,
                "summary": "Clear skies",
                "rain_expected_mb": 0.0,
                "temperature_range_c": "15-25"
            }
        """.trimIndent()
        val weatherDigest = format.decodeFromString<WeatherDigest>(weatherDigestJson)
        assertEquals("Clear skies", weatherDigest.summary)
        assertEquals(0.0f, weatherDigest.rainExpectedMb)
    }
}
