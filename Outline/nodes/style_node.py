from agent.config import get_llm
from agent.state import StoryState, StyleOutput
from prompts.templates import STYLE_PROMPT
from langchain_core.prompts import PromptTemplate

def generate_style(state: StoryState) -> StoryState:
    llm = get_llm().with_structured_output(StyleOutput)
    prompt = PromptTemplate.from_template(STYLE_PROMPT)
    chain = prompt | llm
    
    result = chain.invoke({
        "premise": state.get("premise", ""),
        "canon_ledger": str(state.get("canon_ledger", {}))
    })
    return {
        "prose_style": result.prose_style.model_dump(),
        "ending": result.ending.model_dump()
    }