import asyncio
import pytest
from dotenv import load_dotenv
load_dotenv(override=True)

from src.graph.graph import pipeline   # fixed: was src.graph.pipeline

DEMO_SCENARIOS = [
    {"crop": "Maize",   "location": "Kano, NG",  "region": "Kano",  "quantity_kg": 5000.0, "currency": "NGN"},
    {"crop": "Cassava", "location": "Lagos, NG",  "region": "Lagos", "quantity_kg": 2000.0, "currency": "NGN"},
]

@pytest.mark.parametrize("scenario", DEMO_SCENARIOS)
def test_full_pipeline(scenario):
    initial_state = {
        **scenario,
        "storage_type": None,       # fixed: was missing
        "weather_data": None,       # fixed: was missing
        "coordinates": {},
        "price_data": None,
        "risk_data": None,
        "report_data": None,
        "negotiation_brief": None,
        "errors": []
    }

    result = asyncio.run(pipeline.ainvoke(initial_state))

    assert result["negotiation_brief"] is not None
    assert result["negotiation_brief"]["confidence_score"] >= 1
    assert result["negotiation_brief"]["minimum_acceptable_price"] > 0
    assert len(result["negotiation_brief"]["leverage_points"]) >= 1
    print(f"✓ Full pipeline for {scenario['crop']} in {scenario['location']}: {result['negotiation_brief']}")