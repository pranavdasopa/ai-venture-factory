from app.models.base import ModelProvider
from app.memory.memory import CompanyMemory
from app.core.tasks import TaskManager
from app.core.decisions import DecisionManager


class CEO:

    name = "AI CEO"

    role = """
You are the Chief Executive Officer of AI Venture Factory.

Your responsibilities:

1. Set company priorities.
2. Evaluate business opportunities.
3. Coordinate departments.
4. Make strategic recommendations.
5. Allocate tasks.
6. Identify risks.
7. Challenge weak assumptions.
8. Focus on real customer value.
9. Protect company resources.
10. Escalate important decisions to the human founder.

You do NOT have unlimited authority.

The human founder is the final decision-maker.
"""

    mission = """
Build a technology company capable of repeatedly discovering,
validating, building, launching and scaling valuable products.

Optimize for:

- customer value
- technological advantage
- speed of experimentation
- capital efficiency
- sustainable revenue
- long-term scalability
"""

    def __init__(self, model: ModelProvider):

        self.model = model
        self.memory = CompanyMemory()
        self.tasks = TaskManager()
        self.decisions = DecisionManager()

    def remember(self, category: str, content: str):

        self.memory.remember(category, content)

    def recall(self, category: str | None = None, limit: int = 20):

        return self.memory.recall(category, limit)

    def create_task(
        self,
        title: str,
        description: str,
        owner: str,
        priority: str = "medium",
    ):

        return self.tasks.create(
            title,
            description,
            owner,
            priority,
        )

    def create_decision(
        self,
        title: str,
        description: str,
    ):

        return self.decisions.create(
            title,
            description,
        )

    def think(self, request: str) -> str:

        memories = self.recall(limit=10)

        memory_text = "\n".join(
            f"[{category}] {content}"
            for _, category, content, _ in memories
        )

        prompt = f"""
COMPANY MEMORY:

{memory_text}

CURRENT REQUEST:

{request}

Use relevant company memory when responding.
Do not invent facts that are not supported by the available information.
"""

        return self.model.generate(
            system_prompt=self.role + "\n" + self.mission,
            user_prompt=prompt,
        )