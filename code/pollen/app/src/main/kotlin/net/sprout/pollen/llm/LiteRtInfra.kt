package net.sprout.pollen.llm

import android.content.Context
import android.os.SystemClock
import com.google.ai.edge.litertlm.Backend
import com.google.ai.edge.litertlm.Engine
import com.google.ai.edge.litertlm.EngineConfig
import com.google.ai.edge.litertlm.Message
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.collect
import com.google.ai.edge.litertlm.Content
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import net.sprout.pollen.domain.model.BackendMode
import net.sprout.pollen.domain.model.GenerationMetrics

class LiteRtBackendPolicy {
    fun orderedBackends(preferred: BackendMode): List<BackendMode> {
        return when (preferred) {
            BackendMode.CPU -> listOf(BackendMode.CPU)
            BackendMode.GPU -> listOf(BackendMode.GPU, BackendMode.CPU)
            BackendMode.NPU -> listOf(BackendMode.NPU, BackendMode.CPU)
        }
    }
}

class LiteRtEngineFactory(private val context: Context) {
    fun create(modelPath: String, backendMode: BackendMode): Engine {
        val backend = when (backendMode) {
            BackendMode.CPU -> Backend.CPU()
            BackendMode.GPU -> Backend.GPU()
            BackendMode.NPU -> Backend.NPU(nativeLibraryDir = context.applicationInfo.nativeLibraryDir)
        }
        val config = EngineConfig(
            modelPath = modelPath,
            backend = backend,
            cacheDir = context.cacheDir.path,
            maxNumTokens = 4096 // Aumentado para evitar cortes
        )
        return Engine(config)
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
    ): GenerationMetrics {
        return GenerationMetrics(
            backendMode = backendMode,
            initializeMillis = initializeEnd - initializeStart,
            ttftMillis = firstTokenAt - initializeEnd,
            totalMillis = completedAt - initializeEnd,
            outputChars = output.length,
            temperatureCelsius = temperatureCelsius,
        )
    }
    fun now(): Long = SystemClock.elapsedRealtime()
}

class LiteRtSessionManager(
    private val engineFactory: LiteRtEngineFactory,
    private val backendPolicy: LiteRtBackendPolicy,
    private val metricsCollector: LiteRtMetricsCollector,
) {
    private val mutex = Mutex()
    private var engine: Engine? = null
    var lastMetrics: GenerationMetrics? = null
        private set

    // F1 requirement: Measure Init time
    suspend fun initialize(modelPath: String, preferredBackend: BackendMode): Engine {
        return mutex.withLock {
            engine?.close()
            var lastError: Throwable? = null

            for (candidate in backendPolicy.orderedBackends(preferredBackend)) {
                try {
                    val initStart = metricsCollector.now()
                    val newEngine = engineFactory.create(modelPath, candidate)
                    newEngine.initialize() // Synchronous inside Thread or async? Assuming it's a blocking call here.
                    engine = newEngine
                    val initEnd = metricsCollector.now()
                    
                    lastMetrics = GenerationMetrics(
                        backendMode = candidate,
                        initializeMillis = initEnd - initStart,
                        ttftMillis = 0,
                        totalMillis = 0,
                        outputChars = 0,
                        temperatureCelsius = null
                    )
                    return@withLock newEngine
                } catch (t: Throwable) {
                    lastError = t
                }
            }
            throw IllegalStateException("No se pudo inicializar LiteRT-LM", lastError)
        }
    }

    fun currentEngine(): Engine? = engine

    fun close() {
        engine?.close()
        engine = null
    }
}

class LiteRtChatService(
    private val sessionManager: LiteRtSessionManager,
    private val metricsCollector: LiteRtMetricsCollector
) {
    private var activeConversation: com.google.ai.edge.litertlm.Conversation? = null

    fun resetConversation() {
        activeConversation?.close()
        activeConversation = null
    }

    fun sendPrompt(userText: String, isThinkingEnabled: Boolean = false, temperature: Float? = null): Flow<Pair<String, GenerationMetrics?>> = flow {
        val engine = requireNotNull(sessionManager.currentEngine()) { "Engine no inicializado" }
        
        if (activeConversation == null) {
            val config = com.google.ai.edge.litertlm.ConversationConfig(
                extraContext = if (isThinkingEnabled) mapOf("enable_thinking" to true) else emptyMap()
            )
            activeConversation = engine.createConversation(config)
        }
        val conversation = activeConversation!!
        val start = metricsCollector.now()
        
        try {
            val prompt = Message.user(userText)
            var firstTokenAt: Long? = null
            var output = ""
            
            // NOTE: the API returns Message, we must extract Content.Text from it.
            try {
                conversation.sendMessageAsync(prompt).collect { chunk ->
                    if (firstTokenAt == null) {
                        firstTokenAt = metricsCollector.now()
                    }
                    val textChunk = chunk.contents.contents.filterIsInstance<Content.Text>().joinToString("") { it.text }
                    output += textChunk
                    emit(textChunk to null)
                }
            } catch(e: Exception) {
                // Ignore chunk errors
            }

            val completedAt = metricsCollector.now()
            
            val initialMetrics = sessionManager.lastMetrics
            val finalMetrics = metricsCollector.build(
                backendMode = initialMetrics?.backendMode ?: BackendMode.CPU,
                initializeStart = 0, // already measured in init
                initializeEnd = start, 
                firstTokenAt = firstTokenAt ?: completedAt,
                completedAt = completedAt,
                output = output,
                samplerTemperature = temperature
            ).copy(initializeMillis = initialMetrics?.initializeMillis ?: 0L)
            
            emit("" to finalMetrics)
        } catch(t: Throwable) {
            // handle error if needed
        }
    }
}
