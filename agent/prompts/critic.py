CRITIC_PROMPT = """Evaluate this novel scene draft across multiple parameters.
Scene Plan: {scene_plan}
Draft: {draft}

Respond with structured feedback and scores (0 to 10):
- pacing_score
- logic_score
- overall_score
- feedback_notes
"""