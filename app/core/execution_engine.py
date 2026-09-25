import json
from datetime import datetime, timezone

from app.core.agent_registry import AgentRegistry
from app.core.database import get_connection
from app.core.runtime_schema import initialize_runtime_schema
from app.tools.registry import ToolRegistry


AUTO_STATUSES = {"todo", "READY", "PENDING"}
FINAL_STATUSES = {"COMPLETED", "FAILED", "BLOCKED"}


class ExecutionEngine:
    """Durable task execution spine.

    The engine owns state transitions, dependencies, approvals, agent status,
    execution attempts and audit records. It does not invent task completion:
    a task becomes COMPLETED only after its handler returns successfully.
    """

    def __init__(self, tool_registry=None, agent_registry=None):
        initialize_runtime_schema()
        self.tools = tool_registry or ToolRegistry()
        self.agents = agent_registry or AgentRegistry()

    def _now(self):
        return datetime.now(timezone.utc).isoformat()

    def _audit(self, actor_type, actor_id, action, resource_type, resource_id, status, details):
        connection = get_connection()
        try:
            connection.execute(
                """
                INSERT INTO system_audit_logs
                (actor_type, actor_id, action, resource_type, resource_id, status, details)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    actor_type, actor_id, action, resource_type, str(resource_id),
                    status, json.dumps(details, default=str),
                ),
            )
            connection.commit()
        finally:
            connection.close()

    def create_task(
        self, title, description, agent_role, priority="medium",
        depends_on=None, requires_approval=False, tool_name=None
    ):
        if not self.agents.get(agent_role):
            raise ValueError(f"Unknown agent role: {agent_role}")
        depends_on = depends_on or []
        now = self._now()
        connection = get_connection()
        try:
            cursor = connection.execute(
                """
                INSERT INTO execution_tasks
                (company_id, title, description, department, owner, agent_role,
                 priority, status, position, depends_on, requires_approval, tool_name,
                 created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'todo', 0, ?, ?, ?, ?, ?)
                """,
                (1, title, description, agent_role, agent_role, agent_role,
                 priority, json.dumps(depends_on), int(requires_approval), tool_name, now, now)
            )
            task_id = cursor.lastrowid
            connection.commit()
        finally:
            connection.close()
        self._audit("SYSTEM", "execution_engine", "TASK_CREATED", "task", task_id,
                    "SUCCESS", {"agent_role": agent_role, "tool_name": tool_name,
                                 "requires_approval": requires_approval})
        return task_id

    def _load_task(self, task_id):
        connection = get_connection()
        try:
            row = connection.execute(
                "SELECT * FROM execution_tasks WHERE id=?", (task_id,)
            ).fetchone()
            return dict(row) if row else None
        finally:
            connection.close()

    def _dependencies_complete(self, task):
        dependencies = json.loads(task.get("depends_on") or "[]")
        if not dependencies:
            return True
        connection = get_connection()
        try:
            placeholders = ",".join("?" for _ in dependencies)
            rows = connection.execute(
                f"SELECT id, status FROM execution_tasks WHERE id IN ({placeholders})",
                tuple(dependencies),
            ).fetchall()
            statuses = {row["id"]: row["status"] for row in rows}
            return all(statuses.get(dep) == "COMPLETED" for dep in dependencies)
        finally:
            connection.close()

    def approve(self, task_id, action="execute", decided_by="FOUNDER", reason=""):
        connection = get_connection()
        try:
            connection.execute(
                """
                INSERT INTO founder_approvals (task_id, action, status, decided_at, decided_by, reason)
                VALUES (?, ?, 'APPROVED', ?, ?, ?)
                ON CONFLICT(task_id, action) DO UPDATE SET
                    status='APPROVED', decided_at=excluded.decided_at,
                    decided_by=excluded.decided_by, reason=excluded.reason
                """,
                (task_id, action, self._now(), decided_by, reason),
            )
            connection.commit()
        finally:
            connection.close()
        self._audit(
            "FOUNDER", decided_by, "APPROVAL_GRANTED", "task", task_id,
            "SUCCESS", {"action": action, "reason": reason},
        )

    def _is_approved(self, task_id):
        connection = get_connection()
        try:
            row = connection.execute(
                """
                SELECT status FROM founder_approvals
                WHERE task_id=? AND action='execute'
                """,
                (task_id,),
            ).fetchone()
            return bool(row and row["status"] == "APPROVED")
        finally:
            connection.close()

    def _set_task(self, task_id, status, **fields):
        assignments = ["status=?", "updated_at=?"]
        values = [status, self._now()]
        for key, value in fields.items():
            assignments.append(f"{key}=?")
            values.append(value)
        values.append(task_id)
        connection = get_connection()
        try:
            connection.execute(
                f"UPDATE execution_tasks SET {', '.join(assignments)} WHERE id=?",
                values,
            )
            connection.commit()
        finally:
            connection.close()

    def execute_task(self, task_id, tool_name, payload=None, trigger="manual"):
        task = self._load_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} does not exist.")

        role = task.get("agent_role") or task.get("owner")
        if not role:
            raise ValueError("Task has no agent role.")

        if task["status"] in FINAL_STATUSES:
            return {"task_id": task_id, "status": task["status"], "message": "Task is final."}

        if not self._dependencies_complete(task):
            self._set_task(task_id, "BLOCKED", last_error="Dependencies are not complete.")
            self._audit("SYSTEM", "execution_engine", "TASK_BLOCKED", "task", task_id, "BLOCKED", {})
            return {"task_id": task_id, "status": "BLOCKED"}

        if int(task.get("requires_approval") or 0) and not self._is_approved(task_id):
            self._set_task(task_id, "REQUIRES_HUMAN_APPROVAL")
            self._audit("SYSTEM", "execution_engine", "APPROVAL_REQUIRED", "task", task_id, "BLOCKED", {})
            return {"task_id": task_id, "status": "REQUIRES_HUMAN_APPROVAL"}

        tool = self.tools.authorize(role, tool_name)
        now = self._now()

        connection = get_connection()
        try:
            cursor = connection.execute(
                """
                INSERT INTO execution_runs
                (task_id, status, trigger, started_at)
                VALUES (?, 'RUNNING', ?, ?)
                """,
                (task_id, trigger, now),
            )
            run_id = cursor.lastrowid
            attempt = connection.execute(
                """
                INSERT INTO execution_attempts
                (run_id, task_id, agent_role, status, tool_name, input_payload, started_at)
                VALUES (?, ?, ?, 'RUNNING', ?, ?, ?)
                """,
                (run_id, task_id, role, tool_name, json.dumps(payload or {}), now),
            )
            attempt_id = attempt.lastrowid
            connection.commit()
        finally:
            connection.close()

        self._set_task(task_id, "EXECUTING", started_at=now, last_error=None)
        self.agents.set_status(role, "WORKING", task_id)

        try:
            result = tool.handler(**(payload or {}))
            output = json.dumps(result, default=str)
            completed = self._now()
            connection = get_connection()
            try:
                connection.execute(
                    """
                    UPDATE execution_attempts
                    SET status='COMPLETED', output_payload=?, completed_at=?
                    WHERE id=?
                    """,
                    (output, completed, attempt_id),
                )
                connection.execute(
                    """
                    UPDATE execution_runs
                    SET status='COMPLETED', completed_at=?, result=?
                    WHERE id=?
                    """,
                    (completed, output, run_id),
                )
                connection.commit()
            finally:
                connection.close()

            self._set_task(task_id, "COMPLETED", completed_at=completed, result=output)
            self.agents.set_status(role, "IDLE", None)
            self._audit(
                "AGENT", role, "TASK_COMPLETED", "task", task_id,
                "SUCCESS", {"run_id": run_id, "tool": tool_name},
            )
            return {"task_id": task_id, "run_id": run_id, "status": "COMPLETED", "result": result}
        except Exception as error:
            failed = self._now()
            message = str(error)
            connection = get_connection()
            try:
                connection.execute(
                    """
                    UPDATE execution_attempts
                    SET status='FAILED', error=?, completed_at=?
                    WHERE id=?
                    """,
                    (message, failed, attempt_id),
                )
                connection.execute(
                    """
                    UPDATE execution_runs
                    SET status='FAILED', completed_at=?, error=?
                    WHERE id=?
                    """,
                    (failed, message, run_id),
                )
                connection.commit()
            finally:
                connection.close()

            self._set_task(task_id, "FAILED", completed_at=failed, last_error=message)
            self.agents.set_status(role, "ERROR", task_id)
            self._audit(
                "AGENT", role, "TASK_FAILED", "task", task_id,
                "ERROR", {"run_id": run_id, "tool": tool_name, "error": message},
            )
            return {"task_id": task_id, "run_id": run_id, "status": "FAILED", "error": message}

    def get_pending_tasks(self):
        connection = get_connection()
        try:
            rows = connection.execute(
                """
                SELECT * FROM execution_tasks
                WHERE status IN ('todo', 'READY', 'PENDING')
                ORDER BY priority='high' DESC, id ASC
                """
            ).fetchall()
            return [dict(row) for row in rows]
        finally:
            connection.close()
