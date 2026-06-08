import os
import time
from langchain_groq import ChatGroq
from src.schemas.models import NegotiationBrief
from src.utils.confidence import calculate_confidence


def synthesise_brief(
    price_data: dict,
    risk_data: dict,
    report_data: dict,
    weather_data: dict,
    quantity_kg: float
) -> dict:
    """Runs the final LLM synthesis to produce a NegotiationBrief."""

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.1,
        api_key=os.getenv("GROQ_API_KEY")
    )
    structured_llm = llm.with_structured_output(NegotiationBrief)

    # --- Programmatic confidence score ---
    confidence = calculate_confidence(
        price_data=price_data,
        weather_api_success=risk_data.get("weather_api_success", False),
        similarity_score=report_data.get("similarity_score", 0.0)
    )

    # --- Price fields ---
    currency = price_data.get("currency", "NGN")
    if hasattr(currency, "value"):
        currency = currency.value

    avg_price = price_data.get("avg_price", 0.0)
    high_12m = price_data.get("price_12m_high", 0.0)
    low_12m = price_data.get("price_12m_low", 0.0)

    trend = price_data.get("trend_direction", "STABLE")
    if hasattr(trend, "value"):
        trend = trend.value

    # --- Risk fields — extract enum values individually ---
    spoilage = risk_data.get("storage_spoilage_risk", "Unknown")
    if hasattr(spoilage, "value"):
        spoilage = spoilage.value

    passability = risk_data.get("road_passability_index", "Unknown")
    if hasattr(passability, "value"):
        passability = passability.value

    urgency = risk_data.get("harvest_urgency", "Unknown")
    if hasattr(urgency, "value"):
        urgency = urgency.value

    recovery_days = risk_data.get("road_recovery_days", 0)
    storage_type = risk_data.get("storage_type") or "Not specified"

    # --- Two-window rainfall from WeatherData ---
    near_rain = weather_data.get("forecast_rainfall_near_mm", 0.0)
    far_rain = weather_data.get("forecast_rainfall_far_mm", 0.0)
    avg_humidity = weather_data.get("avg_humidity_pct", 0.0)

    # --- Knowledge fields ---
    middleman_discount = report_data.get("typical_middleman_discount_pct")
    historical_context = report_data.get("historical_context")

    prompt = f"""You are HarvestBridge, an AI negotiation coach for smallholder farmers in Africa.

Your job is to generate a Negotiation Brief that tells the farmer exactly what their 
produce is worth and how to defend that price with a buyer.

--- MARKET DATA ---
Crop: {price_data.get("crop")}
Region: {price_data.get("region")}
Quantity: {quantity_kg}kg
Currency: {currency}
3-Month Average Price: {avg_price} {currency}/kg
12-Month High: {high_12m} {currency}/kg
12-Month Low: {low_12m} {currency}/kg
Price Trend: {trend}

--- WEATHER AND LOGISTICS ---
Rainfall Next 2 Days: {near_rain}mm
Rainfall Days 3-5: {far_rain}mm
Average Humidity: {avg_humidity}%
Storage Type: {storage_type}
Storage Spoilage Risk: {spoilage}
Road Passability: {passability}
Road Recovery Days: {recovery_days}
Harvest Urgency: {urgency}

--- MARKET INTELLIGENCE ---
Typical Middleman Discount: {middleman_discount if middleman_discount else "Not available"}%
Historical Context: {historical_context if historical_context else "Not available"}

--- INSTRUCTIONS ---
1. fair_price_range: Calculate a +-10% band around the average price.
   Include the currency code (e.g. 850 - 1,050 NGN/kg).
2. minimum_acceptable_price: Set the floor at 15% below the average price.
3. leverage_points: Write 2-3 specific points explaining why the farmer
   has negotiating power. Reference the actual numbers above.
   If roads are passable and rain is low, that is leverage.
   If price is near the 12-month high, that is leverage.
   If storage risk is low, the farmer is not under pressure to sell immediately.
4. negotiation_script: Write 3-4 dialogue lines the farmer can say out loud.
   Make them confident, specific, and grounded in the data above.
   Reference actual prices, not vague statements.
5. confidence_score: Set to exactly {confidence}.

Write for a farmer, not a trader. Plain language. No financial jargon."""

    result = structured_llm.invoke(prompt)

    # Always inject programmatic confidence — never trust the LLM's number
    result.confidence_score = confidence

    return {
        "fair_price_range": result.fair_price_range,
        "minimum_acceptable_price": result.minimum_acceptable_price,
        "leverage_points": result.leverage_points,
        "negotiation_script": result.negotiation_script,
        "confidence_score": result.confidence_score
    }


async def orchestrator_node(state: dict) -> dict:
    """The LangGraph wrapper for the Orchestrator. Retries once on failure."""
    start_time = time.time()

    for attempt in range(2):
        try:
            brief = synthesise_brief(
                price_data=state.get("price_data", {}),
                risk_data=state.get("risk_data", {}),
                report_data=state.get("report_data", {}),
                weather_data=state.get("weather_data", {}),
                quantity_kg=state.get("quantity_kg", 0)
            )
            return {"negotiation_brief": brief, "orchestrator_runtime": time.time() - start_time}

        except Exception as e:
            if attempt == 0:
                print(f"[Orchestrator] Attempt 1 failed: {type(e).__name__}: {e} — retrying...")
            else:
                print(f"[Orchestrator] Failed after retry: {type(e).__name__}: {e}")
                return {"negotiation_brief": {
                    "fair_price_range":         "Unable to calculate — please retry",
                    "minimum_acceptable_price": 0.0,
                    "leverage_points":          ["Data unavailable — please retry"],
                    "negotiation_script":       ["Please try again"],
                    "confidence_score":         1
                }}