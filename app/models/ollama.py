import os
import requests


class OllamaModel:

    def __init__(self, model="qwen2.5:0.5b", host="http://localhost:11434"):
        self.model = model
        self.host = os.environ.get("OLLAMA_HOST", host).rstrip("/")

    def generate(self, system_prompt, user_prompt):

        api_key = os.environ.get("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured. "
                "Add it to the server environment."
            )

        url = (
            "https://generativelanguage.googleapis.com/"
            "v1beta/models/gemini-3.6-flash:generateContent"
        )

        response = requests.post(
            url,
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": api_key,
            },
            json={
                "system_instruction": {
                    "parts": [{"text": system_prompt}]
                },
                "contents": [{
                    "role": "user",
                    "parts": [{"text": user_prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.2,
                    "maxOutputTokens": 500
                },
            },
            timeout=60,
        )

        if not response.ok:
            raise RuntimeError(
                f"Gemini API error {response.status_code}: "
                f"{response.text}"
            )

        data = response.json()

        return data["candidates"][0]["content"]["parts"][0]["text"]