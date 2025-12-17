import spacy
import re
from langdetect import detect
from deep_translator import GoogleTranslator
from typing import Dict, List

PlaceholdersCache = Dict[str, Dict[str, Dict[str, str]]]
Rules = Dict[str, Dict[str, List[str]]]


class PromptShield:
    PLACEHOLDER_PATTERN = re.compile(r"\[(\w+)_\d+\]")

    def __init__(self, nlp=None):
        self.ner = nlp or spacy.load("en_core_web_sm")
        self.placeholders_cache: PlaceholdersCache = {}

        self.rules: Rules = {
            'mem': {
                'patterns': [
                    r'\b\d+(?:\.\d+)?\s*(?:B|KB|K|MB|M|GB|G|TB|T)\b'
                ]
            },
            'cvv': {
                'patterns': [
                    r'\b(?:CVV|CVC)\s*[:\-]?\s*\d{3,4}\b',
                ]
            },
            'exp': {
                'patterns': [
                    r'\b(?:exp|expiry|expires)\s*[:\-]?\s*(0[1-9]|1[0-2])[\/\-](\d{2}|\d{4})\b'
                ]
            },
            'card': {
                'patterns': [
                    r'\b(?:\d{4}[- ]\d{4}[- ]\d{4}[- ]\d{4}|\d{16})\b'
                ]
            },
            'date': {
                'patterns': [
                    r'\b(0?[1-9]|[12][0-9]|3[01])[\/\-](0?[1-9]|1[0-2])[\/\-]\d{4}\b',
                    r'\d{4}[\/\-](?:0?[1-9]|1[0-2])[\/\-](?:0?[1-9]|[12][0-9]|3[01])',
                    r'\b(0?[1-9]|[12][0-9]|3[01])(st|nd|rd|th)\b',
                ]
            },
            
            'email': {
                'patterns': [
                    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                ]
            },
            'url': {
                'patterns': [
                    r'https?://[^\s<>"{}|\\^`\[\]]+',
                    r'www\.[^\s<>"{}|\\^`\[\]]+',
                ]
            },
            
            'ip': {
                'patterns': [
                    r'\b(?:IP|ip)\s*[:\-]?\s*((?:\d{1,3}\.){3}\d{1,3})\b',
                    r'\b((?:\d{1,3}\.){3}\d{1,3})\b'
                ]
            },
            'phone': {
                'patterns': [
                    r'\+?\d[\d\s\-\(\)]{8,}\d'
                ]
            },
            'amount': {
                'patterns': [
                    r'[\$\€\£\₽\¥]\s?\d+(?:,\d{3})*(?:\.\d{2})?',
                    r'\d+(?:,\d{3})*(?:\.\d{2})?\s?(?:USD|EUR|GBP|JPY|AUD|CAD|RUB|CNY|dollars?)',
                    r'(?:USD|EUR|GBP|JPY|AUD|CAD|RUB|CNY)\s?\d+'
                ]
            },
           
            'place': {
                'custom': lambda text: {
                    (ent.text, ent.start_char, ent.end_char)
                    for ent in self.ner(text).ents
                    if ent.label_ in ("GPE", "LOC")
                }
            },
            'name': {
                'custom': lambda text: {
                    (ent.text, ent.start_char, ent.end_char)
                    for ent in self.ner(text).ents
                    if ent.label_ == "PERSON"
                }
            },
            'jwt': {
                'patterns': [
                    r"e[yw][A-Za-z0-9-_]+\.(?:e[yw][A-Za-z0-9-_]+)?\.[A-Za-z0-9-_]{2,}"
                ]
            },
            'btc_address': {
                'patterns': [
                    r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b',
                    r'\bbc1[a-z0-9]{39,87}\b',
                ]
            },
            'eth_address': {
                'patterns': [
                    r'\b0x[a-fA-F0-9]{40}\b',
                ]
            },
            'username': {
                'patterns': [
                    r'@[A-Za-z0-9_]{1,15}\b',
                    r'u/[A-Za-z0-9_-]{3,20}\b',
                ]
            },
             'alnum_code': {
                'patterns': [
                    r'\b(?=[A-Za-z0-9\-]*[A-Za-z])(?=[A-Za-z0-9\-]*\d)[A-Za-z0-9\-]+\b'
                ],
                'mode': 'normalize'
            },
            "coors": {
                "patterns": [r'^-?\d{1,2}\.\d+,\s*-?\d{1,3}\.\d+$']
            }
        }

    # =========================
    # Core helpers
    # =========================

    def _get_placeholder(self, entity_value, entity_type):
        if entity_type not in self.placeholders_cache:
            self.placeholders_cache[entity_type] = {'placeholders': {}, 'count': 0}

        placeholders = self.placeholders_cache[entity_type]['placeholders']

        if entity_value not in placeholders:
            self.placeholders_cache[entity_type]['count'] += 1
            idx = self.placeholders_cache[entity_type]['count']
            placeholders[entity_value] = f"[{entity_type.upper()}_{idx}]"

        return placeholders[entity_value]

    def _normalize_alnum(self, value: str) -> str:
        return ''.join(
            'A' if c.isalpha() else
            '0' if c.isdigit() else
            c
            for c in value
        )

    def _replace_pattern(self, text: str, pattern: str, entity_type: str, mode: str = "placeholder") -> str:
        matches = []
        for match in re.finditer(pattern, text):
            matches.append((match.start(), match.end(), match.group()))

        matches.sort(reverse=True, key=lambda x: x[0])

        for start, end, entity_value in matches:
            if mode == "normalize":
                replacement = self._normalize_alnum(entity_value)
            else:
                replacement = self._get_placeholder(entity_value, entity_type)

            text = text[:start] + replacement + text[end:]

        return text

    def _replace_custom(self, text: str, custom_func, entity_type: str) -> str:
        found_entities = list(custom_func(text))
        found_entities.sort(reverse=True, key=lambda x: x[1])

        for entity_value, start, end in found_entities:
            placeholder = self._get_placeholder(entity_value, entity_type)
            text = text[:start] + placeholder + text[end:]

        return text

    def _translate_placeholders(self, text: str, target_lang: str) -> str:
        def repl(match):
            placeholder = match.group(0)
            entity_type = match.group(1)
            try:
                translated = GoogleTranslator(source='en', target=target_lang).translate(entity_type.lower())
                return f"[{translated.upper()}_{placeholder.split('_')[1]}]"
            except:
                return placeholder

        return self.PLACEHOLDER_PATTERN.sub(repl, text)

    # =========================
    # Public API
    # =========================

    def protect(self, text: str, translate: bool = True) -> str:
        try:
            lang = detect(text)
        except:
            lang = "en"

        for entity_type, rule in self.rules.items():
            if 'custom' in rule:
                text = self._replace_custom(text, rule['custom'], entity_type)
            else:
                for pattern in rule.get('patterns', []):
                    text = self._replace_pattern(
                        text,
                        pattern,
                        entity_type,
                        rule.get('mode', 'placeholder')
                    )

        if translate and lang != "en":
            text = self._translate_placeholders(text, lang)

        return text
