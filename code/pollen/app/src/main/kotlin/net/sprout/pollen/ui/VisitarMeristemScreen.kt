package net.sprout.pollen.ui

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CloudUpload
import androidx.compose.material.icons.filled.Download
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.launch
import net.sprout.pollen.schemas.FieldVisit
import net.sprout.pollen.schemas.PolicyPacket
import net.sprout.pollen.schemas.RhizomeSnapshot
import net.sprout.pollen.schemas.DecisionReceipt
import androidx.compose.ui.platform.LocalContext
import net.sprout.pollen.sync.MeristemClient
import net.sprout.pollen.sync.MeristemMockClient

@Composable
fun VisitarMeristemScreen(
    currentSnapshot: RhizomeSnapshot? = null,
    currentReceipts: List<DecisionReceipt> = emptyList(),
    onPolicyDownloaded: (PolicyPacket) -> Unit = {}
) {
    // Para conectar con el portátil del agricultor, instanciar MeristemNetworkClient("http://<IP_MERISTEM>:8080")
    val client: MeristemClient = remember { MeristemMockClient() }
    val scope = rememberCoroutineScope()
    val context = LocalContext.current
    
    var isUploading by remember { mutableStateOf(false) }
    var uploadSuccess by remember { mutableStateOf(false) }
    
    var isDownloading by remember { mutableStateOf(false) }
    var downloadedPolicy by remember { mutableStateOf<PolicyPacket?>(null) }
    
    Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        Text("Conectado a Meristem (Hogar)", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
        Text("Cerebro doméstico", color = MaterialTheme.colorScheme.primary)
        
        Spacer(modifier = Modifier.height(24.dp))
        
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("1. Descargar Datos de Campo", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                Spacer(modifier = Modifier.height(8.dp))
                Text("Transfiere el estado local de Rhizome a Meristem para su asimilación lenta.")
                Spacer(modifier = Modifier.height(16.dp))
                
                Button(
                    onClick = {
                        if (currentSnapshot != null) {
                            scope.launch {
                                isUploading = true
                                val visit = FieldVisit(currentSnapshot, currentReceipts)
                                client.uploadFieldVisit(visit)
                                isUploading = false
                                uploadSuccess = true
                            }
                        }
                    },
                    modifier = Modifier.fillMaxWidth(),
                    enabled = !isUploading && currentSnapshot != null
                ) {
                    if (isUploading) {
                        CircularProgressIndicator(modifier = Modifier.size(20.dp), strokeWidth = 2.dp)
                    } else {
                        Icon(Icons.Default.CloudUpload, contentDescription = "Subir Visita")
                        Spacer(Modifier.width(8.dp))
                        Text(if (currentSnapshot == null) "No hay datos locales" else "Subir Visita de Campo a Meristem")
                    }
                }
                if (uploadSuccess) {
                    Spacer(modifier = Modifier.height(8.dp))
                    Text("¡Visita subida con éxito!", color = MaterialTheme.colorScheme.secondary)
                }
            }
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("2. Cargar Nueva Política", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                Spacer(modifier = Modifier.height(8.dp))
                Text("Recoge la política actualizada calculada por Meristem.")
                Spacer(modifier = Modifier.height(16.dp))
                
                Button(
                    onClick = {
                        scope.launch {
                            isDownloading = true
                            try {
                                val policy = client.getLatestPolicy()
                                downloadedPolicy = policy
                                onPolicyDownloaded(policy)
                            } catch (e: Exception) {
                                // handle error
                            } finally {
                                isDownloading = false
                            }
                        }
                    },
                    modifier = Modifier.fillMaxWidth(),
                    enabled = !isDownloading
                ) {
                    if (isDownloading) {
                        CircularProgressIndicator(modifier = Modifier.size(20.dp), strokeWidth = 2.dp)
                    } else {
                        Icon(Icons.Default.Download, contentDescription = "Descargar Política")
                        Spacer(Modifier.width(8.dp))
                        Text("Descargar Política Actualizada")
                    }
                }
                
                downloadedPolicy?.let { policy ->
                    Spacer(modifier = Modifier.height(16.dp))
                    Divider()
                    Spacer(modifier = Modifier.height(8.dp))
                    Text("Política Recibida: ${policy.policyId}", fontWeight = FontWeight.Bold)
                    Text("Presupuesto de riego: ${policy.rules.dailyWaterBudgetLiters}L/día")
                    Text("Ventana: ${policy.rules.wateringWindow.startHourLocal}h - ${policy.rules.wateringWindow.endHourLocal}h")
                    policy.rationale?.let {
                        Spacer(modifier = Modifier.height(4.dp))
                        Text("Justificación: $it", style = MaterialTheme.typography.bodySmall)
                    }
                }
            }
        }
    }
}
