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
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import com.airbnb.lottie.compose.LottieAnimation
import com.airbnb.lottie.compose.LottieCompositionSpec
import com.airbnb.lottie.compose.LottieConstants
import com.airbnb.lottie.compose.rememberLottieComposition
import net.sprout.pollen.R
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
    val selectedArchetype: String = "Chat Libre",
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

    fun onArchetypeSelected(archetype: String) {
        val newThinkingState = when (archetype) {
            "Misión", "Auditoría" -> true
            else -> false
        }
        _uiState.update { it.copy(selectedArchetype = archetype, isThinkingEnabled = newThinkingState) }
        chatService.resetConversation()
    }

    fun startListening() {
        if (net.sprout.pollen.BuildConfig.FLAVOR == "demo") {
            _uiState.update { it.copy(error = "Funcionalidad no disponible: El motor LLM requiere la variante Device y hardware NPU.") }
            return
        }
        if (_uiState.value.isListening) {
            val audioFile = voiceInfra.stopRecording()
            _uiState.update { it.copy(isListening = false) }
            if (audioFile != null) {
                sendAudio(audioFile)
            }
        } else {
            _uiState.update { it.copy(isListening = true, error = null) }
            try {
                voiceInfra.startRecording()
            } catch (e: Exception) {
                _uiState.update { it.copy(isListening = false, error = e.message) }
            }
        }
    }

    fun send() {
        if (net.sprout.pollen.BuildConfig.FLAVOR == "demo") {
            _uiState.update { it.copy(error = "Funcionalidad no disponible: El motor LLM requiere la variante Device y hardware NPU.") }
            return
        }
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

    private fun sendAudio(audioFile: java.io.File) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, output = "", error = null, metrics = null, prompt = "Mensaje de voz...") }
            
            withContext(Dispatchers.IO) {
                runCatching {
                    val instruction = "Escucha este clip de voz y responde por escrito en español. Responde de forma breve, natural y util. Si no entiendes el audio, dilo sin inventar."
                    chatService.sendAudioFile(audioFile.absolutePath, instruction, _uiState.value.isThinkingEnabled).collect { (chunk, metricsUpdate) ->
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
            audioFile.delete()
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
    onArchetypeSelected: (String) -> Unit
) {
    val haptic = LocalHapticFeedback.current
    Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        val archetypes = listOf("Chat Libre", "Misión", "Auditoría", "Contexto")
        ScrollableTabRow(
            selectedTabIndex = archetypes.indexOf(uiState.selectedArchetype).takeIf { it >= 0 } ?: 0,
            edgePadding = 8.dp,
            modifier = Modifier.fillMaxWidth()
        ) {
            archetypes.forEach { archetype ->
                Tab(
                    selected = uiState.selectedArchetype == archetype,
                    onClick = { onArchetypeSelected(archetype) },
                    text = { Text(archetype) }
                )
            }
        }

        Spacer(Modifier.height(12.dp))

        OutlinedTextField(
            value = uiState.prompt,
            onValueChange = onPromptChanged,
            modifier = Modifier.fillMaxWidth(),
            label = { Text("Mensaje para Pollen") }
        )

        Spacer(Modifier.height(12.dp))

        Row(verticalAlignment = androidx.compose.ui.Alignment.CenterVertically) {
            Button(
                onClick = {
                    haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                    onSend()
                },
                enabled = !uiState.isLoading,
            ) {
                Text(if (uiState.isLoading) "Generando..." else "Enviar")
            }
            Spacer(Modifier.width(8.dp))
            Button(
                onClick = onStartVoice,
                enabled = !uiState.isLoading,
                colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.secondary)
            ) {
                Text(if (uiState.isListening) "⏹️ Detener" else "🎤 Hablar")
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
            Column(modifier = Modifier.fillMaxWidth()) {
                if (uiState.isLoading && uiState.isThinkingEnabled && uiState.output.isEmpty()) {
                    val composition by rememberLottieComposition(LottieCompositionSpec.RawRes(R.raw.sprout_thinking))
                    LottieAnimation(
                        composition = composition,
                        iterations = LottieConstants.IterateForever,
                        modifier = Modifier.size(128.dp).align(androidx.compose.ui.Alignment.CenterHorizontally)
                    )
                }
                SelectionContainer {
                    Text(text = uiState.output, style = MaterialTheme.typography.bodyLarge)
                }
            }
        }
    }
}
