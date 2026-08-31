from app.core.decision_engine import DecisionEngine
from app.core.experiment_engine import ExperimentEngine
from app.core.experiment_registry import ExperimentRegistry


class CommandCenter:

    def __init__(self):
        self.decision_engine = DecisionEngine()
        self.experiment_engine = ExperimentEngine()
        self.registry = ExperimentRegistry()

    def start(self):

        print("=" * 60)
        print("AI VENTURE FACTORY — COMMAND CENTER")
        print("=" * 60)
        print()
        print("Company system: ONLINE")
        print("Founder interface: ONLINE")
        print()
        print("Type 'help' for commands.")
        print("Type 'exit' to close.")
        print()

        while True:

            try:
                command = input("Founder > ").strip()

            except (KeyboardInterrupt, EOFError):
                print()
                print("Command Center closed.")
                break

            if not command:
                continue

            if command.lower() == "exit":
                print("Command Center closed.")
                break

            self.handle_command(command)

    def handle_command(self, command):

        lower = command.lower()

        if lower == "help":
            self.show_help()
            return

        if lower == "status":
            self.show_status()
            return

        if lower == "experiments":
            self.show_experiments()
            return

        if lower.startswith("evaluate "):
            idea = command[9:].strip()
            self.evaluate_idea(idea)
            return

        if lower.startswith("experiment "):
            idea = command[11:].strip()
            self.create_experiment(idea)
            return

        print()
        print("I don't recognize that command.")
        print("Type 'help' to see available commands.")
        print()

    def show_help(self):

        print()
        print("AVAILABLE COMMANDS")
        print("-" * 60)
        print("status")
        print("experiments")
        print("evaluate <startup idea>")
        print("experiment <startup idea>")
        print("help")
        print("exit")
        print()

    def show_status(self):

        print()
        print("=" * 60)
        print("COMPANY STATUS")
        print("=" * 60)

        print("Company: AI Venture Factory")
        print("Core: ONLINE")
        print("Decision Engine: ONLINE")
        print("Experiment Engine: ONLINE")
        print("Experiment Registry: ONLINE")
        print()

    def evaluate_idea(self, idea):

        print()
        print("=" * 60)
        print("DECISION ENGINE")
        print("=" * 60)

        analysis = f"""
Founder submitted the following idea:

{idea}

Current evidence:
- No validated customers.
- No validated revenue.
- No validated willingness to pay.
- No validated product-market fit.
"""

        result = self.decision_engine.decide(
            idea,
            analysis,
        )

        print()
        print(result)
        print()

    def create_experiment(self, idea):

        print()
        print("=" * 60)
        print("EXPERIMENT ENGINE")
        print("=" * 60)

        unknown = (
            "Whether the target customer experiences "
            "the problem strongly enough to care."
        )

        result = self.experiment_engine.create_experiment(
            idea,
            unknown,
        )

        print()

        for key, value in result.items():
            print(f"{key.upper()}:")
            print(value)
            print()

    def show_experiments(self):

        print()
        print("=" * 60)
        print("EXPERIMENT REGISTRY")
        print("=" * 60)

        connection = self.registry._connect()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                id,
                status,
                idea,
                created_at
            FROM experiments
            ORDER BY id DESC
        """)

        rows = cursor.fetchall()

        connection.close()

        if not rows:
            print()
            print("No experiments registered.")
            print()
            return

        for row in rows:

            experiment_id = row[0]
            status = row[1]
            idea = row[2].strip().replace(
                "\n",
                " "
            )
            created_at = row[3]

            print()
            print(f"EXPERIMENT-{experiment_id:04d}")
            print(f"STATUS: {status}")
            print(f"IDEA: {idea}")
            print(f"CREATED: {created_at}")

        print()


if __name__ == "__main__":
    CommandCenter().start()