package net.sprout.pollen.sync

import net.sprout.pollen.schemas.DecisionReceipt
import net.sprout.pollen.schemas.PolicyPacket
import net.sprout.pollen.schemas.RhizomeSnapshot

interface RhizomeClient {
    suspend fun getSnapshot(): RhizomeSnapshot
    suspend fun getDecisionReceipt(): DecisionReceipt
    suspend fun pushPolicy(packet: PolicyPacket): Boolean
}
