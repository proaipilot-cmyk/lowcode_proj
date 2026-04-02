"""Shared pytest fixtures for Playwright tests."""

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
