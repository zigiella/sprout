package net.sprout.pollen.ui.chat

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
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
import net.sprout.pollen.voice.PollenVoiceInfra
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

data class ChatUiState(
    val prompt: String = "",
    val isLoading: Boolean = false,
    val isListening: Boolean = false,
    val output: String = "",
    val error: String? = null,
    val metrics: GenerationMetrics? = null,
    val isThinkingEnabled: Boolean = false,
    val voiceLogs: List<String> = emptyList()
)

class ChatViewModel(
    private val chatService: LiteRtChatService,
    private val sessionManager: LiteRtSessionManager,
    private val voiceInfra: PollenVoiceInfra,
    private val modelPath: String
) : ViewModel() {
    private val _uiState = MutableStateFlow(ChatUiState())
    val uiState: StateFlow<ChatUiState> = _uiState

    init {
        viewModelScope.launch {
            // Recoger logs de VoiceInfra
            launch {
                voiceInfra.logs.collect { logs ->
                    _uiState.update { it.copy(voiceLogs = logs) }
                }
            }

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

    fun onThinkingToggled(enabled: Boolean) {
        _uiState.update { it.copy(isThinkingEnabled = enabled) }
        chatService.resetConversation()
    }

    fun startListening() {
        _uiState.update { it.copy(isListening = true) }
        voiceInfra.startListening(
            onResult = { text ->
                _uiState.update { it.copy(prompt = text, isListening = false) }
                send() // Autodisparar
            },
            onError = { err ->
                _uiState.update { it.copy(isListening = false, error = err) }
            },
            onPartial = { partial ->
                _uiState.update { it.copy(prompt = partial) }
            }
        )
    }

    fun send() {
        val prompt = _uiState.value.prompt.trim()
        if (prompt.isEmpty()) return

        // voiceInfra.stopSpeaking() // Eliminado por petición de usuario

        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, output = "", error = null, metrics = null) }
            
            withContext(Dispatchers.IO) {
                runCatching {
                    chatService.sendPrompt(prompt, _uiState.value.isThinkingEnabled).collect { (chunk, metricsUpdate) ->
                        // Acumular chunk visualmente
                        _uiState.update { state ->
                            state.copy(
                                output = state.output + chunk,
                                metrics = metricsUpdate ?: state.metrics
                            )
                        }
                    }
                    
                    // Al finalizar, (TTS eliminado)

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
    onThinkingToggled: (Boolean) -> Unit,
    onStartVoice: () -> Unit,
    onSend: () -> Unit,
) {
    Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        OutlinedTextField(
            value = uiState.prompt,
            onValueChange = onPromptChanged,
            modifier = Modifier.fillMaxWidth(),
            label = { Text("Mensaje para Pollen") }
        )

        Spacer(Modifier.height(12.dp))

        Row(verticalAlignment = androidx.compose.ui.Alignment.CenterVertically) {
            Button(
                onClick = onSend,
                enabled = !uiState.isLoading,
            ) {
                Text(if (uiState.isLoading) "Generando..." else "Enviar")
            }
            Spacer(Modifier.width(8.dp))
            Button(
                onClick = onStartVoice,
                enabled = !uiState.isLoading && !uiState.isListening,
                colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.secondary)
            ) {
                Text(if (uiState.isListening) "Escuchando..." else "🎤 Hablar")
            }
            Spacer(Modifier.width(16.dp))
            Text("Thinking")
            Switch(
                checked = uiState.isThinkingEnabled,
                onCheckedChange = onThinkingToggled
            )
        }

        Spacer(Modifier.height(8.dp))

        uiState.metrics?.let { m ->
            Card(modifier = Modifier.fillMaxWidth(), colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)) {
                Column(modifier = Modifier.padding(8.dp)) {
                    Text("Backend: ${m.backendMode}", style = MaterialTheme.typography.labelSmall)
                    Text("Init Time: ${m.initializeMillis} ms", style = MaterialTheme.typography.labelSmall)
                    Text("TTFT (1er token): ${m.ttftMillis} ms", style = MaterialTheme.typography.labelSmall)
                    Text("Generación total: ${m.totalMillis} ms", style = MaterialTheme.typography.labelSmall)
                }
            }
        }

        Spacer(Modifier.height(16.dp))

        if (uiState.error != null) {
            Text(text = "Error: ${uiState.error}", color = MaterialTheme.colorScheme.error)
        }

        // Voice logs console
        if (uiState.voiceLogs.isNotEmpty()) {
            Box(modifier = Modifier
                .fillMaxWidth()
                .height(80.dp)
                .background(MaterialTheme.colorScheme.surfaceVariant)
                .padding(4.dp)
                .verticalScroll(rememberScrollState())
            ) {
                Text(
                    text = uiState.voiceLogs.joinToString("\n"),
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            Spacer(Modifier.height(8.dp))
        }

        Box(modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState())) {
            SelectionContainer {
                Text(text = uiState.output, style = MaterialTheme.typography.bodyLarge)
            }
        }
    }
}
