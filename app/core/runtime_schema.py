import json
import sqlite3

from app.core.database import get_connection


def _columns(connection, table_name):
    return {
        row["name"]
        for row in connection.execute(
            f"PRAGMA table_info({table_name})"
        ).fetchall()
    }


def _add_column(connection, table_name, column_name, definition):
    if column_name not in _columns(connection, table_name):
        connection.execute(
            f"ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}"
        )


def initialize_runtime_schema():
    connection = get_connection()
    try:
        _add_column(connection, "execution_tasks", "agent_role", "TEXT")
        _add_column(connection, "execution_tasks", "depends_on", "TEXT NOT NULL DEFAULT '[]'")
        _add_column(connection, "execution_tasks", "requires_approval", "INTEGER NOT NULL DEFAULT 0")
        _add_column(connection, "execution_tasks", "started_at", "TEXT")
        _add_column(connection, "execution_tasks", "completed_at", "TEXT")
        _add_column(connection, "execution_tasks", "last_error", "TEXT")
        _add_column(connection, "execution_tasks", "result", "TEXT")
        _add_column(connection, "execution_tasks", "created_at", "TIMESTAMP")
        _add_column(connection, "execution_tasks", "updated_at", "TIMESTAMP")
        _add_column(connection, "execution_tasks", "tool_name", "TEXT")
        _add_column(connection, "execution_tasks", "max_retries", "INTEGER NOT NULL DEFAULT 2")
        _add_column(connection, "execution_tasks", "retry_count", "INTEGER NOT NULL DEFAULT 0")

        connection.execute("""
            CREATE TABLE IF NOT EXISTS agent_registry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL UNIQUE,
                objective TEXT NOT NULL,
                instructions TEXT NOT NULL DEFAULT '',
                capabilities TEXT NOT NULL DEFAULT '[]',
                permissions TEXT NOT NULL DEFAULT '[]',
                status TEXT NOT NULL DEFAULT 'OFFLINE',
                model_provider TEXT,
                model_name TEXT,
                current_task_id INTEGER,
                last_heartbeat TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS company_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                aggregate_type TEXT,
                aggregate_id TEXT,
                payload TEXT NOT NULL DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed_at TIMESTAMP
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS execution_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER,
                status TEXT NOT NULL,
                trigger TEXT NOT NULL,
                started_at TEXT NOT NULL,
                completed_at TEXT,
                error TEXT,
                result TEXT
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS execution_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER NOT NULL,
                task_id INTEGER NOT NULL,
                agent_role TEXT NOT NULL,
                status TEXT NOT NULL,
                tool_name TEXT,
                input_payload TEXT NOT NULL DEFAULT '{}',
                output_payload TEXT,
                error TEXT,
                started_at TEXT NOT NULL,
                completed_at TEXT,
                FOREIGN KEY(run_id) REFERENCES execution_runs(id),
                FOREIGN KEY(task_id) REFERENCES execution_tasks(id)
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS founder_approvals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'PENDING',
                requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                decided_at TIMESTAMP,
                decided_by TEXT,
                reason TEXT,
                UNIQUE(task_id, action),
                FOREIGN KEY(task_id) REFERENCES execution_tasks(id)
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS system_audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                actor_type TEXT NOT NULL,
                actor_id TEXT,
                action TEXT NOT NULL,
                resource_type TEXT,
                resource_id TEXT,
                status TEXT NOT NULL,
                details TEXT NOT NULL DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS background_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                schedule TEXT,
                status TEXT NOT NULL DEFAULT 'IDLE',
                last_run_at TEXT,
                next_run_at TEXT,
                last_error TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_execution_tasks_status
            ON execution_tasks(status)
        """)
        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_company_events_unprocessed
            ON company_events(processed_at, id)
        """)
        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_audit_created_at
            ON system_audit_logs(created_at)
        """)

        connection.commit()
    finally:
        connection.close()


def seed_default_agents():
    agents = [
        ("CEO", "Coordinate company priorities and consolidate executive decisions."),
        ("CTO", "Own technical architecture, engineering quality and infrastructure."),
        ("CFO", "Own financial analysis, budgets, unit economics and reporting."),
        ("CMO", "Own positioning, marketing research and acquisition systems."),
        ("COO", "Own operational execution, workflows and delivery."),
        ("CPO", "Own customer problems, product requirements and prioritization."),
        ("CRO", "Own sales operations, lead qualification and pipeline execution."),
        ("CUSTOMER_SUCCESS", "Own onboarding, support, feedback and retention operations."),
        ("RESEARCH", "Discover markets, problems, competitors and technology signals."),
        ("LEGAL_COMPLIANCE", "Identify legal and compliance requirements and escalate qualified review."),
        ("SECURITY", "Identify security risks, permissions issues and vulnerabilities."),
        ("QA", "Own automated testing, regression checks and release quality."),
        ("CRITIC", "Challenge assumptions, plans and failure modes.")
    ]
    connection = get_connection()
    try:
        for role, objective in agents:
            connection.execute(
                """
                INSERT OR IGNORE INTO agent_registry
                (role, objective, instructions, capabilities, permissions, status)
                VALUES (?, ?, ?, ?, ?, 'OFFLINE')
                """,
                (role, objective, "", json.dumps([]), json.dumps([])),
            )
        connection.commit()
    finally:
        connection.close()
