"""Test Generator - creates pytest test files from parsed steps and the object repository."""

import os
from typing import Dict, List

from agent.step_parser import sanitize_name


def generate_tests(
    steps: List[Dict],
    execution_log: List[Dict],
    repository_data: Dict,
    output_dir: str,
) -> list:
    """Generate pytest test files from executed steps."""
    tests_dir = os.path.join(output_dir, "tests")
    os.makedirs(tests_dir, exist_ok=True)

    generated_files = []

    conftest_path = _write_conftest(output_dir)
    generated_files.append(conftest_path)

    pytest_ini_path = _write_pytest_ini(output_dir)
    generated_files.append(pytest_ini_path)

    page_groups = _group_steps_by_page(execution_log)

    test_path = _write_test_file(steps, execution_log, page_groups, tests_dir)
    generated_files.append(test_path)

    return generated_files


def _group_steps_by_page(execution_log: List[Dict]) -> Dict[str, List[Dict]]:
    """Group execution log entries by page name."""
    groups: Dict[str, List[Dict]] = {}
    for entry in execution_log:
        page = entry.get("page_name", "unknown_page")
        if page not in groups:
            groups[page] = []
        groups[page].append(entry)
    return groups


def _write_conftest(output_dir: str) -> str:
    """Write conftest.py with shared fixtures."""
    content = '''"""Shared pytest fixtures for Playwright tests."""

import os
import sys

import pytest
from playwright.sync_api import Page

sys.path.insert(0, os.path.dirname(__file__))


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
        "ignore_https_errors": True,
    }


@pytest.fixture
def page(page: Page):
    page.set_default_timeout(15000)
    yield page
'''
    filepath = os.path.join(output_dir, "conftest.py")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return filepath


def _write_pytest_ini(output_dir: str) -> str:
    """Write pytest.ini configuration."""
    content = """[pytest]
addopts = --html=reports/report.html --self-contained-html -v
testpaths = tests
"""
    filepath = os.path.join(output_dir, "pytest.ini")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return filepath


def _write_test_file(
    steps: List[Dict],
    execution_log: List[Dict],
    page_groups: Dict[str, List[Dict]],
    tests_dir: str,
) -> str:
    """Write the main test file that replays user steps."""
    pages_used = list(page_groups.keys())
    imports = _build_imports(pages_used)
    test_body = _build_test_body(steps, execution_log)

    content = f'''{imports}


class TestUserFlow:
    """Auto-generated test from user-provided steps."""

{test_body}
'''
    filepath = os.path.join(tests_dir, "test_user_flow.py")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return filepath


def _build_imports(pages_used: List[str]) -> str:
    """Build import statements for page objects."""
    lines = [
        '"""Auto-generated Playwright tests from user steps."""',
        "",
        "import pytest",
        "from playwright.sync_api import Page, expect",
    ]

    for page_name in pages_used:
        class_name = _to_class_name(page_name)
        lines.append(f"from pages.{page_name} import {class_name}")

    return "\n".join(lines)


def _build_test_body(steps: List[Dict], execution_log: List[Dict]) -> str:
    """Build the test method body from steps."""
    lines = []
    lines.append("    def test_user_flow(self, page: Page):")
    lines.append('        """Replay user-defined steps."""')

    current_page_var = None

    for step, log_entry in zip(steps, execution_log):
        action = step["action"]
        page_name = log_entry.get("page_name", "unknown_page")
        class_name = _to_class_name(page_name)
        page_var = page_name

        lines.append(f"        # Step {step['step_number']}: {step['original_text']}")

        if action == "navigate":
            url = step["url"]
            if not url.startswith("http"):
                url = "https://" + url
            lines.append(f'        page.goto("{url}")')
            lines.append('        page.wait_for_load_state("domcontentloaded")')
            current_page_var = page_var
            lines.append(f"        {page_var} = {class_name}(page)")

        elif action == "input":
            target_name = sanitize_name(step["target"])
            value = step["value"]
            if current_page_var:
                lines.append(f'        {current_page_var}.fill_{target_name}("{value}")')
            else:
                lines.append(f'        page.get_by_label("{step["target"]}").fill("{value}")')

        elif action == "click":
            target_name = sanitize_name(step["target"])
            if current_page_var:
                lines.append(f"        {current_page_var}.click_{target_name}()")
            else:
                lines.append(f'        page.get_by_text("{step["target"]}").click()')
            lines.append('        page.wait_for_load_state("domcontentloaded")')
            if page_name != current_page_var and page_name != "unknown_page":
                current_page_var = page_var
                lines.append(f"        {page_var} = {class_name}(page)")

        elif action == "select":
            target_name = sanitize_name(step["target"])
            value = step["value"]
            if current_page_var:
                lines.append(f'        {current_page_var}.select_{target_name}("{value}")')
            else:
                lines.append(f'        page.locator("select").select_option(label="{value}")')

        elif action == "hover":
            target_name = sanitize_name(step["target"])
            if current_page_var:
                lines.append(f"        {current_page_var}.{target_name}.hover()")
            else:
                lines.append(f'        page.get_by_text("{step["target"]}").hover()')

        elif action == "verify":
            target = step["target"]
            if "page" in target.lower() or "screen" in target.lower():
                lines.append(f'        assert "{_extract_keyword(target)}" in page.url or "{_extract_keyword(target)}" in page.title()')
            else:
                lines.append(f'        expect(page.get_by_text("{target}")).to_be_visible()')

        elif action == "wait":
            if step["value"]:
                lines.append(f'        page.wait_for_timeout({int(step["value"]) * 1000})')
            else:
                lines.append('        page.wait_for_load_state("networkidle")')

        else:
            lines.append(f"        # TODO: Manual step - {step['original_text']}")

        lines.append("")

    return "\n".join(lines)


def _to_class_name(page_name: str) -> str:
    return "".join(word.capitalize() for word in page_name.split("_"))


def _extract_keyword(text: str) -> str:
    """Extract a meaningful keyword from verification text."""
    skip_words = {"page", "screen", "is", "the", "displayed", "loaded", "visible", "appears", "opens"}
    words = text.lower().split()
    for word in words:
        cleaned = word.strip("'\"")
        if cleaned not in skip_words and len(cleaned) > 2:
            return cleaned
    return text.split()[0] if text.split() else "page"
