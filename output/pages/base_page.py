"""Base page object that all page classes inherit from."""

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
