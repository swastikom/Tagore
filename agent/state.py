from typing import TypedDict, List, Dict, Any, Optional

class NovelState(TypedDict):
    master_outline: Dict[str, Any]
    novel_title: str
    genre: str
    prose_style: Dict[str, str]
    current_chapter: int
    current_scene: int
    total_chapters: int
    scene_plan: Optional[Dict[str, Any]]
    rolling_context: List[str]
    recent_scene_texts: List[str]      # NEW: last few FULL drafts, for writer continuity
    continuity_ledger: List[str]       # NEW: facts extracted from approved scenes, grows over time
    flagged_scenes: List[Dict[str, Any]]  # NEW: scenes force-advanced without passing checks
    retrieved_context: str
    current_draft: str
    critic_scores: Dict[str, float]
    critic_feedback: str
    canon_violations: List[str]
    retry_count: int
    passed_critic: bool
    passed_canon: bool
    human_approved: bool
    human_revision_notes: Optional[str]
    is_complete: bool