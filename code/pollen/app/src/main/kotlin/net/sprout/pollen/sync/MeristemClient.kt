package net.sprout.pollen.sync

import net.sprout.pollen.schemas.FieldVisit
import net.sprout.pollen.schemas.PolicyPacket

interface MeristemClient {
    suspend fun uploadFieldVisit(visit: FieldVisit)
    suspend fun getLatestPolicy(): PolicyPacket
}
