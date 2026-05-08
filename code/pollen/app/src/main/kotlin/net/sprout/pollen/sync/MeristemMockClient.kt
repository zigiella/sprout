package net.sprout.pollen.sync

import kotlinx.coroutines.delay
import net.sprout.pollen.schemas.FieldVisit
import net.sprout.pollen.schemas.Mode
import net.sprout.pollen.schemas.PolicyPacket

class MeristemMockClient : MeristemClient {
    override suspend fun uploadFieldVisit(visit: FieldVisit) {
        delay(1500)
    }

    override suspend fun getLatestPolicy(): PolicyPacket {
        delay(1500)
        return PolicyPacket(
            schemaVersion = "1.0",
            createdAt = "2026-04-29T10:00:00Z",
            originNodeId = "meristem_01",
            policyId = "pkt_meristem_mock",
            targetNodeId = "rhizome_01",
            validUntil = "2026-05-29T10:00:00Z",
            versionChain = emptyList(),
            modeDefault = Mode.NORMAL,
            rules = PolicyPacket.Rules(
                wateringWindow = PolicyPacket.WateringWindow(8, 18),
                soilMoistureThresholds = emptyMap(),
                maxWateringDurationS = 300,
                dailyWaterBudgetLiters = 5.0f,
                tankMinimumPct = 10.0f,
                requireVisionConfirmation = false,
                conservativeTriggers = emptyList()
            ),
            rationale = "Mock policy from Meristem",
            notes = "For testing UI"
        )
    }
}
