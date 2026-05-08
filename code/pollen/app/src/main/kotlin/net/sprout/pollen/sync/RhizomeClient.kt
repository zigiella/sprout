package net.sprout.pollen.sync

import net.sprout.pollen.schemas.DecisionReceipt
import net.sprout.pollen.schemas.PolicyPacket
import net.sprout.pollen.schemas.RhizomeSnapshot

interface RhizomeClient {
    suspend fun getSnapshot(): RhizomeSnapshot
    suspend fun getDecisionReceipt(): DecisionReceipt
    suspend fun pushPolicy(packet: PolicyPacket): Boolean
    
    suspend fun getStatus(): Map<String, String>
    suspend fun getLatestSnapshot(): RhizomeSnapshot
    suspend fun getReceipts(since: String? = null): List<DecisionReceipt>
    suspend fun explainDecision(id: String, locale: String = "es"): String
    suspend fun getSummarySince(since: String? = null, locale: String = "es"): net.sprout.pollen.schemas.SummarySinceResponse
}
