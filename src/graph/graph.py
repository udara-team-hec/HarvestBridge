from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END

from src.agents.price_agent import price_agent_node
from src.agents.weather_agent import weather_agent_node
from src.agents.risk_agent import risk_agent_node
from src.agents.knowledge_agent import knowledge_agent_node
from src.agents.orchestrator import orchestrator_node


class GraphState(TypedDict):
    crop: str
    country:str
    location: str
    region: str
    quantity_kg: float
    currency: str
    storage_type: Optional[str]
    coordinates: dict        # {"lat": float, "lon": float}
    weather_data: Optional[dict]
    price_data: Optional[dict]
    risk_data: Optional[dict]
    report_data: Optional[dict]
    negotiation_brief: Optional[dict]
    errors: list


def build_pipeline():
    graph = StateGraph(GraphState)

    graph.add_node("price_agent",     price_agent_node)
    graph.add_node("weather_agent",   weather_agent_node)
    graph.add_node("risk_agent",      risk_agent_node)
    graph.add_node("knowledge_agent", knowledge_agent_node)
    graph.add_node("orchestrator",    orchestrator_node)

    graph.set_entry_point("price_agent")
    graph.add_edge("price_agent",     "weather_agent")
    graph.add_edge("weather_agent",   "risk_agent")
    graph.add_edge("risk_agent",      "knowledge_agent")
    graph.add_edge("knowledge_agent", "orchestrator")
    graph.add_edge("orchestrator",    END)

    return graph.compile()


pipeline = build_pipeline()