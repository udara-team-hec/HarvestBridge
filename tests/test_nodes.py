import asyncio
import os
import pytest
from dotenv import load_dotenv
load_dotenv(override=True)

from src.agents.price_agent import price_agent_node
from src.agents.weather_agent import weather_agent_node
from src.agents.risk_agent import risk_agent_node


MOCK_STATE = {
    "crop": "Maize",
    "location": "Kano, NG",
    "region": "Kano",
    "quantity_kg": 500.0,
    "currency": "NGN",
    "storage_type": None,
    "coordinates": {},
    "weather_data": None,
    "price_data": None,
    "risk_data": None,
    "report_data": None,
    "negotiation_brief": None,
    "errors": []
}


def test_price_node_updates_state():
    result = asyncio.run(price_agent_node(MOCK_STATE))

    assert "price_data" in result
    assert result["price_data"]["avg_price"] > 0
    assert "execution_log" in result["price_data"]
    assert result["price_data"]["execution_log"]["success_status"] is True
    print(f"✓ Price node: {result['price_data']}")


def test_weather_node_updates_state():
    result = asyncio.run(weather_agent_node(MOCK_STATE))

    assert "weather_data" in result
    assert "forecast_rainfall_near_mm" in result["weather_data"]
    assert "forecast_rainfall_far_mm" in result["weather_data"]
    assert "avg_humidity_pct" in result["weather_data"]
    assert result["weather_data"]["weather_api_success"] is True
    assert "execution_log" in result["weather_data"]
    print(f"✓ Weather node: {result['weather_data']}")


def test_risk_node_updates_state():
    state_with_weather = {
        **MOCK_STATE,
        "weather_data": {
            "forecast_rainfall_near_mm": 5.0,
            "forecast_rainfall_far_mm": 3.0,
            "avg_humidity_pct": 55.0,
            "soil_condition_alert": "OPTIMAL",
            "weather_api_success": True
        }
    }
    result = asyncio.run(risk_agent_node(state_with_weather))

    assert "risk_data" in result
    assert "harvest_urgency" in result["risk_data"]
    assert "storage_type" in result["risk_data"]
    assert "execution_log" in result["risk_data"]
    print(f"✓ Risk node: {result['risk_data']}")