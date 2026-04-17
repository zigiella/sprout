package net.sprout.pollen.schemas

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.JsonElement

@Serializable
data class DecisionReceipt(
    @SerialName("schema_version") val schemaVersion: String = "1.0",
    @SerialName("created_at") val createdAt: String,
    @SerialName("origin_node_id") val originNodeId: String,
    @SerialName("signature") val signature: String? = null,
    
    @SerialName("decision_id") val decisionId: String,
    @SerialName("snapshot_id") val snapshotId: String,
    @SerialName("active_policy_id") val activePolicyId: String,
    
    @SerialName("action") val action: ActionType,
    @SerialName("action_params") val actionParams: Map<String, JsonElement>,
    
    @SerialName("rationale_short") val rationaleShort: String,
    @SerialName("rationale_full") val rationaleFull: String,
    
    @SerialName("policy_refs") val policyRefs: List<String>,
    
    @SerialName("contradictions") val contradictions: List<String>,
    @SerialName("confidence") val confidence: Float,
    
    @SerialName("executed") val executed: Boolean,
    @SerialName("execution_details") val executionDetails: ExecutionDetails? = null,
    @SerialName("blocked_reason") val blockedReason: String? = null
) {
    @Serializable
    data class ExecutionDetails(
        @SerialName("sent_to_esp32_at") val sentToEsp32At: String,
        @SerialName("esp32_ack_at") val esp32AckAt: String,
        @SerialName("esp32_ack_status") val esp32AckStatus: String,
        @SerialName("actual_duration_s") val actualDurationS: Float,
        @SerialName("flow_observed_lpm") val flowObservedLpm: Float,
        @SerialName("estimated_liters_actual") val estimatedLitersActual: Float
    )
}
