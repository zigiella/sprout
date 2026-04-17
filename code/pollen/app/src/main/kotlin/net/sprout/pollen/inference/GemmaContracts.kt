package net.sprout.pollen.inference

import net.sprout.pollen.schemas.ContradictionAlert
import net.sprout.pollen.schemas.PolicyDelta

sealed class AuditEvent {
    data class Token(val s: String) : AuditEvent()
    data class Done(val result: AuditResult) : AuditEvent()
}

sealed class AuditResult {
    data class NoDiscrepancy(val rationale: String) : AuditResult()
    data class Discrepancy(
        val alert: ContradictionAlert,
        val suggestedDelta: PolicyDelta?
    ) : AuditResult()
}
