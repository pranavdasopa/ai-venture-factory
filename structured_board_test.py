from app.models.ollama import OllamaModel


model = OllamaModel()


IDEA = """
A SaaS product that helps small businesses automate
one repetitive administrative task.
"""


def ask(role, task):

    print()
    print("=" * 60)
    print(role.upper())
    print("=" * 60)

    prompt = f"""
You are the {role} of a startup.

Business idea:
{IDEA}

TASK:
{task}

RULES:
- Use only information explicitly provided above.
- Do not invent statistics.
- Do not invent customers.
- Do not invent competitors.
- Do not invent technology.
- Do not claim something is evidence unless it was provided.
- If something is unknown, write UNKNOWN.
- Be extremely concise.

Answer in exactly 3 lines:

ANSWER: 
RISK:
ACTION:
"""

    return model.generate(
        system_prompt=f"You are a careful {role}.",
        user_prompt=prompt,
    )


agents = [

    (
        "CMO",
        "Who is the most likely customer and what problem might they have?"
    ),

    (
        "CTO",
        "What is the main technical challenge in building this product?"
    ),

    (
        "CFO",
        "What is one possible way this product could make money?"
    ),

    (
        "CRITIC",
        "What is the single biggest assumption we must test before building?"
    ),
]


for role, task in agents:
    print(ask(role, task))