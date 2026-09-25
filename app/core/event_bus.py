import json
from datetime import datetime, timezone
from app.core.database import get_connection
from app.core.runtime_schema import initialize_runtime_schema

class EventBus:
    def __init__(self):
        initialize_runtime_schema()

    def publish(self, event_type, payload=None, aggregate_type=None, aggregate_id=None):
        connection = get_connection()
        try:
            cur = connection.execute(
                "INSERT INTO company_events (event_type, aggregate_type, aggregate_id, payload) VALUES (?, ?, ?, ?)",
                (event_type, aggregate_type, str(aggregate_id) if aggregate_id is not None else None,
                 json.dumps(payload or {}, default=str))
            )
            connection.commit()
            return cur.lastrowid
        finally:
            connection.close()

    def pending(self, limit=50):
        connection = get_connection()
        try:
            rows = connection.execute(
                "SELECT * FROM company_events WHERE processed_at IS NULL ORDER BY id LIMIT ?",
                (limit,)
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            connection.close()

    def mark_processed(self, event_id):
        connection = get_connection()
        try:
            connection.execute(
                "UPDATE company_events SET processed_at=? WHERE id=?",
                (datetime.now(timezone.utc).isoformat(), event_id)
            )
            connection.commit()
        finally:
            connection.close()
