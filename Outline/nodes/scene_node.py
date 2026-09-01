from config import get_llm
from state import StoryState, ChaptersOutput
from prompts.templates import SCENE_PROMPT
from langchain_core.prompts import PromptTemplate

def generate_scenes(state: StoryState) -> StoryState:
    llm = get_llm().with_structured_output(ChaptersOutput)
    prompt = PromptTemplate.from_template(SCENE_PROMPT)
    chain = prompt | llm
    
    result = chain.invoke({
        "plot_structure": str(state.get("plot_structure", {})),
        "raw_scenes": str(state["raw_scenes"])
    })
    return {"chapters": {k: v.model_dump() for k, v in result.chapters.items()}}