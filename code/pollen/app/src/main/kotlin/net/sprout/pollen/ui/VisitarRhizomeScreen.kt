package net.sprout.pollen.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.border
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Info
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.shrinkVertically
import androidx.compose.animation.fadeOut
import androidx.compose.ui.res.stringResource
import net.sprout.pollen.R
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.rememberScrollState
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.launch
import net.sprout.pollen.schemas.DecisionReceipt
import net.sprout.pollen.schemas.RhizomeSnapshot
import net.sprout.pollen.sync.RhizomeClient
import net.sprout.pollen.sync.RhizomeMockClient
import net.sprout.pollen.sync.RhizomeNetworkClient

@Composable
fun VisitarRhizomeScreen(
    onDataFetched: (RhizomeSnapshot, List<DecisionReceipt>) -> Unit = { _, _ -> },
    onChatClicked: () -> Unit = {},
    onAuditClicked: () -> Unit = {}
) {
    val client: RhizomeClient = remember { 
        if (net.sprout.pollen.BuildConfig.FLAVOR == "demo") {
            RhizomeMockClient()
        } else {
            RhizomeNetworkClient("http://192.168.1.60:13010/")
        }
    }
    val scope = rememberCoroutineScope()
    
    var status by remember { mutableStateOf<Map<String, String>?>(null) }
    var snapshot by remember { mutableStateOf<RhizomeSnapshot?>(null) }
    var receipts by remember { mutableStateOf<List<DecisionReceipt>>(emptyList()) }
    
    var step by remember { mutableIntStateOf(0) }
    var showExplanationDialog by remember { mutableStateOf(false) }
    var explanationText by remember { mutableStateOf("") }
    
    LaunchedEffect(Unit) {
        kotlinx.coroutines.delay(400)
        step = 1 // Conectando a Rhizome (activo)
        status = client.getStatus()
        
        step = 2 // Conectado, descargando snapshot (activo)
        kotlinx.coroutines.delay(300)
        snapshot = client.getLatestSnapshot()
        
        step = 3 // Descargado, leyendo recibos (activo)
        kotlinx.coroutines.delay(300)
        receipts = client.getReceipts()
        
        step = 4 // Listo
        if (snapshot != null) {
            onDataFetched(snapshot!!, receipts)
        }
    }

    Column(modifier = Modifier
        .fillMaxSize()
        .verticalScroll(rememberScrollState())
        .padding(horizontal = 18.dp, vertical = 16.dp)) {
        
        // Checklist Card
        AnimatedVisibility(
            visible = step < 4,
            exit = shrinkVertically() + fadeOut()
        ) {
            Card(
                modifier = Modifier.fillMaxWidth().padding(bottom = 24.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant),
                shape = RoundedCornerShape(12.dp)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(
                        stringResource(R.string.visit_checklist),
                        style = MaterialTheme.typography.labelMedium.copy(
                            fontFamily = androidx.compose.ui.text.font.FontFamily.Monospace,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        ),
                        modifier = Modifier.padding(bottom = 12.dp)
                    )
                    
                    SyncStepUI(label = stringResource(R.string.visit_connect), sub = "BLE / WiFi · 0.4s", status = if (step >= 2) "done" else if (step == 1) "active" else "pending")
                    Spacer(modifier = Modifier.height(12.dp))
                    SyncStepUI(label = stringResource(R.string.visit_snapshot), sub = "6.2 KB", status = if (step >= 3) "done" else if (step == 2) "active" else "pending")
                    Spacer(modifier = Modifier.height(12.dp))
                    SyncStepUI(label = stringResource(R.string.visit_receipts), sub = "Ventana 24h", status = if (step >= 4) "done" else if (step == 3) "active" else "pending")
                }
            }
        }
        
        if (step >= 4) {
            Text(
                stringResource(R.string.telemetry_current),
                style = MaterialTheme.typography.labelMedium.copy(
                    fontFamily = androidx.compose.ui.text.font.FontFamily.Monospace,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                ),
                modifier = Modifier.padding(bottom = 8.dp)
            )
            
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                snapshot?.let { snap ->
                    TelemetryTileUI(label = stringResource(R.string.water_level), value = "${snap.sensors.tankLevelPct.toInt()}", unit = "%", modifier = Modifier.weight(1f))
                    TelemetryTileUI(label = stringResource(R.string.soil_a), value = "${snap.sensors.soilMoistureAPct.toInt()}", unit = "%", modifier = Modifier.weight(1f))
                    TelemetryTileUI(label = stringResource(R.string.soil_b), value = "${snap.sensors.soilMoistureBPct.toInt()}", unit = "%", modifier = Modifier.weight(1f))
                }
            }
            
            Spacer(modifier = Modifier.height(24.dp))
            
            Text(
                stringResource(R.string.last_decision),
                style = MaterialTheme.typography.labelMedium.copy(
                    fontFamily = androidx.compose.ui.text.font.FontFamily.Monospace,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                ),
                modifier = Modifier.padding(bottom = 8.dp)
            )
            
            receipts.forEach { receipt ->
                Card(
                    modifier = Modifier.fillMaxWidth().padding(bottom = 8.dp),
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                    border = androidx.compose.foundation.BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant)
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                            Text(receipt.action.name, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary)
                            Text(receipt.createdAt, style = MaterialTheme.typography.bodySmall, color = Color.Gray)
                        }
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(receipt.rationaleShort, style = MaterialTheme.typography.bodyMedium)
                        
                        Spacer(modifier = Modifier.height(8.dp))
                        OutlinedButton(
                            onClick = {
                                scope.launch {
                                    explanationText = client.explainDecision(receipt.decisionId)
                                    showExplanationDialog = true
                                }
                            },
                            shape = RoundedCornerShape(8.dp)
                        ) {
                            Icon(Icons.Default.Info, contentDescription = "Explicar", modifier = Modifier.size(16.dp))
                            Spacer(Modifier.width(4.dp))
                            Text(stringResource(R.string.explain_decision))
                        }
                    }
                }
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            Button(
                onClick = onChatClicked,
                modifier = Modifier.fillMaxWidth().height(48.dp),
                shape = RoundedCornerShape(14.dp),
                colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.primary)
            ) {
                Text(stringResource(R.string.chat_pollen), fontWeight = FontWeight.Bold)
            }
            Spacer(modifier = Modifier.height(8.dp))
            OutlinedButton(
                onClick = onAuditClicked,
                modifier = Modifier.fillMaxWidth().height(48.dp),
                shape = RoundedCornerShape(14.dp)
            ) {
                Text(stringResource(R.string.audit_pollen), fontWeight = FontWeight.Bold)
            }
        }
    }

    if (showExplanationDialog) {
        AlertDialog(
            onDismissRequest = { showExplanationDialog = false },
            title = { Text(stringResource(R.string.explanation_title)) },
            text = { Text(explanationText) },
            confirmButton = {
                TextButton(onClick = { showExplanationDialog = false }) {
                    Text(stringResource(R.string.close))
                }
            }
        )
    }
}

@Composable
fun SyncStepUI(label: String, sub: String, status: String) {
    val dotColor = when(status) {
        "done" -> Color(0xFF4CAF50)
        "active" -> Color(0xFF8BC34A)
        else -> Color.Transparent
    }
    val textColor = if (status == "pending") Color.Gray else MaterialTheme.colorScheme.onSurface
    
    Row(verticalAlignment = Alignment.CenterVertically) {
        Box(
            modifier = Modifier
                .size(18.dp)
                .background(dotColor, RoundedCornerShape(4.dp))
                .border(
                    1.dp, 
                    if (status == "pending") MaterialTheme.colorScheme.outline else dotColor, 
                    RoundedCornerShape(4.dp)
                ),
            contentAlignment = Alignment.Center
        ) {
            if (status == "done") {
                Icon(
                    Icons.Default.Check,
                    contentDescription = null,
                    tint = Color.White,
                    modifier = Modifier.size(12.dp)
                )
            } else if (status == "active") {
                // Pulso simulado
                Box(modifier = Modifier.size(8.dp).background(Color.White, androidx.compose.foundation.shape.CircleShape))
            }
        }
        Spacer(modifier = Modifier.width(12.dp))
        Column {
            Text(label, style = MaterialTheme.typography.bodyMedium, color = textColor, fontWeight = FontWeight.Medium)
            Text(sub, style = MaterialTheme.typography.bodySmall.copy(fontFamily = androidx.compose.ui.text.font.FontFamily.Monospace), color = Color.Gray)
        }
    }
}

@Composable
fun TelemetryTileUI(label: String, value: String, unit: String, modifier: Modifier = Modifier) {
    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        border = androidx.compose.foundation.BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant)
    ) {
        Column(modifier = Modifier.padding(12.dp)) {
            Text(label, style = MaterialTheme.typography.labelSmall.copy(fontFamily = androidx.compose.ui.text.font.FontFamily.Monospace), color = Color.Gray)
            Spacer(modifier = Modifier.height(4.dp))
            Row(verticalAlignment = Alignment.Bottom) {
                Text(value, style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)
                Text(unit, style = MaterialTheme.typography.bodySmall, modifier = Modifier.padding(bottom = 2.dp, start = 2.dp))
            }
        }
    }
}
