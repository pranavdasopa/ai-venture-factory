import tempfile
from pathlib import Path
import os

import pytest


def test_execution_engine_records_success(monkeypatch):
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "company.db"

        import app.core.database as database
        monkeypatch.setattr(database, "DATABASE_PATH", db)

        from app.core.execution_engine import ExecutionEngine
        from app.core.agent_registry import AgentRegistry
        from app.tools.registry import ToolRegistry

        tools = ToolRegistry()
        tools.register(
            "test.echo",
            lambda value=None: {"echo": value},
            {"QA"},
        )

        engine = ExecutionEngine(
            tool_registry=tools,
            agent_registry=AgentRegistry(),
        )
        task_id = engine.create_task(
            "Test execution",
            "Verify durable execution state.",
            "QA",
        )

        result = engine.execute_task(
            task_id,
            "test.echo",
            {"value": "ok"},
        )

        assert result["status"] == "COMPLETED"

        task = engine._load_task(task_id)
        assert task["status"] == "COMPLETED"
        assert '"echo": "ok"' in task["result"]

def test_sensitive_task_requires_approval(monkeypatch):
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "company.db"

        import app.core.database as database
        monkeypatch.setattr(database, "DATABASE_PATH", db)

        from app.core.execution_engine import ExecutionEngine
        from app.core.agent_registry import AgentRegistry
        from app.tools.registry import ToolRegistry

        tools = ToolRegistry()
        tools.register("test.action", lambda: {"ok": True}, {"CTO"})

        engine = ExecutionEngine(
            tool_registry=tools,
            agent_registry=AgentRegistry(),
        )
        task_id = engine.create_task(
            "Approval test",
            "Must not execute without founder approval.",
            "CTO",
            requires_approval=True,
        )

        blocked = engine.execute_task(task_id, "test.action")
        assert blocked["status"] == "REQUIRES_HUMAN_APPROVAL"

        engine.approve(task_id)
        completed = engine.execute_task(task_id, "test.action")
        assert completed["status"] == "COMPLETED"
