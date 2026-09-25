from app.models.ollama import OllamaModel
from app.agents.memory_agent import MemoryAgent


class SAI:
    """Founder-facing AI interface backed by the configured model provider."""

    def __init__(self):
        self.model = OllamaModel()
        self.memory = MemoryAgent()

    def chat(self, user_prompt):
        if not str(user_prompt).strip():
            raise ValueError("User prompt is required.")

        memory = self.memory.get_memory()
        context = f"""
USER PROFILE:
{memory["profile"]}

USER GOALS:
{memory["goals"]}

IMPORTANT FACTS:
{memory["facts"]}
"""

        system_prompt = f"""
You are the founder-facing AI interface for AI Venture Factory.

You may reason about company strategy, tasks, opportunities, products and
execution plans, but you must distinguish plans from completed actions.

Never invent customers, revenue, employees, agents, uptime, cash, facilities,
or other business metrics. If evidence is unavailable, say so explicitly.

When the founder asks you to perform an action, explain what can be executed
through the available company tools and do not claim execution until evidence
is returned by the execution layer.

Use relevant persistent memory when answering.

{context}
"""
        return self.model.generate(system_prompt, str(user_prompt))
