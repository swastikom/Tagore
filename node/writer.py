from typing import Dict, Any
from config import get_llm, safe_invoke
from prompts.writer import WRITER_PROMPT
from state import NovelState

llm = get_llm(heavy=True)

def _extract_text(content: Any) -> str:
    if isinstance(content, str): return content
    if isinstance(content, list): return "\n".join(item["text"] if isinstance(item, dict) and "text" in item else str(item) for item in content)
    return str(content)

def writer_agent_node(state: NovelState) -> Dict[str, Any]:
    ch = state["current_chapter"]
    sc = state["current_scene"]

    master_outline = state.get("master_outline", {})
    chapters_dict = master_outline.get("chapters", {})
    chapter_info = chapters_dict.get(ch, {})
    scene_raw = chapter_info.get("scenes", {}).get(sc, {})

    global_style = master_outline.get("prose_style", state.get("prose_style", {}))
    active_style = dict(global_style)
    if isinstance(scene_raw, dict) and "prose_style" in scene_raw:
        active_style.update(scene_raw["prose_style"])

    # NEW: language is pulled the same way pov/tense/tone already are — from
    # the (possibly scene-overridden) active_style, defaulting to "English"
    # so outline.json files that don't set "language" keep working unchanged.
    language = active_style.get("language", "English")

    canon_ledger = master_outline.get("canon_ledger", {})
    continuity = master_outline.get("continuity", {})
    characters_context = master_outline.get("characters", {})

    canon_rules_list = []
    if "core_truth" in canon_ledger:
        canon_rules_list.append(f"- Core Truth: {canon_ledger['core_truth']}")
    if "immutable_rules" in canon_ledger:
        for rule in canon_ledger["immutable_rules"]:
            canon_rules_list.append(f"- Immutable Rule: {rule}")
    if "essential_facts" in canon_ledger:
        for fact in canon_ledger["essential_facts"]:
            canon_rules_list.append(f"- Essential Fact: {fact}")
    canon_rules_str = "\n".join(canon_rules_list) if canon_rules_list else "None specified."

    raw_neg_constraints = active_style.get("negative_constraints", [])
    neg_constraints_str = "\n".join([f"- {c}" for c in raw_neg_constraints]) if isinstance(raw_neg_constraints, list) else str(raw_neg_constraints)
    if not neg_constraints_str.strip():
        neg_constraints_str = "None specified."

    context_blocks = []
    if characters_context: context_blocks.append(f"ALLOWED CHARACTER ROSTER:\n{characters_context}")
    if "knowledge_state" in continuity: context_blocks.append(f"KNOWLEDGE STATE:\n{continuity['knowledge_state']}")
    if "locations" in continuity: context_blocks.append(f"LOCATION FACTS:\n{continuity['locations']}")
    if "objects" in continuity: context_blocks.append(f"OBJECT STATES:\n{continuity['objects']}")
    if state.get("retrieved_context"): context_blocks.append(f"PREVIOUS SCENE RECAP:\n{state.get('retrieved_context')}")

    # FIX #1: give the writer the actual verbatim text of the last couple of scenes,
    # not just a plan-derived summary.
    if state.get("recent_scene_texts"):
        joined_recent = "\n\n---\n\n".join(state["recent_scene_texts"])
        context_blocks.append(f"RECENT SCENES (VERBATIM — MAINTAIN VOICE & CONTINUITY):\n{joined_recent}")

    # FIX #5: living continuity ledger — facts established during generation so far,
    # on top of the static outline continuity above.
    if state.get("continuity_ledger"):
        ledger_str = "\n".join(f"- {f}" for f in state["continuity_ledger"][-40:])
        context_blocks.append(f"CONTINUITY FACTS ESTABLISHED SO FAR:\n{ledger_str}")

    full_retrieved_context = "\n\n".join(context_blocks)

    feedback_items = []
    if state.get("critic_feedback"): feedback_items.append(f"CRITIC FEEDBACK: {state['critic_feedback']}")
    if state.get("canon_violations"): feedback_items.append(f"CANON VIOLATIONS TO FIX: {', '.join(state['canon_violations'])}")
    if state.get("human_revision_notes"): feedback_items.append(f"HUMAN REVISION: {state['human_revision_notes']}")
    combined_feedback = "\n".join(feedback_items) if feedback_items else "None"

    genre_data = master_outline.get("genre", state.get("genre", "Fiction"))
    if isinstance(genre_data, dict):
        genre_str = f"{genre_data.get('primary', 'Fiction')} ({', '.join(genre_data.get('secondary', []))})"
    else:
        genre_str = str(genre_data)

    prompt = WRITER_PROMPT.format(
        chapter=ch, scene=sc, genre=genre_str,
        pov=active_style.get("pov", "Third Person Limited"),
        tense=active_style.get("tense", "Past"),
        tone=active_style.get("tone", "Dramatic"),
        language=language,
        scene_plan=scene_raw if scene_raw else state.get("scene_plan", {}),
        canon_rules=canon_rules_str,
        negative_constraints=neg_constraints_str,
        retrieved_context=full_retrieved_context,
        feedback=combined_feedback
    )

    res = safe_invoke(llm, prompt)
    return {"current_draft": _extract_text(res.content)}