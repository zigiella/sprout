package net.sprout.pollen.schemas

import kotlinx.serialization.Serializable

@Serializable
data class MissionPatch(
    val schemaVersion: String = "2.0",
    val patchOp: String, // apply, update, revoke
    val horizonH: Int? = null,
    val priorityPlot: String? = null,
    val budgetCapMl: Int? = null,
    val avoidHours: List<String>? = null,
    val goalMode: String? = null,
    val operatorNote: String? = null
)
