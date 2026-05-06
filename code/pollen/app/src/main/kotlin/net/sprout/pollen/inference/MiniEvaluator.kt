package net.sprout.pollen.inference

import net.sprout.pollen.schemas.*
import java.time.Instant
import java.time.temporal.ChronoUnit

object MiniEvaluator {

    fun evaluate(
        transcript: String,
        missionPatch: MissionPatch,
        rationale_es: String,
        confidence_score: Double?,
        rhizomeSnapshot: RhizomeSnapshot,
        activePolicy: PolicyPacket
    ): EvaluationResult {

        // Regla 1: hard limit
        val hardLimitViolation = checkHardLimits(missionPatch)
        if (hardLimitViolation != null) {
            return EvaluationResult(
                action = EvaluationAction.REFUSE_HARD,
                reasonCode = "HARD_LIMIT_DOMAIN",
                details = hardLimitViolation,
            )
        }

        // Regla 2: alerta activa en Rhizome
        // Assuming RhizomeSnapshot might have alertLatched or mode
        if (rhizomeSnapshot.mode == Mode.ALERT) {
            return EvaluationResult(
                action = EvaluationAction.REFUSE_HARD,
                reasonCode = "RHIZOME_IN_ALERT",
                details = "Rhizome reporta alerta activa al consultar /snapshot/latest",
            )
        }

        // Regla 3: schema validation
        val schemaErrors = validateMissionPatchSchema(missionPatch)
        if (schemaErrors.isNotEmpty()) {
            return EvaluationResult(
                action = EvaluationAction.REFUSE_RETRY,
                reasonCode = "LLM_LOW_CONFIDENCE",
                details = "Schema invalid: ${schemaErrors.joinToString(", ")}",
            )
        }

        // Regla 3-bis: confianza explícita
        if (confidence_score != null && confidence_score < 0.7) {
            return EvaluationResult(
                action = EvaluationAction.REFUSE_RETRY,
                reasonCode = "LLM_LOW_CONFIDENCE",
                details = "confidence_score=$confidence_score < 0.7",
            )
        }

        // Regla 4: match sintáctico-semántico
        val matchOk = checkSyntacticSemanticMatch(transcript, missionPatch, rationale_es)
        if (!matchOk) {
            return EvaluationResult(
                action = EvaluationAction.APPLY_CONSERVATIVE,
                reasonCode = "MODERATE_CONFIDENCE",
                details = "Match con intención humana ambiguo. Aplicado con margen reducido.",
                policyPacket = composePolicyPacket(missionPatch, activePolicy, conservativeMargin = 0.75f),
            )
        }

        // Regla 5: APPLY_AS_IS
        return EvaluationResult(
            action = EvaluationAction.APPLY_AS_IS,
            reasonCode = "STABLE_INTENT",
            details = "Todos los checks pasan.",
            policyPacket = composePolicyPacket(missionPatch, activePolicy, conservativeMargin = 1.0f),
        )
    }

    private fun checkHardLimits(patch: MissionPatch): String? {
        if (patch.tankMinimumPct != null && patch.tankMinimumPct < 20f) return "tank_minimum_pct < 20"
        if (patch.durationS != null && patch.durationS > 180) return "duration_s > 180"
        if (patch.minSecondsBetweenEvents != null && patch.minSecondsBetweenEvents < 60) return "min_seconds_between_events < 60"
        return null
    }

    private fun validateMissionPatchSchema(patch: MissionPatch): List<String> {
        val errors = mutableListOf<String>()
        if (patch.targetNodeId.isEmpty()) errors.add("Missing targetNodeId")
        if (patch.durationS != null && patch.durationS < 0) errors.add("Negative duration_s")
        return errors
    }

    private val STOPWORDS_ES = setOf("el", "la", "los", "las", "un", "una", "unos", "unas", "que", "para", "de", "del", "a", "al", "en", "con", "por", "y", "o")

    private fun checkSyntacticSemanticMatch(transcript: String, patch: MissionPatch, rationaleEs: String): Boolean {
        val transcriptKeywords = transcript.lowercase()
            .split(Regex("\\W+"))
            .filter { it.length > 2 && it !in STOPWORDS_ES }
            .toSet()
            
        val transcriptNumbers = Regex("\\d+").findAll(transcript)
            .map { it.value.toInt() }
            .toSet()

        val rationaleWords = rationaleEs.lowercase().split(Regex("\\W+")).toSet()
        
        val patchNumbers = mutableSetOf<Int>()
        patch.durationS?.let { patchNumbers.add(it) }
        patch.tankMinimumPct?.let { patchNumbers.add(it.toInt()) }
        patch.budgetCapMl?.let { patchNumbers.add(it.toInt()) }
        patch.minSecondsBetweenEvents?.let { patchNumbers.add(it) }

        val keywordMatch = transcriptKeywords.intersect(rationaleWords).isNotEmpty()
        val numberMatch = transcriptNumbers.intersect(patchNumbers).isNotEmpty()

        return keywordMatch || numberMatch
    }

    private fun composePolicyPacket(patch: MissionPatch, activePolicy: PolicyPacket, conservativeMargin: Float): PolicyPacket {
        val duration = (patch.durationS?.toFloat() ?: activePolicy.rules.maxWateringDurationS.toFloat()) * conservativeMargin
        val tankMin = (patch.tankMinimumPct ?: activePolicy.rules.tankMinimumPct) + if (conservativeMargin < 1.0f) 5f else 0f
        val budget = (patch.budgetCapMl ?: activePolicy.rules.dailyWaterBudgetLiters * 1000f) * conservativeMargin

        val newRules = activePolicy.rules.copy(
            maxWateringDurationS = duration.toInt(),
            tankMinimumPct = tankMin,
            dailyWaterBudgetLiters = budget / 1000f
        )

        return PolicyPacket(
            policyId = "pkt_${patch.targetNodeId}_${System.currentTimeMillis()}",
            targetNodeId = patch.targetNodeId,
            originNodeId = "pollen",
            createdAt = Instant.now().toString(),
            validUntil = Instant.now().plus(12, ChronoUnit.HOURS).toString(),
            versionChain = activePolicy.versionChain + activePolicy.policyId,
            modeDefault = activePolicy.modeDefault,
            rules = newRules,
            rationale = patch.rationaleEs,
            policyOrigin = "pollen-visit",
            policyScope = "transient"
        )
    }
}
