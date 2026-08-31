from app.core.database import get_connection


class TaskManager:

    def create(
        self,
        title: str,
        description: str,
        owner: str,
        priority: str = "medium",
    ):

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO tasks
            (title, description, owner, priority)
            VALUES (?, ?, ?, ?)
            """,
            (title, description, owner, priority),
        )

        task_id = cursor.lastrowid

        connection.commit()
        connection.close()

        return task_id

    def list_tasks(self, status: str | None = None):

        connection = get_connection()
        cursor = connection.cursor()

        if status:

            cursor.execute(
                """
                SELECT id, title, description, owner,
                       status, priority, created_at
                FROM tasks
                WHERE status = ?
                ORDER BY id DESC
                """,
                (status,),
            )

        else:

            cursor.execute(
                """
                SELECT id, title, description, owner,
                       status, priority, created_at
                FROM tasks
                ORDER BY id DESC
                """
            )

        rows = cursor.fetchall()

        connection.close()

        return rows