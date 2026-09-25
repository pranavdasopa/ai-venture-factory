from app.core.runtime_schema import initialize_runtime_schema, seed_default_agents
from app.core.supervisor import CompanySupervisor

class CompanyRuntime:
    def __init__(self):
        initialize_runtime_schema()
        seed_default_agents()
        self.supervisor = CompanySupervisor()

    def status(self):
        heartbeat = self.supervisor.heartbeat()
        return {
            "status": "ONLINE",
            "runtime": "READY",
            **heartbeat,
        }

    def run_forever(self, interval_seconds=5):
        return self.supervisor.run_forever(interval_seconds)
