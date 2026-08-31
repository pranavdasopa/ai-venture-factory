class ExperimentEngine:

    def classify_unknown(self, unknown):

        text = unknown.lower()

        if (
            "customer" in text
            or "problem" in text
            or "want" in text
            or "demand" in text
        ):
            return "CUSTOMER_PROBLEM"

        if (
            "pay" in text
            or "price" in text
            or "willingness" in text
            or "revenue" in text
        ):
            return "WILLINGNESS_TO_PAY"

        if (
            "technical" in text
            or "feasible" in text
            or "build" in text
        ):
            return "TECHNICAL_FEASIBILITY"

        return "GENERAL_VALIDATION"

    def create_experiment(self, idea, unknown):

        category = self.classify_unknown(unknown)

        if category == "CUSTOMER_PROBLEM":

            return {
                "category": category,
                "hypothesis":
                    "The target customer experiences this problem frequently enough to care about solving it.",

                "experiment":
                    "Interview 10 relevant potential customers about their current workflow and the problem.",

                "success_criteria":
                    "At least 5 of 10 independently describe the same significant problem.",

                "failure_criteria":
                    "Fewer than 3 of 10 describe the problem as significant.",

                "next_action":
                    "Record the interviews and reassess the problem."
            }

        if category == "WILLINGNESS_TO_PAY":

            return {
                "category": category,
                "hypothesis":
                    "Some target customers will consider paying for a solution to this problem.",

                "experiment":
                    "Show a simple solution concept and pricing range to 10 relevant potential customers.",

                "success_criteria":
                    "At least 2 customers show concrete willingness to pay or request a paid trial.",

                "failure_criteria":
                    "No customer shows meaningful willingness to pay.",

                "next_action":
                    "Record responses and reassess pricing and value."
            }

        if category == "TECHNICAL_FEASIBILITY":

            return {
                "category": category,
                "hypothesis":
                    "A minimal version of the proposed solution can technically perform the required task.",

                "experiment":
                    "Build the smallest possible prototype that performs the core task.",

                "success_criteria":
                    "The prototype successfully performs the core task on predefined test cases.",

                "failure_criteria":
                    "The prototype cannot reliably perform the core task.",

                "next_action":
                    "Evaluate the prototype and decide whether further technical work is justified."
            }

        return {
            "category": category,
            "hypothesis":
                "The proposed business idea contains a meaningful problem worth investigating.",

            "experiment":
                "Conduct a small set of customer discovery conversations.",

            "success_criteria":
                "Clear recurring evidence of a meaningful customer problem.",

            "failure_criteria":
                "No meaningful recurring problem is identified.",

            "next_action":
                "Review the evidence and update the business hypothesis."
        }


if __name__ == "__main__":

    engine = ExperimentEngine()

    idea = """
    A SaaS product that helps small businesses
    automate one repetitive administrative task.
    """

    unknown = """
    Whether small businesses actually experience
    this problem strongly enough to want a solution.
    """

    print("=" * 60)
    print("AI VENTURE FACTORY — EXPERIMENT ENGINE TEST")
    print("=" * 60)

    experiment = engine.create_experiment(
        idea,
        unknown,
    )

    print()

    for key, value in experiment.items():

        print(f"{key.upper()}:")
        print(value)
        print()

    print("=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)