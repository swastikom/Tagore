CHAPTER_OUTLINER_PROMPT = """You are an expert novel outliner.
Using the approved Story Bible below, generate the chapter and scene briefs specifically for ACT {current_act}.

### STORY BIBLE
{bible}

### REVISION CONTEXT
{revision_block}

Break Act {current_act} into logical Chapters, and each Chapter into Scenes. 
Ensure the pacing builds towards this act's structural milestones.
Return only the structured outline data for this specific act.
"""