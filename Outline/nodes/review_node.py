from agent.config import get_llm
from agent.state import StoryState, ReviewOutput
from langchain_core.prompts import PromptTemplate

# FIXED: Added the closing triple quotes at the end of this string
REVIEW_PROMPT = """
You are a ruthless Story Editor. Review the generated story bible against the original raw scenes.
Look for:
1. Hallucinations (characters or events that do not exist in the raw scenes).
2. Logical paradoxes in the continuity or timeline.
3. Missing schema elements.

Original Raw Scenes: {raw_scenes}
Generated Story Bible: {story_bible}

If it is perfect, set is_valid to true. If there are errors, set is_valid to false and provide specific, actionable feedback on what must be fixed.
"""

def evaluate_bible(state: StoryState) -> StoryState:
    llm = get_llm().with_structured_output(ReviewOutput)
    prompt = PromptTemplate.from_template(REVIEW_PROMPT)
    chain = prompt | llm
    
    # We only care about the core generated parts for the review
    bible_subset = {k: state.get(k) for k in ["characters", "plot_structure", "chapters", "canon_ledger"]}
    
    result = chain.invoke({
        "raw_scenes": str(state.get("raw_scenes")),
        "story_bible": str(bible_subset)
    })
    
    current_count = state.get("revision_count", 0)
    
    return {
        "is_valid": result.is_valid,
        "feedback": result.feedback,
        "revision_count": current_count + 1
    }