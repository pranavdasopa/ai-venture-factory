import sqlite3
from datetime import datetime
from pathlib import Path


DATABASE_PATH = (
    Path(__file__).resolve().parents[2]
    / "company.db"
)


class CompanyOrchestrator:

    def __init__(self):

        self.database_path = DATABASE_PATH

        self._create_tables()


    def _connect(self):

        return sqlite3.connect(
            self.database_path
        )


    def _create_tables(self):

        connection = self._connect()

        cursor = connection.cursor()


        cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            mission TEXT NOT NULL,

            target_customer TEXT,

            status TEXT NOT NULL,

            created_at TEXT NOT NULL,

            updated_at TEXT NOT NULL

        )
        """)


        cursor.execute("""
        CREATE TABLE IF NOT EXISTS project_tasks (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            project_id INTEGER NOT NULL,

            department TEXT NOT NULL,

            title TEXT NOT NULL,

            description TEXT NOT NULL,

            status TEXT NOT NULL,

            priority TEXT NOT NULL,

            created_at TEXT NOT NULL,

            FOREIGN KEY(project_id)
                REFERENCES projects(id)

        )
        """)


        connection.commit()

        connection.close()


    def create_project(
        self,
        name,
        mission,
        target_customer=""
    ):

        now = datetime.now().isoformat(
            timespec="seconds"
        )


        connection = self._connect()

        cursor = connection.cursor()


        cursor.execute("""
        INSERT INTO projects
        (
            name,
            mission,
            target_customer,
            status,
            created_at,
            updated_at
        )

        VALUES (?, ?, ?, ?, ?, ?)
        """, (

            name,

            mission,

            target_customer,

            "PLANNING",

            now,

            now

        ))


        project_id = cursor.lastrowid


        connection.commit()

        connection.close()


        return project_id


    def create_task(
        self,
        project_id,
        department,
        title,
        description,
        priority="HIGH"
    ):

        connection = self._connect()

        cursor = connection.cursor()


        cursor.execute("""
        INSERT INTO project_tasks
        (
            project_id,
            department,
            title,
            description,
            status,
            priority,
            created_at
        )

        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (

            project_id,

            department,

            title,

            description,

            "TODO",

            priority,

            datetime.now().isoformat(
                timespec="seconds"
            )

        ))


        task_id = cursor.lastrowid


        connection.commit()

        connection.close()


        return task_id


    def build_company(
        self,
        name,
        mission,
        target_customer=""
    ):

        project_id = self.create_project(
            name=name,
            mission=mission,
            target_customer=target_customer
        )


        tasks = [

            (
                "CEO",
                "Define company strategy",
                (
                    "Define the product vision, "
                    "initial milestones, priorities, "
                    "and key success metrics."
                ),
                "HIGH"
            ),

            (
                "CMO",
                "Validate target customer",
                (
                    "Identify the target customer, "
                    "their main problems, competing "
                    "solutions, and customer discovery plan."
                ),
                "HIGH"
            ),

            (
                "CTO",
                "Design technical architecture",
                (
                    "Design the initial technical "
                    "architecture, technology stack, "
                    "security boundaries, and MVP scope."
                ),
                "HIGH"
            ),

            (
                "CFO",
                "Create initial economics",
                (
                    "Define possible business models, "
                    "major cost categories, pricing "
                    "hypotheses, and financial risks."
                ),
                "MEDIUM"
            ),

            (
                "PRODUCT",
                "Create MVP specification",
                (
                    "Define the smallest useful product, "
                    "core user journey, required screens, "
                    "and acceptance criteria."
                ),
                "HIGH"
            ),

            (
                "RESEARCH",
                "Gather evidence",
                (
                    "Research the customer problem, "
                    "existing alternatives, and "
                    "important assumptions that require validation."
                ),
                "HIGH"
            ),

            (
                "CRITIC",
                "Challenge the company plan",
                (
                    "Identify the strongest reasons the "
                    "company could fail and propose tests "
                    "that reduce the biggest risks."
                ),
                "HIGH"
            ),

            (
                "QA",
                "Define quality gates",
                (
                    "Define functional, usability, "
                    "security, performance, and reliability "
                    "checks for the MVP."
                ),
                "MEDIUM"
            )

        ]


        created_tasks = []


        for task in tasks:

            task_id = self.create_task(
                project_id=project_id,
                department=task[0],
                title=task[1],
                description=task[2],
                priority=task[3]
            )

            created_tasks.append({

                "id": task_id,

                "department": task[0],

                "title": task[1],

                "status": "TODO",

                "priority": task[3]

            })


        return {

            "project_id": project_id,

            "name": name,

            "status": "PLANNING",

            "tasks": created_tasks

        }


    def get_project(self, project_id):

        connection = self._connect()

        cursor = connection.cursor()


        cursor.execute("""
        SELECT
            id,
            name,
            mission,
            target_customer,
            status,
            created_at,
            updated_at

        FROM projects

        WHERE id = ?
        """, (
            project_id,
        ))


        project = cursor.fetchone()


        connection.close()


        return project


    def list_projects(self):

        connection = self._connect()

        cursor = connection.cursor()


        cursor.execute("""
        SELECT
            id,
            name,
            mission,
            target_customer,
            status,
            created_at,
            updated_at

        FROM projects

        ORDER BY id DESC
        """)


        projects = cursor.fetchall()


        connection.close()


        return projects


    def list_tasks(
        self,
        project_id
    ):

        connection = self._connect()

        cursor = connection.cursor()


        cursor.execute("""
        SELECT
            id,
            department,
            title,
            description,
            status,
            priority,
            created_at

        FROM project_tasks

        WHERE project_id = ?

        ORDER BY id
        """, (
            project_id,
        ))


        tasks = cursor.fetchall()


        connection.close()


        return tasks


if __name__ == "__main__":

    orchestrator = CompanyOrchestrator()


    print("=" * 60)

    print(
        "AI VENTURE FACTORY — COMPANY ORCHESTRATOR"
    )

    print("=" * 60)


    result = orchestrator.build_company(

        name="SAI — Sahayak AI",

        mission=(
            "Build a persistent personal AI agent "
            "that helps people learn, build careers, "
            "find opportunities, make decisions, "
            "and increasingly execute digital work "
            "with user control."
        ),

        target_customer=(
            "College students aged approximately 18–25 "
            "as the initial market."
        )

    )


    print()

    print(
        f"PROJECT-{result['project_id']:04d}"
    )

    print(
        f"NAME: {result['name']}"
    )

    print(
        f"STATUS: {result['status']}"
    )


    print()

    print("CREATED EXECUTIVE TASKS")

    print("-" * 60)


    for task in result["tasks"]:

        print(
            f"[{task['department']}] "
            f"{task['title']} "
            f"| {task['status']} "
            f"| {task['priority']}"
        )


    print()

    print("=" * 60)

    print("ORCHESTRATOR TEST COMPLETE")

    print("=" * 60)