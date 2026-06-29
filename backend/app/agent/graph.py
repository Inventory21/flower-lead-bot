from langgraph.graph import StateGraph, END
from app.agent.nodes import agent_node, save_lead_node
from typing import TypedDict, Optional


class AgentState(TypedDict, total=False):
    telegram_id: int
    username: Optional[str]
    messages: list
    reply: str


def build_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("register_lead", save_lead_node)
    workflow.add_node("agent", agent_node)

    workflow.set_entry_point("register_lead")
    workflow.add_edge("register_lead", "agent")
    workflow.add_edge("agent", END)

    return workflow.compile()


graph = build_graph()