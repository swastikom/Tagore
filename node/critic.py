from pydantic import BaseModel, Field
from config import get_llm, safe_invoke
from prompts.critic import CRITIC_PROMPT
from state import NovelState
from typing import Dict, Any

class CriticEvaluation(BaseModel):
    pacing_score: float = Field(description="Score from 0.0 to 10.0 evaluating pacing")
    logic_score: float = Field(description="Score from 0.0 to 10.0 evaluating plot logic")
    overall_score: float = Field(description="Overall draft score from 0.0 to 10.0")
    feedback_notes: str = Field(description="Detailed critique and suggestions for improvement")

raw_llm = get_llm(heavy=False)
structured_llm = raw_llm.with_structured_output(CriticEvaluation)

def critic_agent_node(state: NovelState) -> Dict[str, Any]:
    prompt = CRITIC_PROMPT.format(
        scene_plan=state.get("scene_plan", {}),
        draft=state.get("current_draft", "")
    )

    eval_result: CriticEvaluation = safe_invoke(structured_llm, prompt)
    score = eval_result.overall_score
    passed = score >= 8.5  # honest score — no self-forced pass here

    # FIX: always increment, regardless of pass/fail. This is what guarantees
    # route_critic's MAX_RETRIES check can actually fire and force a human
    # checkpoint. Previously retry_count only incremented on failure, which
    # meant that once it hit the local forced-pass threshold, it froze and
    # could never reach MAX_RETRIES — letting a scene loop
    # writer -> critic -> canon_guard -> writer forever if canon_guard kept
    # rejecting an otherwise well-scored draft.
    retry_count = state.get("retry_count", 0) + 1

    print(f"--> [CRITIC SCORE]: {score:.1f}/10 | Passed: {passed} | Attempt: {retry_count}")
    return {
        "critic_feedback": eval_result.feedback_notes,
        "passed_critic": passed,
        "retry_count": retry_count
    }