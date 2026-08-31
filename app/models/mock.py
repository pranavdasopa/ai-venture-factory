from app.models.base import ModelProvider


class MockModel(ModelProvider):

    def generate(self, system_prompt: str, user_prompt: str) -> str:

        return (
            "AI BRAIN TEST SUCCESSFUL\n\n"
            "The company model interface is working.\n"
            "A real model can be connected later without changing "
            "the company architecture."
        )