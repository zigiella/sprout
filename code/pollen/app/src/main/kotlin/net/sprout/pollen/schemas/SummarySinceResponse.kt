package net.sprout.pollen.schemas

import kotlinx.serialization.Serializable

@Serializable
data class SummarySinceResponse(
    val headline: String,
    val summary: String,
    val highlights: List<String>,
    val recommendation: String,
    val severity: String
)
