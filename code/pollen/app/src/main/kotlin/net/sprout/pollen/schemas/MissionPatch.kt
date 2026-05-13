package net.sprout.pollen.schemas

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class MissionPatch(
    @SerialName("target_node_id") val targetNodeId: String = "",
    @SerialName("action") val action: String = "",
    @SerialName("priority_plot") val priorityPlot: String? = null,
    @SerialName("duration_s") val durationS: Int? = null,
    @SerialName("tank_minimum_pct") val tankMinimumPct: Float? = null,
    @SerialName("budget_cap_ml") val budgetCapMl: Float? = null,
    @SerialName("min_seconds_between_events") val minSecondsBetweenEvents: Int? = null,
    @SerialName("rationale_es") val rationaleEs: String = "",
    @SerialName("schema_version") val schemaVersion: String = "2.0",
    @SerialName("patch_op") val patchOp: String = "",
    @SerialName("horizon_h") val horizonH: Int? = null,
    @SerialName("avoid_hours") val avoidHours: List<String>? = null,
    @SerialName("goal_mode") val goalMode: String? = null,
    @SerialName("operator_note") val operatorNote: String? = null
)
