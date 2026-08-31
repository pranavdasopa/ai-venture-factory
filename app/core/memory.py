import sqlite3
from pathlib import Path
from datetime import datetime


DB_PATH = Path(__file__).resolve().parent.parent.parent / "company.db"


class CompanyMemory:

    def __init__(self):
        self.db_path = DB_PATH
        self._initialize()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _initialize(self):

        with self._connect() as conn:

            conn.execute("""
                CREATE TABLE IF NOT EXISTS company_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    memory_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)

            conn.commit()

    def remember(self, memory_type, title, content):

        with self._connect() as conn:

            conn.execute(
                """
                INSERT INTO company_memory
                (memory_type, title, content, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    memory_type,
                    title,
                    content,
                    datetime.now().isoformat(timespec="seconds"),
                ),
            )

            conn.commit()

    def recall(self, memory_type=None, limit=10):

        with self._connect() as conn:

            if memory_type:

                rows = conn.execute(
                    """
                    SELECT id, memory_type, title, content, created_at
                    FROM company_memory
                    WHERE memory_type = ?
                    ORDER BY id DESC
                    LIMIT ?
                    """,
                    (memory_type, limit),
                ).fetchall()

            else:

                rows = conn.execute(
                    """
                    SELECT id, memory_type, title, content, created_at
                    FROM company_memory
                    ORDER BY id DESC
                    LIMIT ?
                    """,
                    (limit,),
                ).fetchall()

        return rows

    def clear(self):

        with self._connect() as conn:

            conn.execute("DELETE FROM company_memory")
            conn.commit()


if __name__ == "__main__":

    memory = CompanyMemory()

    memory.remember(
        "decision",
        "Memory System Test",
        "AI Venture Factory successfully created shared company memory.",
    )

    print("=" * 60)
    print("COMPANY MEMORY TEST")
    print("=" * 60)

    records = memory.recall()

    for record in records:
        print(record)