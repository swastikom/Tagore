from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from config import get_llm, safe_invoke
from prompts.chapter_outliner import CHAPTER_OUTLINER_PROMPT
from state import NovelState

class SceneBrief(BaseModel):
    title: str
    brief: str
    purpose: str
    key_events: List[str]
    character_change: str
    new_information: str
    cliffhanger_or_transition: str

class ChapterBrief(BaseModel):
    title: str
    purpose: str
    scenes: Dict[int, SceneBrief]

class ActOutline(BaseModel):
    chapters: Dict[int, ChapterBrief]

llm = get_llm(heavy=True)
structured_outliner = llm.with_structured_output(ActOutline)

def _format_revision(existing: Dict[str, Any], notes: Optional[str], act: int) -> str:
    if existing and notes:
        return f"Previous drafts:\n{existing}\n\nHuman Revision Notes:\n{notes}"
    return "First draft for this act."

def chapter_outliner_node(state: NovelState) -> Dict[str, Any]:
    act = state.get("current_planning_act", 1)
    
    prompt = CHAPTER_OUTLINER_PROMPT.format(
        current_act=act,
        bible=state.get("bible", {}),
        revision_block=_format_revision(state.get("drafted_chapters", {}), state.get("chapters_revision_notes"), act)
    )
    
    result: ActOutline = safe_invoke(structured_outliner, prompt)
    
    # Auto-increment chapter keys to avoid overwriting previous acts
    drafted_chapters = state.get("drafted_chapters", {})
    current_max_ch = max([int(k) for k in drafted_chapters.keys()] + [0])
    
    new_chapters = {}
    for i, (old_ch_num, ch_data) in enumerate(result.chapters.items(), start=1):
        new_chapters[str(current_max_ch + i)] = ch_data.model_dump()
        
    return {
        "drafted_chapters": {**drafted_chapters, **new_chapters},
        "current_planning_act": act + 1,
        "chapters_approved": False
    }