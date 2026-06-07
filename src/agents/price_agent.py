import sqlite3
import time
from src.schemas.models import TrendDirection

CROP_COLUMN_MAP = {
    "cassava":  "c_gari_fao",
    "gari":     "c_gari_fao",
    "maize":    "c_maize_fao",
    "rice":     "c_rice_fao",
    "yam":      "c_yam",
    "beans":    "c_beans",
    "millet":   "c_millet_fao",
    "sorghum":  "c_sorghum_fao"
}

REGION_CURRENCY_MAP = {
    "nigeria":  "NGN",
    "ethiopia": "ETB",
}


def analyze_price(crop: str, region: str, currency: str = "NGN") -> dict:
    db_column = CROP_COLUMN_MAP.get(crop.lower())
    if not db_column:
        raise ValueError(f"Crop '{crop}' not found in database schema.")

    conn = sqlite3.connect("data/harvestbridge.db")
    cursor = conn.cursor()

    cursor.execute(f"""
        SELECT
            AVG({db_column})                                  AS avg_price,
            MAX({db_column})                                  AS high_12m,
            MIN({db_column})                                  AS low_12m,
            AVG(CASE WHEN year >= 2025 THEN {db_column} END) AS avg_3m,
            MAX(price_date)                                   AS latest_date,
            COUNT({db_column})                                AS data_points
        FROM market_prices
        WHERE adm1_name LIKE ?
        AND {db_column} IS NOT NULL
    """, (f"%{region}%",))

    row = cursor.fetchone()
    conn.close()

    avg_price, high_12m, low_12m, avg_3m, latest_date, data_points = row

    # Guard — no data found for this region/crop combination
    if not avg_price:
        return {
            "crop": crop,
            "region": region,
            "currency": currency,
            "avg_price": 0.0,
            "trend_direction": TrendDirection.STABLE,
            "price_12m_high": 0.0,
            "price_12m_low": 0.0,
            "latest_data_date": "unknown",
            "data_points_count": 0,
        }

    if avg_3m and avg_3m > avg_price * 1.05:
        trend = TrendDirection.RISING
    elif avg_3m and avg_3m < avg_price * 0.95:
        trend = TrendDirection.FALLING
    else:
        trend = TrendDirection.STABLE

    return {
        "crop": crop,
        "region": region,
        "currency": currency,
        "avg_price": round(avg_price, 2),
        "trend_direction": trend,
        "price_12m_high": round(high_12m, 2),
        "price_12m_low": round(low_12m, 2),
        "latest_data_date": latest_date or "unknown",
        "data_points_count": data_points or 0,
    }


async def price_agent_node(state: dict) -> dict:
    start_time = time.time()

    crop_input     = state.get("crop")
    region_input   = state.get("region")
    currency_input = state.get("currency", "NGN")

    price_result = analyze_price(
        crop=crop_input,
        region=region_input,
        currency=currency_input
    )

    execution_time = time.time() - start_time
    price_result["execution_log"] = {
        "agent_runtime": execution_time,
        "success_status": True,
        "token_usage": 0
    }

    return {"price_data": price_result}