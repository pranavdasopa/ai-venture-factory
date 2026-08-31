import sqlite3
from datetime import datetime


class ExperimentRegistry:

    def __init__(self, database_path="company.db"):
        self.database_path = database_path
        self._create_table()

    def _connect(self):
        return sqlite3.connect(self.database_path)

    def _create_table(self):

        connection = self._connect()
        cursor = connection.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS experiments (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            idea TEXT NOT NULL,
            unknown TEXT NOT NULL,
            hypothesis TEXT NOT NULL,
            experiment TEXT NOT NULL,
            success_criteria TEXT NOT NULL,
            failure_criteria TEXT NOT NULL,

            status TEXT NOT NULL,

            result TEXT,
            decision TEXT,

            created_at TEXT NOT NULL,
            started_at TEXT,
            completed_at TEXT

        )
        """)

        # Upgrade databases created by older versions.
        cursor.execute("PRAGMA table_info(experiments)")
        columns = [row[1] for row in cursor.fetchall()]

        if "started_at" not in columns:
            cursor.execute("""
            ALTER TABLE experiments
            ADD COLUMN started_at TEXT
            """)

        if "completed_at" not in columns:
            cursor.execute("""
            ALTER TABLE experiments
            ADD COLUMN completed_at TEXT
            """)

        connection.commit()
        connection.close()

    def create_experiment(
        self,
        idea,
        unknown,
        hypothesis,
        experiment,
        success_criteria,
        failure_criteria,
    ):

        connection = self._connect()
        cursor = connection.cursor()

        created_at = datetime.now().isoformat()

        cursor.execute("""
        INSERT INTO experiments (
            idea,
            unknown,
            hypothesis,
            experiment,
            success_criteria,
            failure_criteria,
            status,
            created_at
        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            idea,
            unknown,
            hypothesis,
            experiment,
            success_criteria,
            failure_criteria,
            "PLANNED",
            created_at,
        ))

        experiment_id = cursor.lastrowid

        connection.commit()
        connection.close()

        return experiment_id

    def start_experiment(self, experiment_id):

        connection = self._connect()
        cursor = connection.cursor()

        cursor.execute("""
        SELECT status
        FROM experiments
        WHERE id = ?
        """, (experiment_id,))

        row = cursor.fetchone()

        if row is None:
            connection.close()
            raise ValueError("Experiment does not exist.")

        if row[0] != "PLANNED":
            connection.close()
            raise ValueError(
                f"Experiment cannot start from status: {row[0]}"
            )

        started_at = datetime.now().isoformat()

        cursor.execute("""
        UPDATE experiments

        SET
            status = ?,
            started_at = ?

        WHERE id = ?
        """, (
            "RUNNING",
            started_at,
            experiment_id,
        ))

        connection.commit()
        connection.close()

    def complete_experiment(
        self,
        experiment_id,
        result,
        decision,
    ):

        connection = self._connect()
        cursor = connection.cursor()

        cursor.execute("""
        SELECT status
        FROM experiments
        WHERE id = ?
        """, (experiment_id,))

        row = cursor.fetchone()

        if row is None:
            connection.close()
            raise ValueError("Experiment does not exist.")

        if row[0] != "RUNNING":
            connection.close()
            raise ValueError(
                f"Experiment cannot be completed from status: {row[0]}"
            )

        completed_at = datetime.now().isoformat()

        cursor.execute("""
        UPDATE experiments

        SET
            status = ?,
            result = ?,
            decision = ?,
            completed_at = ?

        WHERE id = ?
        """, (
            "COMPLETED",
            result,
            decision,
            completed_at,
            experiment_id,
        ))

        connection.commit()
        connection.close()

    def get_experiment(self, experiment_id):

        connection = self._connect()
        cursor = connection.cursor()

        cursor.execute("""
        SELECT *
        FROM experiments
        WHERE id = ?
        """, (experiment_id,))

        result = cursor.fetchone()

        connection.close()

        return result

    def list_experiments(self):

        connection = self._connect()
        cursor = connection.cursor()

        cursor.execute("""
        SELECT
            id,
            idea,
            status,
            result,
            decision,
            created_at,
            started_at,
            completed_at
        FROM experiments
        ORDER BY id DESC
        """)

        results = cursor.fetchall()

        connection.close()

        return results


if __name__ == "__main__":

    registry = ExperimentRegistry()

    print("=" * 60)
    print("AI VENTURE FACTORY — EXPERIMENT LIFECYCLE TEST")
    print("=" * 60)

    experiment_id = registry.create_experiment(

        idea="SaaS for automating one repetitive administrative task.",

        unknown="Whether small businesses experience the problem strongly enough to care.",

        hypothesis="Target customers experience this problem frequently enough to want a solution.",

        experiment="Interview 10 relevant small-business owners.",

        success_criteria="At least 5 of 10 independently describe the same significant problem.",

        failure_criteria="Fewer than 3 of 10 describe the problem as significant.",
    )

    print()
    print(f"Created: EXPERIMENT-{experiment_id:04d}")

    experiment = registry.get_experiment(experiment_id)

    print(f"Initial status: {experiment[7]}")

    registry.start_experiment(experiment_id)

    experiment = registry.get_experiment(experiment_id)

    print(f"After start: {experiment[7]}")

    registry.complete_experiment(
        experiment_id,
        result="6 of 10 interviewed businesses reported the problem as significant.",
        decision="CONTINUE",
    )

    experiment = registry.get_experiment(experiment_id)

    print(f"After completion: {experiment[7]}")
    print(f"Result: {experiment[8]}")
    print(f"Decision: {experiment[9]}")

    print()
    print("=" * 60)
    print("LIFECYCLE TEST COMPLETE")
    print("=" * 60)