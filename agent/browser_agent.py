"""Browser Agent - executes steps via Playwright and discovers page elements."""

import re
import time
from typing import Dict, List, Tuple
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright, Page, Locator

from agent.step_parser import sanitize_name
from agent.object_repository import ObjectRepository


INTERACTIVE_SELECTORS = (
    "input, textarea, select, button, a[href], "
    "[role='button'], [role='link'], [role='textbox'], "
    "[role='checkbox'], [role='radio'], [role='combobox'], "
    "[role='menuitem'], [role='tab'], [role='switch'], "
    "[type='submit'], [type='reset']"
)


class BrowserAgent:
    """Drives a Playwright browser, executes user steps, and discovers elements."""

    def __init__(self, repository: ObjectRepository, headless: bool = True):
        self.repository = repository
        self.headless = headless
        self.current_page_name = "unknown_page"
        self.execution_log: List[Dict] = []

    def run(self, steps: List[Dict]) -> List[Dict]:
        """Execute all steps and return an execution log."""
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=self.headless)
            context = browser.new_context(
                viewport={"width": 1280, "height": 720},
                ignore_https_errors=True,
            )
            page = context.new_page()

            for step in steps:
                result = self._execute_step(page, step)
                self.execution_log.append(result)
                page.wait_for_load_state("domcontentloaded")
                time.sleep(0.5)
                self._discover_elements(page)

            browser.close()

        self.repository.save()
        return self.execution_log

    def _execute_step(self, page: Page, step: Dict) -> Dict:
        """Execute a single parsed step and return result dict."""
        action = step["action"]
        result = {
            "step_number": step["step_number"],
            "action": action,
            "original_text": step["original_text"],
            "status": "passed",
            "error": "",
            "page_name": self.current_page_name,
        }

        try:
            if action == "navigate":
                url = step["url"]
                if not url.startswith("http"):
                    url = "https://" + url
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                self._detect_page(page)

            elif action == "input":
                locator = self._find_element(page, step["target"])
                locator.fill(step["value"])
                self._record_element(step["target"], "input", locator, page)

            elif action == "click":
                locator = self._find_element(page, step["target"])
                locator.click()
                self._record_element(step["target"], "button", locator, page)
                page.wait_for_load_state("domcontentloaded")
                self._detect_page(page)

            elif action == "select":
                locator = self._find_element(page, step["target"])
                locator.select_option(label=step["value"])
                self._record_element(step["target"], "select", locator, page)

            elif action == "hover":
                locator = self._find_element(page, step["target"])
                locator.hover()
                self._record_element(step["target"], "element", locator, page)

            elif action == "verify":
                target = step["target"]
                if "page" in target.lower() or "screen" in target.lower():
                    page.wait_for_load_state("domcontentloaded")
                    result["page_name"] = self.current_page_name
                else:
                    locator = self._find_element(page, target)
                    locator.wait_for(state="visible", timeout=10000)
                    self._record_element(target, "element", locator, page)

            elif action == "wait":
                if step["value"]:
                    time.sleep(int(step["value"]))
                else:
                    page.wait_for_load_state("networkidle")

            else:
                result["status"] = "skipped"
                result["error"] = f"Unknown action: {action}"

        except Exception as exc:
            result["status"] = "failed"
            result["error"] = str(exc)

        result["page_name"] = self.current_page_name
        return result

    def _detect_page(self, page: Page):
        """Detect current page from URL and register it in the repository."""
        url = page.url
        parsed = urlparse(url)
        path = parsed.path.strip("/")

        if not path or path == "/":
            page_name = "home_page"
        else:
            page_name = sanitize_name(path.split("/")[-1]) + "_page"

        self.current_page_name = page_name
        url_pattern = f"*{parsed.path}" if parsed.path else url
        self.repository.add_page(page_name, url_pattern)

    def _find_element(self, page: Page, target: str) -> Locator:
        """Find an element using a cascade of locator strategies."""
        strategies = [
            lambda: page.get_by_role("button", name=re.compile(target, re.IGNORECASE)).first,
            lambda: page.get_by_role("link", name=re.compile(target, re.IGNORECASE)).first,
            lambda: page.get_by_role("textbox", name=re.compile(target, re.IGNORECASE)).first,
            lambda: page.get_by_label(re.compile(target, re.IGNORECASE)).first,
            lambda: page.get_by_placeholder(re.compile(target, re.IGNORECASE)).first,
            lambda: page.get_by_text(re.compile(target, re.IGNORECASE)).first,
            lambda: page.locator(f"[aria-label*='{target}' i]").first,
            lambda: page.locator(f"#{sanitize_name(target)}").first,
            lambda: page.locator(f"[name*='{target}' i]").first,
        ]

        for strategy in strategies:
            try:
                locator = strategy()
                if locator.is_visible():
                    return locator
            except Exception:
                continue

        return page.get_by_text(target).first

    def _record_element(
        self, target: str, element_type: str, locator: Locator, page: Page
    ):
        """Record a discovered element into the object repository."""
        element_name = sanitize_name(target)
        locator_type, locator_value = self._best_locator(target, locator, page)

        self.repository.add_element(
            page_name=self.current_page_name,
            element_name=element_name,
            element_type=element_type,
            locator_type=locator_type,
            locator_value=locator_value,
            description=target,
        )

    def _best_locator(
        self, target: str, locator: Locator, page: Page
    ) -> Tuple[str, str]:
        """Determine the best locator strategy for an element."""
        try:
            label = locator.evaluate("el => el.getAttribute('aria-label')")
            if label:
                return ("get_by_label", label)
        except Exception:
            pass

        try:
            placeholder = locator.evaluate("el => el.getAttribute('placeholder')")
            if placeholder:
                return ("get_by_placeholder", placeholder)
        except Exception:
            pass

        try:
            role = locator.evaluate("el => el.getAttribute('role')")
            tag = locator.evaluate("el => el.tagName.toLowerCase()")
            if role:
                return ("get_by_role", f"{role}, name={target}")
            if tag in ("button", "a"):
                mapped_role = "button" if tag == "button" else "link"
                return ("get_by_role", f"{mapped_role}, name={target}")
        except Exception:
            pass

        try:
            el_id = locator.evaluate("el => el.id")
            if el_id:
                return ("css", f"#{el_id}")
        except Exception:
            pass

        try:
            name_attr = locator.evaluate("el => el.getAttribute('name')")
            if name_attr:
                return ("css", f"[name='{name_attr}']")
        except Exception:
            pass

        return ("get_by_text", target)

    def _discover_elements(self, page: Page):
        """Snapshot all interactive elements on the current page."""
        try:
            elements = page.query_selector_all(INTERACTIVE_SELECTORS)
            for el in elements[:50]:
                try:
                    tag = el.evaluate("e => e.tagName.toLowerCase()")
                    el_type = el.get_attribute("type") or ""
                    role = el.get_attribute("role") or ""
                    name = (
                        el.get_attribute("aria-label")
                        or el.get_attribute("placeholder")
                        or el.get_attribute("name")
                        or el.get_attribute("id")
                        or el.inner_text()[:40]
                    )
                    if not name or not name.strip():
                        continue

                    element_name = sanitize_name(name)
                    mapped_type = self._map_element_type(tag, el_type, role)
                    locator_type, locator_value = self._resolve_locator_from_attrs(el, name)

                    self.repository.add_element(
                        page_name=self.current_page_name,
                        element_name=element_name,
                        element_type=mapped_type,
                        locator_type=locator_type,
                        locator_value=locator_value,
                        description=name,
                    )
                except Exception:
                    continue
        except Exception:
            pass

    def _map_element_type(self, tag: str, el_type: str, role: str) -> str:
        if tag == "input" and el_type in ("text", "email", "password", "search", "tel", "url", ""):
            return "input"
        if tag == "textarea":
            return "input"
        if tag == "select":
            return "select"
        if tag == "button" or role == "button" or el_type in ("submit", "reset"):
            return "button"
        if tag == "a" or role == "link":
            return "link"
        if el_type in ("checkbox",):
            return "checkbox"
        if el_type in ("radio",):
            return "radio"
        return "element"

    def _resolve_locator_from_attrs(
        self, el, name: str
    ) -> Tuple[str, str]:
        aria_label = el.get_attribute("aria-label")
        if aria_label:
            return ("get_by_label", aria_label)

        placeholder = el.get_attribute("placeholder")
        if placeholder:
            return ("get_by_placeholder", placeholder)

        el_id = el.get_attribute("id")
        if el_id:
            return ("css", f"#{el_id}")

        name_attr = el.get_attribute("name")
        if name_attr:
            return ("css", f"[name='{name_attr}']")

        return ("get_by_text", name)
