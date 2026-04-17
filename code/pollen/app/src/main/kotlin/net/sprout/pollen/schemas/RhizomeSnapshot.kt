package net.sprout.pollen.schemas

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class RhizomeSnapshot(
    @SerialName("schema_version") val schemaVersion: String = "1.0",
    @SerialName("created_at") val createdAt: String,
    @SerialName("origin_node_id") val originNodeId: String,
    @SerialName("signature") val signature: String? = null,
    
    @SerialName("snapshot_id") val snapshotId: String,
    @SerialName("mode") val mode: Mode,
    
    @SerialName("active_policy_id") val activePolicyId: String,
    @SerialName("active_policy_expires_at") val activePolicyExpiresAt: String,
    
    @SerialName("sensors") val sensors: Sensors,
    @SerialName("vision") val vision: Vision,
    @SerialName("health") val health: Health,
    
    @SerialName("last_decision_id") val lastDecisionId: String? = null,
    @SerialName("pending_contradictions") val pendingContradictions: List<String> = emptyList()
) {
    @Serializable
    data class Sensors(
        @SerialName("soil_moisture_a_pct") val soilMoistureAPct: Float,
        @SerialName("soil_moisture_b_pct") val soilMoistureBPct: Float,
        @SerialName("tank_level_pct") val tankLevelPct: Float,
        @SerialName("flow_rate_lpm") val flowRateLpm: Float,
        @SerialName("last_reading_at") val lastReadingAt: String
    )

    @Serializable
    data class Vision(
        @SerialName("last_capture_at") val lastCaptureAt: String? = null,
        @SerialName("parcel_a_status") val parcelAStatus: String? = null,
        @SerialName("parcel_b_status") val parcelBStatus: String? = null,
        @SerialName("visual_notes") val visualNotes: String? = null
    )

    @Serializable
    data class Health(
        @SerialName("cpu_temp_c") val cpuTempC: Float,
        @SerialName("cpu_load_pct") val cpuLoadPct: Float,
        @SerialName("ram_used_gb") val ramUsedGb: Float,
        @SerialName("ram_total_gb") val ramTotalGb: Float,
        @SerialName("esp32_heartbeat_ok") val esp32HeartbeatOk: Boolean,
        @SerialName("last_esp32_ack_at") val lastEsp32AckAt: String? = null
    )
}
