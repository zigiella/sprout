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

    // Removidos: testWeatherPacketRoundTrip + testPolicyDeltaRoundTrip
    // Estos schemas (WeatherPacket, PolicyDelta) se eliminaron en commit
    // 56dafaf como parte de la migracion a contratos V2 (WeatherDigest,
    // MissionPatch, PolicyPacket). testV2SchemasRoundTrip cubre los nuevos.

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
        assertEquals(500f, missionPatch.budgetCapMl)

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
