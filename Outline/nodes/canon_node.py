from agent.config import get_llm
from agent.state import StoryState, CanonOutput
from prompts.templates import CANON_PROMPT
from langchain_core.prompts import PromptTemplate

def generate_canon(state: StoryState) -> StoryState:
    llm = get_llm().with_structured_output(CanonOutput)
    prompt = PromptTemplate.from_template(CANON_PROMPT)
    chain = prompt | llm
    
    result = chain.invoke({
        "characters": str(state.get("characters", {})),
        "plot_structure": str(state.get("plot_structure", {})),
        "chapters": str(state.get("chapters", {}))
    })
    return {
        "canon_ledger": result.canon_ledger.model_dump(),
        "continuity": result.continuity.model_dump()
    }