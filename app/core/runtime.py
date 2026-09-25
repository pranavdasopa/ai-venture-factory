import os
import sqlite3
from datetime import datetime, timezone

from app.core.database import get_connection


def _check_database():
    try:
        connection = get_connection()
        connection.execute("SELECT 1").fetchone()
        tables = {
            row["name"]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        connection.close()
        return {
            "ok": True,
            "path_configured": True,
            "tables": sorted(tables),
        }
    except Exception as error:
        return {
            "ok": False,
            "path_configured": True,
            "error": str(error),
        }


def _check_model_configuration():
    provider = os.environ.get("AI_MODEL_PROVIDER", "gemini")
    configured = bool(os.environ.get("GEMINI_API_KEY"))
    return {
        "provider": provider,
        "configured": configured,
        "mode": "real" if configured else "blocked",
    }


def get_runtime_status():
    database = _check_database()
    model = _check_model_configuration()

    return {
        "company": "AI Venture Factory",
        "service": "company-core",
        "status": "ONLINE" if database["ok"] else "DEGRADED",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": database,
        "model": model,
        "truth_policy": {
            "synthetic_metrics": False,
            "unverified_claims": False,
            "status": "evidence-backed",
        },
    }
