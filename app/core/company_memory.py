import sqlite3
from datetime import datetime


class CompanyMemory:

    def __init__(self, database_path="company.db"):
        self.database_path = database_path
        self._create_tables()

    def _connect(self):
        return sqlite3.connect(self.database_path)

    def _create_tables(self):

        connection = self._connect()
        cursor = connection.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_message TEXT NOT NULL,

            company_response TEXT NOT NULL,

            created_at TEXT NOT NULL

        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS decisions (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            idea TEXT NOT NULL,

            decision TEXT NOT NULL,

            reason TEXT,

            created_at TEXT NOT NULL

        )
        """)

        connection.commit()
        connection.close()

    def save_conversation(
        self,
        user_message,
        company_response
    ):

        connection = self._connect()
        cursor = connection.cursor()

        cursor.execute("""
        INSERT INTO conversations
        (user_message, company_response, created_at)

        VALUES (?, ?, ?)
        """, (
            user_message,
            company_response,
            datetime.now().isoformat()
        ))

        connection.commit()
        connection.close()

    def save_decision(
        self,
        idea,
        decision,
        reason=""
    ):

        connection = self._connect()
        cursor = connection.cursor()

        cursor.execute("""
        INSERT INTO decisions
        (idea, decision, reason, created_at)

        VALUES (?, ?, ?, ?)
        """, (
            idea,
            decision,
            reason,
            datetime.now().isoformat()
        ))

        connection.commit()
        connection.close()

    def get_recent_conversations(
        self,
        limit=10
    ):

        connection = self._connect()
        cursor = connection.cursor()

        cursor.execute("""
        SELECT
            id,
            user_message,
            company_response,
            created_at

        FROM conversations

        ORDER BY id DESC

        LIMIT ?
        """, (limit,))

        rows = cursor.fetchall()

        connection.close()

        return rows

    def get_recent_decisions(
        self,
        limit=10
    ):

        connection = self._connect()
        cursor = connection.cursor()

        cursor.execute("""
        SELECT
            id,
            idea,
            decision,
            reason,
            created_at

        FROM decisions

        ORDER BY id DESC

        LIMIT ?
        """, (limit,))

        rows = cursor.fetchall()

        connection.close()

        return rows


if __name__ == "__main__":

    memory = CompanyMemory()

    memory.save_conversation(
        "Memory test",
        "Company memory is working."
    )

    memory.save_decision(
        "Memory test idea",
        "TEST",
        "Testing persistent company memory."
    )

    print("=" * 60)
    print("AI VENTURE FACTORY — COMPANY MEMORY")
    print("=" * 60)

    print()
    print("Recent conversations:")

    for row in memory.get_recent_conversations():

        print(row)

    print()
    print("Recent decisions:")

    for row in memory.get_recent_decisions():

        print(row)

    print()
    print("=" * 60)
    print("MEMORY TEST COMPLETE")
    print("=" * 60)