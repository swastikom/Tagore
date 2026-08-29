FACT_EXTRACTOR_PROMPT = """Read the scene draft below and extract any NEW continuity facts it establishes: object state changes, character knowledge changes, location facts, or timeline events.
Only list facts that are genuinely NEW — not already covered in the existing continuity ledger. If nothing new was established, return an empty list.

Existing Continuity Ledger:
{existing_ledger}

Scene Draft:
{draft}

Return a structured JSON list of new_facts (short, single-sentence facts, present tense).
"""