from pathlib import Path
from app.models.ollama import OllamaModel


class AutoFixAgent:

    def __init__(self):
        self.model = OllamaModel()

    def fix(self, project_path, errors):

        project = Path(project_path)

        results = []

        for error in errors:

            filename = self._find_file(error)

            if not filename:
                continue

            file_path = project / filename

            if not file_path.exists():
                continue

            current_code = file_path.read_text(
                encoding="utf-8"
            )

            prompt = f"""
Fix this code.

FILE:
{filename}

CURRENT CODE:
{current_code}

ERROR:
{error}

Return ONLY the complete corrected source code.
No markdown.
No explanation.
"""

            fixed_code = self.model.generate(
                "You are an expert software debugging agent.",
                prompt
            )

            file_path.write_text(
                str(fixed_code).strip(),
                encoding="utf-8"
            )

            results.append(filename)

        return results

    def _find_file(self, error):

        error_text = str(error)

        for filename in [
            "index.html",
            "style.css",
            "app.js"
        ]:
            if filename in error_text:
                return filename

        return None