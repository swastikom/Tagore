from typing import Dict, Any, List
from pydantic import BaseModel, Field
from config import get_llm, safe_invoke
from prompts.fact_extractor import FACT_EXTRACTOR_PROMPT
from state import NovelState

class ContinuityUpdate(BaseModel):
    new_facts: List[str] = Field(default_factory=list, description="New continuity facts established in this scene.")

_fact_llm = get_llm(heavy=False)
_structured_fact_llm = _fact_llm.with_structured_output(ContinuityUpdate)

def _extract_new_facts(draft: str, existing_ledger: List[str]) -> List[str]:
    if not draft.strip():
        return []
    prompt = FACT_EXTRACTOR_PROMPT.format(
        existing_ledger="\n".join(existing_ledger[-30:]) or "None yet.",
        draft=draft
    )
    try:
        result: ContinuityUpdate = safe_invoke(_structured_fact_llm, prompt)
        return result.new_facts
    except Exception as e:
        print(f"⚠️ Continuity fact extraction failed: {e}")
        return []

def manager_agent_node(state: NovelState) -> Dict[str, Any]:
    ch = state["current_chapter"]
    sc = state["current_scene"]
    draft = state.get("current_draft", "")

    # FIX #2: rolling context (used by the planner) now summarizes the ACTUAL
    # written prose, not the pre-writing plan — plans and prose regularly diverge.
    prose_snippet = draft.strip().replace("\n", " ")
    summary_snippet = f"Ch {ch} Sc {sc}: {prose_snippet[:400]}..."
    updated_rolling_context = state.get("rolling_context", []) + [summary_snippet]

    # FIX #1: keep the last couple of FULL scene drafts so the writer has real
    # short-term memory of what just happened, not just a truncated summary.
    recent_scene_texts = (state.get("recent_scene_texts", []) + [draft])[-2:]

    # FIX #5: continuity ledger grows with facts actually established in the prose,
    # instead of staying frozen at whatever was in outline.json at story start.
    existing_ledger = state.get("continuity_ledger", [])
    new_facts = _extract_new_facts(draft, existing_ledger)
    updated_ledger = existing_ledger + new_facts

    # FIX #4 (bookkeeping half): record scenes that got force-advanced without
    # passing critic/canon, so main.py can skip writing them and you can review later.
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
    current_chapter_data = chapters_dict.get(ch, {})
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
        "continuity_ledger": updated_ledger,
        "flagged_scenes": flagged_scenes,
        "current_scene": next_scene,
        "current_chapter": next_chapter,
        "retry_count": 0,
        "is_complete": is_complete,
        "critic_feedback": "",
        "canon_violations": [],
        "current_draft": "",
        "human_approved": False,       # FIX #3: require a fresh approval for each new scene
        "human_revision_notes": None
    }