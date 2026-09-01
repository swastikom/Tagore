from agent.config import get_llm, safe_invoke
from agent.prompts.planner import PLANNER_PROMPT
from agent.state import NovelState
from typing import Dict, Any

llm = get_llm(heavy=False)

def _extract_text(content) -> str:
    if isinstance(content, str): return content
    if isinstance(content, list): return "\n".join(item["text"] if isinstance(item, dict) and "text" in item else str(item) for item in content)
    return str(content)

def scene_planner_node(state: NovelState) -> Dict[str, Any]:
    ch = state["current_chapter"] # INT
    sc = state["current_scene"]   # INT
    
    chapters_dict = state["master_outline"].get("chapters", {})
    chapter_info = chapters_dict.get(ch, {})
    scene_raw = chapter_info.get("scenes", {}).get(sc, "Draft the scene following general novel outline.")
    scene_brief = scene_raw.get("brief", "") if isinstance(scene_raw, dict) else str(scene_raw)
    
    prompt = PLANNER_PROMPT.format(
        chapter=ch,
        scene=sc,
        scene_brief=scene_brief,
        outline=state["master_outline"].get("Premise", ""),
        rolling_context="\n".join(state.get("rolling_context", [])[-3:])
    )
    res = safe_invoke(llm, prompt)
    return {
        "scene_plan": {"raw_plan": _extract_text(res.content)},
        "retrieved_context": f"Scene brief loaded: {scene_brief}"
    }