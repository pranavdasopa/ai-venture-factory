from app.models.ollama import OllamaModel
from app.core.memory import CompanyMemory


class ExecutiveBoard:

    def __init__(self):

        self.model = OllamaModel()
        self.memory = CompanyMemory()

    def ask(self, role, task, context=""):

        prompt = f"""
You are the {role} of AI Venture Factory.

BUSINESS IDEA:
Build a SaaS product that helps small businesses
automate one repetitive administrative task.

CONTEXT FROM OTHER EXECUTIVES:
{context}

YOUR TASK:
{task}

RULES:
- Be concise.
- Do not invent facts.
- Do not invent statistics.
- Do not pretend assumptions are evidence.
- If something is unknown, say UNKNOWN.
- Challenge weak assumptions.

Return:

ANSWER:
RISK:
ACTION:
"""

        return self.model.generate(
            system_prompt=f"You are a careful {role}.",
            user_prompt=prompt,
        )

    def run_meeting(self):

        print()
        print("=" * 60)
        print("AI VENTURE FACTORY — EXECUTIVE BOARD")
        print("=" * 60)

        # CMO
        cmo = self.ask(
            "CMO",
            "Identify the likely customer, their possible problem, "
            "and what must be validated.",
        )

        print()
        print("CMO")
        print("-" * 60)
        print(cmo)

        self.memory.remember(
            "executive_analysis",
            "CMO Analysis",
            cmo,
        )

        # CTO receives CMO analysis
        cto = self.ask(
            "CTO",
            "Evaluate the technical challenge based on the CMO analysis.",
            cmo,
        )

        print()
        print("CTO")
        print("-" * 60)
        print(cto)

        self.memory.remember(
            "executive_analysis",
            "CTO Analysis",
            cto,
        )

        # CFO receives CMO + CTO
        cfo_context = f"""
CMO:
{cmo}

CTO:
{cto}
"""

        cfo = self.ask(
            "CFO",
            "Evaluate a possible business model and the biggest "
            "financial uncertainty.",
            cfo_context,
        )

        print()
        print("CFO")
        print("-" * 60)
        print(cfo)

        self.memory.remember(
            "executive_analysis",
            "CFO Analysis",
            cfo,
        )

        # Critic receives all previous analysis
        critic_context = f"""
CMO:
{cmo}

CTO:
{cto}

CFO:
{cfo}
"""

        critic = self.ask(
            "CRITIC",
            "Attack the idea. Identify the most dangerous "
            "assumption that must be tested.",
            critic_context,
        )

        print()
        print("CRITIC")
        print("-" * 60)
        print(critic)

        self.memory.remember(
            "executive_analysis",
            "Critic Analysis",
            critic,
        )

        # CEO receives the complete discussion
        ceo_context = f"""
CMO:
{cmo}

CTO:
{cto}

CFO:
{cfo}

CRITIC:
{critic}
"""

        ceo = self.ask(
            "CEO",
            """
Make the final preliminary recommendation.

Choose exactly one:

BUILD
TEST
REJECT

Then give one reason and one next action.

Remember:
This is only a preliminary decision.
No real customer evidence exists yet.
""",
            ceo_context,
        )

        print()
        print("CEO")
        print("-" * 60)
        print(ceo)

        self.memory.remember(
            "decision",
            "CEO Preliminary Decision",
            ceo,
        )

        print()
        print("=" * 60)
        print("MEETING COMPLETE")
        print("=" * 60)


if __name__ == "__main__":

    board = ExecutiveBoard()
    board.run_meeting()