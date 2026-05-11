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
import net.sprout.pollen.sync.MeristemNetworkClient
import net.sprout.pollen.sync.MeristemMockClient

import android.widget.Toast
import android.util.Log
import androidx.compose.ui.graphics.Color
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

@Composable
fun VisitarMeristemScreen(
    currentSnapshot: RhizomeSnapshot? = null,
    currentReceipts: List<DecisionReceipt> = emptyList(),
    onPolicyDownloaded: (PolicyPacket) -> Unit = {}
) {
    val client: MeristemClient = remember { 
        MeristemNetworkClient("http://192.168.1.42:13000/")
    }
    val scope = rememberCoroutineScope()
    val context = LocalContext.current
    
    var isConnected by remember { mutableStateOf(false) }
    var lastConnectionDate by remember { mutableStateOf<String>("Nunca") }
    
    var isUploading by remember { mutableStateOf(false) }
    var uploadSuccess by remember { mutableStateOf(false) }
    
    var isDownloading by remember { mutableStateOf(false) }
    var downloadedPolicy by remember { mutableStateOf<PolicyPacket?>(null) }
    
    var syncLogs by remember { mutableStateOf(listOf<String>()) }
    fun addLog(msg: String) {
        val time = LocalDateTime.now().format(DateTimeFormatter.ofPattern("HH:mm:ss"))
        syncLogs = syncLogs + "[$time] $msg"
    }

    LaunchedEffect(Unit) {
        addLog("Comprobando conexión con Meristem...")
        val isUp = client.checkHealth()
        isConnected = isUp
        if (isUp) {
            lastConnectionDate = LocalDateTime.now().format(DateTimeFormatter.ofPattern("dd/MM/yyyy HH:mm:ss"))
            addLog("Conexión establecida OK.")
        } else {
            addLog("Error: Meristem no accesible.")
        }
    }
    
    val scrollState = rememberScrollState()
    
    Column(modifier = Modifier.fillMaxSize().padding(16.dp).verticalScroll(scrollState)) {
        Text("Conectado a Meristem (Hogar)", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
        Text("Cerebro doméstico", color = MaterialTheme.colorScheme.primary)
        
        Spacer(modifier = Modifier.height(8.dp))
        Row(verticalAlignment = Alignment.CenterVertically) {
            val statusColor = if (isConnected) Color(0xFF4CAF50) else Color(0xFFF44336)
            val statusText = if (isConnected) "Conectado" else "Desconectado"
            Surface(shape = RoundedCornerShape(4.dp), color = statusColor.copy(alpha = 0.2f)) {
                Text(
                    text = "● $statusText",
                    color = statusColor,
                    modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                    style = MaterialTheme.typography.labelMedium,
                    fontWeight = FontWeight.Bold
                )
            }
            Spacer(modifier = Modifier.width(8.dp))
            Text("Última vez: $lastConnectionDate", style = MaterialTheme.typography.bodySmall, color = Color.Gray)
        }
        
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
                                addLog("Iniciando subida de snapshot ${currentSnapshot.snapshotId}...")
                                try {
                                    val visit = FieldVisit(currentSnapshot, currentReceipts)
                                    client.uploadFieldVisit(visit)
                                    uploadSuccess = true
                                    addLog("Subida completada con éxito.")
                                    Toast.makeText(context, "Upload success!", Toast.LENGTH_SHORT).show()
                                } catch (e: Exception) {
                                    Log.e("VisitarMeristem", "Upload failed", e)
                                    addLog("Error en subida: ${e.message}")
                                    Toast.makeText(context, "Error: ${e.message}", Toast.LENGTH_LONG).show()
                                } finally {
                                    isUploading = false
                                }
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
                            val targetId = currentSnapshot?.originNodeId ?: "rhizome_01"
                            addLog("Solicitando política para nodo: $targetId...")
                            try {
                                val policy = client.getLatestPolicy(targetId)
                                downloadedPolicy = policy
                                onPolicyDownloaded(policy)
                                addLog("Política ${policy.policyId} descargada y guardada.")
                                Toast.makeText(context, "Policy downloaded!", Toast.LENGTH_SHORT).show()
                            } catch (e: Exception) {
                                Log.e("VisitarMeristem", "Download failed", e)
                                addLog("Error en descarga: ${e.message}")
                                Toast.makeText(context, "Error: ${e.message}", Toast.LENGTH_LONG).show()
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
        
        Spacer(modifier = Modifier.height(24.dp))
        Text("Log de Sincronización", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
        Spacer(modifier = Modifier.height(8.dp))
        Surface(
            modifier = Modifier.fillMaxWidth().heightIn(min = 100.dp, max = 200.dp),
            color = Color.Black,
            shape = RoundedCornerShape(8.dp)
        ) {
            Column(modifier = Modifier.padding(8.dp)) {
                syncLogs.forEach { logLine ->
                    Text(text = logLine, color = Color.Green, style = MaterialTheme.typography.bodySmall.copy(fontFamily = androidx.compose.ui.text.font.FontFamily.Monospace))
                }
            }
        }
        Spacer(modifier = Modifier.height(32.dp))
    }
}
