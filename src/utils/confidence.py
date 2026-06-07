from datetime import datetime


def calculate_confidence(
    price_data: dict,
    weather_api_success: bool,
    similarity_score: float
) -> int:
    """
    Calculates a reliability score from 1-10 based on three real signals.
    Never ask the LLM for this number.

    Data freshness  — max 4 points
    Weather success — max 2 points
    RAG similarity  — max 4 points
    """
    score = 0

    # 1. Data freshness (max 4 points)
    latest_date_str = price_data.get("latest_data_date")
    if latest_date_str and latest_date_str != "unknown":
        try:
            latest_date = datetime.strptime(latest_date_str, "%Y-%m-%d")
            months_old = (datetime.now() - latest_date).days / 30

            if months_old <= 1:
                score += 4
            elif months_old <= 3:
                score += 3
            elif months_old <= 6:
                score += 2
            else:
                score += 1
        except ValueError:
            score += 1
    else:
        score += 1

    # 2. Weather API success (max 2 points)
    if weather_api_success:
        score += 2

    # 3. RAG similarity (max 4 points)
    if similarity_score >= 0.80:
        score += 4
    elif similarity_score >= 0.65:
        score += 3
    elif similarity_score >= 0.50:
        score += 2
    else:
        score += 1

    return max(1, min(10, score))