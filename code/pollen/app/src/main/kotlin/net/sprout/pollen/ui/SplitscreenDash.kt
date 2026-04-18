package net.sprout.pollen.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.Divider
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
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

@Composable
fun SplitscreenDash() {
    val mockClient = remember { RhizomeMockClient() }
    val snapshot = remember { mockClient.getSnapshot() }
    val receipt = remember { mockClient.getDecisionReceipt() }
    
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

        // Lower Half: Active Policy & TTL
        Box(
            modifier = Modifier
                .weight(1f)
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            ActivePolicyPanel(snapshot, currentTime)
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
