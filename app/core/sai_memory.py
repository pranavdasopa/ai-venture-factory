import sqlite3
from datetime import datetime


class SAIMemory:

    def __init__(self, database_path="company.db"):
        self.database_path = database_path
        self._create_tables()

    def _connect(self):
        return sqlite3.connect(self.database_path)

    def _create_tables(self):

        connection = self._connect()
        cursor = connection.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sai_profile (

            id INTEGER PRIMARY KEY CHECK (id = 1),

            name TEXT,
            education TEXT,
            skills TEXT,
            interests TEXT,
            goals TEXT,

            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sai_memory (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            memory TEXT NOT NULL,

            created_at TEXT NOT NULL
        )
        """)

        connection.commit()
        connection.close()

    def get_profile(self):

        connection = self._connect()
        cursor = connection.cursor()

        cursor.execute("""
        SELECT
            name,
            education,
            skills,
            interests,
            goals
        FROM sai_profile
        WHERE id = 1
        """)

        row = cursor.fetchone()

        connection.close()

        if not row:
            return {
                "name": "",
                "education": "",
                "skills": "",
                "interests": "",
                "goals": ""
            }

        return {
            "name": row[0] or "",
            "education": row[1] or "",
            "skills": row[2] or "",
            "interests": row[3] or "",
            "goals": row[4] or ""
        }

    def save_profile(
        self,
        name="",
        education="",
        skills="",
        interests="",
        goals=""
    ):

        now = datetime.utcnow().isoformat()

        connection = self._connect()
        cursor = connection.cursor()

        cursor.execute("""
        INSERT INTO sai_profile (
            id,
            name,
            education,
            skills,
            interests,
            goals,
            created_at,
            updated_at
        )

        VALUES (
            1, ?, ?, ?, ?, ?, ?, ?
        )

        ON CONFLICT(id)
        DO UPDATE SET

            name = excluded.name,
            education = excluded.education,
            skills = excluded.skills,
            interests = excluded.interests,
            goals = excluded.goals,
            updated_at = excluded.updated_at
        """, (
            name,
            education,
            skills,
            interests,
            goals,
            now,
            now
        ))

        connection.commit()
        connection.close()

    def add_memory(self, memory):

        if not memory:
            return

        connection = self._connect()
        cursor = connection.cursor()

        cursor.execute("""
        INSERT INTO sai_memory (
            memory,
            created_at
        )

        VALUES (?, ?)
        """, (
            memory.strip(),
            datetime.utcnow().isoformat()
        ))

        connection.commit()
        connection.close()

    def get_memories(self, limit=20):

        connection = self._connect()
        cursor = connection.cursor()

        cursor.execute("""
        SELECT memory, created_at
        FROM sai_memory
        ORDER BY id DESC
        LIMIT ?
        """, (limit,))

        rows = cursor.fetchall()

        connection.close()

        return [
            {
                "memory": row[0],
                "created_at": row[1]
            }
            for row in rows
        ]

    def build_context(self):

        profile = self.get_profile()
        memories = self.get_memories(10)

        context = []

        context.append("USER PROFILE:")

        for key, value in profile.items():

            if value:
                context.append(
                    f"{key.upper()}: {value}"
                )

        if memories:

            context.append("")
            context.append("RELEVANT MEMORY:")

            for item in memories:

                context.append(
                    f"- {item['memory']}"
                )

        return "\n".join(context)