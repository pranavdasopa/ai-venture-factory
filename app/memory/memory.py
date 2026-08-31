from app.core.database import get_connection


class CompanyMemory:

    def remember(self, category: str, content: str):
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO memories (category, content)
            VALUES (?, ?)
            """,
            (category, content),
        )

        connection.commit()
        connection.close()

    def recall(self, category: str | None = None, limit: int = 20):

        connection = get_connection()
        cursor = connection.cursor()

        if category:
            cursor.execute(
                """
                SELECT id, category, content, created_at
                FROM memories
                WHERE category = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (category, limit),
            )
        else:
            cursor.execute(
                """
                SELECT id, category, content, created_at
                FROM memories
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            )

        rows = cursor.fetchall()
        connection.close()

        return rows