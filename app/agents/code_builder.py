from app.models.ollama import OllamaModel


class CodeBuilder:

    def __init__(self):
        self.model = OllamaModel()

    def generate_file(self, specification, filename):

        system_prompt = f"""
You are a coding agent inside AI Venture Factory.

Generate ONLY the complete contents of this file:

{filename}

Product specification:
{specification}

Rules:
- Return ONLY source code.
- No markdown.
- No explanations.
- Keep the implementation small.
- The code must be complete.
"""

        return self.model.generate(
            system_prompt,
            f"Generate the complete file: {filename}"
        )