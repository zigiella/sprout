package net.sprout.pollen.schemas

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class FieldVisit(
    @SerialName("snapshot") val snapshot: RhizomeSnapshot,
    @SerialName("receipts") val receipts: List<DecisionReceipt>
)
