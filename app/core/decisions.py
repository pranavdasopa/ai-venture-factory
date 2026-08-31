from app.core.database import get_connection


class DecisionManager:

    def create(
        self,
        title: str,
        description: str,
    ):

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO decisions
            (title, description)
            VALUES (?, ?)
            """,
            (title, description),
        )

        decision_id = cursor.lastrowid

        connection.commit()
        connection.close()

        return decision_id

    def list_decisions(self):

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id, title, description,
                   decision, status, created_at
            FROM decisions
            ORDER BY id DESC
            """
        )

        rows = cursor.fetchall()

        connection.close()

        return rows