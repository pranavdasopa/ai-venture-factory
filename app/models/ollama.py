import os
import requests


class OllamaModel:

    def __init__(self, model="qwen2.5:0.5b", host="http://localhost:11434"):
        self.model = model
        self.host = os.environ.get("OLLAMA_HOST", host).rstrip("/")

    def generate(self, system_prompt, user_prompt):

        api_key = os.environ.get("GEMINI_API_KEY")

        if api_key:
            url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent"

            response = requests.post(
                url,
                headers={
                    "Content-Type": "application/json",
                    "x-goog-api-key": api_key
                },
                json={
                    "system_instruction": {
                        "parts": [{"text": system_prompt}]
                    },
                    "contents": [
                        {
                            "role": "user",
                            "parts": [{"text": user_prompt}]
                        }
                    ]
                },
                timeout=60
            )

            if not response.ok:
                raise RuntimeError(
                    f"Gemini API error {response.status_code}: {response.text}"
                )

            data = response.json()

            return data["candidates"][0]["content"]["parts"][0]["text"]

        response = requests.post(
            f"{self.host}/api/chat",
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "stream": False
            },
            timeout=180
        )

        response.raise_for_status()

        return response.json()["message"]["content"]
