"""Page Object Generator - creates Playwright Python POM classes from the object repository."""

import os
from typing import Dict

ACTION_METHOD_TEMPLATES = {
    "input": (
        "    def fill_{name}(self, value: str):\n"
        "        self.{name}.fill(value)\n"
        "        return self\n"
    ),
    "button": (
        "    def click_{name}(self):\n"
        "        self.{name}.click()\n"
        "        return self\n"
    ),
    "link": (
        "    def click_{name}(self):\n"
        "        self.{name}.click()\n"
        "        return self\n"
    ),
    "select": (
        "    def select_{name}(self, value: str):\n"
        "        self.{name}.select_option(label=value)\n"
        "        return self\n"
    ),
    "checkbox": (
        "    def toggle_{name}(self):\n"
        "        self.{name}.click()\n"
        "        return self\n"
    ),
    "radio": (
        "    def select_{name}(self):\n"
        "        self.{name}.click()\n"
        "        return self\n"
    ),
    "element": (
        "    def click_{name}(self):\n"
        "        self.{name}.click()\n"
        "        return self\n"
    ),
}


def generate_pages(repository_data: Dict, output_dir: str) -> list:
    """Generate Page Object Model Python files from repository data."""
    pages_dir = os.path.join(output_dir, "pages")
    os.makedirs(pages_dir, exist_ok=True)

    generated_files = []

    _write_base_page(pages_dir)
    generated_files.append(os.path.join(pages_dir, "base_page.py"))

    for page_name, page_data in repository_data.get("pages", {}).items():
        filepath = _generate_page_file(page_name, page_data, pages_dir)
        generated_files.append(filepath)

    _write_pages_init(pages_dir, repository_data.get("pages", {}))
    generated_files.append(os.path.join(pages_dir, "__init__.py"))

    return generated_files


def _write_base_page(pages_dir: str):
    """Write the BasePage class that all page objects inherit from."""
    content = '''"""Base page object that all page classes inherit from."""

from playwright.sync_api import Page, expect


class BasePage:
    """Base class providing common page operations."""

    def __init__(self, page: Page):
        self.page = page

    def navigate(self, url: str):
        self.page.goto(url, wait_until="domcontentloaded")
        return self

    def get_title(self) -> str:
        return self.page.title()

    def get_url(self) -> str:
        return self.page.url

    def wait_for_load(self):
        self.page.wait_for_load_state("domcontentloaded")
        return self

    def take_screenshot(self, path: str):
        self.page.screenshot(path=path)
        return self
'''
    filepath = os.path.join(pages_dir, "base_page.py")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


def _generate_page_file(page_name: str, page_data: Dict, pages_dir: str) -> str:
    """Generate a single page object file."""
    class_name = _to_class_name(page_name)
    elements = page_data.get("elements", {})
    url_pattern = page_data.get("url_pattern", "")

    lines = [
        f'"""Page object for {page_name}."""\n',
        "from pages.base_page import BasePage\n\n",
        f"class {class_name}(BasePage):\n",
        f'    URL_PATTERN = "{url_pattern}"\n\n',
        "    def __init__(self, page):\n",
        "        super().__init__(page)\n",
    ]

    for el_name, el_data in elements.items():
        locator_code = _build_locator(el_data)
        lines.append(f"        self.{el_name} = {locator_code}\n")

    lines.append("\n")

    for el_name, el_data in elements.items():
        el_type = el_data.get("type", "element")
        template = ACTION_METHOD_TEMPLATES.get(el_type, ACTION_METHOD_TEMPLATES["element"])
        method = template.format(name=el_name)
        lines.append(method)
        lines.append("\n")

    filepath = os.path.join(pages_dir, f"{page_name}.py")
    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(lines)

    return filepath


def _build_locator(el_data: Dict) -> str:
    """Build a Playwright locator expression from element data."""
    loc_type = el_data.get("locator_type", "get_by_text")
    loc_value = el_data.get("locator_value", "")

    if loc_type == "get_by_role":
        parts = loc_value.split(", name=", 1)
        role = parts[0] if parts else "button"
        name = parts[1] if len(parts) > 1 else loc_value
        return f'self.page.get_by_role("{role}", name="{name}")'

    if loc_type == "get_by_label":
        return f'self.page.get_by_label("{loc_value}")'

    if loc_type == "get_by_placeholder":
        return f'self.page.get_by_placeholder("{loc_value}")'

    if loc_type == "get_by_text":
        return f'self.page.get_by_text("{loc_value}")'

    if loc_type == "css":
        return f'self.page.locator("{loc_value}")'

    return f'self.page.get_by_text("{loc_value}")'


def _to_class_name(page_name: str) -> str:
    """Convert snake_case page name to PascalCase class name."""
    return "".join(word.capitalize() for word in page_name.split("_"))


def _write_pages_init(pages_dir: str, pages: Dict):
    """Write __init__.py that exports all page classes."""
    lines = ['"""Generated page objects."""\n\n']
    for page_name in pages:
        class_name = _to_class_name(page_name)
        lines.append(f"from pages.{page_name} import {class_name}\n")

    filepath = os.path.join(pages_dir, "__init__.py")
    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(lines)
