from typing import Dict
from pydantic import BaseModel
from config import get_llm
from state import (
    StoryState, 
    Character, 
    PlotStructure, 
    ChapterDetail, 
    CanonLedger
) # FIXED: Added the missing closing parenthesis here
from langchain_core.prompts import PromptTemplate

# Create a composite Pydantic model specifically for the Refine node 
# to enforce strict schema adherence when rewriting multiple parts of the state.
class RefinedBible(BaseModel):
    characters: Dict[str, Character]
    plot_structure: PlotStructure
    chapters: Dict[str, ChapterDetail]
    canon_ledger: CanonLedger

# FIXED: Added the missing closing triple quotes at the end of this string
REFINE_PROMPT = """
You are the Master Fixer. You have been given a generated story bible and specific feedback from the Editor detailing what is wrong with it (e.g., hallucinations, paradoxes, missing schema elements).

Fix the errors in the story bible based strictly on the feedback. Do not change parts that are already correct. Ensure the output strictly follows the required schema.

Editor Feedback: 
{feedback}

Current Story Bible: 
{story_bible}
"""

def refine_bible(state: StoryState) -> StoryState:
    # Use with_structured_output to guarantee the refined JSON doesn't break the pipeline
    llm = get_llm().with_structured_output(RefinedBible) 
    prompt = PromptTemplate.from_template(REFINE_PROMPT)
    chain = prompt | llm
    
    # Isolate only the sections that were reviewed and might need patching
    bible_subset = {
        "characters": state.get("characters", {}),
        "plot_structure": state.get("plot_structure", {}),
        "chapters": state.get("chapters", {}),
        "canon_ledger": state.get("canon_ledger", {})
    }
    
    print("Refining story bible based on feedback...")
    
    # Invoke the LLM to regenerate the corrected subset
    result: RefinedBible = chain.invoke({
        "feedback": state.get("feedback", ""),
        "story_bible": str(bible_subset)
    })
    
    # Return the patched dictionary to LangGraph, which will overwrite the old state values.
    # We dump the Pydantic models back into standard dictionaries.
    return {
        "characters": {k: v.model_dump() for k, v in result.characters.items()},
        "plot_structure": result.plot_structure.model_dump(),
        "chapters": {k: v.model_dump() for k, v in result.chapters.items()},
        "canon_ledger": result.canon_ledger.model_dump(),
        "feedback": "Refinement applied. Awaiting re-evaluation."
    }