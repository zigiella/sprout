package net.sprout.pollen.schemas

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
enum class NodeType {
    @SerialName("rhizome") RHIZOME,
    @SerialName("pollen") POLLEN,
    @SerialName("meristem") MERISTEM
}

@Serializable
enum class Mode {
    @SerialName("normal") NORMAL,
    @SerialName("conservative") CONSERVATIVE,
    @SerialName("alert") ALERT
}

@Serializable
enum class ActionType {
    @SerialName("WATER_A") WATER_A,
    @SerialName("WATER_B") WATER_B,
    @SerialName("WATER_BOTH") WATER_BOTH,
    @SerialName("SKIP") SKIP,
    @SerialName("DEFER") DEFER,
    @SerialName("ALERT") ALERT,
    @SerialName("BLOCK") BLOCK,
    @SerialName("SHUTDOWN") SHUTDOWN
}

@Serializable
enum class ContradictionType {
    @SerialName("sensor_vs_vision") SENSOR_VS_VISION,
    @SerialName("policy_expired") POLICY_EXPIRED,
    @SerialName("deposit_inconsistent") DEPOSIT_INCONSISTENT,
    @SerialName("flow_vs_pump") FLOW_VS_PUMP,
    @SerialName("weather_conflict") WEATHER_CONFLICT,
    @SerialName("tank_underflow") TANK_UNDERFLOW
}

@Serializable
enum class Severity {
    @SerialName("info") INFO,
    @SerialName("warning") WARNING,
    @SerialName("critical") CRITICAL
}

@Serializable
enum class WeatherProvenance {
    @SerialName("local_station") LOCAL_STATION,
    @SerialName("ferried") FERRIED,
    @SerialName("forecast_api") FORECAST_API
}
