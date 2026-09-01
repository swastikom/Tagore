import sqlite3
import json
from typing import Dict, Any, Optional

class CanonDatabase:
    def __init__(self, db_path: str = "canon_store.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS characters (
                    name TEXT PRIMARY KEY,
                    details JSON
                )
            """)
            conn.commit()

    def set_character(self, name: str, data: Dict[str, Any]):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO characters (name, details) VALUES (?, ?)",
                (name, json.dumps(data))
            )
            conn.commit()  # NOTE: original code never committed this insert

    def get_character(self, name: str) -> Optional[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT details FROM characters WHERE name = ?", (name,))
            row = cursor.fetchone()
            return json.loads(row[0]) if row else None

    def get_all_characters(self) -> Dict[str, Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, details FROM characters")
            return {name: json.loads(details) for name, details in cursor.fetchall()}