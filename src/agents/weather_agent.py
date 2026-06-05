import os
import time
import requests
from datetime import datetime, timezone
from collections import defaultdict
from src.schemas.models import SoilCondition


def get_coordinates(region_name: str, api_key: str):
    """Dynamically translates a region string into exact lat/lon floats."""
    geo_url = "http://api.openweathermap.org/geo/1.0/direct"
    payload = {"q": region_name, "limit": 1, "appid": api_key}

    response = requests.get(geo_url, params=payload)
    data = response.json()

    if not data:
        raise ValueError(f"Could not find coordinates for region: {region_name}")

    return data[0].get("lat"), data[0].get("lon")


def analyze_weather(lat: float, lon: float, api_key: str) -> dict:
    """Fetches 5-day forecast and groups rainfall into daily buckets."""
    forecast_url = "https://api.openweathermap.org/data/2.5/forecast"
    forecast_response = requests.get(
        forecast_url,
        params={"lat": lat, "lon": lon, "appid": api_key, "units": "metric"}
    )
    forecast_data = forecast_response.json()

    daily_future_rain = defaultdict(float)
    for chunk in forecast_data.get("list", [])[:40]:  # 40 x 3hr chunks = 5 days
        date_str = datetime.fromtimestamp(chunk.get("dt"), tz=timezone.utc).strftime('%Y-%m-%d')
        daily_future_rain[date_str] += chunk.get("rain", {}).get("3h", 0.0)

    future_rain_series = list(daily_future_rain.values())
    total_rain_future = sum(future_rain_series)

    if total_rain_future > 50.0:
        condition = SoilCondition.FLOOD_RISK
    elif total_rain_future < 10.0:
        condition = SoilCondition.DROUGHT
    else:
        condition = SoilCondition.OPTIMAL

    return {
        "future_rain_daily_mm": future_rain_series,
        "soil_condition_alert": condition,
        "weather_api_success": True
    }


async def weather_agent_node(state: dict) -> dict:
    """The LangGraph wrapper for the Weather Engine."""
    start_time = time.time()
    region_input = state.get("region")

    api_key = os.getenv("OPENWEATHERMAP_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENWEATHERMAP_API_KEY is not set in environment.")

    try:
        lat, lon = get_coordinates(region_name=region_input, api_key=api_key)
        weather_result = analyze_weather(lat=lat, lon=lon, api_key=api_key)
        success = True

    except (ValueError, requests.RequestException):
        weather_result = {
            "future_rain_daily_mm": [0.0],
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