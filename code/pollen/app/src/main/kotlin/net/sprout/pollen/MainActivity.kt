package net.sprout.pollen

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import androidx.core.content.ContextCompat
import net.sprout.pollen.ui.chat.ChatScreen
import net.sprout.pollen.ui.chat.ChatViewModel
import net.sprout.pollen.llm.LiteRtEngineFactory
import net.sprout.pollen.llm.LiteRtBackendPolicy
import net.sprout.pollen.llm.LiteRtMetricsCollector
import net.sprout.pollen.llm.LiteRtSessionManager
import net.sprout.pollen.llm.LiteRtChatService
import net.sprout.pollen.voice.PollenVoiceInfra
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.foundation.layout.Column
import androidx.compose.material3.Tab
import androidx.compose.material3.TabRow
import androidx.compose.material3.Text
import net.sprout.pollen.schemas.DecisionReceipt
import net.sprout.pollen.schemas.RhizomeSnapshot
import net.sprout.pollen.schemas.PolicyPacket
import net.sprout.pollen.ui.VisitarMeristemScreen
import net.sprout.pollen.ui.VisitarRhizomeScreen
import net.sprout.pollen.ui.AuditLogScreen
import net.sprout.pollen.ui.HomeScreen
import androidx.compose.ui.res.stringResource
import net.sprout.pollen.R
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.TextButton
import androidx.compose.material3.Button
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.width
import androidx.compose.ui.Alignment
import androidx.compose.ui.unit.dp

enum class AppScreen {
    HOME, MERISTEM, RHIZOME_DETAIL, CHAT, AUDIT
}

class MainActivity : ComponentActivity() {

    private val requestPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted: Boolean ->
        // Si no lo concede, el log de VoiceInfra avisará
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            requestPermissionLauncher.launch(Manifest.permission.RECORD_AUDIO)
        }

        val engineFactory = LiteRtEngineFactory(this)
        val backendPolicy = LiteRtBackendPolicy()
        val metricsCollector = LiteRtMetricsCollector()
        val sessionManager = LiteRtSessionManager(engineFactory, backendPolicy, metricsCollector)
        val chatService = LiteRtChatService(sessionManager, metricsCollector)
        val voiceInfra = PollenVoiceInfra(this)
        
        val viewModel = ChatViewModel(chatService, sessionManager, voiceInfra, "/data/local/tmp/gemma-4-E4B-it.litertlm")

        setContent {
            MaterialTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    var currentScreen by remember { mutableStateOf(AppScreen.HOME) }
                    var selectedRhizomeId by remember { mutableStateOf("") }
                    
                    var globalSnapshot by remember { mutableStateOf<RhizomeSnapshot?>(null) }
                    var globalReceipts by remember { mutableStateOf<List<DecisionReceipt>>(emptyList()) }
                    var globalPolicy by remember { mutableStateOf<PolicyPacket?>(null) }
                    
                    var showVisionAlert by remember { mutableStateOf(false) }

                    if (showVisionAlert) {
                        AlertDialog(
                            onDismissRequest = { showVisionAlert = false },
                            title = { Text(stringResource(R.string.notif_vision_title)) },
                            text = { Text(stringResource(R.string.notif_vision_desc)) },
                            confirmButton = {
                                TextButton(onClick = { showVisionAlert = false }) { Text("OK") }
                            }
                        )
                    }

                    Column(modifier = Modifier.fillMaxSize()) {
                        if (currentScreen != AppScreen.HOME) {
                            Row(modifier = Modifier.fillMaxWidth().padding(8.dp), verticalAlignment = Alignment.CenterVertically) {
                                IconButton(onClick = { currentScreen = AppScreen.HOME }) {
                                    Icon(Icons.Default.ArrowBack, contentDescription = "Volver")
                                }
                                Text("Volver a Inicio", style = MaterialTheme.typography.titleMedium)
                            }
                        }

                        when (currentScreen) {
                            AppScreen.HOME -> {
                                HomeScreen(
                                    onNavigateToRhizome = { rhId ->
                                        selectedRhizomeId = rhId
                                        currentScreen = AppScreen.RHIZOME_DETAIL
                                    },
                                    onNavigateToMeristem = {
                                        currentScreen = AppScreen.MERISTEM
                                    }
                                )
                            }
                            AppScreen.CHAT -> {
                                val uiState = viewModel.uiState.collectAsState().value
                                Text("Contexto: $selectedRhizomeId", modifier = Modifier.padding(start=16.dp), color=MaterialTheme.colorScheme.primary)
                                ChatScreen(
                                    uiState = uiState,
                                    onPromptChanged = { viewModel.onPromptChanged(it) },
                                    onThinkingToggled = { viewModel.onThinkingToggled(it) },
                                    onSend = { viewModel.send() },
                                    onStartVoice = { viewModel.startListening() },
                                    onArchetypeSelected = { viewModel.onArchetypeSelected(it) }
                                )
                            }
                            AppScreen.RHIZOME_DETAIL -> {
                                Column {
                                    Text("Parcela Seleccionada: $selectedRhizomeId", modifier = Modifier.padding(16.dp), style = MaterialTheme.typography.titleLarge)
                                    Row(modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp)) {
                                        Button(onClick = { currentScreen = AppScreen.CHAT }, modifier = Modifier.weight(1f)) {
                                            Text("Chatear con Pollen")
                                        }
                                        Spacer(modifier = Modifier.width(8.dp))
                                        Button(onClick = { currentScreen = AppScreen.AUDIT }, modifier = Modifier.weight(1f)) {
                                            Text("Historial")
                                        }
                                    }
                                    VisitarRhizomeScreen(
                                        onDataFetched = { snap, rec -> 
                                            globalSnapshot = snap
                                            globalReceipts = rec 
                                        }
                                    )
                                }
                            }
                            AppScreen.MERISTEM -> {
                                VisitarMeristemScreen(
                                    currentSnapshot = globalSnapshot,
                                    currentReceipts = globalReceipts,
                                    onPolicyDownloaded = { policy ->
                                        globalPolicy = policy
                                        if (policy.rules.requireVisionConfirmation) {
                                            showVisionAlert = true
                                        }
                                    }
                                )
                            }
                            AppScreen.AUDIT -> {
                                AuditLogScreen(receipts = globalReceipts, policy = globalPolicy)
                            }
                        }
                    }
                }
            }
        }
    }
}
