package net.sprout.pollen.ui.chat

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.text.selection.SelectionContainer
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import net.sprout.pollen.domain.model.GenerationMetrics
import net.sprout.pollen.llm.LiteRtChatService
import net.sprout.pollen.llm.LiteRtSessionManager
import net.sprout.pollen.domain.model.BackendMode
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

data class ChatUiState(
    val prompt: String = "",
    val isLoading: Boolean = false,
    val output: String = "",
    val error: String? = null,
    val metrics: GenerationMetrics? = null
)

class ChatViewModel(
    private val chatService: LiteRtChatService,
    private val sessionManager: LiteRtSessionManager,
    private val modelPath: String
) : ViewModel() {
    private val _uiState = MutableStateFlow(ChatUiState())
    val uiState: StateFlow<ChatUiState> = _uiState

    init {
        // Initialize engine strictly on background IO thread
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, output = "Iniciando motor LiteRT-LM en CPU...") }
            try {
                withContext(Dispatchers.IO) {
                    sessionManager.initialize(modelPath, BackendMode.CPU)
                }
                _uiState.update { it.copy(
                    isLoading = false, 
                    output = "Engine listo.\nTiempo init: ${sessionManager.lastMetrics?.initializeMillis}ms",
                    metrics = sessionManager.lastMetrics
                ) }
            } catch (e: Exception) {
                _uiState.update { it.copy(isLoading = false, error = e.message, output = "Fallo: ${e.message}") }
            }
        }
    }

    fun onPromptChanged(value: String) {
        _uiState.update { it.copy(prompt = value) }
    }

    fun send() {
        val prompt = _uiState.value.prompt.trim()
        if (prompt.isEmpty()) return

        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, output = "", error = null, metrics = null) }
            
            withContext(Dispatchers.IO) {
                runCatching {
                    chatService.sendPrompt(prompt).collect { (chunk, metricsUpdate) ->
                        _uiState.update { state ->
                            state.copy(
                                output = state.output + chunk,
                                metrics = metricsUpdate ?: state.metrics
                            )
                        }
                    }
                }.onFailure { t ->
                    _uiState.update { it.copy(error = t.message) }
                }
            }
            _uiState.update { it.copy(isLoading = false) }
        }
    }
}

@Composable
fun ChatScreen(
    uiState: ChatUiState,
    onPromptChanged: (String) -> Unit,
    onSend: () -> Unit,
) {
    Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        OutlinedTextField(
            value = uiState.prompt,
            onValueChange = onPromptChanged,
            modifier = Modifier.fillMaxWidth(),
            label = { Text("Mensaje para Gemma 4 E4B") }
        )

        Spacer(Modifier.height(12.dp))

        Button(
            onClick = onSend,
            enabled = !uiState.isLoading,
        ) {
            Text(if (uiState.isLoading) "Pensando / Generando..." else "Enviar")
        }

        Spacer(Modifier.height(8.dp))

        uiState.metrics?.let { m ->
            Card(modifier = Modifier.fillMaxWidth(), colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)) {
                Column(modifier = Modifier.padding(8.dp)) {
                    Text("Backend: ${m.backendMode}", style = MaterialTheme.typography.labelSmall)
                    Text("Init Time: ${m.initializeMillis} ms", style = MaterialTheme.typography.labelSmall)
                    Text("TTFT (1er token): ${m.ttftMillis} ms", style = MaterialTheme.typography.labelSmall)
                    Text("Generación total: ${m.totalMillis} ms", style = MaterialTheme.typography.labelSmall)
                    Text("Tokens(chars): ${m.outputChars}", style = MaterialTheme.typography.labelSmall)
                }
            }
        }

        Spacer(Modifier.height(16.dp))

        if (uiState.error != null) {
            Text(text = "Error: ${uiState.error}", color = MaterialTheme.colorScheme.error)
        }

        SelectionContainer {
            Text(text = uiState.output, style = MaterialTheme.typography.bodyLarge)
        }
    }
}
