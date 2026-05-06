package net.sprout.pollen.schemas

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class MissionPatch(
    @SerialName("target_node_id") val targetNodeId: String,
    @SerialName("action") val action: String, // e.g., "water_extra", "skip_next_cycle", "update_budget"
    @SerialName("priority_plot") val priorityPlot: String? = null,
    @SerialName("duration_s") val durationS: Int? = null,
    @SerialName("tank_minimum_pct") val tankMinimumPct: Float? = null,
    @SerialName("budget_cap_ml") val budgetCapMl: Float? = null,
    @SerialName("min_seconds_between_events") val minSecondsBetweenEvents: Int? = null,
    @SerialName("rationale_es") val rationaleEs: String
)
