package net.sprout.pollen.ui

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import net.sprout.pollen.inference.AuditEvent
import net.sprout.pollen.inference.AuditResult
import net.sprout.pollen.inference.GemmaEngine
import net.sprout.pollen.schemas.DecisionReceipt
import net.sprout.pollen.schemas.RhizomeSnapshot

sealed class AuditUiState {
    object Idle : AuditUiState()
    object Loading : AuditUiState()
    data class Streaming(val text: String) : AuditUiState()
    data class Done(val text: String, val result: AuditResult) : AuditUiState()
    data class Error(val message: String) : AuditUiState()
}

class PollenViewModel(private val engine: GemmaEngine) : ViewModel() {
    private val _uiState = MutableStateFlow<AuditUiState>(AuditUiState.Idle)
    val uiState: StateFlow<AuditUiState> = _uiState.asStateFlow()

    fun runAudit(snapshot: RhizomeSnapshot, receipt: DecisionReceipt) {
        viewModelScope.launch {
            _uiState.value = AuditUiState.Loading
            try {
                var accumulatedText = ""
                engine.runAudit(snapshot, receipt).collect { event ->
                    when (event) {
                        is AuditEvent.Token -> {
                            accumulatedText += event.s
                            _uiState.value = AuditUiState.Streaming(accumulatedText)
                        }
                        is AuditEvent.Done -> {
                            _uiState.value = AuditUiState.Done(accumulatedText, event.result)
                        }
                    }
                }
            } catch (e: Exception) {
                _uiState.value = AuditUiState.Error(e.localizedMessage ?: "Unknown error during inference")
            }
        }
    }
}
