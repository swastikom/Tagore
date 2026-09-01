from typing import Dict, Any
from agent.state import NovelState

def human_checkpoint_node(state: NovelState) -> Dict[str, Any]:
    # Pass-through node. Execution actually pauses HERE because graph.py compiles
    # with interrupt_before=["human_checkpoint"]. main.py inspects the paused state,
    # sets human_approved / human_revision_notes via app.update_state(), then resumes.
    return {}