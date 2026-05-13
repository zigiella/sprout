package net.sprout.pollen.schemas

enum class EvaluationAction {
    APPLY_AS_IS,
    APPLY_CONSERVATIVE,
    REFUSE_RETRY,
    REFUSE_HARD
}

data class EvaluationResult(
    val action: EvaluationAction,
    val reasonCode: String,
    val details: String,
    val policyPacket: PolicyPacket? = null
)
