from app.core.experiment_engine import ExperimentEngine
from app.core.experiment_registry import ExperimentRegistry
from app.core.decision_engine import DecisionEngine


class VentureWorkflow:

    def __init__(self):

        self.decision_engine = DecisionEngine()
        self.experiment_engine = ExperimentEngine()
        self.registry = ExperimentRegistry()

    def evaluate(self, idea, analysis):

        print("=" * 60)
        print("AI VENTURE FACTORY — VENTURE WORKFLOW")
        print("=" * 60)

        print()
        print("STEP 1 — DECISION ENGINE")
        print("-" * 60)

        decision_output = self.decision_engine.decide(
            idea,
            analysis,
        )

        print(decision_output)

        # DecisionEngine may return:
        #   "text"
        # or:
        #   ("text", "TEST")
        decision = self._extract_decision(
            decision_output
        )

        print()
        print(f"PARSED DECISION: {decision}")

        if decision == "REJECT":

            print()
            print("WORKFLOW RESULT: REJECT")
            print("No experiment created.")

            return {
                "decision": "REJECT"
            }

        if decision == "BUILD":

            print()
            print("WORKFLOW RESULT: BUILD")
            print(
                "Product-building workflow will be "
                "added in a later stage."
            )

            return {
                "decision": "BUILD"
            }

        if decision == "TEST":

            decision_text = self._get_text(
                decision_output
            )

            unknown = self._extract_field(
                decision_text,
                "UNKNOWN:"
            )

            print()
            print("STEP 2 — EXPERIMENT ENGINE")
            print("-" * 60)

            experiment = self.experiment_engine.create_experiment(
                idea,
                unknown,
            )

            for key, value in experiment.items():

                print(f"{key.upper()}:")
                print(value)
                print()

            print("STEP 3 — EXPERIMENT REGISTRY")
            print("-" * 60)

            experiment_id = self.registry.create_experiment(
                idea=idea,
                unknown=unknown,
                hypothesis=experiment["hypothesis"],
                experiment=experiment["experiment"],
                success_criteria=experiment["success_criteria"],
                failure_criteria=experiment["failure_criteria"],
            )

            print(
                f"Experiment registered: "
                f"EXPERIMENT-{experiment_id:04d}"
            )

            print()
            print("STATUS: PLANNED")

            return {
                "decision": "TEST",
                "experiment_id": experiment_id,
                "experiment": experiment,
            }

        raise ValueError(
            "Decision Engine returned an invalid decision."
        )

    def _get_text(self, output):

        if isinstance(output, tuple):

            return str(output[0])

        return str(output)

    def _extract_decision(self, output):

        # If DecisionEngine already supplied
        # the parsed decision as the second tuple item.
        if isinstance(output, tuple):

            if len(output) >= 2:

                candidate = str(
                    output[1]
                ).strip().upper()

                if candidate in {
                    "TEST",
                    "BUILD",
                    "REJECT",
                }:
                    return candidate

        text = self._get_text(output)

        for line in text.splitlines():

            line = line.strip().upper()

            if line.startswith("DECISION:"):

                value = line.split(
                    ":",
                    1
                )[1].strip()

                if value in {
                    "TEST",
                    "BUILD",
                    "REJECT",
                }:
                    return value

        # Safety-first fallback.
        return "TEST"

    def _extract_field(self, text, field):

        lines = text.splitlines()

        for index, line in enumerate(lines):

            if line.strip().upper().startswith(
                field.upper()
            ):

                parts = line.split(
                    ":",
                    1
                )

                if len(parts) == 2:

                    value = parts[1].strip()

                    if value:
                        return value

                if index + 1 < len(lines):

                    return lines[index + 1].strip()

        return "Customer demand is unknown."


if __name__ == "__main__":

    workflow = VentureWorkflow()

    idea = """
    A SaaS product that helps small businesses
    automate one repetitive administrative task.
    """

    analysis = """
    CMO:
    We do not know whether small businesses actually
    experience this problem strongly enough to care.

    CTO:
    The technical implementation appears possible,
    but the exact task has not been selected.

    CFO:
    A subscription model is possible,
    but willingness to pay is unknown.

    CRITIC:
    Customer demand has not been validated.
    """

    result = workflow.evaluate(
        idea,
        analysis,
    )

    print()
    print("=" * 60)
    print("WORKFLOW COMPLETE")
    print("=" * 60)

    print()
    print(result)