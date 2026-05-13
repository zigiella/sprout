package net.sprout.pollen.schemas

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class FieldVisit(
    @SerialName("source_pollen_id") val sourcePollenId: String,
    @SerialName("target_rhizome_id") val targetRhizomeId: String,
    @SerialName("active_policy_id") val activePolicyId: String,
    @SerialName("rhizome_snapshot") val rhizomeSnapshot: RhizomeSnapshot,
    
    @SerialName("bundle_id") val bundleId: String? = null,
    @SerialName("received_at") val receivedAt: String? = null,
    @SerialName("decision_receipts") val decisionReceipts: List<DecisionReceipt> = emptyList()
)
