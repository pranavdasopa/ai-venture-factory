import requests


class OllamaModel:

    def __init__(
        self,
        model: str = "qwen2.5:0.5b",
        host: str = "http://localhost:11434",
    ):
        self.model = model
        self.host = host.rstrip("/")

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:

        response = requests.post(
            f"{self.host}/api/chat",
            json={
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "num_predict": 160,
                    "num_ctx": 2048,
                },
                "keep_alive": "10m",
            },
            timeout=180,
        )

        response.raise_for_status()

        data = response.json()

        return data["message"]["content"]