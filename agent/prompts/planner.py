PLANNER_PROMPT = """You are an expert novel planner. Plan Chapter {chapter}, Scene {scene} based on the scene brief below.
Author's Scene Brief: {scene_brief}
Master Premise: {outline}
Previous Context Summary: {rolling_context}

Return a structured plan with:
- scene_goal
- active_characters
- location
- conflict
- info_to_reveal
"""