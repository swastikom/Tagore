from typing import Dict, Any, List
from pydantic import BaseModel, Field
from config import get_llm, safe_invoke
from prompts.fact_extractor import FACT_EXTRACTOR_PROMPT
from state import NovelState
from vector_db import VectorMemory # Add this import at the top
from db import CanonDatabase

class EntityStateUpdate(BaseModel):
    entity_name: str = Field(description="Exact name of the character, location, or object")
    category: str = Field(description="'Character', 'Location', or 'Object'")
    new_facts: List[str] = Field(description="List of new facts established in this scene")

class ContinuityUpdate(BaseModel):
    updates: List[EntityStateUpdate] = Field(default_factory=list)

_fact_llm = get_llm(heavy=False)
_structured_fact_llm = _fact_llm.with_structured_output(ContinuityUpdate)

def _extract_and_save_facts(draft: str):
    if not draft.strip():
        return
    prompt = FACT_EXTRACTOR_PROMPT.format(draft=draft)
    try:
        result = safe_invoke(_structured_fact_llm, prompt)
        db = CanonDatabase()
        vec_db = VectorMemory() # Initialize Vector DB
        
        for update in result.updates:
            db.upsert_entity(update.entity_name, update.category, update.new_facts)
            vec_db.add_facts(update.entity_name, update.category, update.new_facts) # Save to RAG
    except Exception as e:
        print(f"  Fact extraction failed: {e}")

def manager_agent_node(state: NovelState) -> Dict[str, Any]:
    ch = state["current_chapter"]
    sc = state["current_scene"]
    draft = state.get("current_draft", "")
    
    prose_snippet = draft.strip().replace("\n", " ")
    summary_snippet = f"Ch {ch} Sc {sc}: {prose_snippet[:400]}..."
    updated_rolling_context = state.get("rolling_context", []) + [summary_snippet]
    recent_scene_texts = (state.get("recent_scene_texts", []) + [draft])[-2:]

    # Write directly to SQLite instead of appending to state
    _extract_and_save_facts(draft)

    flagged_scenes = list(state.get("flagged_scenes", []))
    if not (state.get("passed_critic") and state.get("passed_canon")):
        flagged_scenes.append({
            "chapter": ch,
            "scene": sc,
            "passed_critic": state.get("passed_critic", False),
            "passed_canon": state.get("passed_canon", False),
            "canon_violations": state.get("canon_violations", []),
            "critic_feedback": state.get("critic_feedback", "")
        })

    chapters_dict = state["master_outline"].get("chapters", {})
    # Handle string vs int chapter keys gracefully
    current_chapter_data = chapters_dict.get(str(ch), chapters_dict.get(ch, {}))
    total_scenes_in_this_ch = len(current_chapter_data.get("scenes", {})) or 1
    
    next_scene = sc + 1
    next_chapter = ch
    
    if next_scene > total_scenes_in_this_ch:
        next_scene = 1
        next_chapter += 1
        
    total_chapters_count = len(chapters_dict) or state.get("total_chapters", 1)
    is_complete = next_chapter > total_chapters_count

    return {
        "rolling_context": updated_rolling_context,
        "recent_scene_texts": recent_scene_texts,
        "flagged_scenes": flagged_scenes,
        "current_scene": next_scene,
        "current_chapter": next_chapter,
        "retry_count": 0,
        "is_complete": is_complete,
        "critic_feedback": "",
        "canon_violations": [],
        "current_draft": "",
        "human_approved": False,
        "human_revision_notes": None
    }