package net.sprout.pollen.sync

import net.sprout.pollen.schemas.FieldVisit
import net.sprout.pollen.schemas.PolicyPacket
import kotlinx.serialization.Serializable

@Serializable
data class PollenHello(
    val pollen_id: String,
    val app_version: String,
    val bundles_pending_count: Int
)

@Serializable
data class PoliciesPulledPayload(
    val count: Int,
    val policy_ids: List<String>
)

interface MeristemClient {
    suspend fun uploadFieldVisit(visit: FieldVisit)
    suspend fun getLatestPolicy(targetId: String): PolicyPacket
    suspend fun checkHealth(): Boolean
    suspend fun sendHello(hello: PollenHello): Boolean
    suspend fun sendHeartbeat(hello: PollenHello): Boolean
    suspend fun sendBundlesPushed(): Boolean
    suspend fun sendPoliciesPulled(payload: PoliciesPulledPayload): Boolean
}
