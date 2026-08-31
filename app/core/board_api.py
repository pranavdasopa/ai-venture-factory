from app.models.ollama import OllamaModel


class BoardAPI:

    def __init__(self):
        self.model = OllamaModel()

    def analyze(self, idea):

        departments = {
            "CMO": """
Analyze the customer and market side.

Focus on:
- Who has the problem?
- Is the problem meaningful?
- What must be validated?
- Do not invent market statistics.
""",

            "CTO": """
Analyze the technical side.

Focus on:
- Is an initial version technically feasible?
- What is the smallest useful product?
- What are the major technical risks?
- Do not assume technology that has not been tested.
""",

            "CFO": """
Analyze the financial side.

Focus on:
- Who could pay?
- What value could justify payment?
- What costs could matter?
- What financial assumptions are unknown?
- Do not invent revenue or customer numbers.
""",

            "CRITIC": """
Attack the idea.

Find:
- unsupported assumptions
- missing evidence
- customer risks
- technical risks
- business risks

Be skeptical.
"""
        }

        results = {}

        for department, instructions in departments.items():

            prompt = f"""
You are the {department} of AI Venture Factory.

STARTUP IDEA:
{idea}

{instructions}

Return a concise analysis.
Clearly distinguish facts from assumptions.
"""

            results[department] = self.model.generate(
                system_prompt=f"You are the {department} of AI Venture Factory.",
                user_prompt=prompt,
            )

        return results


if __name__ == "__main__":

    board = BoardAPI()

    idea = """
    A SaaS product that helps small businesses
    automate one repetitive administrative task.
    """

    results = board.analyze(idea)

    print("=" * 60)
    print("AI VENTURE FACTORY — BOARD TEST")
    print("=" * 60)

    for department, result in results.items():

        print()
        print(department)
        print("-" * 60)
        print(result)

    print()
    print("=" * 60)
    print("BOARD TEST COMPLETE")
    print("=" * 60)