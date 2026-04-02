"""Parse freeform user steps into structured action dicts."""

import re
from typing import List, Dict


ACTION_PATTERNS = [
    {
        "action": "navigate",
        "patterns": [
            r"(?:go\s+to|navigate\s+to|open|visit|launch|browse\s+to)\s+['\"]?(?P<url>https?://\S+)['\"]?",
            r"(?:go\s+to|navigate\s+to|open|visit|launch|browse\s+to)\s+['\"]?(?P<url>\S+\.\S+)['\"]?",
        ],
    },
    {
        "action": "input",
        "patterns": [
            r"(?:enter|type|fill|input|write)\s+['\"](?P<value>[^'\"]+)['\"]\s+(?:in|into|on|at)\s+(?:the\s+)?['\"]?(?P<target>.+?)['\"]?\s*(?:field|input|textbox|box)?$",
            r"(?:enter|type|fill|input|write)\s+(?P<value>\S+)\s+(?:in|into|on|at)\s+(?:the\s+)?['\"]?(?P<target>.+?)['\"]?\s*(?:field|input|textbox|box)?$",
        ],
    },
    {
        "action": "click",
        "patterns": [
            r"(?:click|press|tap|hit)\s+(?:on\s+)?(?:the\s+)?['\"]?(?P<target>.+?)['\"]?\s*(?:button|link|tab|menu|icon|element)?$",
        ],
    },
    {
        "action": "select",
        "patterns": [
            r"(?:select|choose|pick)\s+['\"]?(?P<value>[^'\"]+)['\"]?\s+(?:from|in)\s+(?:the\s+)?['\"]?(?P<target>.+?)['\"]?\s*(?:dropdown|select|list)?$",
        ],
    },
    {
        "action": "hover",
        "patterns": [
            r"(?:hover|mouse\s+over|move\s+to)\s+(?:on\s+)?(?:the\s+)?['\"]?(?P<target>.+?)['\"]?$",
        ],
    },
    {
        "action": "verify",
        "patterns": [
            r"(?:verify|check|assert|ensure|confirm|validate)\s+(?:that\s+)?(?:the\s+)?['\"]?(?P<target>.+?)['\"]?\s+(?:is\s+)?(?:displayed|visible|present|shown|loaded|exists|appears)",
            r"(?:verify|check|assert|ensure|confirm|validate)\s+(?:that\s+)?(?:the\s+)?(?P<target>.+?)\s+(?:page|screen)\s+(?:is\s+)?(?:displayed|visible|loaded|opens|appears)",
            r"(?:verify|check|assert|ensure|confirm|validate)\s+(?:that\s+)?['\"]?(?P<target>.+?)['\"]?\s*$",
        ],
    },
    {
        "action": "wait",
        "patterns": [
            r"(?:wait|pause)\s+(?:for\s+)?(?P<value>\d+)\s*(?:seconds?|secs?|s)?",
            r"(?:wait|pause)\s+(?:for\s+)?(?:the\s+)?['\"]?(?P<target>.+?)['\"]?\s+(?:to\s+)?(?:load|appear|display)",
        ],
    },
]


def parse_steps(raw_text: str) -> List[Dict]:
    """Parse freeform text into a list of structured step dicts."""
    lines = _split_into_lines(raw_text)
    parsed_steps = []

    for idx, line in enumerate(lines, start=1):
        step = _parse_single_step(line, idx)
        parsed_steps.append(step)

    return parsed_steps


def _split_into_lines(raw_text: str) -> List[str]:
    """Split raw input into individual step lines."""
    lines = []
    for line in raw_text.strip().split("\n"):
        cleaned = re.sub(r"^\s*\d+[\.\)\-\:]\s*", "", line).strip()
        if cleaned:
            lines.append(cleaned)
    return lines


def _parse_single_step(line: str, step_number: int) -> Dict:
    """Parse a single line into a structured step dict."""
    for action_def in ACTION_PATTERNS:
        for pattern in action_def["patterns"]:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                groups = match.groupdict()
                return {
                    "step_number": step_number,
                    "action": action_def["action"],
                    "target": groups.get("target", ""),
                    "value": groups.get("value", ""),
                    "url": groups.get("url", ""),
                    "original_text": line,
                }

    return {
        "step_number": step_number,
        "action": "unknown",
        "target": line,
        "value": "",
        "url": "",
        "original_text": line,
    }


def sanitize_name(text: str) -> str:
    """Convert text to a valid Python identifier."""
    name = re.sub(r"[^a-zA-Z0-9]+", "_", text.lower()).strip("_")
    if name and name[0].isdigit():
        name = "el_" + name
    return name or "unnamed"
