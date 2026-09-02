import json
from app.models.ollama import OllamaModel


class ExecutionAgent:

    def __init__(self):
        self.model = OllamaModel()

    def create_plan(self, company, blueprint):

        if not company:
            raise ValueError("Company information is required.")

        if not blueprint:
            raise ValueError("Company blueprint is required.")

        system_prompt = """
You are the Execution Orchestrator inside AI Venture Factory.

Your job is to transform a startup company blueprint into a
practical execution plan.

You coordinate these departments:

Strategy
Product
Engineering
Design
Marketing
Sales
Operations
Finance

Think like an experienced startup COO working with a CTO,
product leader, growth leader and founder.

The goal is execution, not inspiration.

Create concrete tasks that a small startup team can actually execute.

Important:

- Do not claim that anything has already been completed.
- Do not invent customers, contracts, revenue or partnerships.
- Separate planning from execution.
- Technical tasks should be specific enough for an engineer or coding
  agent to implement.
- Marketing tasks should produce concrete assets.
- Sales tasks should produce concrete outreach or sales infrastructure.
- Tasks should have logical dependencies.
- Start with validation and MVP construction before scaling.
- Keep the first execution plan focused.

Return ONLY valid JSON.

Do not use markdown.
Do not use ```json.
Do not add explanations before or after the JSON.

Return exactly this structure:

{
  "execution_strategy": "",
  "immediate_goal": "",
  "tasks": [
    {
      "title": "",
      "description": "",
      "department": "",
      "priority": "",
      "depends_on": []
    }
  ]
}

Priority must be exactly one of:

"high"
"medium"
"low"

Create approximately 10-20 tasks.

The first tasks should normally establish:

1. customer/problem validation
2. product requirements
3. MVP architecture
4. development
5. testing
6. deployment
7. initial marketing
8. sales preparation
9. customer acquisition
10. feedback and iteration
"""

        user_prompt = f"""
COMPANY:

{json.dumps(company, indent=2)}

COMPANY BLUEPRINT:

{json.dumps(blueprint, indent=2)}

Create the initial execution plan.
"""

        raw_response = self.model.generate(
            system_prompt,
            user_prompt
        )

        return self._parse_response(raw_response)

    def _parse_response(self, raw_response):

        if not raw_response:
            raise RuntimeError(
                "The AI returned an empty execution plan."
            )

        text = raw_response.strip()

        if text.startswith("```"):
            lines = text.splitlines()

            if lines and lines[0].strip().startswith("```"):
                lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            text = "\n".join(lines).strip()

        try:
            data = json.loads(text)

        except json.JSONDecodeError as error:

            start = text.find("{")
            end = text.rfind("}")

            if start == -1 or end == -1 or end <= start:
                raise RuntimeError(
                    "Gemini returned invalid execution plan JSON."
                ) from error

            try:
                data = json.loads(
                    text[start:end + 1]
                )

            except json.JSONDecodeError as second_error:

                raise RuntimeError(
                    "Gemini returned malformed execution plan JSON."
                ) from second_error

        self._validate(data)

        return data

    def _validate(self, data):

        if not isinstance(data, dict):
            raise RuntimeError(
                "Execution plan must be a JSON object."
            )

        required = [
            "execution_strategy",
            "immediate_goal",
            "tasks"
        ]

        for field in required:

            if field not in data:
                raise RuntimeError(
                    "Execution plan is missing field: "
                    + field
                )

        if not isinstance(data["tasks"], list):
            raise RuntimeError(
                "Execution plan tasks must be a list."
            )

        for task in data["tasks"]:

            if not isinstance(task, dict):
                raise RuntimeError(
                    "Each execution task must be an object."
                )

            required_task_fields = [
                "title",
                "description",
                "department",
                "priority",
                "depends_on"
            ]

            for field in required_task_fields:

                if field not in task:
                    raise RuntimeError(
                        "Execution task is missing field: "
                        + field
                    )

            if task["priority"] not in [
                "high",
                "medium",
                "low"
            ]:
                task["priority"] = "medium"

            if not isinstance(
                task["depends_on"],
                list
            ):
                task["depends_on"] = []