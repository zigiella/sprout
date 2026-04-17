package net.sprout.pollen.schemas

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class WeatherPacket(
    @SerialName("schema_version") val schemaVersion: String = "1.0",
    @SerialName("created_at") val createdAt: String,
    @SerialName("origin_node_id") val originNodeId: String,
    @SerialName("signature") val signature: String? = null,
    
    @SerialName("packet_id") val packetId: String,
    @SerialName("observed_at") val observedAt: String,
    @SerialName("observed_by_node_id") val observedByNodeId: String,
    @SerialName("provenance") val provenance: WeatherProvenance,
    @SerialName("valid_until") val validUntil: String,
    
    @SerialName("location") val location: Location,
    @SerialName("measurements") val measurements: Measurements = Measurements(),
    
    @SerialName("confidence") val confidence: Float,
    @SerialName("notes") val notes: String? = null
) {
    @Serializable
    data class Location(
        @SerialName("lat") val lat: Float,
        @SerialName("lon") val lon: Float,
        @SerialName("altitude_m") val altitudeM: Float? = null,
        @SerialName("label") val label: String? = null
    )

    @Serializable
    data class Measurements(
        @SerialName("temperature_c") val temperatureC: Float? = null,
        @SerialName("humidity_rel_pct") val humidityRelPct: Float? = null,
        @SerialName("pressure_hpa") val pressureHpa: Float? = null,
        @SerialName("rain_last_1h_mm") val rainLast1hMm: Float? = null,
        @SerialName("rain_last_24h_mm") val rainLast24hMm: Float? = null,
        @SerialName("wind_speed_kmh") val windSpeedKmh: Float? = null,
        @SerialName("wind_direction_deg") val windDirectionDeg: Int? = null,
        @SerialName("solar_radiation_wm2") val solarRadiationWm2: Float? = null,
        @SerialName("uv_index") val uvIndex: Float? = null
    )
}
