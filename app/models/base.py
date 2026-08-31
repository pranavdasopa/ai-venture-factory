from abc import ABC, abstractmethod


class ModelProvider(ABC):

    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """
        Generate a response from the AI model.
        """
        pass