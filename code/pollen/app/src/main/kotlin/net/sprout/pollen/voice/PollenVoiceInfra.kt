package net.sprout.pollen.voice

import android.content.Context
import android.speech.tts.TextToSpeech
import android.util.Log
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.update
import java.io.File
import java.util.Locale

class PollenVoiceInfra(private val context: Context) {
    
    private val _logs = MutableStateFlow<List<String>>(emptyList())
    val logs: StateFlow<List<String>> = _logs

    private var tts: TextToSpeech? = null
    private val audioRecorder = AudioClipRecorder(context)

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

    fun startRecording() {
        try {
            audioRecorder.start()
            log("Grabando voz en WAV...")
        } catch (e: Exception) {
            log("Error al grabar: ${e.message}")
            throw e
        }
    }

    fun stopRecording(): File? {
        log("Deteniendo grabacion...")
        return try {
            val file = audioRecorder.stopAndSave()
            log("WAV guardado: ${file.absolutePath}")
            file
        } catch (e: Exception) {
            log("Error al detener grabacion: ${e.message}")
            null
        }
    }
    
    fun cancelRecording() {
        audioRecorder.cancel()
        log("Grabacion cancelada.")
    }

    fun destroy() {
        tts?.stop()
        tts?.shutdown()
        audioRecorder.cancel()
    }
}
