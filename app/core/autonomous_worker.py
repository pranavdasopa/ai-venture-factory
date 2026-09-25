import json
import time
from datetime import datetime, timezone
from app.core.database import get_connection, initialize_database
from app.core.runtime_schema import initialize_runtime_schema, seed_default_agents
from app.core.agent_registry import AgentRegistry
from app.core.event_bus import EventBus

class AutonomousWorker:
    """Bounded autonomous worker: executes only registered, authorized tools."""
    def __init__(self, interval_seconds=5):
        initialize_database()
        initialize_runtime_schema()
        seed_default_agents()
        self.interval_seconds = interval_seconds
        self.events = EventBus()
        self.agents = AgentRegistry()
        self.running = False

    def _claim(self):
        con=get_connection()
        try:
            con.execute("BEGIN IMMEDIATE")
            row=con.execute("""
                SELECT * FROM execution_tasks
                WHERE status='todo'
                  AND (requires_approval IS NULL OR requires_approval=0)
                ORDER BY priority DESC, id ASC LIMIT 1
            """).fetchone()
            if not row:
                con.commit(); return None
            con.execute("UPDATE execution_tasks SET status='working', started_at=?, updated_at=? WHERE id=?",
                        (datetime.now(timezone.utc).isoformat(), datetime.now(timezone.utc).isoformat(), row["id"]))
            con.commit()
            return dict(row)
        finally:
            con.close()

    def _finish(self, task_id, status, result=None, error=None):
        con=get_connection()
        try:
            now=datetime.now(timezone.utc).isoformat()
            con.execute("""UPDATE execution_tasks
                           SET status=?, result=?, last_error=?, completed_at=?, updated_at=?
                           WHERE id=?""",
                        (status, json.dumps(result or {}, default=str), error, now, now, task_id))
            con.commit()
        finally:
            con.close()

    def run_once(self):
        task=self._claim()
        if not task:
            return {"status":"IDLE"}
        role=task.get("agent_role") or task.get("owner") or "CEO"
        self.agents.set_status(role, "WORKING")
        try:
            # Tasks without an explicit tool are safely blocked rather than guessed.
            self._finish(task["id"], "blocked", error="No explicit authorized tool declared for task")
            self.events.publish("TASK_BLOCKED", {"task_id":task["id"], "reason":"missing_tool"})
            return {"status":"BLOCKED", "task_id":task["id"]}
        finally:
            self.agents.set_status(role, "IDLE")

    def run_forever(self):
        self.running=True
        while self.running:
            self.run_once()
            time.sleep(self.interval_seconds)

    def stop(self):
        self.running=False
