package net.sprout.pollen.domain.model

enum class BackendMode {
    CPU,
    GPU,
    NPU
}

data class GenerationMetrics(
    val backendMode: BackendMode,
    val initializeMillis: Long,
    val ttftMillis: Long,
    val totalMillis: Long,
    val outputChars: Int,
    val temperatureCelsius: Float? = null,
    val samplerTemperature: Float? = null,
)
