package net.sprout.pollen.schemas

import kotlinx.serialization.Serializable

@Serializable
data class WeatherDigest(
    val isStale: Boolean = false,
    val summary: String,
    val rainExpectedMb: Float? = null,
    val temperatureRangeC: String? = null
)
