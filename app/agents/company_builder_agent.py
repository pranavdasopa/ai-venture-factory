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

IMPORTANT OUTPUT RULES:

1. Return EXACTLY ONE JSON OBJECT.
2. The first character of your response MUST be {.
3. The last character of your response MUST be }.
4. Do NOT write anything before or after the JSON.
5. Do NOT use markdown.
6. Do NOT use ```json.
7. Use valid JSON syntax.
8. Use double quotes for every JSON key and string.
9. Never use trailing commas.
10. Do not include comments inside JSON.
11. Do not invent specific market statistics, contracts,
revenue numbers, or competitor facts unless clearly marked
as hypotheses.

The JSON must have exactly these fields:

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

execution_tasks must contain approximately 8-15 objects.

Each execution task MUST contain:

{
  "title": "",
  "description": "",
  "department": "",
  "priority": ""
}

Priority MUST be exactly one of:

"high"
"medium"
"low"

Departments may include:

Strategy
Product
Engineering
Design
Marketing
Sales
Operations
Finance

The blueprint must be practical enough to start an MVP.
"""

        user_prompt = f"""
Build the company blueprint for this startup idea:

{idea}

Return ONLY the JSON object.
"""

        raw_response = self.model.generate(
            system_prompt,
            user_prompt
        )

        return self._parse_response(raw_response)

    def _extract_json(self, text):

        if not text:
            return None

        text = text.strip()

        # Remove common markdown fences.
        text = re.sub(
            r"```json\s*",
            "",
            text,
            flags=re.IGNORECASE
        )

        text = re.sub(
            r"```\s*",
            "",
            text
        )

        text = text.strip()

        # First attempt: entire response.
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Second attempt:
        # Find the first JSON object and use
        # the matching closing brace.
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

                    candidate = text[
                        start:index + 1
                    ]

                    try:
                        return json.loads(candidate)
                    except json.JSONDecodeError:
                        return None

        return None

    def _parse_response(self, raw_response):

        if not raw_response:
            raise RuntimeError(
                "The AI returned an empty company blueprint."
            )

        data = self._extract_json(raw_response)

        if data is None:

            # Give a useful diagnostic without dumping
            # potentially huge model output.
            preview = str(raw_response).strip()

            if len(preview) > 500:
                preview = preview[:500] + "..."

            raise RuntimeError(
                "Gemini returned malformed company blueprint JSON. "
                "Response preview: "
                + preview
            )

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