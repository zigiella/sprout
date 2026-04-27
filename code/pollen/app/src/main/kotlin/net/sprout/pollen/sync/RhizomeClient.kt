package net.sprout.pollen.sync

import net.sprout.pollen.schemas.DecisionReceipt
import net.sprout.pollen.schemas.RhizomeSnapshot

interface RhizomeClient {
    suspend fun getStatus(): Map<String, String>
    suspend fun getLatestSnapshot(): RhizomeSnapshot
    suspend fun getReceipts(since: String? = null): List<DecisionReceipt>
    suspend fun explainDecision(id: String): String
}
