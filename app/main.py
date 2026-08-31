from app.core.company import start_company
from app.core.board import ExecutiveBoard
from app.core.meeting import BoardMeeting

from app.agents.ceo import CEO
from app.agents.cto import CTO
from app.agents.cfo import CFO
from app.agents.cmo import CMO
from app.agents.critic import Critic

from app.models.ollama import OllamaModel


def main():

    start_company()

    model = OllamaModel(
        model="qwen2.5:0.5b"
    )

    ceo = CEO(model)
    cto = CTO(model)
    cfo = CFO(model)
    cmo = CMO(model)
    critic = Critic(model)

    board = ExecutiveBoard(
        ceo=ceo,
        cto=cto,
        cfo=cfo,
        cmo=cmo,
        critic=critic,
    )

    board.status()

    meeting = BoardMeeting(
        ceo=ceo,
        cto=cto,
        cfo=cfo,
        cmo=cmo,
        critic=critic,
    )

    idea = """
    Build a SaaS product that helps small businesses
    automate repetitive administrative work.
    """

    meeting.evaluate_idea(idea)


if __name__ == "__main__":
    main()