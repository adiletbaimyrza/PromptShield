import re
import sys
from typing import Dict, List, Tuple
import json
import os
import tempfile

CACHE_FILE = os.path.join(tempfile.gettempdir(), "anonimizacja_cache.json")

# =========================
# Types
# =========================

PlaceholdersCache = Dict[str, Dict[str, Dict[str, str]]]

PLACEHOLDER_RE = re.compile(r"\[[A-Z_]+_\d+\]")

# =========================
# Anonymizer
# =========================

class PromptShieldRegex:
    def __init__(self):
        self.placeholders_cache: PlaceholdersCache = {}

        self.rules = {
            "EMAIL": [
                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
            ],
            "PHONE": [
                r"\+?\d[\d\s\-\(\)]{8,}\d"
            ],
            "IP": [
                r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
            ],
            "URL": [
                r"https?://[^\s<>()]+",
                r"\bwww\.[^\s<>()]+\b",
            ],
            "CARD": [
                r"\b(?:\d{4}[- ]?){3}\d{4}\b"
            ],
            "DATE": [
                r"\b\d{4}-\d{2}-\d{2}\b",
                r"\b\d{2}/\d{2}/\d{4}\b",
            ],
            "AMOUNT": [
                r"\b\d+(?:[.,]\d{2})\s?(?:zł|PLN|USD|EUR)\b"
            ],
        }

    def _get_placeholder(self, value: str, entity_type: str) -> str:
        if entity_type not in self.placeholders_cache:
            self.placeholders_cache[entity_type] = {
                "placeholders": {},
                "count": 0
            }

        cache = self.placeholders_cache[entity_type]

        if value not in cache["placeholders"]:
            cache["count"] += 1
            cache["placeholders"][value] = f"[{entity_type}_{cache['count']}]"

        return cache["placeholders"][value]

    def protect(self, text: str) -> str:
        matches: List[Tuple[int, int, str, str]] = []

        for entity_type, patterns in self.rules.items():
            for pattern in patterns:
                for m in re.finditer(pattern, text):
                    if PLACEHOLDER_RE.search(m.group()):
                        continue
                    matches.append((m.start(), m.end(), m.group(), entity_type))

        matches.sort(key=lambda x: (x[0], -x[1]))
        filtered = []
        last_end = -1

        for start, end, value, etype in matches:
            if start >= last_end:
                filtered.append((start, end, value, etype))
                last_end = end

        for _, _, value, etype in filtered:
            self._get_placeholder(value, etype)

        for start, end, value, etype in sorted(filtered, reverse=True):
            text = text[:start] + self._get_placeholder(value, etype) + text[end:]

        return text

    def restore_placeholder(self, placeholder: str) -> str:
        mapping = self.get_mapping()
        return mapping.get(placeholder, placeholder)

    def get_mapping(self) -> Dict[str, str]:
        mapping = {}
        for cache in self.placeholders_cache.values():
            for original, placeholder in cache["placeholders"].items():
                mapping[placeholder] = original
        return mapping


# =========================
# Global instance
# =========================

_shield = PromptShieldRegex()

def anonimizacja(text: str) -> str:
    result = _shield.protect(text)

    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(_shield.get_mapping(), f, ensure_ascii=False)

    return result


def cofanie_anonimizacji(selection: str) -> str:
    if not os.path.exists(CACHE_FILE):
        return selection

    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        mapping = json.load(f)

    return mapping.get(selection.strip(), selection)

# =========================
# CLI ENTRYPOINT (CRITICAL)
# =========================

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "anon"
    input_text = sys.stdin.read()

    if mode == "anon":
        output = anonimizacja(input_text)
    elif mode == "reverse":
        output = cofanie_anonimizacji(input_text)
    else:
        output = input_text

    sys.stdout.write(output)
