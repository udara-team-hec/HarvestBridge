import asyncio
import traceback
import streamlit as st
from dotenv import load_dotenv
load_dotenv(override=True)

from src.graph.graph import pipeline
from src.ui.components import (
    render_sidebar,
    render_trace_panel,
    render_results,
    render_empty_state,
)


def run_pipeline(state: dict) -> dict:
    return asyncio.run(pipeline.ainvoke(state))


st.set_page_config(
    page_title="HarvestBridge",
    page_icon="🌾",
    layout="wide"
)

st.title("🌾 HarvestBridge")
st.caption("AI-powered negotiation coaching for smallholder farmers in Africa")
st.divider()

inputs = render_sidebar()

if inputs["run"]:
    initial_state = {
        "crop":              inputs["crop"],
        "country":           inputs["country"],
        "location":          inputs["location"],
        "region":            inputs["region"],
        "quantity_kg":       inputs["quantity_kg"],
        "currency":          inputs["currency"],
        "storage_type":      inputs["storage_type"],
        "coordinates":       {},
        "weather_data":      None,
        "price_data":        None,
        "risk_data":         None,
        "report_data":       None,
        "negotiation_brief": None,
        "errors":            []
    }

    placeholders = render_trace_panel()

    # Set all agents to pending before pipeline starts
    pending_labels = {
        "price":        "Price Agent — fetching market data",
        "weather":      "Weather Agent — fetching forecast",
        "risk":         "Risk Agent — analysing conditions",
        "knowledge":    "Knowledge Agent — searching reports",
        "orchestrator": "Orchestrator — generating brief",
    }
    for key, label in pending_labels.items():
        placeholders[key].info(f"⏳ {label}...")

    with st.spinner("Running pipeline..."):
        try:
            result = run_pipeline(initial_state)

            done_labels = {
                "price":        "Price Agent",
                "weather":      "Weather Agent",
                "risk":         "Risk Agent",
                "knowledge":    "Knowledge Agent",
                "orchestrator": "Orchestrator",
            }
            for key, label in done_labels.items():
                placeholders[key].success(f"✅ {label} — done")

        except Exception as err:
            st.error(f"Pipeline failed: {type(err).__name__}: {err}")
            st.code(traceback.format_exc())
            st.stop()

    st.divider()
    render_results(result, inputs["currency"], inputs["quantity_kg"])

else:
    render_empty_state()