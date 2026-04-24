package net.sprout.pollen.voice

import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.speech.tts.TextToSpeech
import android.util.Log
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.update
import java.util.Locale

class PollenVoiceInfra(private val context: Context) {
    
    // Observabilidad: flujo de logs para mostrar en pantalla
    private val _logs = MutableStateFlow<List<String>>(emptyList())
    val logs: StateFlow<List<String>> = _logs

    private var tts: TextToSpeech? = null
    private var stt: SpeechRecognizer? = null

    init {
        log("VoiceInfra: Inicializando...")
        initTTS()
    }

    private fun log(message: String) {
        Log.d("PollenVoice", message)
        _logs.update { current -> 
            val newLogs = current + message
            if (newLogs.size > 20) newLogs.takeLast(20) else newLogs
        }
    }

    private fun initTTS() {
        tts = TextToSpeech(context) { status ->
            if (status == TextToSpeech.SUCCESS) {
                // Forzamos un locale, por ejemplo Español
                val result = tts?.setLanguage(Locale("es", "ES"))
                if (result == TextToSpeech.LANG_MISSING_DATA || result == TextToSpeech.LANG_NOT_SUPPORTED) {
                    log("TTS: Lenguaje no soportado")
                } else {
                    log("TTS: Listo y configurado")
                }
            } else {
                log("TTS: Fallo al inicializar (status: ${status})")
            }
        }
    }

    fun speak(text: String) {
        if (text.isBlank()) return
        log("TTS: Hablando (${text.take(15)}...)")
        tts?.speak(text, TextToSpeech.QUEUE_FLUSH, null, "PollenTTS")
    }

    fun stopSpeaking() {
        tts?.stop()
    }

    fun startListening(
        onResult: (String) -> Unit,
        onError: (String) -> Unit,
        onPartial: (String) -> Unit
    ) {
        if (!SpeechRecognizer.isRecognitionAvailable(context)) {
            log("STT: No disponible en este dispositivo")
            onError("Reconocimiento no disponible")
            return
        }

        if (stt == null) {
            stt = SpeechRecognizer.createSpeechRecognizer(context)
        }

        val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            putExtra(RecognizerIntent.EXTRA_LANGUAGE, "es-ES")
            putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, true)
        }

        stt?.setRecognitionListener(object : RecognitionListener {
            override fun onReadyForSpeech(params: Bundle?) { log("STT: Escuchando...") }
            override fun onBeginningOfSpeech() { log("STT: Usuario hablando") }
            override fun onRmsChanged(rmsdB: Float) {}
            override fun onBufferReceived(buffer: ByteArray?) {}
            override fun onEndOfSpeech() { log("STT: Procesando...") }
            
            override fun onError(error: Int) {
                val errorMsg = when (error) {
                    SpeechRecognizer.ERROR_AUDIO -> "Error de audio"
                    SpeechRecognizer.ERROR_CLIENT -> "Error del cliente"
                    SpeechRecognizer.ERROR_INSUFFICIENT_PERMISSIONS -> "Faltan permisos (RECORD_AUDIO)"
                    SpeechRecognizer.ERROR_NETWORK -> "Error de red"
                    SpeechRecognizer.ERROR_NETWORK_TIMEOUT -> "Timeout de red"
                    SpeechRecognizer.ERROR_NO_MATCH -> "No se entendió nada"
                    SpeechRecognizer.ERROR_RECOGNIZER_BUSY -> "Reconocedor ocupado"
                    SpeechRecognizer.ERROR_SERVER -> "Error de servidor"
                    SpeechRecognizer.ERROR_SPEECH_TIMEOUT -> "Timeout de voz"
                    else -> "Error desconocido ($error)"
                }
                log("STT Error: $errorMsg")
                onError(errorMsg)
            }

            override fun onResults(results: Bundle?) {
                val matches = results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                val text = matches?.firstOrNull() ?: ""
                log("STT OK: $text")
                onResult(text)
            }

            override fun onPartialResults(partialResults: Bundle?) {
                val matches = partialResults?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                val text = matches?.firstOrNull() ?: ""
                onPartial(text)
            }

            override fun onEvent(eventType: Int, params: Bundle?) {}
        })

        stt?.startListening(intent)
    }

    fun stopListening() {
        log("STT: Detenido por el sistema/usuario")
        stt?.stopListening()
    }

    fun destroy() {
        tts?.stop()
        tts?.shutdown()
        stt?.destroy()
    }
}
