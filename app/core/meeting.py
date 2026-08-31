class BoardMeeting:

    def __init__(self, ceo, cto, cfo, cmo, critic):

        self.ceo = ceo
        self.cto = cto
        self.cfo = cfo
        self.cmo = cmo
        self.critic = critic

    def evaluate_idea(self, idea):

        print()
        print("=" * 60)
        print("EXECUTIVE BOARD MEETING")
        print("=" * 60)

        print()
        print("BUSINESS IDEA:")
        print(idea)

        print()
        print("CMO — MARKET ANALYSIS")
        print("-" * 60)

        market = self.cmo.analyze(
            f"Evaluate the market potential of this idea:\n{idea}"
        )

        print(market)

        print()
        print("CTO — TECHNICAL ANALYSIS")
        print("-" * 60)

        technical = self.cto.analyze(
            f"Evaluate the technical feasibility of this idea:\n{idea}"
        )

        print(technical)

        print()
        print("CFO — FINANCIAL ANALYSIS")
        print("-" * 60)

        financial = self.cfo.analyze(
            f"Evaluate the financial potential and risks of this idea:\n{idea}"
        )

        print(financial)

        combined_analysis = f"""
BUSINESS IDEA:
{idea}

MARKET ANALYSIS:
{market}

TECHNICAL ANALYSIS:
{technical}

FINANCIAL ANALYSIS:
{financial}
"""

        print()
        print("CRITIC — ADVERSARIAL REVIEW")
        print("-" * 60)

        criticism = self.critic.analyze(
            combined_analysis
        )

        print(criticism)

        final_request = f"""
Evaluate this business proposal.

{combined_analysis}

CRITIC REVIEW:
{criticism}

Provide a final strategic recommendation.
"""

        print()
        print("CEO — FINAL RECOMMENDATION")
        print("-" * 60)

        recommendation = self.ceo.think(
            final_request
        )

        print(recommendation)

        self.ceo.remember(
            "board_meeting",
            f"""
Idea:
{idea}

Market:
{market}

Technical:
{technical}

Financial:
{financial}

Critic:
{criticism}

CEO Recommendation:
{recommendation}
""",
        )

        return recommendation