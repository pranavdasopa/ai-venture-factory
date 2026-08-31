from pathlib import Path


class FileBuilder:

    def build_file(
        self,
        content,
        filename,
        project_name="generated_product"
    ):

        root = (
            Path("generated_products")
            / project_name
        )

        destination = root / filename

        if (
            Path(filename).is_absolute()
            or ".." in Path(filename).parts
        ):
            raise ValueError("Unsafe file path.")

        destination.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        destination.write_text(
            str(content).strip(),
            encoding="utf-8"
        )

        return {
            "project": str(root),
            "file": str(destination),
            "success": True
        }