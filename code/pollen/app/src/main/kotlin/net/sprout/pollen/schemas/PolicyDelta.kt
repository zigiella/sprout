package net.sprout.pollen.schemas

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.JsonElement

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
