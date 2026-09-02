import json
import re

from app.models.ollama import OllamaModel


class CompanyBuilderAgent:

    def __init__(self):
        self.model = OllamaModel()

    def build(self, idea):

        idea = str(idea or "").strip()

        if not idea:
            raise ValueError("Startup idea is required.")

        if len(idea) < 10:
            raise ValueError(
                "Startup idea is too short. "
                "Please describe the idea in more detail."
            )

        system_prompt = """
You are the Company Strategy Agent inside AI Venture Factory.

Transform the startup idea into a practical company blueprint.

Think like:
- startup founder
- product strategist
- CTO
- CFO
- marketing strategist
- sales strategist
- operations leader

Be realistic. Do not invent specific market statistics,
customer contracts, revenue numbers, or facts.

CRITICAL OUTPUT RULES:

Return ONLY one valid JSON object.

Do not use markdown.
Do not use ```json.
Do not write explanations before or after the JSON.

Keep every string concise.

The JSON must have exactly these top-level fields:

{
  "company_name": "",
  "industry": "",
  "problem": "",
  "target_customer": "",
  "proposed_solution": "",
  "value_proposition": "",
  "market_hypothesis": "",
  "competitors": [],
  "business_model": "",
  "pricing_hypothesis": "",
  "mvp_scope": [],
  "technical_architecture": "",
  "technology_stack": [],
  "risks": [],
  "validation_experiments": [],
  "next_actions": [],
  "execution_tasks": []
}

execution_tasks must contain 8 useful tasks.

Every task must have exactly:

{
  "title": "",
  "description": "",
  "department": "",
  "priority": ""
}

Allowed priority values:

"high"
"medium"
"low"

Allowed departments:

Strategy
Product
Engineering
Design
Marketing
Sales
Operations
Finance

Keep arrays concise.

The result must be valid JSON that can be parsed directly
by Python json.loads().
"""

        user_prompt = f"""
Create the company blueprint for:

{idea}
"""

        raw_response = self.model.generate(
            system_prompt,
            user_prompt
        )

        return self._parse_response(raw_response)

    def _extract_json(self, text):

        text = text.strip()

        # Remove markdown fences if the model ignored the instruction.
        text = re.sub(
            r"```(?:json)?",
            "",
            text,
            flags=re.IGNORECASE
        )

        text = text.replace("```", "").strip()

        # Find the outermost JSON object.
        start = text.find("{")

        if start == -1:
            return None

        depth = 0
        in_string = False
        escaped = False

        for index in range(start, len(text)):

            char = text[index]

            if in_string:

                if escaped:
                    escaped = False

                elif char == "\\":
                    escaped = True

                elif char == '"':
                    in_string = False

                continue

            if char == '"':
                in_string = True

            elif char == "{":
                depth += 1

            elif char == "}":

                depth -= 1

                if depth == 0:
                    return text[start:index + 1]

        return None

    def _parse_response(self, raw_response):

        if not raw_response:
            raise RuntimeError(
                "The AI returned an empty company blueprint."
            )

        text = str(raw_response).strip()

        json_text = self._extract_json(text)

        if not json_text:

            preview = text[:500].replace("\n", " ")

            raise RuntimeError(
                "Gemini returned incomplete company blueprint JSON. "
                f"Response preview: {preview}"
            )

        try:

            data = json.loads(json_text)

        except json.JSONDecodeError as error:

            preview = text[:500].replace("\n", " ")

            raise RuntimeError(
                "Gemini returned malformed company blueprint JSON. "
                f"Response preview: {preview}"
            ) from error

        self._validate(data)

        return data

    def _validate(self, data):

        required_fields = [
            "company_name",
            "industry",
            "problem",
            "target_customer",
            "proposed_solution",
            "value_proposition",
            "market_hypothesis",
            "competitors",
            "business_model",
            "pricing_hypothesis",
            "mvp_scope",
            "technical_architecture",
            "technology_stack",
            "risks",
            "validation_experiments",
            "next_actions",
            "execution_tasks"
        ]

        if not isinstance(data, dict):

            raise RuntimeError(
                "Company blueprint must be a JSON object."
            )

        missing = [
            field
            for field in required_fields
            if field not in data
        ]

        if missing:

            raise RuntimeError(
                "Company blueprint is missing fields: "
                + ", ".join(missing)
            )

        list_fields = [
            "competitors",
            "mvp_scope",
            "technology_stack",
            "risks",
            "validation_experiments",
            "next_actions",
            "execution_tasks"
        ]

        for field in list_fields:

            if not isinstance(data[field], list):

                raise RuntimeError(
                    f"Blueprint field '{field}' must be a list."
                )

        for task in data["execution_tasks"]:

            if not isinstance(task, dict):

                raise RuntimeError(
                    "Each execution task must be an object."
                )

            for field in [
                "title",
                "description",
                "department",
                "priority"
            ]:

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