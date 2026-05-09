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
import net.sprout.pollen.inference.GemmaEngine
import net.sprout.pollen.inference.MiniEvaluator
import net.sprout.pollen.schemas.Mode
import net.sprout.pollen.schemas.PolicyPacket
import net.sprout.pollen.schemas.RhizomeSnapshot
import net.sprout.pollen.sync.RhizomeClient
import net.sprout.pollen.voice.PollenVoiceInfra

@Composable
fun VoiceBetaPanel(client: RhizomeClient, snapshot: RhizomeSnapshot) {
    var state by remember { mutableStateOf("Idle") }
    var resultText by remember { mutableStateOf("") }
    var isRecording by remember { mutableStateOf(false) }
    
    val coroutineScope = rememberCoroutineScope()
    val context = LocalContext.current
    val voiceInfra = remember { PollenVoiceInfra(context) }
    
    val permissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        if (isGranted) {
            isRecording = true
            voiceInfra.startRecording()
            state = "Recording audio (.wav 16kHz)..."
        } else {
            state = "Error: Microphone permission denied."
        }
    }
    
    Column(modifier = Modifier.fillMaxWidth().padding(top = 16.dp)) {
        Row(verticalAlignment = androidx.compose.ui.Alignment.CenterVertically) {
            Text(text = "Voice Command", style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Bold)
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
            text = "Esta feature está en beta — si el sistema no entiende con seguridad, te lo dirá.",
            style = MaterialTheme.typography.bodySmall,
            color = Color.Gray
        )
        Spacer(modifier = Modifier.height(8.dp))
        
        Text("Status: $state", color = MaterialTheme.colorScheme.primary, fontWeight = FontWeight.Bold)
        if (resultText.isNotEmpty()) {
            Text(text = resultText, style = MaterialTheme.typography.bodyMedium, color = Color.DarkGray)
        }
        
        Spacer(modifier = Modifier.height(8.dp))
        Button(
            onClick = {
                if (isRecording) {
                    // Stop recording and process
                    isRecording = false
                    val file = voiceInfra.stopRecording()
                    if (file != null) {
                        coroutineScope.launch {
                            state = "Listening & Compiling (LiteRT-LM)..."
                            resultText = "Processing audio file: ${file.name}"
                            val engine = GemmaEngine(context)
                            val patch = engine.parseVoiceFileToMissionPatch(file, snapshot)
                            
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
                                modeDefault = Mode.NORMAL,
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

                            val eval = MiniEvaluator.evaluate("Riega la parcela A 30 segundos más", patch, patch.rationaleEs, 0.85, snapshot, activePolicy)
                            
                            if (eval.action == net.sprout.pollen.schemas.EvaluationAction.APPLY_AS_IS || eval.action == net.sprout.pollen.schemas.EvaluationAction.APPLY_CONSERVATIVE) {
                                state = "Sending Policy to Rhizome..."
                                delay(500)
                                client.pushPolicy(eval.policyPacket!!)
                                state = "Acknowledged"
                                resultText = "Action: ${eval.action}\nDetail: ${eval.details}"
                            } else {
                                state = "Refused"
                                resultText = "Action: ${eval.action}\nReason: ${eval.reasonCode}\nDetail: ${eval.details}"
                            }
                        }
                    } else {
                        state = "Error saving audio file"
                    }
                } else {
                    // Request permission and start recording
                    if (ContextCompat.checkSelfPermission(context, Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED) {
                        isRecording = true
                        voiceInfra.startRecording()
                        state = "Recording audio (.wav 16kHz)..."
                    } else {
                        permissionLauncher.launch(Manifest.permission.RECORD_AUDIO)
                    }
                }
            },
            modifier = Modifier.fillMaxWidth().height(48.dp),
            shape = RoundedCornerShape(14.dp),
            enabled = state == "Idle" || state == "Acknowledged" || state == "Refused" || isRecording,
            colors = ButtonDefaults.buttonColors(
                containerColor = if (isRecording) Color.Red else MaterialTheme.colorScheme.primary
            )
        ) {
            Text(if (isRecording) "Stop Recording" else "Chat with Rhizome", fontWeight = FontWeight.Bold)
        }
    }
}
