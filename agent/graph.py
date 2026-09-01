import sqlite3
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from agent.state import NovelState
from agent.node.planner import scene_planner_node
from agent.node.writer import writer_agent_node
from agent.node.critic import critic_agent_node
from agent.node.canon_guard import canon_guard_node
from agent.node.manager import manager_agent_node
from agent.node.human_checkpoint import human_checkpoint_node
from agent.config import MAX_RETRIES

def route_critic(state: NovelState) -> str:
    if state.get("passed_critic") and state.get("passed_canon"):
        return "human_checkpoint"
    if state.get("retry_count", 0) >= MAX_RETRIES:
        return "human_checkpoint"
    return "writer"

def route_human(state: NovelState) -> str:
    if state.get("human_approved"):
        return "manager"
    return "writer"

def route_completion(state: NovelState) -> str:
    if state.get("is_complete"):
        return END
    return "planner"

def build_graph():
    workflow = StateGraph(NovelState)

    workflow.add_node("planner", scene_planner_node)
    workflow.add_node("writer", writer_agent_node)
    workflow.add_node("critic", critic_agent_node)
    workflow.add_node("canon_guard", canon_guard_node)
    workflow.add_node("human_checkpoint", human_checkpoint_node)  # FIX #3
    workflow.add_node("manager", manager_agent_node)

    workflow.add_edge(START, "planner")
    workflow.add_edge("planner", "writer")
    workflow.add_edge("writer", "critic")
    workflow.add_edge("critic", "canon_guard")

    workflow.add_conditional_edges(
        "canon_guard",
        route_critic,
        {"writer": "writer", "human_checkpoint": "human_checkpoint"}
    )

    # FIX #3: this conditional edge previously existed but was unreachable, because
    # route_critic used to send straight to "manager" instead of "human_checkpoint".
    workflow.add_conditional_edges(
        "human_checkpoint",
        route_human,
        {"manager": "manager", "writer": "writer"}
    )

    workflow.add_conditional_edges(
        "manager",
        route_completion,
        {"planner": "planner", END: END}
    )

    conn = sqlite3.connect("state_checkpoint.db", check_same_thread=False)
    memory = SqliteSaver(conn)

    # FIX #3: this is what actually makes the checkpoint pause execution and wait
    # for a human decision, instead of auto-flowing through.
    return workflow.compile(checkpointer=memory, interrupt_before=["human_checkpoint"])