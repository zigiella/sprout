package net.sprout.pollen.schemas

import kotlinx.serialization.Serializable

@Serializable
data class ValidationStamp(
    val status: String, // confirmed, disputed, caution
    val evidence: List<String> = emptyList(),
    val visitAmendment: VisitAmendment? = null
)

@Serializable
data class VisitAmendment(
    val policyOverride: String,
    val durationH: Int
)
