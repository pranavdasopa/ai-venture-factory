import time
from app.core.agent_registry import AgentRegistry
from app.core.event_bus import EventBus
from app.core.execution_engine import ExecutionEngine

class CompanySupervisor:
    def __init__(self, engine=None):
        self.engine = engine or ExecutionEngine()
        self.events = EventBus()
        self.agents = AgentRegistry()
        self.running = False

    def heartbeat(self):
        return {
            "company": "AI Venture Factory",
            "running": self.running,
            "pending_tasks": len(self.engine.get_pending_tasks()),
            "pending_events": len(self.events.pending()),
            "agents": self.agents.list_agents(),
        }

    def run_once(self):
        self.running = True
        pending = self.engine.get_pending_tasks()
        # Task execution is deliberately explicit until a task declares a tool.
        # This supervisor never invents a tool or falsely marks a task complete.
        return {
            "status": "HEARTBEAT",
            "pending_tasks": len(pending),
            "pending_events": len(self.events.pending()),
        }

    def run_forever(self, interval_seconds=5):
        self.running = True
        while self.running:
            self.run_once()
            time.sleep(interval_seconds)

    def stop(self):
        self.running = False
