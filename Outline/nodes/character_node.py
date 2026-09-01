from agent.config import get_llm
from agent.state import StoryState, CharactersOutput
from prompts.templates import CHARACTER_PROMPT
from langchain_core.prompts import PromptTemplate

def generate_characters(state: StoryState) -> StoryState:
    llm = get_llm().with_structured_output(CharactersOutput)
    prompt = PromptTemplate.from_template(CHARACTER_PROMPT)
    chain = prompt | llm
    
    result = chain.invoke({
        "premise": state.get("premise", ""),
        "raw_scenes": str(state["raw_scenes"])
    })
    return {"characters": {k: v.model_dump() for k, v in result.characters.items()}}