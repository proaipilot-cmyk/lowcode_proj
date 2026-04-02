"""Object Repository - stores element locators per page in a shareable JSON format."""

import json
import os
from typing import Dict, Optional


class ObjectRepository:
    """Manages a JSON-based object repository for page element locators."""

    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.data: Dict = {"pages": {}}
        if os.path.exists(repo_path):
            self._load()

    def _load(self):
        with open(self.repo_path, "r", encoding="utf-8") as f:
            self.data = json.load(f)

    def save(self):
        os.makedirs(os.path.dirname(self.repo_path), exist_ok=True)
        with open(self.repo_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def add_page(self, page_name: str, url_pattern: str):
        if page_name not in self.data["pages"]:
            self.data["pages"][page_name] = {
                "url_pattern": url_pattern,
                "elements": {},
            }

    def add_element(
        self,
        page_name: str,
        element_name: str,
        element_type: str,
        locator_type: str,
        locator_value: str,
        description: str = "",
    ):
        if page_name not in self.data["pages"]:
            self.add_page(page_name, "")

        self.data["pages"][page_name]["elements"][element_name] = {
            "type": element_type,
            "locator_type": locator_type,
            "locator_value": locator_value,
            "description": description,
        }

    def get_page(self, page_name: str) -> Optional[Dict]:
        return self.data["pages"].get(page_name)

    def get_element(self, page_name: str, element_name: str) -> Optional[Dict]:
        page = self.get_page(page_name)
        if page:
            return page["elements"].get(element_name)
        return None

    def get_all_pages(self) -> Dict:
        return self.data["pages"]

    def to_dict(self) -> Dict:
        return self.data
