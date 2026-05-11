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

interface MeristemClient {
    suspend fun uploadFieldVisit(visit: FieldVisit)
    suspend fun getLatestPolicy(targetId: String): PolicyPacket
    suspend fun checkHealth(): Boolean
    suspend fun sendHello(hello: PollenHello): Boolean
    suspend fun sendHeartbeat(hello: PollenHello): Boolean
    suspend fun sendBundlesPushed(): Boolean
    suspend fun sendPoliciesPulled(): Boolean
}
