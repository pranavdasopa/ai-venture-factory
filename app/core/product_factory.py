from app.agents.product_builder import ProductBuilder
from app.agents.code_builder import CodeBuilder
from app.agents.file_builder import FileBuilder
from app.agents.test_agent import TestAgent
from app.agents.auto_fix_agent import AutoFixAgent


class ProductFactory:

    def __init__(self):
        self.product_builder = ProductBuilder()
        self.code_builder = CodeBuilder()
        self.file_builder = FileBuilder()
        self.test_agent = TestAgent()
        self.auto_fix_agent = AutoFixAgent()

    def build(self, idea, project_name):

        print("STEP 1 — PRODUCT DESIGN")
        specification = self.product_builder.design(idea)

        print("STEP 2 — CODE GENERATION")

        files = [
            "index.html",
            "style.css",
            "app.js"
        ]

        for filename in files:

            print(f"Generating {filename}...")

            code = self.code_builder.generate_file(
                specification,
                filename
            )

            self.file_builder.build_file(
                code,
                filename,
                project_name
            )

        project_path = (
            f"generated_products/{project_name}"
        )

        print("STEP 3 — TESTING")

        for attempt in range(3):

            test = self.test_agent.test(
                project_path
            )

            if test["success"]:

                print("TEST PASSED")
                break

            print(
                f"TEST FAILED — AUTO-FIX {attempt + 1}/3"
            )

            self.auto_fix_agent.fix(
                project_path,
                test["errors"]
            )

        else:

            print("BUILD FAILED")

            return {
                "success": False,
                "project": project_path,
                "error": "Could not produce a valid build."
            }

        print("PRODUCT BUILD COMPLETE")

        return {
            "success": True,
            "project": project_path,
            "files": files
        }