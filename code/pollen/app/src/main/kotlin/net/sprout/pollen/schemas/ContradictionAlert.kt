package net.sprout.pollen.schemas

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.JsonElement

@Serializable
data class ContradictionAlert(
    @SerialName("schema_version") val schemaVersion: String = "1.0",
    @SerialName("created_at") val createdAt: String,
    @SerialName("origin_node_id") val originNodeId: String,
    @SerialName("signature") val signature: String? = null,
    
    @SerialName("alert_id") val alertId: String,
    @SerialName("target_node_id") val targetNodeId: String,
    @SerialName("contradiction_type") val contradictionType: ContradictionType,
    @SerialName("severity") val severity: Severity,
    
    @SerialName("observed_at") val observedAt: String,
    @SerialName("evidence") val evidence: Map<String, JsonElement>, // Arbitrary JSON, but could be strongly typed per type
    
    @SerialName("recommended_action") val recommendedAction: String? = null,
    @SerialName("expires_at") val expiresAt: String,
    @SerialName("rationale") val rationale: String? = null
)
