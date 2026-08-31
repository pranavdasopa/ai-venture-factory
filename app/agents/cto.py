from app.models.base import ModelProvider


class CTO:

    name = "AI CTO"

    role = """
You are the Chief Technology Officer of AI Venture Factory.

Your responsibilities:

1. Evaluate technical feasibility.
2. Design software architecture.
3. Lead engineering.
4. Evaluate technology choices.
5. Identify technical risks.
6. Estimate development complexity.
7. Maintain engineering quality.
8. Build scalable technology.

You report to the CEO.
"""

    def __init__(self, model: ModelProvider):
        self.model = model

    def analyze(self, request: str) -> str:

        return self.model.generate(
            system_prompt=self.role,
            user_prompt=request,
        )