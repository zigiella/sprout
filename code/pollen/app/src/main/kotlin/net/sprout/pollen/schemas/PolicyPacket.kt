package net.sprout.pollen.schemas

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class PolicyPacket(
    @SerialName("schema_version") val schemaVersion: String = "1.0",
    @SerialName("created_at") val createdAt: String? = null,
    @SerialName("origin_node_id") val originNodeId: String? = null,
    @SerialName("signature") val signature: String? = null,
    
    @SerialName("policy_id") val policyId: String,
    @SerialName("target_node_id") val targetNodeId: String,
    @SerialName("valid_until") val validUntil: String,
    
    @SerialName("version_chain") val versionChain: List<String>? = null,
    @SerialName("mode_default") val modeDefault: String, // Cambiado a String para soportar "normal"
    
    @SerialName("rules") val rules: Rules,
    
    @SerialName("rationale") val rationale: String? = null,
    @SerialName("notes") val notes: String? = null,
    
    @SerialName("policy_origin") val policyOrigin: String? = null,
    @SerialName("policy_scope") val policyScope: String? = null
) {
    @Serializable
    data class Rules(
        // Campos legacy o específicos de Pollen
        @SerialName("watering_window") val wateringWindow: WateringWindow? = null,
        @SerialName("soil_moisture_thresholds") val soilMoistureThresholds: Map<String, Threshold>? = null,
        @SerialName("max_watering_duration_s") val maxWateringDurationS: Int? = null,
        @SerialName("daily_water_budget_liters") val dailyWaterBudgetLiters: Float? = null,
        @SerialName("tank_minimum_pct") val tankMinimumPct: Float? = null,
        @SerialName("require_vision_confirmation") val requireVisionConfirmation: Boolean? = null,
        @SerialName("conservative_triggers") val conservativeTriggers: List<String>? = null,
        
        // Campos nuevos de Meristem
        @SerialName("soil_dry_threshold_pct") val soilDryThresholdPct: Float? = null,
        @SerialName("max_seconds_per_event") val maxSecondsPerEvent: Int? = null,
        @SerialName("watering_windows") val wateringWindows: List<String>? = null,
        @SerialName("daily_budget_ml") val dailyBudgetMl: Int? = null
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
