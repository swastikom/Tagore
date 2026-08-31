import sqlite3
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from state import NovelState

from node.bible_generator import bible_generator_node
from node.chapter_outliner import chapter_outliner_node
from node.planner import scene_planner_node
from node.writer import writer_agent_node
from node.critic import critic_agent_node
from node.canon_guard import canon_guard_node
from node.human_checkpoint import human_checkpoint_node
from node.manager import manager_agent_node
from config import MAX_RETRIES

def bible_checkpoint_node(state: NovelState): return {}
def chapter_checkpoint_node(state: NovelState): return {}

def route_bible(state: NovelState) -> str:
    if state.get("bible_approved"): return "chapter_outliner"
    return "bible_generator"

def route_outliner(state: NovelState) -> str:
    if state.get("current_planning_act", 1) <= 3: return "chapter_outliner"
    return "chapter_checkpoint"

def route_chapter_checkpoint(state: NovelState) -> str:
    if state.get("chapters_approved"): return END  # Route to END instead of planner
    return "chapter_outliner"

def route_critic(state: NovelState) -> str:
    if state.get("passed_critic") and state.get("passed_canon"): return "human_checkpoint"
    if state.get("retry_count", 0) >= MAX_RETRIES: return "human_checkpoint"
    return "writer"

def route_human(state: NovelState) -> str:
    if state.get("human_approved"): return "manager"
    return "writer"

def route_completion(state: NovelState) -> str:
    if state.get("is_complete"): return END
    return "planner"

def get_checkpointer():
    conn = sqlite3.connect("state_checkpoint.db", check_same_thread=False)
    return SqliteSaver(conn)

def build_outline_graph():
    workflow = StateGraph(NovelState)
    workflow.add_node("bible_generator", bible_generator_node)
    workflow.add_node("bible_checkpoint", bible_checkpoint_node)
    workflow.add_node("chapter_outliner", chapter_outliner_node)
    workflow.add_node("chapter_checkpoint", chapter_checkpoint_node)
    
    workflow.add_edge(START, "bible_generator")
    workflow.add_edge("bible_generator", "bible_checkpoint")
    workflow.add_conditional_edges("bible_checkpoint", route_bible)
    workflow.add_conditional_edges("chapter_outliner", route_outliner)
    workflow.add_conditional_edges("chapter_checkpoint", route_chapter_checkpoint)
    
    return workflow.compile(checkpointer=get_checkpointer(), interrupt_before=["bible_checkpoint", "chapter_checkpoint"])

def build_drafting_graph():
    workflow = StateGraph(NovelState)
    workflow.add_node("planner", scene_planner_node)
    workflow.add_node("writer", writer_agent_node)
    workflow.add_node("critic", critic_agent_node)
    workflow.add_node("canon_guard", canon_guard_node)
    workflow.add_node("human_checkpoint", human_checkpoint_node)
    workflow.add_node("manager", manager_agent_node)

    workflow.add_edge(START, "planner")
    workflow.add_edge("planner", "writer")
    workflow.add_edge("writer", "critic")
    workflow.add_edge("critic", "canon_guard")
    workflow.add_conditional_edges("canon_guard", route_critic, {"writer": "writer", "human_checkpoint": "human_checkpoint"})
    workflow.add_conditional_edges("human_checkpoint", route_human, {"manager": "manager", "writer": "writer"})
    workflow.add_conditional_edges("manager", route_completion, {"planner": "planner", END: END})
    
    return workflow.compile(checkpointer=get_checkpointer(), interrupt_before=["human_checkpoint"])