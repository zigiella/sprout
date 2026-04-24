package net.sprout.pollen

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import net.sprout.pollen.ui.chat.ChatScreen
import net.sprout.pollen.ui.chat.ChatViewModel
import net.sprout.pollen.llm.LiteRtEngineFactory
import net.sprout.pollen.llm.LiteRtBackendPolicy
import net.sprout.pollen.llm.LiteRtMetricsCollector
import net.sprout.pollen.llm.LiteRtSessionManager
import net.sprout.pollen.llm.LiteRtChatService
import androidx.compose.runtime.collectAsState
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        val engineFactory = LiteRtEngineFactory(this)
        val backendPolicy = LiteRtBackendPolicy()
        val metricsCollector = LiteRtMetricsCollector()
        val sessionManager = LiteRtSessionManager(engineFactory, backendPolicy, metricsCollector)
        val chatService = LiteRtChatService(sessionManager, metricsCollector)
        
        // As per F0, model is located at C:\DATA\PETS\TEST\T6A2-POLLEN\models\gemma-4-E4B-it.litertlm
        // But on Android device it will be pushed to /data/local/tmp/gemma-4-E4B-it.litertlm
        val viewModel = ChatViewModel(chatService, sessionManager, "/data/local/tmp/gemma-4-E4B-it.litertlm")

        setContent {
            MaterialTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    val uiState = viewModel.uiState.collectAsState().value
                    ChatScreen(
                        uiState = uiState,
                        onPromptChanged = { viewModel.onPromptChanged(it) },
                        onSend = { viewModel.send() }
                    )
                }
            }
        }
    }
}
