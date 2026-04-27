package net.sprout.pollen.schemas

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class MissionPatch(
    @SerialName("schema_version") val schemaVersion: String = "2.0",
    @SerialName("patch_op") val patchOp: String, // apply, update, revoke
    @SerialName("horizon_h") val horizonH: Int? = null,
    @SerialName("priority_plot") val priorityPlot: String? = null,
    @SerialName("budget_cap_ml") val budgetCapMl: Int? = null,
    @SerialName("avoid_hours") val avoidHours: List<String>? = null,
    @SerialName("goal_mode") val goalMode: String? = null,
    @SerialName("operator_note") val operatorNote: String? = null
)
