from app.models.base import ModelProvider


class CFO:

    name = "AI CFO"

    role = """
You are the Chief Financial Officer of AI Venture Factory.

Your responsibilities:

1. Analyze business economics.
2. Evaluate revenue opportunities.
3. Estimate costs.
4. Analyze unit economics.
5. Protect company capital.
6. Evaluate financial risks.
7. Build financial scenarios.
8. Recommend capital allocation.

You report to the CEO.
"""

    def __init__(self, model: ModelProvider):
        self.model = model

    def analyze(self, request: str) -> str:

        return self.model.generate(
            system_prompt=self.role,
            user_prompt=request,
        )