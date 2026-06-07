import pytest
from dotenv import load_dotenv
from src.agents.price_agent import analyze_price
from src.agents.weather_agent import analyze_weather, get_coordinates
from src.agents.risk_agent import analyze_risk
from src.schemas.models import TrendDirection
import os

load_dotenv(override=True)
# --- Price Agent ---
def test_price_agent_returns_real_data():
    result = analyze_price(crop="Maize", region="Kano")
    
    assert result["avg_price"] > 0, "avg_price should be a real number from the database"
    assert result["price_12m_high"] >= result["avg_price"], "12m high should be >= average"
    assert result["price_12m_low"] <= result["avg_price"], "12m low should be <= average"
    assert result["trend_direction"] in [TrendDirection.RISING, TrendDirection.FALLING, TrendDirection.STABLE]
    assert result["data_points_count"] > 0
    print(f"✓ Price Agent: {result}")

def test_price_agent_unknown_crop_raises():
    with pytest.raises(ValueError):
        analyze_price(crop="Avocado", region="Kano")

def test_price_agent_unknown_region_returns_zero():
    result = analyze_price(crop="Maize", region="ZZZnonexistent")
    assert result["avg_price"] == 0.0
    print(f"✓ Price Agent graceful empty region: {result}")


# --- Weather Agent ---
def test_weather_agent_geocoding():
    api_key = os.getenv("OPENWEATHERMAP_API_KEY")
    lat, lon = get_coordinates("Kano, NG", api_key)  # NG = Nigeria ISO code

    assert lat is not None
    assert lon is not None
    assert 4.0 < lat < 14.0, "Latitude should be within Nigeria's range"
    print(f"✓ Geocoding: lat={lat}, lon={lon}")

def test_weather_agent_returns_forecast():
    api_key = os.getenv("OPENWEATHERMAP_API_KEY")
    lat, lon = get_coordinates("Kano, NG", api_key)
    result = analyze_weather(lat=lat, lon=lon, api_key=api_key)

    assert "forecast_rainfall_near_mm" in result
    assert "forecast_rainfall_far_mm" in result
    assert "avg_humidity_pct" in result
    assert result["weather_api_success"] is True
    assert result["forecast_rainfall_near_mm"] >= 0
    assert result["forecast_rainfall_far_mm"] >= 0
    assert 0 <= result["avg_humidity_pct"] <= 100
    print(f"✓ Weather Agent: {result}")

# --- Risk Agent ---
def test_risk_agent_with_dry_forecast():
    mock_weather = {
        "forecast_rainfall_near_mm": 0.0,
        "forecast_rainfall_far_mm": 0.0,
        "avg_humidity_pct": 45.0,
        "soil_condition_alert": "OPTIMAL",
        "weather_api_success": True
    }
    result = analyze_risk(
        weather_data=mock_weather,
        crop="maize",
        storage_type="Traditional open bags"
    )
    assert result["road_passability_index"].value == "Low"
    assert result["road_recovery_days"] == 0
    assert result["weather_api_success"] is True
    print(f"✓ Risk Agent dry: {result}")


def test_risk_agent_with_heavy_rain():
    mock_weather = {
        "forecast_rainfall_near_mm": 45.0,
        "forecast_rainfall_far_mm": 30.0,
        "avg_humidity_pct": 85.0,
        "soil_condition_alert": "FLOOD_RISK",
        "weather_api_success": True
    }
    result = analyze_risk(
        weather_data=mock_weather,
        crop="sesame",
        storage_type="Traditional open bags"
    )
    assert result["road_passability_index"].value == "Medium"  # near_saturation = 30.0
    assert result["storage_spoilage_risk"].value == "High"     # sesame threshold is 30.0, humidity pushes it over
    assert result["harvest_urgency"].value == "High"           # near_rain 45.0 > 30.0 threshold
    print(f"✓ Risk Agent heavy rain: {result}")

def test_risk_agent_with_extreme_rain():
    mock_weather = {
        "forecast_rainfall_near_mm": 80.0,   # 80 - 15 = 65.0 → HIGH
        "forecast_rainfall_far_mm": 50.0,
        "avg_humidity_pct": 90.0,
        "soil_condition_alert": "FLOOD_RISK",
        "weather_api_success": True
    }
    result = analyze_risk(
        weather_data=mock_weather,
        crop="sesame",
        storage_type="Traditional open bags"
    )
    assert result["road_passability_index"].value == "High"
    assert result["road_recovery_days"] == 5
    print(f"✓ Risk Agent extreme rain: {result}")

def test_risk_agent_handles_api_failure():
    mock_weather = {
        "forecast_rainfall_near_mm": 0.0,
        "forecast_rainfall_far_mm": 0.0,
        "avg_humidity_pct": 0.0,
        "soil_condition_alert": "UNKNOWN",
        "weather_api_success": False
    }
    result = analyze_risk(
        weather_data=mock_weather,
        crop="maize",
        storage_type=None
    )
    assert result["weather_api_success"] is False
    assert result["road_passability_index"].value == "High"
    print(f"✓ Risk Agent API failure handled: {result}")


def test_risk_agent_with_no_storage():
    mock_weather = {
        "forecast_rainfall_near_mm": 20.0,
        "forecast_rainfall_far_mm": 10.0,
        "avg_humidity_pct": 70.0,
        "soil_condition_alert": "OPTIMAL",
        "weather_api_success": True
    }
    result = analyze_risk(
        weather_data=mock_weather,
        crop="maize",
        storage_type=None
    )
    assert result["storage_spoilage_risk"] is not None
    assert result["weather_api_success"] is True
    print(f"✓ Risk Agent no storage: {result}")
