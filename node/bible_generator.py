#node/bible_generator.py

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from config import get_llm, safe_invoke
from prompts.bible_generator import BIBLE_GENERATOR_PROMPT
from state import NovelState


# --- Structured-output schema, mirroring template.json's top-level shape
# (minus "chapters" — that's the next stage's job, once the bible is confirmed) ---

class Genre(BaseModel):
    primary: str
    secondary: List[str] = Field(default_factory=list)

class Setting(BaseModel):
    primary_location: str
    primary_era: str
    secondary_locations: List[str] = Field(default_factory=list)
    atmosphere: str

class StoryEngine(BaseModel):
    central_conflict: str
    protagonist_goal: str
    protagonist_need: str
    central_stakes: str
    opposing_force: str
    core_question: str

class CanonLedger(BaseModel):
    core_truth: str
    inciting_incident: str
    hidden_truth: str
    major_reversals: List[str] = Field(default_factory=list)
    essential_facts: List[str] = Field(default_factory=list)
    immutable_rules: List[str] = Field(default_factory=list)

class Character(BaseModel):
    role: str
    traits: List[str] = Field(default_factory=list)
    external_goal: str
    internal_need: str
    fear: str
    secret: str
    motivation: str
    character_arc: str
    relationships: Dict[str, str] = Field(default_factory=dict)
    key_quote_or_anchor: Optional[str] = None

class Act1(BaseModel):
    purpose: str
    turning_point: str

class Act2(BaseModel):
    purpose: str
    midpoint: str
    low_point: str

class Act3(BaseModel):
    purpose: str
    climax: str
    resolution: str

class PlotStructure(BaseModel):
    act_1: Act1
    act_2: Act2
    act_3: Act3

class ProseStyle(BaseModel):
    pov: str
    tense: str
    tone: str
    narrative_distance: str
    language: str
    style_principles: List[str] = Field(default_factory=list)
    anchor_motifs: List[str] = Field(default_factory=list)
    negative_constraints: List[str] = Field(default_factory=list)

class Continuity(BaseModel):
    timeline: List[str] = Field(default_factory=list)
    locations: List[str] = Field(default_factory=list)
    objects: List[str] = Field(default_factory=list)
    knowledge_state: Dict[str, List[str]] = Field(default_factory=dict)

class Ending(BaseModel):
    emotional_note: str
    final_image: str
    theme: str
    resolution_status: str

class StoryBible(BaseModel):
    title: str
    genre: Genre
    setting: Setting
    premise: str
    story_engine: StoryEngine
    canon_ledger: CanonLedger
    characters: Dict[str, Character] = Field(default_factory=dict)
    plot_structure: PlotStructure
    prose_style: ProseStyle
    continuity: Continuity
    ending: Ending


llm = get_llm(heavy=True)
structured_bible_llm = llm.with_structured_output(StoryBible)


def _format_revision_block(existing_bible: Optional[Dict[str, Any]], revision_notes: Optional[str]) -> str:
    if existing_bible and revision_notes:
        return (
            "You previously drafted this story bible:\n"
            f"{existing_bible}\n\n"
            "The author reviewed it and left this note. Apply it faithfully, and keep "
            "everything else that the note doesn't ask you to change:\n"
            f"{revision_notes}"
        )
    return "This is the first draft — there is no existing bible yet."


def bible_generator_node(state: NovelState) -> Dict[str, Any]:
    story_idea = state.get("story_idea", "")
    revision_block = _format_revision_block(state.get("bible"), state.get("bible_revision_notes"))

    prompt = BIBLE_GENERATOR_PROMPT.format(
        story_idea=story_idea or "No idea provided — invent something original and compelling.",
        revision_block=revision_block
    )

    result: StoryBible = safe_invoke(structured_bible_llm, prompt)
    return {
        "bible": result.model_dump(),
        "bible_approved": False,
        "bible_revision_notes": None
    }