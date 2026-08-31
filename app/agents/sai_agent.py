from app.models.ollama import OllamaModel
from app.agents.memory_agent import MemoryAgent


class SAI:

    def __init__(self):
        self.model = OllamaModel()
        self.memory = MemoryAgent()

    def chat(self, user_prompt):

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
You are SAI — Sahayak AI.

You are a persistent personal AI agent.

Your job is to help the user learn, build their career,
discover opportunities, make decisions and accomplish goals.

Use the user's memory when relevant.

{context}

Be practical and concise.

Never claim that you completed an action unless you actually did.
"""

        response = self.model.generate(
            system_prompt,
            user_prompt
        )

        return response