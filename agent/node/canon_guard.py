from typing import Dict, Any, List
from pydantic import BaseModel, Field
from agent.config import get_llm
from agent.prompts.canon_guard import CANON_GUARD_PROMPT
from agent.state import NovelState

class CanonCheckResult(BaseModel):
    passed: bool = Field(description="True if the draft complies with all canon rules and negative constraints.")
    violations: List[str] = Field(default_factory=list, description="List of specific canon or continuity violations.")
    reasoning: str = Field(description="Structured explanation for the decision.")

llm = get_llm(heavy=False)
structured_canon_llm = llm.with_structured_output(CanonCheckResult)

def canon_guard_node(state: NovelState) -> Dict[str, Any]:
    draft = state.get("current_draft", "")
    master_outline = state.get("master_outline", {})

    canon_ledger = master_outline.get("canon_ledger", {})
    continuity = master_outline.get("continuity", {})
    characters = master_outline.get("characters", {})
    prose_style = master_outline.get("prose_style", {})

    allowed_character_names = list(characters.keys())
    negative_constraints = prose_style.get("negative_constraints", [])

    # FIX: canon_guard previously judged every scene against the whole novel's
    # rules with no idea which plot beats belong to THIS scene vs. a later one.
    # That caused false positives — e.g. rejecting a scene for not confronting
    # a character who, per the outline, isn't even present until a later scene.
    # Pulling in the scene brief (same as writer.py/planner.py already do)
    # lets the guard distinguish "this scene contradicts canon" from
    # "this scene just hasn't gotten to that beat yet."
    ch = state.get("current_chapter")
    sc = state.get("current_scene")
    chapters_dict = master_outline.get("chapters", {})
    scene_raw = chapters_dict.get(ch, {}).get("scenes", {}).get(sc, {})
    scene_brief = scene_raw.get("brief", "") if isinstance(scene_raw, dict) else str(scene_raw)

    prompt = CANON_GUARD_PROMPT.format(
        allowed_character_names=allowed_character_names,
        scene_brief=scene_brief or "No specific brief provided for this scene.",
        canon_ledger=canon_ledger,
        continuity=continuity,
        negative_constraints=negative_constraints,
        draft=draft
    )

    try:
        res: CanonCheckResult = structured_canon_llm.invoke(prompt)
        print(f"--> [CANON CHECK]: Passed: {res.passed} | Reasoning: {res.reasoning}")
        return {
            "passed_canon": res.passed,
            "canon_violations": res.violations if not res.passed else []
        }
    except Exception as e:
        print(f"⚠️ Canon Guard fallback triggered: {e}")
        return {"passed_canon": False, "canon_violations": ["Validation error occurred."]}