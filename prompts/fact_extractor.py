FACT_EXTRACTOR_PROMPT = """Read the scene draft below and extract any NEW facts established about specific entities (Characters, Locations, Objects). 
Only list facts that fundamentally change an entity's physical state, acquired knowledge, or location.

Scene Draft:
{draft}

Return a structured JSON list of updates. If nothing new was established, return an empty list.
"""