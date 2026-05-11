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
import androidx.compose.ui.res.stringResource
import net.sprout.pollen.R

@Composable
fun VisitarMeristemScreen(
    currentSnapshot: RhizomeSnapshot? = null,
    currentReceipts: List<DecisionReceipt> = emptyList(),
    onPolicyDownloaded: (PolicyPacket) -> Unit = {}
) {
    val client: MeristemClient = remember { 
        MeristemNetworkClient("http://192.168.1.36:13000/")
    }
    val scope = rememberCoroutineScope()
    val context = LocalContext.current
    
    var isConnected by remember { mutableStateOf(false) }
    var lastConnectionDate by remember { mutableStateOf<String>("-") }
    
    var isUploading by remember { mutableStateOf(false) }
    var uploadSuccess by remember { mutableStateOf(false) }
    
    var isDownloading by remember { mutableStateOf(false) }
    var downloadedPolicy by remember { mutableStateOf<PolicyPacket?>(null) }
    
    var syncLogs by remember { mutableStateOf(listOf<String>()) }
    fun addLog(msg: String) {
        val time = LocalDateTime.now().format(DateTimeFormatter.ofPattern("HH:mm:ss"))
        syncLogs = syncLogs + "[$time] $msg"
    }

    val checkingConnectionStr = stringResource(R.string.meristem_checking_connection)
    val connectionOkStr = stringResource(R.string.meristem_connection_ok)
    val connectionErrorStr = stringResource(R.string.meristem_connection_error)

    LaunchedEffect(Unit) {
        addLog(checkingConnectionStr)
        var first = true
        while(true) {
            val pendingCount = if (currentSnapshot != null) 1 else 0
            val isUp = client.sendHello(net.sprout.pollen.sync.PollenHello(
                pollen_id = "pollen-dev-01",
                app_version = "1.0.0",
                bundles_pending_count = pendingCount
            ))
            
            isConnected = isUp
            if (isUp) {
                lastConnectionDate = LocalDateTime.now().format(DateTimeFormatter.ofPattern("dd/MM/yyyy HH:mm:ss"))
                if (first) {
                    addLog(connectionOkStr)
                    first = false
                }
            } else {
                if (first) {
                    addLog(connectionErrorStr)
                    first = false
                }
            }
            kotlinx.coroutines.delay(5000) // Heartbeat cada 5 segundos
        }
    }
    
    val scrollState = rememberScrollState()
    
    Column(modifier = Modifier.fillMaxSize().padding(16.dp).verticalScroll(scrollState)) {
        Text(stringResource(R.string.meristem_connected_home), style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
        Text(stringResource(R.string.meristem_domestic_brain), color = MaterialTheme.colorScheme.primary)
        
        Spacer(modifier = Modifier.height(8.dp))
        Row(verticalAlignment = Alignment.CenterVertically) {
            val statusColor = if (isConnected) Color(0xFF4CAF50) else Color(0xFFF44336)
            val statusText = if (isConnected) stringResource(R.string.meristem_status_connected) else stringResource(R.string.meristem_status_disconnected)
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
            Text("${stringResource(R.string.meristem_last_time)} $lastConnectionDate", style = MaterialTheme.typography.bodySmall, color = Color.Gray)
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(stringResource(R.string.meristem_step1_title), style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                Spacer(modifier = Modifier.height(8.dp))
                Text(stringResource(R.string.meristem_step1_desc))
                Spacer(modifier = Modifier.height(16.dp))
                
                val uploadStartFormat = stringResource(R.string.meristem_upload_start)
                val uploadSuccessStr = stringResource(R.string.meristem_upload_success)
                val uploadErrorFormat = stringResource(R.string.meristem_upload_error)
                val uploadDoneMsgStr = stringResource(R.string.meristem_upload_done_msg)
                
                Button(
                    onClick = {
                        if (currentSnapshot != null) {
                            scope.launch {
                                isUploading = true
                                addLog(String.format(uploadStartFormat, currentSnapshot.snapshotId))
                                try {
                                    val visit = FieldVisit(currentSnapshot, currentReceipts)
                                    client.uploadFieldVisit(visit)
                                    uploadSuccess = true
                                    addLog(uploadSuccessStr)
                                    Toast.makeText(context, uploadDoneMsgStr, Toast.LENGTH_SHORT).show()
                                } catch (e: Exception) {
                                    Log.e("VisitarMeristem", "Upload failed", e)
                                    val err = String.format(uploadErrorFormat, e.message)
                                    addLog(err)
                                    Toast.makeText(context, err, Toast.LENGTH_LONG).show()
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
                        Text(if (currentSnapshot == null) stringResource(R.string.meristem_no_local_data) else stringResource(R.string.meristem_upload_btn))
                    }
                }
                if (uploadSuccess) {
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(stringResource(R.string.meristem_upload_done_msg), color = MaterialTheme.colorScheme.secondary)
                }
            }
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(stringResource(R.string.meristem_step2_title), style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                Spacer(modifier = Modifier.height(8.dp))
                Text(stringResource(R.string.meristem_step2_desc))
                Spacer(modifier = Modifier.height(16.dp))
                
                val downloadStartFormat = stringResource(R.string.meristem_download_start)
                val downloadSuccessFormat = stringResource(R.string.meristem_download_success)
                val downloadErrorFormat = stringResource(R.string.meristem_download_error)
                
                Button(
                    onClick = {
                        scope.launch {
                            isDownloading = true
                            val targetId = currentSnapshot?.originNodeId ?: "rhizome_01"
                            addLog(String.format(downloadStartFormat, targetId))
                            try {
                                val policy = client.getLatestPolicy(targetId)
                                downloadedPolicy = policy
                                onPolicyDownloaded(policy)
                                addLog(String.format(downloadSuccessFormat, policy.policyId))
                                Toast.makeText(context, "Policy downloaded!", Toast.LENGTH_SHORT).show()
                            } catch (e: Exception) {
                                Log.e("VisitarMeristem", "Download failed", e)
                                val err = String.format(downloadErrorFormat, e.message)
                                addLog(err)
                                Toast.makeText(context, err, Toast.LENGTH_LONG).show()
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
                        Text(stringResource(R.string.meristem_download_btn))
                    }
                }
                
                val receivedPolicyFormat = stringResource(R.string.meristem_received_policy)
                val waterBudgetFormat = stringResource(R.string.meristem_water_budget)
                val windowFormat = stringResource(R.string.meristem_window)
                val rationaleFormat = stringResource(R.string.meristem_rationale)
                
                downloadedPolicy?.let { policy ->
                    Spacer(modifier = Modifier.height(16.dp))
                    Divider()
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(String.format(receivedPolicyFormat, policy.policyId), fontWeight = FontWeight.Bold)
                    Text(String.format(waterBudgetFormat, policy.rules.dailyWaterBudgetLiters.toString()))
                    Text(String.format(windowFormat, policy.rules.wateringWindow.startHourLocal.toString(), policy.rules.wateringWindow.endHourLocal.toString()))
                    policy.rationale?.let {
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(String.format(rationaleFormat, it), style = MaterialTheme.typography.bodySmall)
                    }
                }
            }
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        Text(stringResource(R.string.meristem_sync_log), style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
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
