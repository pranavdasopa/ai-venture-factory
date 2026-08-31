import subprocess
from pathlib import Path


class TestAgent:

    def test(self, project_path):

        project = Path(project_path)

        if not project.exists():
            return {
                "success": False,
                "errors": ["Project does not exist."]
            }

        errors = []

        # Check required files
        for filename in ["index.html", "style.css", "app.js"]:
            if not (project / filename).exists():
                errors.append(
                    f"Missing file: {filename}"
                )

        # Basic JavaScript syntax check
        js_file = project / "app.js"

        if js_file.exists():

            try:
                subprocess.run(
                    ["node", "--check", str(js_file)],
                    capture_output=True,
                    text=True,
                    check=True
                )

            except FileNotFoundError:
                errors.append(
                    "Node.js is not installed or not available."
                )

            except subprocess.CalledProcessError as error:
                errors.append(
                    error.stderr.strip()
                )

        return {
            "success": len(errors) == 0,
            "errors": errors
        }