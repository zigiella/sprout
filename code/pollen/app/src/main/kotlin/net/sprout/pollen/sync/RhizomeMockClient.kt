package net.sprout.pollen.sync

import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonPrimitive
import net.sprout.pollen.schemas.*

class RhizomeMockClient : RhizomeClient {

    override suspend fun getStatus(): Map<String, String> {
        return mapOf(
            "status" to "online",
            "uptime_s" to "3600",
            "version" to "0.2.0"
        )
    }

    override suspend fun getLatestSnapshot(): RhizomeSnapshot {
        return RhizomeSnapshot(
            schemaVersion = "1.0",
            createdAt = "2026-04-16T14:32:05Z",
            originNodeId = "rhizome_01",
            snapshotId = "snap_rhizome_01_20260416T143205_a3f2",
            mode = Mode.NORMAL,
            activePolicyId = "pkt_rhizome_01_20260416T083015_d5e7",
            activePolicyExpiresAt = "2026-04-17T08:30:15Z",
            sensors = RhizomeSnapshot.Sensors(
                soilMoistureAPct = 38.2f,
                soilMoistureBPct = 41.7f,
                tankLevelPct = 72.0f,
                flowRateLpm = 0.0f,
                lastReadingAt = "2026-04-16T14:31:58Z"
            ),
            vision = RhizomeSnapshot.Vision(
                lastCaptureAt = "2026-04-16T14:25:00Z",
                parcelAStatus = "healthy",
                parcelBStatus = "healthy",
                visualNotes = "hojas firmes, color normal en ambas parcelas"
            ),
            health = RhizomeSnapshot.Health(
                cpuTempC = 58.4f,
                cpuLoadPct = 41.0f,
                ramUsedGb = 4.8f,
                ramTotalGb = 7.4f,
                esp32HeartbeatOk = true,
                lastEsp32AckAt = "2026-04-16T14:32:00Z"
            ),
            lastDecisionId = "rec_rhizome_01_20260416T143000_91ba"
        )
    }

    override suspend fun getReceipts(since: String?, locale: String): List<DecisionReceipt> {
        return listOf(
            DecisionReceipt(
                schemaVersion = "1.0",
                createdAt = "2026-04-16T14:30:10Z",
                originNodeId = "rhizome_01",
                decisionId = "rec_rhizome_01_20260416T143010_91ba",
                snapshotId = "snap_rhizome_01_20260416T143005_a3f2",
                activePolicyId = "pkt_rhizome_01_20260416T083015_d5e7",
                action = ActionType.WATER_A,
                actionParams = mapOf(
                    "duration_s" to JsonPrimitive(30),
                    "expected_liters" to JsonPrimitive(1.5f)
                ),
                rationaleShort = "Moisture A at 38%, below 45% threshold.",
                rationaleFull = "Recent snapshot shows plot A moisture at 38.2%, minimum threshold 45%.",
                policyRefs = listOf("rules.soil_moisture_thresholds.parcel_a.min_pct"),
                contradictions = emptyList(),
                confidence = 0.87f,
                executed = true,
                executionDetails = DecisionReceipt.ExecutionDetails(
                    sentToEsp32At = "2026-04-16T14:30:10Z",
                    esp32AckAt = "2026-04-16T14:30:11Z",
                    esp32AckStatus = "OK",
                    actualDurationS = 30.2f,
                    flowObservedLpm = 3.1f,
                    estimatedLitersActual = 1.56f
                )
            ),
            DecisionReceipt(
                schemaVersion = "1.0",
                createdAt = "2026-04-15T08:15:00Z",
                originNodeId = "rhizome_01",
                decisionId = "rec_rhizome_01_20260415T081500_82cd",
                snapshotId = "snap_rhizome_01_20260415T081400_b4e1",
                activePolicyId = "pkt_rhizome_01_20260414T090000_c3d6",
                action = ActionType.SKIP,
                actionParams = emptyMap(),
                rationaleShort = "Rain forecast in 2h. Watering cancelled.",
                rationaleFull = "Moisture at 46%. WeatherDigest warns of imminent rain.",
                policyRefs = listOf("rules.weather_override.rain_expected"),
                contradictions = emptyList(),
                confidence = 0.95f,
                executed = true,
                executionDetails = null
            ),
            DecisionReceipt(
                schemaVersion = "1.0",
                createdAt = "2026-04-14T19:45:20Z",
                originNodeId = "rhizome_01",
                decisionId = "rec_rhizome_01_20260414T194520_73ef",
                snapshotId = "snap_rhizome_01_20260414T194500_c5f2",
                activePolicyId = "pkt_rhizome_01_20260414T090000_c3d6",
                action = ActionType.WATER_B,
                actionParams = mapOf(
                    "duration_s" to JsonPrimitive(45),
                    "expected_liters" to JsonPrimitive(2.2f)
                ),
                rationaleShort = "Moisture B critical (22%). Executing emergency watering.",
                rationaleFull = "Plot B moisture dropped to 22%, triggering safeguard rule.",
                policyRefs = listOf("rules.soil_moisture_thresholds.parcel_b.critical_pct"),
                contradictions = emptyList(),
                confidence = 0.99f,
                executed = true,
                executionDetails = DecisionReceipt.ExecutionDetails(
                    sentToEsp32At = "2026-04-14T19:45:20Z",
                    esp32AckAt = "2026-04-14T19:45:21Z",
                    esp32AckStatus = "OK",
                    actualDurationS = 45.0f,
                    flowObservedLpm = 3.0f,
                    estimatedLitersActual = 2.25f
                )
            ),
            DecisionReceipt(
                schemaVersion = "1.0",
                createdAt = "2026-04-13T07:10:05Z",
                originNodeId = "rhizome_01",
                decisionId = "rec_rhizome_01_20260413T071005_12ab",
                snapshotId = "snap_rhizome_01_20260413T070900_d6a3",
                activePolicyId = "pkt_rhizome_01_20260410T100000_e7b8",
                action = ActionType.BLOCK,
                actionParams = emptyMap(),
                rationaleShort = "Insufficient tank level (8%) for watering cycle.",
                rationaleFull = "Watering attempt on plot A blocked by empty pump failsafe.",
                policyRefs = listOf("rules.failsafe_defaults.tank_minimum_pct"),
                contradictions = emptyList(),
                confidence = 1.0f,
                executed = true,
                executionDetails = null
            )
        )
    }

    override suspend fun getSnapshot(): RhizomeSnapshot = getLatestSnapshot()
    override suspend fun getDecisionReceipt(): DecisionReceipt = getReceipts().first()

    override suspend fun pushPolicy(packet: PolicyPacket): Boolean {
        // Mock successful push
        return true
    }

    override suspend fun explainDecision(id: String, locale: String): String {
        kotlinx.coroutines.delay(1200) // Simular latencia real de red y generación LLM
        if (locale == "es") {
            return "El modelo Gemma 4 E2B en Rhizome decidió regar porque la humedad del suelo estaba por debajo del umbral de la política activa, y había agua suficiente en el depósito."
        } else {
            return "The Gemma 4 E2B model on Rhizome decided to water because soil moisture was below the active policy threshold, and there was enough water in the tank."
        }
    }

    override suspend fun getSummarySince(since: String?, locale: String): net.sprout.pollen.schemas.SummarySinceResponse {
        kotlinx.coroutines.delay(1000)
        return net.sprout.pollen.schemas.SummarySinceResponse(
            headline = if (locale == "es") "2 alertas resueltas" else "2 alerts resolved",
            summary = if (locale == "es") "El nivel de humedad del suelo bajó peligrosamente pero se compensó con el riego nocturno. El tanque requiere atención." else "Soil moisture dropped dangerously but was compensated by night watering. Tank requires attention.",
            highlights = if (locale == "es") listOf("Riego de emergencia: +15%", "Alerta: Tanque bajo") else listOf("Emergency watering: +15%", "Alert: Low tank"),
            recommendation = if (locale == "es") "Rellenar tanque principal." else "Refill main tank.",
            severity = "warning"
        )
    }
}
