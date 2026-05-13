package net.sprout.pollen.ui

import android.Manifest
import android.content.pm.PackageManager
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import net.sprout.pollen.inference.MiniEvaluator
import net.sprout.pollen.schemas.MissionPatch
import net.sprout.pollen.schemas.PolicyPacket
import net.sprout.pollen.schemas.RhizomeSnapshot
import net.sprout.pollen.sync.RhizomeClient
import net.sprout.pollen.voice.PollenVoiceInfra

import android.app.Activity
import android.content.Intent
import android.speech.RecognizerIntent

import kotlinx.serialization.json.Json

import androidx.compose.ui.res.stringResource
import net.sprout.pollen.R
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll

/**
 * BETA placeholder: en el flujo real (device build), la compilacion voz -> MissionPatch
 * la hace LiteRtInfra.sendAudioFile() devolviendo JSON estructurado del modelo Gemma 4 E4B.
 * Aqui, sobre el flujo SpeechRecognizer + transcript-text, generamos un MissionPatch placeholder
 * razonable a partir de heuristicas de keywords para que la UI BETA siga ejercitando
 * MiniEvaluator (los chequeos deterministas son la pieza contractual; el LLM solo
 * propone) sin requerir el modelo descargado en device.
 */
private fun buildPlaceholderMissionPatch(transcript: String, snapshot: RhizomeSnapshot): MissionPatch {
    val t = transcript.lowercase()
    val priorityPlot = if (t.contains("parcela b") || t.contains("plot b")) "B" else "A"
    val horizonH = Regex("""(\d+)\s*(h(oras)?|hour)""").find(t)?.groupValues?.get(1)?.toIntOrNull() ?: 72
    val budgetCapMl = if (t.contains("menos") || t.contains("less")) 900f else 1500f
    val rationale = "Compile placeholder: prioridad ${priorityPlot}, horizonte ${horizonH}h, tope ${budgetCapMl}ml."
    return MissionPatch(
        targetNodeId = snapshot.originNodeId,
        action = "water_extra",
        priorityPlot = priorityPlot,
        horizonH = horizonH,
        budgetCapMl = budgetCapMl,
        rationaleEs = rationale,
        operatorNote = transcript,
        patchOp = "apply"
    )
}

@Composable
fun VoiceBetaPanel(client: RhizomeClient, snapshot: RhizomeSnapshot) {
    var state by remember { mutableStateOf("Idle") }
    var resultText by remember { mutableStateOf("") }
    var isRecording by remember { mutableStateOf(false) }
    
    var showPolicyDialog by remember { mutableStateOf(false) }
    var policyJsonText by remember { mutableStateOf("") }
    
    val coroutineScope = rememberCoroutineScope()
    val context = LocalContext.current
    
    val speechLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.StartActivityForResult()
    ) { result ->
        isRecording = false
        if (result.resultCode == Activity.RESULT_OK) {
            val data = result.data
            val matches = data?.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS)
            val recognizedText = matches?.firstOrNull() ?: ""
            
            if (recognizedText.isNotEmpty()) {
                coroutineScope.launch {
                    state = "Listening & Compiling (LiteRT-LM)..."
                    resultText = "Transcribed: \"$recognizedText\""
                    val patch = buildPlaceholderMissionPatch(recognizedText, snapshot)
                    
                    state = "Validating (Mini-Evaluator)..."
                    delay(800)
                    
                    // Dummy active policy for evaluation
                    val activePolicy = PolicyPacket(
                        policyId = "pol_mock",
                        targetNodeId = snapshot.originNodeId,
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

                    val eval = MiniEvaluator.evaluate(recognizedText, patch, patch.rationaleEs, 0.85, snapshot, activePolicy)
                    
                    if (eval.policyPacket != null) {
                        val json = Json { prettyPrint = true }
                        policyJsonText = json.encodeToString(PolicyPacket.serializer(), eval.policyPacket)
                    }
                    
                    if (eval.action == net.sprout.pollen.schemas.EvaluationAction.APPLY_AS_IS || eval.action == net.sprout.pollen.schemas.EvaluationAction.APPLY_CONSERVATIVE) {
                        state = "Sending Policy to Rhizome..."
                        delay(500)
                        try {
                            client.pushPolicy(eval.policyPacket!!)
                            state = "Acknowledged"
                            resultText = "Action: ${eval.action}\nDetail: ${eval.details}"
                        } catch (e: Exception) {
                            state = "Error: Rhizome rejected policy"
                            resultText = e.message ?: "Unknown error"
                        }
                    } else {
                        state = "Refused"
                        resultText = "Action: ${eval.action}\nReason: ${eval.reasonCode}\nDetail: ${eval.details}"
                    }
                }
            } else {
                state = "Error: No text recognized"
            }
        } else {
            state = "Cancelled speech recognition"
        }
    }
    
    Column(modifier = Modifier.fillMaxWidth().padding(top = 16.dp)) {
        Row(verticalAlignment = androidx.compose.ui.Alignment.CenterVertically) {
            Text(text = stringResource(R.string.voice_command_title), style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Bold)
            Spacer(modifier = Modifier.width(8.dp))
            Surface(
                color = Color(0xFFFF9800), // Amber/Orange
                shape = RoundedCornerShape(4.dp)
            ) {
                Text(
                    text = "BETA", 
                    color = Color.White,
                    style = MaterialTheme.typography.labelSmall,
                    modifier = Modifier.padding(horizontal = 4.dp, vertical = 2.dp)
                )
            }
        }
        Text(
            text = stringResource(R.string.voice_beta_disclaimer),
            style = MaterialTheme.typography.bodySmall,
            color = Color.Gray
        )
        Spacer(modifier = Modifier.height(8.dp))
        
        Text(stringResource(R.string.status_label, state), color = MaterialTheme.colorScheme.primary, fontWeight = FontWeight.Bold)
        if (resultText.isNotEmpty()) {
            Text(text = resultText, style = MaterialTheme.typography.bodyMedium, color = Color.DarkGray)
        }
        
        if (policyJsonText.isNotEmpty()) {
            Spacer(modifier = Modifier.height(4.dp))
            TextButton(onClick = { showPolicyDialog = true }) {
                Text(stringResource(R.string.view_generated_policy))
            }
        }
        
        Spacer(modifier = Modifier.height(8.dp))
        
        val speechPrompt = stringResource(R.string.speech_prompt)
        Button(
            onClick = {
                val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
                    putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
                    putExtra(RecognizerIntent.EXTRA_LANGUAGE, "es-ES")
                    putExtra(RecognizerIntent.EXTRA_PROMPT, speechPrompt)
                }
                isRecording = true
                speechLauncher.launch(intent)
            },
            modifier = Modifier.fillMaxWidth().height(48.dp),
            shape = RoundedCornerShape(14.dp),
            enabled = state == "Idle" || state == "Acknowledged" || state == "Refused" || isRecording,
            colors = ButtonDefaults.buttonColors(
                containerColor = if (isRecording) Color.Red else MaterialTheme.colorScheme.primary
            )
        ) {
            Text(if (isRecording) stringResource(R.string.stop_recording) else stringResource(R.string.chat_with_rhizome), fontWeight = FontWeight.Bold)
        }
    }
    
    if (showPolicyDialog) {
        AlertDialog(
            onDismissRequest = { showPolicyDialog = false },
            title = { Text(stringResource(R.string.policy_dialog_title)) },
            text = { 
                Text(
                    text = policyJsonText, 
                    style = MaterialTheme.typography.bodySmall.copy(fontFamily = androidx.compose.ui.text.font.FontFamily.Monospace),
                    modifier = Modifier.verticalScroll(rememberScrollState())
                ) 
            },
            confirmButton = {
                TextButton(onClick = { showPolicyDialog = false }) { Text(stringResource(R.string.close_dialog)) }
            }
        )
    }
}
