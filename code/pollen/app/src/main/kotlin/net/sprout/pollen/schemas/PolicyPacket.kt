package net.sprout.pollen.schemas

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.JsonElement

@Serializable
data class PolicyPacket(
    @SerialName("schema_version") val schemaVersion: String = "1.0",
    @SerialName("created_at") val createdAt: String,
    @SerialName("origin_node_id") val originNodeId: String,
    @SerialName("signature") val signature: String? = null,
    
    @SerialName("policy_id") val policyId: String,
    @SerialName("target_node_id") val targetNodeId: String,
    @SerialName("valid_until") val validUntil: String,
    
    @SerialName("version_chain") val versionChain: List<String>,
    @SerialName("mode_default") val modeDefault: Mode,
    
    @SerialName("rules") val rules: Rules,
    
    @SerialName("rationale") val rationale: String? = null,
    @SerialName("notes") val notes: String? = null
) {
    @Serializable
    data class Rules(
        @SerialName("watering_window") val wateringWindow: WateringWindow,
        @SerialName("soil_moisture_thresholds") val soilMoistureThresholds: Map<String, Threshold>,
        @SerialName("max_watering_duration_s") val maxWateringDurationS: Int,
        @SerialName("daily_water_budget_liters") val dailyWaterBudgetLiters: Float,
        @SerialName("tank_minimum_pct") val tankMinimumPct: Float,
        @SerialName("require_vision_confirmation") val requireVisionConfirmation: Boolean,
        @SerialName("conservative_triggers") val conservativeTriggers: List<String>
    )

    @Serializable
    data class WateringWindow(
        @SerialName("start_hour_local") val startHourLocal: Int,
        @SerialName("end_hour_local") val endHourLocal: Int
    )

    @Serializable
    data class Threshold(
        @SerialName("min_pct") val minPct: Float,
        @SerialName("target_pct") val targetPct: Float
    )
}

@Serializable
data class PolicyDelta(
    @SerialName("schema_version") val schemaVersion: String = "1.0",
    @SerialName("created_at") val createdAt: String,
    @SerialName("origin_node_id") val originNodeId: String,
    @SerialName("signature") val signature: String? = null,
    
    @SerialName("delta_id") val deltaId: String,
    @SerialName("target_node_id") val targetNodeId: String,
    @SerialName("base_policy_id") val basePolicyId: String,
    
    @SerialName("patches") val patches: List<Patch>,
    
    @SerialName("rationale") val rationale: String? = null,
    @SerialName("ttl_seconds") val ttlSeconds: Int,
    @SerialName("priority") val priority: String // "low", "normal", "high", "critical"
) {
    @Serializable
    data class Patch(
        @SerialName("op") val op: String, // "replace", "add", "remove"
        @SerialName("path") val path: String,
        @SerialName("value") val value: JsonElement? = null
    )
}
