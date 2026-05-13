package net.sprout.pollen.schemas

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class ValidationStamp(
    @SerialName("status") val status: String, // confirmed, disputed, caution
    @SerialName("evidence") val evidence: List<String> = emptyList(),
    @SerialName("visit_amendment") val visitAmendment: VisitAmendment? = null
)

@Serializable
data class VisitAmendment(
    @SerialName("policy_override") val policyOverride: String,
    @SerialName("duration_h") val durationH: Int
)
