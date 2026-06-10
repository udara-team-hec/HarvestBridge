import os
import sqlite3
import streamlit as st
from src.ui.config import (
    LOCATIONS, CROPS_BY_COUNTRY, STORAGE_TYPES,
    STORAGE_MAP, RISK_COLOURS
)


def confidence_colour(score: int) -> str:
    if score >= 8:
        return "green"
    elif score >= 5:
        return "orange"
    else:
        return "red"


def render_sidebar() -> dict:
    with st.sidebar:
        st.header("Your Harvest Details")

        country = st.selectbox("Country", list(LOCATIONS.keys()), key="main_country")
        available_crops = CROPS_BY_COUNTRY[country]
        crop = st.selectbox("Crop", available_crops, key="main_crop")

        state_options = list(LOCATIONS[country]["states"].keys())
        state = st.selectbox("State / Region", state_options, key="main_state")

        market_options = list(LOCATIONS[country]["states"][state].keys())
        market = st.selectbox("Local Market", market_options, key="main_market")

        currency = LOCATIONS[country]["currency"]
        st.info(f"Currency: **{currency}**")

        quantity_kg = st.number_input(
            "Quantity (kg)",
            min_value=1.0,
            max_value=100000.0,
            value=1000.0,
            step=100.0,
            key="main_quantity"
        )

        storage_display = st.selectbox("Storage Type", STORAGE_TYPES, key="main_storage")
        storage_type = STORAGE_MAP[storage_display]

        st.divider()
        run_button = st.button(
            "🚀 Generate Negotiation Brief",
            use_container_width=True
        )
        st.divider()
        render_registration_form()

    location_full = LOCATIONS[country]["states"][state][market]

    return {
        "crop":         crop,
        "country":      country,
        "location":     location_full,
        "region":       state,
        "quantity_kg":  quantity_kg,
        "currency":     currency,
        "storage_type": storage_type,
        "run":          run_button,
    }


def render_trace_panel() -> dict:
    """Renders the agent trace panel and returns the status placeholders."""
    st.subheader("⚙️ Pipeline Running...")
    container = st.container()
    with container:
        return {
            "price":        st.empty(),
            "weather":      st.empty(),
            "risk":         st.empty(),
            "knowledge":    st.empty(),
            "orchestrator": st.empty(),
        }


def update_trace(placeholders: dict, stage: str):
    """Updates all trace statuses up to the current stage."""
    stages = ["price", "weather", "risk", "knowledge", "orchestrator"]
    labels = {
        "price":        "Price Agent — fetching market data",
        "weather":      "Weather Agent — fetching forecast",
        "risk":         "Risk Agent — analysing conditions",
        "knowledge":    "Knowledge Agent — searching reports",
        "orchestrator": "Orchestrator — generating brief",
    }
    current_index = stages.index(stage)
    for i, s in enumerate(stages):
        if i < current_index:
            placeholders[s].success(f"✅ {labels[s]}")
        elif i == current_index:
            placeholders[s].info(f"⏳ {labels[s]}...")
        else:
            placeholders[s].empty()


def render_results(result: dict, currency: str, quantity_kg: float = 0):
    """Renders the full results panel from pipeline output."""
    brief        = result.get("negotiation_brief", {})
    price_data   = result.get("price_data", {})
    risk_data    = result.get("risk_data", {})
    weather_data = result.get("weather_data", {})
    report_data  = result.get("report_data", {})

    st.subheader("📋 Negotiation Brief")

    # Confidence score
    confidence = brief.get("confidence_score", 1)
    colour = confidence_colour(confidence)
    st.markdown(f"**Confidence Score:** :{colour}[{confidence}/10]")

    st.divider()

    # Price range and floor
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Fair Price Range**")
        st.markdown(f"### {brief.get('fair_price_range', 'N/A')}")
    with col2:
        st.metric(
            label="Minimum Acceptable Price",
            value=f"{brief.get('minimum_acceptable_price', 0):,.0f} {currency}"
        )

    # Total harvest value
    if quantity_kg > 0:
        avg_price = price_data.get("avg_price", 0)
        min_price = brief.get("minimum_acceptable_price", 0)
        total_fair = avg_price * quantity_kg
        total_min  = min_price * quantity_kg
        st.caption(
            f"💰 Total harvest value at fair price: {total_fair:,.0f} {currency} · "
            f"Minimum total: {total_min:,.0f} {currency}"
        )

    st.divider()

    # Risk summary
    st.subheader("⚠️ Risk Summary")
    r1, r2, r3 = st.columns(3)

    spoilage    = risk_data.get("storage_spoilage_risk")
    passability = risk_data.get("road_passability_index")
    urgency     = risk_data.get("harvest_urgency")

    spoilage_val    = spoilage.value    if hasattr(spoilage,    "value") else str(spoilage)
    passability_val = passability.value if hasattr(passability, "value") else str(passability)
    urgency_val     = urgency.value     if hasattr(urgency,     "value") else str(urgency)

    with r1:
        st.metric(
            "Storage Spoilage Risk",
            f"{RISK_COLOURS.get(spoilage_val, '')} {spoilage_val}"
        )
    with r2:
        st.metric(
            "Road Passability Risk",
            f"{RISK_COLOURS.get(passability_val, '')} {passability_val}"
        )
    with r3:
        st.metric(
            "Harvest Urgency",
            f"{RISK_COLOURS.get(urgency_val, '')} {urgency_val}"
        )

    near_rain = weather_data.get("forecast_rainfall_near_mm", 0.0)
    far_rain  = weather_data.get("forecast_rainfall_far_mm",  0.0)
    humidity  = weather_data.get("avg_humidity_pct",          0.0)
    st.caption(
        f"📡 Forecast: {near_rain}mm next 2 days · "
        f"{far_rain}mm days 3–5 · "
        f"Avg humidity {humidity}%"
    )

    st.divider()

    # Leverage points
    st.subheader("💪 Your Leverage Points")
    for point in brief.get("leverage_points", []):
        st.markdown(f"- {point}")

    st.divider()

    # Negotiation script
    st.subheader("🗣️ What to Say to the Buyer")
    for i, line in enumerate(brief.get("negotiation_script", []), 1):
        st.markdown(f"**{i}.** {line}")

    st.divider()

    # Full market data expander
    with st.expander("📊 Full Market Data"):
        mc1, mc2 = st.columns(2)
        with mc1:
            st.write("**Price Data**")
            st.write(f"Average Price: {price_data.get('avg_price', 0):,.2f} {currency}/kg")
            st.write(f"12-Month High: {price_data.get('price_12m_high', 0):,.2f} {currency}/kg")
            st.write(f"12-Month Low:  {price_data.get('price_12m_low',  0):,.2f} {currency}/kg")
            trend = price_data.get('trend_direction', 'N/A')
            trend_display = trend.value if hasattr(trend, 'value') else str(trend)
            st.write(f"Trend: {trend_display}")
            st.write(f"Data Points: {price_data.get('data_points_count', 0)}")
            st.write(f"Latest Data: {price_data.get('latest_data_date', 'N/A')}")
        with mc2:
            st.write("**Knowledge Base**")
            st.write(f"RAG Similarity: {report_data.get('similarity_score', 0):.2f}")
            discount = report_data.get("typical_middleman_discount_pct")
            st.write(
                f"Middleman Discount: {discount}%"
                if discount else
                "Middleman Discount: Not found in documents"
            )
            context = report_data.get("historical_context")
            if context:
                st.write(f"Context: {context}")

def render_empty_state():
    """Renders the landing screen before any brief is generated."""
    st.info(
        "👈 Fill in your harvest details in the sidebar and click "
        "**Generate Negotiation Brief** to get started."
    )
    st.markdown("""
    ### How it works
    1. **Select** your crop, region, quantity and storage type
    2. **Click** Generate — the pipeline runs 4 AI agents in sequence
    3. **Receive** a data-grounded negotiation brief with exact prices,
       risk analysis, and a script to use with your buyer
    """)




def register_farmer(
    name: str,
    phone: str,
    crop: str,
    region: str,
    country: str,
    currency: str,
    threshold_pct: float
) -> bool:
    """Saves farmer registration to the database."""
    db_path = os.getenv("DB_PATH", "data/harvestbridge.db")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO farmers_registry
                (name, phone_number, crop, region, country, currency, price_threshold_pct)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, phone, crop, region, country, currency, threshold_pct))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False  # duplicate phone number
    except Exception as e:
        print(f"Registration error: {e}")
        return False


def render_registration_form():
    """Renders the farmer registration form for WhatsApp alerts."""
    with st.expander("🔔 Register for Price Alerts"):
        st.caption("Get WhatsApp notifications when your crop price changes.")

        with st.form("registration_form"):
            reg_name    = st.text_input("Your Name", key="reg_name")
            reg_phone   = st.text_input(
                "WhatsApp Number",
                placeholder="+2348012345678",
                key="reg_phone"
            )
            reg_country = st.selectbox(
                "Country",
                list(LOCATIONS.keys()),
                key="reg_country"
            )
            reg_crop = st.selectbox(
                "Crop",
                CROPS_BY_COUNTRY[reg_country],
                key="reg_crop"
            )
            reg_state = st.selectbox(
                "State / Region",
                list(LOCATIONS[reg_country]["states"].keys()),
                key="reg_state"
            )
            reg_threshold = st.slider(
                "Alert me when price moves by (%)",
                min_value=5,
                max_value=30,
                value=10,
                step=5,
                key="reg_threshold"
            )
            submitted = st.form_submit_button("Register")

        if submitted:
            if not reg_name or not reg_phone:
                st.error("Name and phone number are required.")
            else:
                success = register_farmer(
                    name=reg_name,
                    phone=reg_phone,
                    crop=reg_crop,
                    region=reg_state,
                    country=reg_country,
                    currency=LOCATIONS[reg_country]["currency"],
                    threshold_pct=float(reg_threshold)
                )
                if success:
                    st.success(
                        f"✅ Registered! You will receive WhatsApp alerts "
                        f"when {reg_crop} prices move by {reg_threshold}%."
                    )
                else:
                    st.error("Registration failed. This number may already be registered.")