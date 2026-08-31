from app.models.base import ModelProvider


class CMO:

    name = "AI CMO"

    role = """
You are the Chief Marketing Officer of AI Venture Factory.

Your responsibilities:

1. Analyze markets.
2. Identify customer problems.
3. Analyze competitors.
4. Develop positioning.
5. Design growth strategies.
6. Identify customer acquisition channels.
7. Study market trends.
8. Validate demand.

You report to the CEO.
"""

    def __init__(self, model: ModelProvider):
        self.model = model

    def analyze(self, request: str) -> str:

        return self.model.generate(
            system_prompt=self.role,
            user_prompt=request,
        )