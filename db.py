import sqlite3
import json
from typing import Dict, Any, Optional, List

class CanonDatabase:
    def __init__(self, db_path: str = "canon_store.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entities (
                    name TEXT PRIMARY KEY,
                    category TEXT,
                    state_data JSON
                )
            """)
            conn.commit()

    def upsert_entity(self, name: str, category: str, new_facts: List[str]):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT state_data FROM entities WHERE name = ?", (name,))
            row = cursor.fetchone()
            
            existing_facts = json.loads(row[0]) if row else []
            # Merge new facts, avoiding duplicates
            for fact in new_facts:
                if fact not in existing_facts:
                    existing_facts.append(fact)

            conn.execute(
                "INSERT OR REPLACE INTO entities (name, category, state_data) VALUES (?, ?, ?)",
                (name, category, json.dumps(existing_facts))
            )
            conn.commit()

    def get_entity(self, name: str) -> Optional[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT category, state_data FROM entities WHERE name = ?", (name,))
            row = cursor.fetchone()
            return {"category": row[0], "facts": json.loads(row[1])} if row else None

    def get_all_entity_names(self) -> List[str]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM entities")
            return [row[0] for row in cursor.fetchall()]