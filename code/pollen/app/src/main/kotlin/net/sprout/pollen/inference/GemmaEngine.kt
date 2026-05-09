package net.sprout.pollen.inference

import android.content.Context
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import net.sprout.pollen.schemas.DecisionReceipt
import net.sprout.pollen.schemas.RhizomeSnapshot
// AuditEvent / AuditResult viven en el mismo paquete (GemmaContracts.kt),
// no hace falta import. Fix de compilacion por Cambium (Floema OOO 19-20 abril).
// import com.google.mediapipe.tasks.genai.llminference.LlmInference

class GemmaEngine(private val context: Context, private val modelPath: String = "/data/local/tmp/gemma-4-e2b.bin") {

    // private var llmInference: LlmInference? = null
    // init { 
    //     // Setup LlmInference. LlmInferenceOptions...
    // }

    fun runAudit(snapshot: RhizomeSnapshot, receipt: DecisionReceipt): Flow<AuditEvent> = flow {
        // Here we format the prompt using the data schemas.
        val prompt = buildString {
            appendLine("Role: You are Pollen, an auditor node using Gemma 4 E2B.")
            appendLine("Task: Analyze Rhizome's rationale against its metrics.")
            appendLine("Rhizome Snapshot: Mode=${snapshot.mode}, Tank=${snapshot.sensors.tankLevelPct}%, Moisture A/B=${snapshot.sensors.soilMoistureAPct}%/${snapshot.sensors.soilMoistureBPct}%")
            appendLine("Decision: ${receipt.action} - Rationale: ${receipt.rationaleShort}")
        }

        // Simulating the prompt processing delay
        delay(500)

        // Simulating token streaming from MediaPipe
        val simulatedResponse = "Analyzing Rhizome decision...\nMetrics align with conservative threshold logic.\nNo conflicts found in the policy execution.\nConclusion: No discrepancy."
        val tokens = simulatedResponse.split(" ")
        
        for (i in tokens.indices) {
            val tokenStr = tokens[i] + if (i < tokens.size - 1) " " else ""
            emit(AuditEvent.Token(tokenStr))
            delay(150) // Simulating TTFT and inter-token latency
        }
        
        // Simulating the structured JSON parse from the output text
        delay(300)
        emit(AuditEvent.Done(AuditResult.NoDiscrepancy(rationale = "Metrics align with conservative threshold logic. No conflicts found in the policy execution.")))
    }

    suspend fun parseVoiceToMissionPatch(transcript: String, snapshot: RhizomeSnapshot): net.sprout.pollen.schemas.MissionPatch {
        delay(1000) // Simulate LiteRT-LM latency
        
        val lower = transcript.lowercase()
        
        val agricultureKeywords = setOf("riega", "regar", "agua", "humedad", "calor", "seco", "parcela", "minutos", "segundos", "salta", "ciclo", "más", "menos", "regarla", "riégala")
        val isNonsense = lower.split(Regex("\\W+")).none { it in agricultureKeywords }
        
        if (isNonsense) {
            return net.sprout.pollen.schemas.MissionPatch(
                targetNodeId = snapshot.originNodeId,
                action = "REFUSE",
                durationS = null,
                rationaleEs = "El operario solicitó una acción incomprensible o fuera de contexto: '$transcript'."
            )
        }

        val duration = Regex("\\d+").find(lower)?.value?.toInt() ?: 30
        
        return net.sprout.pollen.schemas.MissionPatch(
            targetNodeId = snapshot.originNodeId,
            action = if (lower.contains("salta")) "skip_next_cycle" else "water_extra",
            durationS = if (lower.contains("salta")) null else duration,
            rationaleEs = "El operario solicitó riego manual por comandos de voz."
        )
    }

    suspend fun parseVoiceFileToMissionPatch(audioFile: java.io.File, snapshot: RhizomeSnapshot): net.sprout.pollen.schemas.MissionPatch {
        delay(1500) // Simulate LiteRT-LM multimodal inference latency
        
        // Simulating the STT output from the Gemma 4 E4B model for the audio file
        val mockTranscript = "Riega la parcela A 30 segundos más"
        
        return parseVoiceToMissionPatch(mockTranscript, snapshot)
    }
}
