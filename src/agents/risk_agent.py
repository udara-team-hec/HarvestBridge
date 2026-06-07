import time
from src.schemas.models import RiskLevel, SoilCondition

CROP_SPOILAGE_THRESHOLDS = {
    "cassava":  {"high": 50.0, "medium": 25.0},
    "maize":    {"high": 55.0, "medium": 30.0},
    "yam":      {"high": 45.0, "medium": 20.0},
    "beans":    {"high": 40.0, "medium": 18.0},
    "rice":     {"high": 70.0, "medium": 40.0},
    "millet":   {"high": 35.0, "medium": 15.0},
    "sorghum":  {"high": 35.0, "medium": 15.0},
    "sesame":   {"high": 30.0, "medium": 12.0},
}
DEFAULT_SPOILAGE_THRESHOLDS = {"high": 60.0, "medium": 30.0}

STORAGE_SPOILAGE_MULTIPLIERS = {
    "Traditional open bags": 1.4,
    "Hermetic bags":         0.7,
    "Warehouse / silo":      0.5,
}


def analyze_risk(weather_data: dict, crop: str, storage_type: str = "Traditional open bags") -> dict:
    """Derives logistics risk from two-window weather data, crop type, and storage type."""

    # 1. Handle API failure
    if weather_data.get("soil_condition_alert") == SoilCondition.UNKNOWN:
        return {
            "storage_spoilage_risk": RiskLevel.HIGH,
            "road_passability_index": RiskLevel.HIGH,
            "road_recovery_days": 0,
            "harvest_urgency": RiskLevel.HIGH,
            "weather_api_success": False
        }

    near_rain = weather_data.get("forecast_rainfall_near_mm", 0.0)
    far_rain = weather_data.get("forecast_rainfall_far_mm", 0.0)
    avg_humidity = weather_data.get("avg_humidity_pct", 0.0)

    # 2. Soil saturation bucket model on near window only
    # Near rain is what affects roads and storage right now
    evaporation_rate = 15.0
    current_saturation = max(0.0, near_rain - evaporation_rate)

    # 3. Road passability from near saturation
    if current_saturation < 10.0:
        recovery_days = 0
        passability = RiskLevel.LOW
    elif current_saturation <= 50.0:
        recovery_days = 2
        passability = RiskLevel.MEDIUM
    else:
        recovery_days = 5
        passability = RiskLevel.HIGH

    # 4. Spoilage — crop-aware + storage-aware
    thresholds = CROP_SPOILAGE_THRESHOLDS.get(crop.lower(), DEFAULT_SPOILAGE_THRESHOLDS)
    multiplier = STORAGE_SPOILAGE_MULTIPLIERS.get(storage_type, 1.0)

    # Humidity compounds moisture risk alongside rainfall
    humidity_factor = 1.0 + max(0.0, (avg_humidity - 70) / 100)
    adjusted_saturation = current_saturation * multiplier * humidity_factor

    if adjusted_saturation > thresholds["high"]:
        spoilage = RiskLevel.HIGH
    elif adjusted_saturation > thresholds["medium"]:
        spoilage = RiskLevel.MEDIUM
    else:
        spoilage = RiskLevel.LOW

    # 5. Harvest urgency — near rain = act now, far rain = act soon
    if near_rain > 30.0 or (spoilage == RiskLevel.HIGH and passability == RiskLevel.HIGH):
        urgency = RiskLevel.HIGH
    elif far_rain > 20.0 or passability == RiskLevel.MEDIUM:
        urgency = RiskLevel.MEDIUM
    else:
        urgency = RiskLevel.LOW

    return {
        "storage_spoilage_risk": spoilage,
        "road_passability_index": passability,
        "road_recovery_days": recovery_days,
        "harvest_urgency": urgency,
        "weather_api_success": True
    }


async def risk_agent_node(state: dict) -> dict:
    start_time = time.time()

    weather_facts = state.get("weather_data", {})
    crop_input = state.get("crop")
    storage_input = state.get("storage_type", "Traditional open bags")

    risk_result = analyze_risk(
        weather_data=weather_facts,
        crop=crop_input,
        storage_type=storage_input
    )

    execution_time = time.time() - start_time
    risk_result["execution_log"] = {
        "agent_runtime": execution_time,
        "success_status": risk_result["weather_api_success"],
        "token_usage": 0
    }

    return {"risk_data": risk_result}