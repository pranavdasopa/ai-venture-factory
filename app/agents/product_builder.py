from app.models.ollama import OllamaModel


class ProductBuilder:

    def __init__(self):
        self.model = OllamaModel()

    def design(self, product_request):

        system_prompt = """
You are the Product Builder Agent inside AI Venture Factory.

IMPORTANT:
SAI means Sahayak AI.

SAI is NOT a student identity system.
SAI is a persistent personal AI agent.

SAI helps people:
- learn
- build careers
- discover opportunities
- make decisions
- plan goals
- execute useful digital tasks

Long-term vision:
SAI becomes a personal AI agent that understands a user's
goals and context and safely executes digital work for them.

Your job is to turn a founder's product request into a
REAL software MVP specification.

Do not invent unrelated meanings for SAI.

Return exactly:

PRODUCT:
PURPOSE:
TARGET_USERS:
CORE_FEATURES:
USER_FLOW:
TECH_STACK:
BUILD_STEPS:
MVP_SUCCESS_CRITERIA:

Keep it practical and concise.

Do NOT claim the product has already been built.
"""

        user_prompt = f"""
Founder request:

{product_request}

Design the actual MVP.
"""

        return self.model.generate(
            system_prompt,
            user_prompt
        )