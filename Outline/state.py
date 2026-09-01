from typing import Dict, List, Any, Optional
from typing_extensions import TypedDict
from pydantic import BaseModel, Field

# --- Pydantic Models for Structured Output ---


# Add this model to your Pydantic schemas
class ReviewOutput(BaseModel):
    is_valid: bool
    feedback: str

class Genre(BaseModel):
    primary: str
    secondary: List[str]

class Setting(BaseModel):
    primary_location: str
    primary_era: str
    secondary_locations: List[str]
    atmosphere: str

class ConceptOutput(BaseModel):
    title: str
    genre: Genre
    setting: Setting
    premise: str

class Character(BaseModel):
    role: str
    traits: List[str]
    external_goal: str
    internal_need: str
    fear: str
    secret: str
    motivation: str
    character_arc: str
    relationships: Dict[str, str]
    key_quote_or_anchor: Optional[str] = None

class CharactersOutput(BaseModel):
    characters: Dict[str, Character]

class StoryEngine(BaseModel):
    central_conflict: str
    protagonist_goal: str
    protagonist_need: str
    central_stakes: str
    opposing_force: str
    core_question: str

class DynamicAct(BaseModel):
    act_number: int
    name: str
    purpose: str
    major_beat: str
    chapters_covered: List[str]

class PlotStructure(BaseModel):
    structure_type: str
    acts: List[DynamicAct]

class PlotOutput(BaseModel):
    story_engine: StoryEngine
    plot_structure: PlotStructure

class SceneDetail(BaseModel):
    title: str
    brief: str
    purpose: str
    key_events: List[str]
    character_change: str
    new_information: str
    cliffhanger_or_transition: str

class ChapterDetail(BaseModel):
    title: str
    purpose: str
    scenes: Dict[str, SceneDetail]

class ChaptersOutput(BaseModel):
    chapters: Dict[str, ChapterDetail]

class CanonLedger(BaseModel):
    core_truth: str
    inciting_incident: str
    hidden_truth: str
    major_reversals: List[str]
    essential_facts: List[str]
    immutable_rules: List[str]

class Continuity(BaseModel):
    timeline: List[str]
    locations: List[str]
    objects: List[str]
    knowledge_state: Dict[str, List[str]]

class CanonOutput(BaseModel):
    canon_ledger: CanonLedger
    continuity: Continuity

class ProseStyle(BaseModel):
    pov: str
    tense: str
    tone: str
    narrative_distance: str
    language: str
    style_principles: List[str]
    anchor_motifs: List[str]
    negative_constraints: List[str]

class Ending(BaseModel):
    emotional_note: str
    final_image: str
    theme: str
    resolution_status: str

class StyleOutput(BaseModel):
    prose_style: ProseStyle
    ending: Ending

# --- LangGraph State ---
class StoryState(TypedDict, total=False):
    # Input
    raw_scenes: Dict[str, Any]
    
    # Aggregated States
    title: str
    genre: dict
    setting: dict
    premise: str
    characters: dict
    story_engine: dict
    plot_structure: dict
    chapters: dict
    canon_ledger: dict
    continuity: dict
    prose_style: dict
    ending: dict
    is_valid: bool
    feedback: str
    revision_count: int