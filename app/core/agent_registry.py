from datetime import datetime, timezone
import json

from app.core.database import get_connection
from app.core.runtime_schema import initialize_runtime_schema, seed_default_agents


class AgentRegistry:
    def __init__(self):
        initialize_runtime_schema()
        seed_default_agents()

    def set_status(self, role, status, current_task_id=None, model_provider=None, model_name=None):
        now = datetime.now(timezone.utc).isoformat()
        connection = get_connection()
        try:
            connection.execute(
                """
                UPDATE agent_registry
                SET status=?, current_task_id=?, model_provider=COALESCE(?, model_provider),
                    model_name=COALESCE(?, model_name), last_heartbeat=?, updated_at=?
                WHERE role=?
                """,
                (status, current_task_id, model_provider, model_name, now, now, role),
            )
            connection.commit()
        finally:
            connection.close()

    def get(self, role):
        connection = get_connection()
        try:
            row = connection.execute(
                "SELECT * FROM agent_registry WHERE role=?", (role,)
            ).fetchone()
            return dict(row) if row else None
        finally:
            connection.close()

    def list_agents(self):
        connection = get_connection()
        try:
            return [dict(row) for row in connection.execute(
                "SELECT * FROM agent_registry ORDER BY role"
            ).fetchall()]
        finally:
            connection.close()
