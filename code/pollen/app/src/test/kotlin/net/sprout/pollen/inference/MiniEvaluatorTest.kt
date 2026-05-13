package net.sprout.pollen.inference

import net.sprout.pollen.schemas.*
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Test

class MiniEvaluatorTest {

    private val baseSnapshot = RhizomeSnapshot(
        schemaVersion = "1.0",
        createdAt = "2026-05-05T12:00:00Z",
        originNodeId = "rhizome_01",
        snapshotId = "snap_1",
        mode = Mode.NORMAL,
        activePolicyId = "pol_1",
        activePolicyExpiresAt = "2026-05-06T12:00:00Z",
        sensors = RhizomeSnapshot.Sensors(0f, 0f, 50f, 0f, ""),
        vision = RhizomeSnapshot.Vision(),
        health = RhizomeSnapshot.Health(0f, 0f, 0f, 0f, true)
    )

    private val basePolicy = PolicyPacket(
        policyId = "pol_1",
        targetNodeId = "rhizome_01",
        originNodeId = "meristem",
        createdAt = "2026-05-01T12:00:00Z",
        validUntil = "2026-05-10T12:00:00Z",
        versionChain = emptyList(),
        modeDefault = "normal",
        rules = PolicyPacket.Rules(
            wateringWindow = PolicyPacket.WateringWindow(0, 23),
            soilMoistureThresholds = emptyMap(),
            maxWateringDurationS = 120,
            dailyWaterBudgetLiters = 10f,
            tankMinimumPct = 15f,
            requireVisionConfirmation = false,
            conservativeTriggers = emptyList()
        )
    )

    @Test
    fun testHappyPathWaterMore() {
        val patch = MissionPatch("rhizome_01", "water_extra", null, 30, null, null, null, "Aplicar 30 segundos extra a parcela A")
        val transcript = "riega la parcela A 30 segundos más"
        val result = MiniEvaluator.evaluate(transcript, patch, patch.rationaleEs, 0.9, baseSnapshot, basePolicy)
        
        assertEquals(EvaluationAction.APPLY_AS_IS, result.action)
        assertEquals("STABLE_INTENT", result.reasonCode)
        assertNotNull(result.policyPacket)
        assertEquals(30, result.policyPacket?.rules?.maxWateringDurationS)
    }

    @Test
    fun testConservativeNoKeywordMatch() {
        // El patch propone 20s (dentro de MAX_WATER_SECONDS_MVP=30). El transcript
        // "agua un poco más" no contiene keywords fuertes ni números que matcheen
        // con los campos del patch, asi que el evaluator aplica margen conservador
        // del 75%: 20 * 0.75 = 15s.
        val patch = MissionPatch("rhizome_01", "water_extra", null, 20, null, null, null, "Aplicar 20 segundos")
        val transcript = "agua un poco más"
        val result = MiniEvaluator.evaluate(transcript, patch, patch.rationaleEs, 0.9, baseSnapshot, basePolicy)

        assertEquals(EvaluationAction.APPLY_CONSERVATIVE, result.action)
        assertEquals("MODERATE_CONFIDENCE", result.reasonCode)
        assertEquals(15, result.policyPacket?.rules?.maxWateringDurationS) // 20 * 0.75
    }

    @Test
    fun testRefuseHardDurationAboveFirmwareLimit() {
        // Cualquier patch con durationS > MAX_WATER_SECONDS_MVP (30) debe rechazarse
        // como REFUSE_HARD antes de evaluar match semántico, para proteger el sobre
        // físico del firmware.
        val patch = MissionPatch("rhizome_01", "water_extra", null, 60, null, null, null, "Aplicar 60 segundos")
        val transcript = "riega la parcela A 60 segundos"
        val result = MiniEvaluator.evaluate(transcript, patch, patch.rationaleEs, 0.9, baseSnapshot, basePolicy)

        assertEquals(EvaluationAction.REFUSE_HARD, result.action)
        assertEquals("HARD_LIMIT_DOMAIN", result.reasonCode)
    }

    @Test
    fun testRefuseRetryInvalidSchema() {
        val patch = MissionPatch("", "water_extra", null, 30, null, null, null, "rationale")
        val result = MiniEvaluator.evaluate("transcript", patch, patch.rationaleEs, 0.9, baseSnapshot, basePolicy)
        
        assertEquals(EvaluationAction.REFUSE_RETRY, result.action)
        assertEquals("LLM_LOW_CONFIDENCE", result.reasonCode)
    }

    @Test
    fun testRefuseHardTankMinimum() {
        val patch = MissionPatch("rhizome_01", "water_extra", null, 30, 10f, null, null, "rationale")
        val result = MiniEvaluator.evaluate("transcript", patch, patch.rationaleEs, 0.9, baseSnapshot, basePolicy)
        
        assertEquals(EvaluationAction.REFUSE_HARD, result.action)
        assertEquals("HARD_LIMIT_DOMAIN", result.reasonCode)
    }

    @Test
    fun testRefuseHardAlertMode() {
        val alertSnapshot = baseSnapshot.copy(mode = Mode.ALERT)
        val patch = MissionPatch("rhizome_01", "water_extra", null, 30, null, null, null, "rationale")
        val result = MiniEvaluator.evaluate("riega 30", patch, patch.rationaleEs, 0.9, alertSnapshot, basePolicy)
        
        assertEquals(EvaluationAction.REFUSE_HARD, result.action)
        assertEquals("RHIZOME_IN_ALERT", result.reasonCode)
    }
}
