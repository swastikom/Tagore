#prompts/bible_generator.py

BIBLE_GENERATOR_PROMPT = """You are an expert novel architect. Design a complete, internally consistent story bible for a novel based on the author's idea below. This bible will become the single source of truth every later drafting and continuity-checking step is measured against, so be specific and concrete — never use placeholder-style language.

### AUTHOR'S STORY IDEA
{story_idea}

### REVISION CONTEXT
{revision_block}

Design:
- Title, genre (primary + secondary subgenres), and setting (primary location, era, secondary locations, atmosphere).
- A one-to-two sentence premise.
- The story engine: central conflict, protagonist goal, protagonist need, central stakes, opposing force, core question.
- A canon ledger: core truth, inciting incident, hidden truth, 2-4 major reversals, essential facts the story must never contradict, and immutable rules the writer must never break.
- A focused character roster (only characters who could plausibly appear in the story — do not pad it). For each: role, traits, external goal, internal need, fear, secret, motivation, character arc, relationships to other named characters, and an optional anchor line/philosophy.
- A three-act plot structure (purpose + turning point for act 1; purpose + midpoint + low point for act 2; purpose + climax + resolution for act 3).
- Prose style: POV, tense, tone, narrative distance, language, style principles, anchor motifs, and negative constraints (banned tropes/phrases).
- Continuity starting state: timeline, locations, objects, and each named character's knowledge state at the start of the story.
- An ending: emotional note, final image, theme, and resolution status.

Ensure the canon ledger, character secrets, and the ending are mutually consistent — nothing here should contradict anything else here.
"""