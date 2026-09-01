from config import get_llm
from state import StoryState, ConceptOutput
from prompts.templates import CONCEPT_PROMPT
from langchain_core.prompts import PromptTemplate

def generate_concept(state: StoryState) -> StoryState:
    llm = get_llm().with_structured_output(ConceptOutput)
    prompt = PromptTemplate.from_template(CONCEPT_PROMPT)
    chain = prompt | llm
    
    result = chain.invoke({"raw_scenes": str(state["raw_scenes"])})
    return {
        "title": result.title,
        "genre": result.genre.model_dump(),
        "setting": result.setting.model_dump(),
        "premise": result.premise
    }