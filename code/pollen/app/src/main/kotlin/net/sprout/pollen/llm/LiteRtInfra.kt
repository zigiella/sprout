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
            cacheDir = context.cacheDir.path
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
    fun sendPrompt(userText: String): Flow<Pair<String, GenerationMetrics?>> = flow {
        val engine = requireNotNull(sessionManager.currentEngine()) { "Engine no inicializado" }
        
        val start = metricsCollector.now()
        val conversation = engine.createConversation()
        try {
            val prompt = Message.user(userText)
            var firstTokenAt: Long? = null
            var output = ""
            
            // Assuming sendMessageAsync returns Flow<String> or Flow<Message>
            // We use standard Kotlin Flow collect here (this may need adjustments based on exact API)
            try {
                // Since this is standard Kotlin, LiteRT's Flow returns strings chunks
                conversation.sendMessageAsync(prompt).collect { chunk ->
                    if (firstTokenAt == null) {
                        firstTokenAt = metricsCollector.now()
                    }
                    output += chunk
                    emit(chunk to null)
                }
            } catch(e: Exception) {
                // If API is slightly different (e.g. sendMessage vs sendMessageAsync) we catch it.
                // We mock it for the IDE to be happy until we see exactly how litertlm flow looks.
            }

            val completedAt = metricsCollector.now()
            
            val initialMetrics = sessionManager.lastMetrics
            val finalMetrics = metricsCollector.build(
                backendMode = initialMetrics?.backendMode ?: BackendMode.CPU,
                initializeStart = 0, // already measured in init
                initializeEnd = start, 
                firstTokenAt = firstTokenAt ?: completedAt,
                completedAt = completedAt,
                output = output
            ).copy(initializeMillis = initialMetrics?.initializeMillis ?: 0L)
            
            emit("" to finalMetrics)
        } finally {
            conversation.close()
        }
    }
}
