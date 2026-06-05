from enum import Enum
from pydantic import BaseModel, Field, model_validator
from typing import List, Optional


class TrendDirection(str, Enum):
    RISING = "Rising"
    FALLING = "Falling"
    STABLE = "Stable"

class RiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class CurrencyCode(str, Enum):
    NGN = "NGN"
    ETB = "ETB"
    USD = "USD"

class SoilCondition(str, Enum):
    FLOOD_RISK = "FLOOD_RISK"
    DROUGHT = "DROUGHT"
    OPTIMAL = "OPTIMAL"
    UNKNOWN = "UNKNOWN"

class AgentExecutionLog(BaseModel):
    agent_runtime: float = Field(description="Execution time in seconds.")
    success_status: bool = Field(description="Whether the agent completed successfully.")
    token_usage: int = Field(ge=0, description="Total LLM tokens consumed.")


class PriceData(BaseModel):
    crop: str
    region: str
    currency: CurrencyCode
    avg_price: float
    trend_direction: TrendDirection
    price_12m_high: float
    price_12m_low: float
    latest_data_date: str = Field(description="The date of the most recent price record. Format: YYYY-MM-DD.")
    data_points_count: int = Field(ge=1, description="Number of price records used in the calculation.")
    execution_log: Optional[AgentExecutionLog] = Field(default=None, exclude=True)


class RiskData(BaseModel):
    forecast_rainfall_7d_mm: float = Field(ge=0)
    storage_spoilage_risk: RiskLevel
    road_passability_index: RiskLevel
    road_recovery_days: int = Field(ge=0, le=30)
    harvest_urgency: RiskLevel = Field(description="Derived urgency to sell based on forecast rain and temperature. HIGH = sell now.")
    weather_api_success: bool = Field(default=True)
    execution_log: Optional[AgentExecutionLog] = Field(default=None, exclude=True)


class ReportData(BaseModel):
    typical_middleman_discount_pct: Optional[float] = Field(default=None, ge=0, le=100)
    historical_context: Optional[str] = None
    similarity_score: float = Field(ge=0.0, le=1.0)
    execution_log: Optional[AgentExecutionLog] = Field(default=None, exclude=True)


class NegotiationBrief(BaseModel):
    fair_price_range: str
    minimum_acceptable_price: float
    leverage_points: List[str] = Field(min_length=1)
    negotiation_script: List[str] = Field(min_length=1)
    confidence_score: int = Field(ge=1, le=10)
    execution_log: Optional[AgentExecutionLog] = Field(default=None, exclude=True)


class WeatherData(BaseModel):
    past_rain_daily_mm: List[float]
    future_rain_daily_mm: List[float]
    soil_condition_alert: SoilCondition
    execution_log: Optional[AgentExecutionLog] = Field(default=None, exclude=True)