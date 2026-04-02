"""Scaffold - creates the output project directory structure."""

import os


OUTPUT_DIRS = [
    "object_repository",
    "pages",
    "tests",
    "reports",
]


def ensure_project_structure(output_dir: str) -> str:
    """Create the output project directory tree if it doesn't exist."""
    os.makedirs(output_dir, exist_ok=True)

    for sub in OUTPUT_DIRS:
        os.makedirs(os.path.join(output_dir, sub), exist_ok=True)

    tests_init = os.path.join(output_dir, "tests", "__init__.py")
    if not os.path.exists(tests_init):
        with open(tests_init, "w", encoding="utf-8") as f:
            f.write("")

    pages_init = os.path.join(output_dir, "pages", "__init__.py")
    if not os.path.exists(pages_init):
        with open(pages_init, "w", encoding="utf-8") as f:
            f.write("")

    return output_dir


def get_project_tree(output_dir: str) -> str:
    """Return a text representation of the output project tree."""
    lines = []
    for root, dirs, files in os.walk(output_dir):
        dirs[:] = sorted(dirs)
        level = root.replace(output_dir, "").count(os.sep)
        indent = "│   " * level
        basename = os.path.basename(root)
        lines.append(f"{indent}├── {basename}/")
        sub_indent = "│   " * (level + 1)
        for f in sorted(files):
            lines.append(f"{sub_indent}├── {f}")
    return "\n".join(lines)
