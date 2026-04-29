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
import net.sprout.pollen.ui.VisitarMeristemScreen
import net.sprout.pollen.ui.VisitarRhizomeScreen

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
                    var selectedTab by remember { mutableStateOf(0) }
                    val tabs = listOf("Chat Pollen", "Visitar Rhizome", "Visitar Meristem")
                    
                    var globalSnapshot by remember { mutableStateOf<RhizomeSnapshot?>(null) }
                    var globalReceipts by remember { mutableStateOf<List<DecisionReceipt>>(emptyList()) }

                    Column(modifier = Modifier.fillMaxSize()) {
                        TabRow(selectedTabIndex = selectedTab) {
                            tabs.forEachIndexed { index, title ->
                                Tab(
                                    selected = selectedTab == index,
                                    onClick = { selectedTab = index },
                                    text = { Text(title) }
                                )
                            }
                        }
                        
                        if (selectedTab == 0) {
                            val uiState = viewModel.uiState.collectAsState().value
                            ChatScreen(
                                uiState = uiState,
                                onPromptChanged = { viewModel.onPromptChanged(it) },
                                onThinkingToggled = { viewModel.onThinkingToggled(it) },
                                onSend = { viewModel.send() },
                                onStartVoice = { viewModel.startListening() },
                                onArchetypeSelected = { viewModel.onArchetypeSelected(it) }
                            )
                        } else if (selectedTab == 1) {
                            VisitarRhizomeScreen(
                                onDataFetched = { snap, rec -> 
                                    globalSnapshot = snap
                                    globalReceipts = rec 
                                }
                            )
                        } else {
                            VisitarMeristemScreen(
                                currentSnapshot = globalSnapshot,
                                currentReceipts = globalReceipts
                            )
                        }
                    }
                }
            }
        }
    }
}
