package net.sprout.pollen.sync

import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonPrimitive
import net.sprout.pollen.schemas.*

class RhizomeMockClient {

    suspend fun getStatus(): Map<String, String> {
        return mapOf(
            "status" to "online",
            "uptime_s" to "3600",
            "version" to "0.2.0"
        )
    }

    suspend fun getLatestSnapshot(): RhizomeSnapshot {
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

    suspend fun getReceipts(since: String? = null): List<DecisionReceipt> {
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
            rationaleShort = "Humedad A en 38%, por debajo del umbral 45%. Dentro de ventana de riego. Deposito al 72%.",
            rationaleFull = "El snapshot reciente muestra humedad parcela A al 38.2%, umbral minimo 45% segun politica vigente pkt_...d5e7. Hora local 08:32 dentro de ventana 06-09. Deposito al 72%, muy por encima del minimo 15%. Vision confirma planta sana. Sin alertas activas. Se autoriza riego parcela A por 30s.",
            policyRefs = listOf(
                "rules.soil_moisture_thresholds.parcel_a.min_pct",
                "rules.watering_window",
                "rules.tank_minimum_pct"
            ),
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
        )
    }

    suspend fun explainDecision(id: String): String {
        return "El modelo Gemma 4 E2B en Rhizome decidió regar porque la humedad del suelo estaba por debajo del umbral de la política activa, y había agua suficiente en el depósito."
    }
}
