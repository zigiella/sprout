package net.sprout.pollen.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Info
import androidx.compose.material3.*
import androidx.compose.runtime.*
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
    onDataFetched: (RhizomeSnapshot, List<DecisionReceipt>) -> Unit = { _, _ -> }
) {
    val client: RhizomeClient = remember { 
        if (net.sprout.pollen.BuildConfig.FLAVOR == "demo") {
            RhizomeMockClient()
        } else {
            // TODO: Ajustar esta IP a la que confirme Endo
            RhizomeNetworkClient("http://192.168.1.100:8080")
        }
    }
    val scope = rememberCoroutineScope()
    
    var status by remember { mutableStateOf<Map<String, String>?>(null) }
    var snapshot by remember { mutableStateOf<RhizomeSnapshot?>(null) }
    var receipts by remember { mutableStateOf<List<DecisionReceipt>>(emptyList()) }
    var isLoading by remember { mutableStateOf(true) }
    
    var showExplanationDialog by remember { mutableStateOf(false) }
    var explanationText by remember { mutableStateOf("") }
    
    LaunchedEffect(Unit) {
        // "Descubrir Rhizome"
        status = client.getStatus()
        snapshot = client.getLatestSnapshot()
        receipts = client.getReceipts()
        isLoading = false
        if (snapshot != null) {
            onDataFetched(snapshot!!, receipts)
        }
    }

    if (isLoading) {
        Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
            CircularProgressIndicator()
        }
        return
    }

    Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        Text("Conectado a Rhizome", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
        status?.let {
            Text("Estado: ${it["status"]} | Versión: ${it["version"]}", color = MaterialTheme.colorScheme.primary)
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        snapshot?.let { snap ->
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("Snapshot Local", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                    Spacer(modifier = Modifier.height(8.dp))
                    Text("Modo: ${snap.mode}")
                    Text("Depósito: ${snap.sensors.tankLevelPct}%")
                    Text("Humedad Suelo A/B: ${snap.sensors.soilMoistureAPct}% / ${snap.sensors.soilMoistureBPct}%")
                    Text("Política Activa: ${snap.activePolicyId.take(15)}...")
                }
            }
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        Text("Últimos Recibos de Decisión", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
        Spacer(modifier = Modifier.height(8.dp))
        
        LazyColumn {
            items(receipts) { receipt ->
                Card(
                    modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp),
                    elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Text(receipt.action.name, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.secondary)
                            Spacer(modifier = Modifier.weight(1f))
                            Text(receipt.createdAt, style = MaterialTheme.typography.bodySmall, color = Color.Gray)
                        }
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(receipt.rationaleShort, style = MaterialTheme.typography.bodyMedium)
                        Spacer(modifier = Modifier.height(8.dp))
                        
                        OutlinedButton(onClick = {
                            scope.launch {
                                explanationText = client.explainDecision(receipt.decisionId)
                                showExplanationDialog = true
                            }
                        }) {
                            Icon(Icons.Default.Info, contentDescription = "Explicar", modifier = Modifier.size(16.dp))
                            Spacer(Modifier.width(4.dp))
                            Text("Explicar Decisión (Gemma)")
                        }
                    }
                }
            }
        }
    }

    if (showExplanationDialog) {
        AlertDialog(
            onDismissRequest = { showExplanationDialog = false },
            title = { Text("Explicación de Gemma 4 E2B") },
            text = { Text(explanationText) },
            confirmButton = {
                TextButton(onClick = { showExplanationDialog = false }) {
                    Text("Cerrar")
                }
            }
        )
    }
}
