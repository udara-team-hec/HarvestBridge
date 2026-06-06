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


def analyze_risk(weather_data: dict, crop: str) -> dict:
    """Evaluates forecast weather facts to determine logistics risk."""

    # 1. Handle the error state first
    if weather_data.get("soil_condition_alert") == SoilCondition.UNKNOWN:
        return {
            "storage_spoilage_risk": RiskLevel.HIGH,
            "road_passability_index": RiskLevel.HIGH,
            "road_recovery_days": 0,
            "harvest_urgency": RiskLevel.HIGH,
            "weather_api_success": False
        }

    future_rain = weather_data.get("future_rain_daily_mm", [])

    # 2. Soil saturation bucket model — forecast only on free tier
    current_saturation = 0.0
    evaporation_rate = 15.0

    for daily_rain in future_rain:
        current_saturation += daily_rain
        current_saturation -= evaporation_rate
        current_saturation = max(0.0, current_saturation)

    # 3. Road passability from final saturation
    if current_saturation < 10.0:
        recovery_days = 0
        passability = RiskLevel.LOW
    elif current_saturation <= 50.0:
        recovery_days = 2
        passability = RiskLevel.MEDIUM
    else:
        recovery_days = 5
        passability = RiskLevel.HIGH

    # 4. Spoilage — crop-aware thresholds
    thresholds = CROP_SPOILAGE_THRESHOLDS.get(crop.lower(), DEFAULT_SPOILAGE_THRESHOLDS)

    if current_saturation > thresholds["high"]:
        spoilage = RiskLevel.HIGH
    elif current_saturation > thresholds["medium"]:
        spoilage = RiskLevel.MEDIUM
    else:
        spoilage = RiskLevel.LOW

    # 5. Harvest urgency — should the farmer sell before conditions worsen?
    total_future_rain = sum(future_rain)
    if total_future_rain > 40.0 or (spoilage == RiskLevel.HIGH and passability == RiskLevel.HIGH):
        urgency = RiskLevel.HIGH
    elif total_future_rain > 15.0 or passability == RiskLevel.MEDIUM:
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
    """The LangGraph wrapper for the Risk Engine."""
    start_time = time.time()

    weather_facts = state.get("weather_data", {})
    crop_input = state.get("crop")

    risk_result = analyze_risk(weather_data=weather_facts, crop=crop_input)

    execution_time = time.time() - start_time
    risk_result["execution_log"] = {
        "agent_runtime": execution_time,
        "success_status": risk_result["weather_api_success"],
        "token_usage": 0
    }

    return {"risk_data": risk_result}