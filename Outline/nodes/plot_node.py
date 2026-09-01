from agent.config import get_llm
from agent.state import StoryState, PlotOutput
from prompts.templates import PLOT_PROMPT
from langchain_core.prompts import PromptTemplate

def generate_plot(state: StoryState) -> StoryState:
    llm = get_llm().with_structured_output(PlotOutput)
    prompt = PromptTemplate.from_template(PLOT_PROMPT)
    chain = prompt | llm
    
    result = chain.invoke({
        "premise": state.get("premise", ""),
        "characters": str(state.get("characters", {})),
        "raw_scenes": str(state["raw_scenes"])
    })
    return {
        "story_engine": result.story_engine.model_dump(),
        "plot_structure": result.plot_structure.model_dump()
    }