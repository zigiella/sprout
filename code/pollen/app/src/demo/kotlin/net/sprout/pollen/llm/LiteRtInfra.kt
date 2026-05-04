package net.sprout.pollen.llm

import android.content.Context
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import net.sprout.pollen.domain.model.BackendMode
import net.sprout.pollen.domain.model.GenerationMetrics

class LiteRtBackendPolicy {
    fun orderedBackends(preferred: BackendMode): List<BackendMode> = listOf(preferred)
}

class LiteRtEngineFactory(private val context: Context) {
    // Return Any since we don't have litertlm Engine class in demo
    fun create(modelPath: String, backendMode: BackendMode): Any {
        return Any()
    }
}

class LiteRtMetricsCollector {
    fun build(
        backendMode: BackendMode,
        initializeStart: Long,
        initializeEnd: Long,
        firstTokenAt: Long,
        completedAt: Long,
        output: String,
        temperatureCelsius: Float? = null,
        samplerTemperature: Float? = null,
    ): GenerationMetrics {
        return GenerationMetrics(
            backendMode = backendMode,
            initializeMillis = initializeEnd - initializeStart,
            ttftMillis = firstTokenAt - initializeEnd,
            totalMillis = completedAt - initializeEnd,
            outputChars = output.length,
            temperatureCelsius = temperatureCelsius,
            samplerTemperature = samplerTemperature,
        )
    }
    fun now(): Long = System.currentTimeMillis()
}

class LiteRtSessionManager(
    private val engineFactory: LiteRtEngineFactory,
    private val backendPolicy: LiteRtBackendPolicy,
    private val metricsCollector: LiteRtMetricsCollector,
) {
    var lastMetrics: GenerationMetrics? = null
        private set

    // F1 requirement: Measure Init time
    suspend fun initialize(modelPath: String, preferredBackend: BackendMode): Any {
        delay(100) // fake load time
        lastMetrics = GenerationMetrics(
            backendMode = preferredBackend,
            initializeMillis = 100L,
            ttftMillis = 0,
            totalMillis = 0,
            outputChars = 0,
            temperatureCelsius = null
        )
        return Any()
    }

    fun currentEngine(): Any? = Any()

    fun close() {}
}

class LiteRtChatService(
    private val sessionManager: LiteRtSessionManager,
    private val metricsCollector: LiteRtMetricsCollector
) {
    fun resetConversation() {}

    fun sendPrompt(userText: String, isThinkingEnabled: Boolean = false, temperature: Float? = null): Flow<Pair<String, GenerationMetrics?>> = flow {
        val start = metricsCollector.now()
        
        delay(800) // Simulated TTFT
        val firstTokenAt = metricsCollector.now()
        
        val mockResponse = if (isThinkingEnabled) {
            "Simulated response for: \$userText\n\nI have carefully analyzed the context. The metrics align perfectly with the established policy. No anomalies detected in Rhizome's rationale."
        } else {
            "Simulated quick response: Policy execution is correct."
        }

        val tokens = mockResponse.split(" ")
        var output = ""

        for ((index, token) in tokens.withIndex()) {
            val chunk = token + if (index < tokens.size - 1) " " else ""
            output += chunk
            emit(chunk to null)
            delay(50) // Simulated streaming
        }
        
        val completedAt = metricsCollector.now()
        
        val finalMetrics = metricsCollector.build(
            backendMode = BackendMode.CPU,
            initializeStart = 0,
            initializeEnd = start, 
            firstTokenAt = firstTokenAt,
            completedAt = completedAt,
            output = output,
            samplerTemperature = temperature
        )
        
        emit("" to finalMetrics)
    }

    fun sendAudioFile(audioPath: String, instruction: String, isThinkingEnabled: Boolean = false): Flow<Pair<String, GenerationMetrics?>> = flow {
        val start = metricsCollector.now()
        
        delay(800) // Simulated TTFT
        val firstTokenAt = metricsCollector.now()
        
        val mockResponse = if (isThinkingEnabled) {
            "Simulated audio response for: \$audioPath\n\nI have carefully analyzed the context. The metrics align perfectly with the established policy. No anomalies detected in Rhizome's rationale."
        } else {
            "He escuchado el audio. Todo está correcto."
        }

        val tokens = mockResponse.split(" ")
        var output = ""

        for ((index, token) in tokens.withIndex()) {
            val chunk = token + if (index < tokens.size - 1) " " else ""
            output += chunk
            emit(chunk to null)
            delay(50) // Simulated streaming
        }
        
        val completedAt = metricsCollector.now()
        
        val finalMetrics = metricsCollector.build(
            backendMode = BackendMode.CPU,
            initializeStart = 0,
            initializeEnd = start, 
            firstTokenAt = firstTokenAt,
            completedAt = completedAt,
            output = output
        )
        
        emit("" to finalMetrics)
    }
}
