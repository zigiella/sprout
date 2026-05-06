package net.sprout.pollen.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import net.sprout.pollen.schemas.DecisionReceipt
import net.sprout.pollen.schemas.RhizomeSnapshot
import net.sprout.pollen.sync.RhizomeMockClient
import java.time.Instant
import java.time.Duration
import kotlinx.coroutines.delay
import net.sprout.pollen.inference.GemmaEngine
// androidx.lifecycle.viewmodel.compose.viewModel / ViewModelProvider eran
// imports sin uso y requerian dependencia no declarada. Removidos por Cambium.

@Composable
fun SplitscreenDash(viewModel: PollenViewModel) {
    val mockClient = remember { RhizomeMockClient() }
    val snapshot = remember { mockClient.getSnapshot() }
    val receipt = remember { mockClient.getDecisionReceipt() }
    
    val auditState by viewModel.uiState.collectAsState()
    
    // Simulate current time progression to illustrate TTL countdown
    var currentTime by remember { mutableStateOf(Instant.parse(snapshot.createdAt)) }
    
    LaunchedEffect(Unit) {
        while (true) {
            delay(1000)
            currentTime = currentTime.plusSeconds(60) // Accelerate time for testing visual updates
        }
    }

    Column(modifier = Modifier.fillMaxSize()) {
        // Upper Half: Rhizome State & rationale_short
        Box(
            modifier = Modifier
                .weight(1f)
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            RhizomeStatePanel(snapshot, receipt)
        }

        Divider(color = Color.DarkGray, thickness = 2.dp)

        // Middle Half: Audit Streamer
        Box(
            modifier = Modifier
                .weight(1f)
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            AuditPanel(auditState) {
                viewModel.runAudit(snapshot, receipt)
            }
        }

        Divider(color = Color.DarkGray, thickness = 2.dp)

        // Lower Half: Active Policy & TTL
        Box(
            modifier = Modifier
                .weight(1f)
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            ActivePolicyPanel(snapshot, currentTime)
        }

        Divider(color = Color.DarkGray, thickness = 2.dp)

        // Bottom Half: Voice Beta
        Box(
            modifier = Modifier
                .weight(1f)
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            VoiceBetaPanel(mockClient, snapshot)
        }
    }
}

@Composable
fun VoiceBetaPanel(client: RhizomeMockClient, snapshot: RhizomeSnapshot) {
    var state by remember { mutableStateOf("Idle") }
    
    Column {
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
        
        Text("Status: $state", color = MaterialTheme.colorScheme.primary)
        
        Spacer(modifier = Modifier.height(8.dp))
        Button(onClick = {
            state = "compiling -> validating -> sending -> ack"
        }) {
            Text("Simular Voz: 'Riega 30s más'")
        }
    }
}

@Composable
fun AuditPanel(state: AuditUiState, onRunAudit: () -> Unit) {
    Column {
        Text(text = "Gemma 4 Auditor", style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Bold)
        Spacer(modifier = Modifier.height(8.dp))
        when (state) {
            is AuditUiState.Idle -> {
                androidx.compose.material3.Button(onClick = onRunAudit) {
                    Text("Run Audit")
                }
            }
            is AuditUiState.Loading -> {
                Text("Loading model context...", color = Color.Gray)
            }
            is AuditUiState.Streaming -> {
                Text(state.text, style = MaterialTheme.typography.bodyMedium)
                Spacer(modifier = Modifier.height(8.dp))
                // Simulated generic loading indicator via text
                Text("[Streaming...]", color = Color.Blue)
            }
            is AuditUiState.Done -> {
                Text(state.text, style = MaterialTheme.typography.bodyMedium)
                Spacer(modifier = Modifier.height(8.dp))
                Text("Result: ${state.result}", color = Color.Green, fontWeight = FontWeight.Bold)
            }
            is AuditUiState.Error -> {
                Text("Error: ${state.message}", color = Color.Red)
            }
        }
    }
}

@Composable
fun RhizomeStatePanel(snapshot: RhizomeSnapshot, receipt: DecisionReceipt) {
    Column {
        Text(text = "Rhizome State", style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Bold)
        Spacer(modifier = Modifier.height(8.dp))
        Text(text = "Mode: ${snapshot.mode}")
        Text(text = "Tank Level: ${snapshot.sensors.tankLevelPct}%")
        Text(text = "Soil A/B: ${snapshot.sensors.soilMoistureAPct}% / ${snapshot.sensors.soilMoistureBPct}%")
        Spacer(modifier = Modifier.height(16.dp))
        Text(text = "Last Decision", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
        Text(text = "Action: ${receipt.action}")
        Text(text = "Rationale: ${receipt.rationaleShort}", color = Color.Gray)
    }
}

@Composable
fun ActivePolicyPanel(snapshot: RhizomeSnapshot, currentTime: Instant) {
    val creationTime = Instant.parse(snapshot.createdAt) // Roughly when policy was activated for this calculation
    val expiryTime = Instant.parse(snapshot.activePolicyExpiresAt)
    val totalDuration = Duration.between(creationTime, expiryTime).seconds
    val remainingDuration = Duration.between(currentTime, expiryTime).seconds
    
    // Critical zone is < 20%
    val isCritical = if (totalDuration > 0) {
        remainingDuration.toDouble() / totalDuration < 0.20
    } else {
        true
    }

    val ttlColor = if (isCritical) Color.Red else Color.Unspecified

    Column {
        Text(text = "Active Policy", style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Bold)
        Spacer(modifier = Modifier.height(8.dp))
        Text(text = "ID: ${snapshot.activePolicyId}")
        Spacer(modifier = Modifier.height(16.dp))
        
        Text(text = "TTL Indicator", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
        Text(
            text = "Expires at: ${snapshot.activePolicyExpiresAt}",
            color = ttlColor,
            fontWeight = if (isCritical) FontWeight.Bold else FontWeight.Normal
        )
        Text(
            text = if (remainingDuration > 0) "Remaining TTL: $remainingDuration seconds" else "POLICY EXPIRED",
            color = ttlColor,
            fontWeight = if (isCritical) FontWeight.Bold else FontWeight.Normal
        )
    }
}
