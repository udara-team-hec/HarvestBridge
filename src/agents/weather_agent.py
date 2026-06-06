import os
import time
import requests
from datetime import datetime, timezone
from src.schemas.models import SoilCondition


def get_coordinates(region_name: str, api_key: str):
    """Dynamically translates a region string into exact lat/lon floats."""
    geo_url = "http://api.openweathermap.org/geo/1.0/direct"
    payload = {"q": region_name, "limit": 1, "appid": api_key}

    response = requests.get(geo_url, params=payload)
    data = response.json()

    if not isinstance(data, list) or len(data) == 0:
        raise ValueError(f"Could not find coordinates for region: {region_name}")

    return data[0].get("lat"), data[0].get("lon")


def analyze_weather(lat: float, lon: float, api_key: str) -> dict:
    """Fetches 5-day forecast and splits into near (days 1-2) and far (days 3-5) windows."""
    response = requests.get(
        "https://api.openweathermap.org/data/2.5/forecast",
        params={"lat": lat, "lon": lon, "appid": api_key, "units": "metric"}
    )
    forecast_list = response.json().get("list", [])
    now = datetime.now(tz=timezone.utc)

    near_rain, near_humidity = [], []
    far_rain, far_humidity = [], []

    for entry in forecast_list:
        entry_time = datetime.fromtimestamp(entry["dt"], tz=timezone.utc)
        days_ahead = (entry_time - now).total_seconds() / 86400
        rain = entry.get("rain", {}).get("3h", 0.0)
        humidity = entry.get("main", {}).get("humidity", 0.0)

        if days_ahead <= 2:
            near_rain.append(rain)
            near_humidity.append(humidity)
        elif days_ahead <= 5:
            far_rain.append(rain)
            far_humidity.append(humidity)

    near_rain_total = round(sum(near_rain), 2)
    far_rain_total = round(sum(far_rain), 2)
    all_humidity = near_humidity + far_humidity
    avg_humidity = round(sum(all_humidity) / max(len(all_humidity), 1), 2)

    total_rain = near_rain_total + far_rain_total
    if total_rain > 50.0:
        condition = SoilCondition.FLOOD_RISK
    elif total_rain < 10.0:
        condition = SoilCondition.DROUGHT
    else:
        condition = SoilCondition.OPTIMAL

    return {
        "forecast_rainfall_near_mm": near_rain_total,
        "forecast_rainfall_far_mm": far_rain_total,
        "avg_humidity_pct": avg_humidity,
        "soil_condition_alert": condition,
        "weather_api_success": True
    }


async def weather_agent_node(state: dict) -> dict:
    """The LangGraph wrapper for the Weather Engine."""
    start_time = time.time()
    region_input = state.get("location")   # aligned with GraphState key

    api_key = os.getenv("OPENWEATHERMAP_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENWEATHERMAP_API_KEY is not set in environment.")

    try:
        lat, lon = get_coordinates(region_name=region_input, api_key=api_key)
        weather_result = analyze_weather(lat=lat, lon=lon, api_key=api_key)
        success = True

    except (ValueError, requests.RequestException):
        weather_result = {
            "forecast_rainfall_near_mm": 0.0,
            "forecast_rainfall_far_mm": 0.0,
            "avg_humidity_pct": 0.0,
            "soil_condition_alert": SoilCondition.UNKNOWN,
            "weather_api_success": False
        }
        success = False

    execution_time = time.time() - start_time
    weather_result["execution_log"] = {
        "agent_runtime": execution_time,
        "success_status": success,
        "token_usage": 0
    }

    return {"weather_data": weather_result}