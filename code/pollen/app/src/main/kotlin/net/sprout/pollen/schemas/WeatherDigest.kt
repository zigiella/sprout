package net.sprout.pollen.schemas

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class WeatherDigest(
    @SerialName("is_stale") val isStale: Boolean = false,
    @SerialName("summary") val summary: String,
    @SerialName("rain_expected_mb") val rainExpectedMb: Float? = null,
    @SerialName("temperature_range_c") val temperatureRangeC: String? = null
)
