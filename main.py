import asyncio
import streamlit as st
from dotenv import load_dotenv
load_dotenv(override=True)

from src.graph.graph import pipeline
from src.ui.components import (
    render_sidebar,
    render_trace_panel,
    update_trace,
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

    update_trace(placeholders, "price")
    update_trace(placeholders, "weather")
    update_trace(placeholders, "risk")
    update_trace(placeholders, "knowledge")
    update_trace(placeholders, "orchestrator")

    with st.spinner("Running pipeline..."):
        try:
            result = run_pipeline(initial_state)
            for stage in ["price", "weather", "risk", "knowledge", "orchestrator"]:
                placeholders[stage].success(
                    f"✅ {stage.capitalize()} Agent — done"
                )
        except Exception as e:
            st.error(f"Pipeline failed: {e}")
            st.stop()

    st.divider()
    render_results(result, inputs["currency"])

else:
    render_empty_state()