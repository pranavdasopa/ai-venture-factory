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

Your job is to transform a raw startup idea into a practical,
structured company blueprint that can be used by other AI agents.

Think like a combination of:

- elite startup founder
- product strategist
- market researcher
- CTO
- CFO
- growth strategist
- operations leader

Be realistic and evidence-aware.

Do not invent specific market statistics, customer contracts,
revenue numbers, or verified competitor facts.

If something is uncertain, describe it as a hypothesis.

IMPORTANT OUTPUT RULES:

Return ONLY ONE valid JSON object.

The response MUST begin with {
and MUST end with }.

Do not write anything before the JSON.

Do not write anything after the JSON.

Do not use markdown.

Do not use ```json.

Do not use ```.

Do not include comments.

Do not return multiple JSON objects.

Do not include trailing commas.

All JSON strings must use double quotes.

The JSON must contain exactly these top-level fields:

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

FIELD REQUIREMENTS:

company_name:
A concise potential company name.

industry:
The primary industry.

problem:
The specific customer problem.

target_customer:
The ideal first customer.

proposed_solution:
What the company will build.

value_proposition:
Why the customer should care.

market_hypothesis:
A testable hypothesis about the market.
Do not invent precise market-size numbers.

competitors:
An array of known or plausible competing solutions.
Do not claim unsupported facts.

business_model:
How the company could make money.

pricing_hypothesis:
An initial pricing hypothesis, clearly treated as a hypothesis.

mvp_scope:
An array of the smallest useful MVP capabilities.

technical_architecture:
A concise technical architecture for the MVP.

technology_stack:
An array of technologies appropriate for the MVP.

risks:
An array of important business, technical and market risks.

validation_experiments:
An array of experiments that can test the most important assumptions.

next_actions:
An array of immediate actions for the founder.

execution_tasks:
An array containing approximately 8-12 actionable tasks.

Each execution task MUST have exactly these fields:

{
  "title": "",
  "description": "",
  "department": "",
  "priority": ""
}

Allowed department values:

"Strategy"
"Product"
"Engineering"
"Design"
"Marketing"
"Sales"
"Operations"
"Finance"

Allowed priority values:

"high"
"medium"
"low"

Make execution tasks concrete and useful.

The blueprint must be suitable for actually starting an MVP.

Avoid generic motivational advice.

Prioritize customer validation, MVP development,
distribution and measurable execution.
"""

        user_prompt = f"""
Build a company blueprint for this startup idea:

{idea}
"""

        raw_response = self.model.generate(
            system_prompt,
            user_prompt
        )

        return self._parse_response(raw_response)


    def _parse_response(self, raw_response):

        if not raw_response:
            raise RuntimeError(
                "The AI returned an empty company blueprint."
            )

        text = raw_response.strip()

        # Remove accidental markdown fences.
        text = re.sub(
            r"^```(?:json)?\s*",
            "",
            text,
            flags=re.IGNORECASE
        )

        text = re.sub(
            r"\s*```$",
            "",
            text
        )

        # First attempt: parse the entire response.
        try:

            data = json.loads(text)

        except json.JSONDecodeError:

            # Second attempt: recover a JSON object
            # if the model accidentally added surrounding text.
            start = text.find("{")
            end = text.rfind("}")

            if start == -1 or end == -1 or end <= start:

                raise RuntimeError(
                    "Gemini returned invalid JSON for the "
                    "company blueprint."
                )

            candidate = text[start:end + 1]

            try:

                data = json.loads(candidate)

            except json.JSONDecodeError as error:

                raise RuntimeError(
                    "Gemini returned malformed company "
                    "blueprint JSON."
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


            required_task_fields = [

                "title",
                "description",
                "department",
                "priority"

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