"""Canonical example payload builders for shared schemas."""

from __future__ import annotations

from copy import deepcopy


def rhizome_snapshot_example() -> dict:
    return {
        "schema_version": "1.0",
        "created_at": "2026-04-16T14:32:05Z",
        "origin_node_id": "rhizome_01",
        "signature": None,
        "snapshot_id": "snap_rhizome_01_20260416T143205_a3f2",
        "mode": "normal",
        "active_policy_id": "pkt_rhizome_01_20260416T083015_d5e7",
        "active_policy_expires_at": "2026-04-17T08:30:15Z",
        "sensors": {
            "soil_moisture_a_pct": 38.2,
            "soil_moisture_b_pct": 41.7,
            "tank_level_pct": 72.0,
            "flow_rate_lpm": 0.0,
            "last_reading_at": "2026-04-16T14:31:58Z",
        },
        "vision": {
            "last_capture_at": "2026-04-16T14:25:00Z",
            "parcel_a_status": "healthy",
            "parcel_b_status": "healthy",
            "visual_notes": "hojas firmes, color normal en ambas parcelas",
        },
        "health": {
            "cpu_temp_c": 58.4,
            "cpu_load_pct": 41.0,
            "ram_used_gb": 4.8,
            "ram_total_gb": 7.4,
            "esp32_heartbeat_ok": True,
            "last_esp32_ack_at": "2026-04-16T14:32:00Z",
        },
        "last_decision_id": "rec_rhizome_01_20260416T143000_91ba",
        "pending_contradictions": [],
    }


def policy_packet_example() -> dict:
    return {
        "schema_version": "1.0",
        "created_at": "2026-04-16T08:30:15Z",
        "origin_node_id": "meristem_01",
        "signature": None,
        "policy_id": "pkt_rhizome_01_20260416T083015_d5e7",
        "target_node_id": "rhizome_01",
        "valid_until": "2026-04-17T08:30:15Z",
        "version_chain": [
            "pkt_rhizome_01_20260415T083015_1234",
            "pkt_rhizome_01_20260416T083015_d5e7",
        ],
        "mode_default": "normal",
        "rules": {
            "watering_window": {"start_hour_local": 6, "end_hour_local": 9},
            "soil_moisture_thresholds": {
                "parcel_a": {"min_pct": 35.0, "target_pct": 55.0},
                "parcel_b": {"min_pct": 30.0, "target_pct": 50.0},
            },
            "max_watering_duration_s": 45,
            "daily_water_budget_liters": 8.0,
            "tank_minimum_pct": 20.0,
            "require_vision_confirmation": False,
            "conservative_triggers": [
                "tank_level_below_30",
                "no_pollen_visit_48h",
                "policy_expires_within_3h",
            ],
        },
        "rationale": "Post-lluvia del 15 abril. Humedad general alta. Subir umbrales parcela B que suele retener mas.",
        "notes": "Primera iteracion tras validacion semanal.",
    }


def policy_delta_example() -> dict:
    return {
        "schema_version": "1.0",
        "created_at": "2026-04-16T15:00:00Z",
        "origin_node_id": "meristem_01",
        "signature": None,
        "delta_id": "delta_meristem_01_20260416T150000_c92d",
        "target_node_id": "rhizome_01",
        "base_policy_id": "pkt_rhizome_01_20260416T083015_d5e7",
        "patches": [
            {
                "op": "replace",
                "path": "rules.soil_moisture_thresholds.parcel_b.min_pct",
                "value": 32.0,
            },
            {
                "op": "replace",
                "path": "rules.daily_water_budget_liters",
                "value": 10.0,
            },
            {
                "op": "add",
                "path": "rules.conservative_triggers",
                "value": "humidity_below_25_forecast",
            },
        ],
        "rationale": "Forecast Pollen trae humedad baja esperada en 24h. Subir budget y anadir trigger.",
        "ttl_seconds": 86400,
        "priority": "normal",
    }


def weather_packet_example() -> dict:
    return {
        "schema_version": "1.0",
        "created_at": "2026-04-16T12:15:00Z",
        "origin_node_id": "pollen_01",
        "signature": None,
        "packet_id": "pkt_weather_pollen_01_20260416T121500_e7a2",
        "observed_at": "2026-04-16T11:45:00Z",
        "observed_by_node_id": "rhizome_02",
        "provenance": "ferried",
        "valid_until": "2026-04-16T17:45:00Z",
        "location": {
            "lat": 42.1828,
            "lon": 1.9931,
            "altitude_m": 1100,
            "label": "Castellar de n'Hug, parcela A",
        },
        "measurements": {
            "temperature_c": 18.4,
            "humidity_rel_pct": 62.0,
            "pressure_hpa": 1013.5,
            "rain_last_1h_mm": 0.0,
            "rain_last_24h_mm": 2.4,
            "wind_speed_kmh": 8.2,
            "wind_direction_deg": 220,
            "solar_radiation_wm2": 485,
            "uv_index": 4.8,
        },
        "confidence": 0.85,
        "notes": "Estacion WS90 en rhizome_02. Ultima calibracion hace 3 semanas.",
    }


def contradiction_alert_example() -> dict:
    return {
        "schema_version": "1.0",
        "created_at": "2026-04-16T13:22:30Z",
        "origin_node_id": "pollen_01",
        "signature": None,
        "alert_id": "alert_pollen_01_20260416T132230_f108",
        "target_node_id": "rhizome_01",
        "contradiction_type": "sensor_vs_vision",
        "severity": "warning",
        "observed_at": "2026-04-16T13:20:00Z",
        "evidence": {
            "sensor_reading": {
                "source": "snap_rhizome_01_20260416T131800_4c5e",
                "soil_moisture_a_pct": 42.0,
            },
            "vision_reading": {
                "source": "pollen_capture_20260416T132015",
                "assessment": "severe_stress",
                "notes": "Hojas claramente caidas en parcela A, decoloracion en los bordes.",
            },
        },
        "recommended_action": "defer_and_review",
        "expires_at": "2026-04-16T19:22:30Z",
        "rationale": "Humedad 42% es razonable en estacion seca, pero el estado visual indica estres claro. Puede haber sensor mal calibrado o problema de raiz.",
    }


def decision_receipt_example() -> dict:
    return {
        "schema_version": "1.0",
        "created_at": "2026-04-16T14:30:10Z",
        "origin_node_id": "rhizome_01",
        "signature": None,
        "decision_id": "rec_rhizome_01_20260416T143010_91ba",
        "snapshot_id": "snap_rhizome_01_20260416T143005_a3f2",
        "active_policy_id": "pkt_rhizome_01_20260416T083015_d5e7",
        "action": "WATER_A",
        "action_params": {"duration_s": 30, "expected_liters": 1.5},
        "rationale_short": "Humedad A en 38%, por debajo del umbral 45%. Dentro de ventana de riego. Deposito al 72%.",
        "rationale_full": "El snapshot reciente muestra humedad parcela A al 38.2%, umbral minimo 45% segun politica vigente. Hora local dentro de ventana 06-09. Deposito al 72%. Vision confirma planta sana.",
        "policy_refs": [
            "rules.soil_moisture_thresholds.parcel_a.min_pct",
            "rules.watering_window",
            "rules.tank_minimum_pct",
        ],
        "contradictions": [],
        "confidence": 0.87,
        "executed": True,
        "execution_details": {
            "sent_to_esp32_at": "2026-04-16T14:30:10Z",
            "esp32_ack_at": "2026-04-16T14:30:11Z",
            "esp32_ack_status": "OK",
            "actual_duration_s": 30.2,
            "flow_observed_lpm": 3.1,
            "estimated_liters_actual": 1.56,
        },
        "blocked_reason": None,
    }


def decision_receipt_blocked_example() -> dict:
    return {
        "schema_version": "1.0",
        "created_at": "2026-04-16T17:05:40Z",
        "origin_node_id": "rhizome_01",
        "signature": None,
        "decision_id": "rec_rhizome_01_20260416T170540_6f4c",
        "snapshot_id": "snap_rhizome_01_20260416T170500_77ae",
        "active_policy_id": "pkt_rhizome_01_20260416T083015_d5e7",
        "action": "BLOCK",
        "action_params": {
            "blocked_action": "WATER_A",
            "reason": "tank_minimum_pct reached",
        },
        "rationale_short": "Riego bloqueado: deposito al 18%, por debajo del minimo de seguridad.",
        "rationale_full": "El snapshot reporta deposito al 18%, por debajo del 20% exigido por la politica activa. Aunque la parcela A esta seca, Rhizome no envia comando al ESP32 y eleva bloqueo preventivo.",
        "policy_refs": [
            "rules.soil_moisture_thresholds.parcel_a.min_pct",
            "rules.tank_minimum_pct",
        ],
        "contradictions": ["alert_pollen_01_20260416T132230_f108"],
        "confidence": 0.94,
        "executed": False,
        "execution_details": None,
        "blocked_reason": "tank_below_minimum_pct",
    }


def canonical_examples() -> dict[str, dict]:
    return {
        "rhizome_snapshot": deepcopy(rhizome_snapshot_example()),
        "policy_packet": deepcopy(policy_packet_example()),
        "policy_delta": deepcopy(policy_delta_example()),
        "weather_packet": deepcopy(weather_packet_example()),
        "contradiction_alert": deepcopy(contradiction_alert_example()),
        "decision_receipt": deepcopy(decision_receipt_example()),
    }


def supplemental_examples() -> dict[str, dict]:
    return {
        "decision_receipt_blocked": deepcopy(decision_receipt_blocked_example()),
    }
