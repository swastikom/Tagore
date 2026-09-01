# FIXED: Added closing triple quotes to EVERY individual prompt variable.

CONCEPT_PROMPT = """
You are an expert structural editor. Based on the following raw scene outlines, deduce the high-level concept.
Generate the title, genre, setting, and premise.
Raw Scenes: {raw_scenes}
"""

CHARACTER_PROMPT = """
Analyze the raw scenes and the premise to extract a comprehensive list of characters.
Deduce their traits, internal needs, and arcs based on their actions.
Premise: {premise}
Raw Scenes: {raw_scenes}
"""

PLOT_PROMPT = """
Map out the story engine and the macro plot structure (Dynamic Acts) based on the scenes and characters.
Premise: {premise}
Characters: {characters}
Raw Scenes: {raw_scenes}
"""

SCENE_PROMPT = """
Transform the raw scenes into the rich scene schema, assigning purpose, character change, and transitions to each beat.
Plot Structure: {plot_structure}
Raw Scenes: {raw_scenes}
"""

CANON_PROMPT = """
Establish the canon ledger and continuity tracker based on all previous story elements. Ensure no logical paradoxes exist.
Characters: {characters}
Plot: {plot_structure}
Rich Scenes: {chapters}
"""

STYLE_PROMPT = """
Determine the prose style rules, banned tropes, and define the ending criteria based on the developed story bible.
Premise: {premise}
Canon: {canon_ledger}
"""