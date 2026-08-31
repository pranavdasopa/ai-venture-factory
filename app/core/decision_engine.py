from app.models.ollama import OllamaModel


class DecisionEngine:

    def __init__(self):
        self.model = OllamaModel()

    def decide(self, idea, analysis):

        prompt = f"""
You are the decision engine of AI Venture Factory.

IDEA:
{idea}

EXECUTIVE ANALYSIS:
{analysis}

Your job is to decide whether the company should TEST,
BUILD, or REJECT this idea.

Rules:

1. TEST if important customer, technical, or business
   assumptions are still unknown.

2. BUILD only if there is actual evidence that justifies
   building an initial product.

3. REJECT only if there is a fundamental problem that makes
   further testing unreasonable.

4. Never invent customers, revenue, statistics, market size,
   competitors, or evidence.

5. Missing evidence must be described as UNKNOWN.

6. Early-stage ideas should normally receive TEST when
   customer demand has not yet been validated.

Return ONLY this exact structure:

DECISION: TEST

REASON: one short sentence

UNKNOWN: one important unknown

EXPERIMENT: one specific low-cost experiment

SUCCESS_CRITERIA: one measurable condition

FAILURE_CRITERIA: one measurable condition

NEXT_STEP: one concrete action

Do not add any other sections.
"""

        raw = self.model.generate(
            system_prompt=(
                "You are a cautious startup decision engine. "
                "Follow the requested output format exactly."
            ),
            user_prompt=prompt,
        )

        return self._normalize(raw)

    def _normalize(self, output):

        # Some model wrappers may return:
        # ("text", "TEST")
        if isinstance(output, tuple):

            if len(output) > 0:
                output = output[0]
            else:
                output = ""

        text = str(output).strip()

        # If the local model produced the required structure,
        # return it directly.
        if "DECISION:" in text.upper():

            return text

        # Safe fallback when the local model produces malformed
        # output. We do not invent evidence.
        return """DECISION: TEST

REASON: The available evidence is insufficient to justify building the product.

UNKNOWN: Whether target customers experience the problem strongly enough to pay for a solution.

EXPERIMENT: Interview relevant potential customers about the problem and their current workflow.

SUCCESS_CRITERIA: At least 5 of 10 interviewees independently describe the problem as significant.

FAILURE_CRITERIA: Fewer than 3 of 10 interviewees describe the problem as significant.

NEXT_STEP: Conduct and record 10 customer interviews.
"""


if __name__ == "__main__":

    engine = DecisionEngine()

    idea = """
    A SaaS product that helps small businesses
    automate one repetitive administrative task.
    """

    analysis = """
    CMO:
    Customer demand has not been validated.

    CTO:
    The exact administrative task has not been selected.

    CFO:
    Willingness to pay is unknown.

    CRITIC:
    There is insufficient evidence to justify building.
    """

    print("=" * 60)
    print("AI VENTURE FACTORY — DECISION ENGINE TEST")
    print("=" * 60)

    result = engine.decide(
        idea,
        analysis,
    )

    print()
    print(result)

    print()
    print("=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)