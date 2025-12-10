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
            'email': {
                'patterns': [
                    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                ]
            },
            'phone': {
                'patterns': [
                    r'\+?\d[\d\s\-\(\)]{8,}\d'
                ]
            },
            'amount': {
                'patterns': [
                    r'\$\s?\d+(?:,\d{3})*(?:\.\d{2})?',
                    r'\d+(?:,\d{3})*(?:\.\d{2})?\s?(?:USD|EUR|GBP|dollars?)',
                    r'(?:USD|EUR|GBP)\s?\d+'
                ]
            },
            'name': {
                'custom': lambda text: {
                    (ent.text, ent.start_char, ent.end_char)
                    for ent in self.ner(text).ents
                    if ent.label_ == "PERSON"
                }
            }
        }

    def _get_placeholder(self, entity_value, entity_type):
        if entity_type not in self.placeholders_cache:
            self.placeholders_cache[entity_type] = {'placeholders': {}, 'count': 0}

        placeholders = self.placeholders_cache[entity_type]['placeholders']

        if entity_value not in placeholders:
            self.placeholders_cache[entity_type]['count'] += 1
            idx = self.placeholders_cache[entity_type]['count']
            placeholders[entity_value] = f"[{entity_type.upper()}_{idx}]"

        return placeholders[entity_value]

    def _translate_placeholders(self, text: str, target_lang: str) -> str:
        def repl(match):
            placeholder = match.group(0)           # e.g., [EMAIL_1]
            entity_type = match.group(1)           # e.g., EMAIL
            try:
                translated_type = GoogleTranslator(source='en', target=target_lang).translate(entity_type.lower())
                return f"[{translated_type.upper()}_{placeholder.split('_')[1]}]"
            except:
                return placeholder
        return self.PLACEHOLDER_PATTERN.sub(repl, text)

    def protect(self, text: str, translate=True) -> str:
        # Detect language
        try:
            lang = detect(text)
        except:
            lang = "en"

        pending_replacements = []

        for entity_type, rule in self.rules.items():
            if 'custom' in rule:
                found_entities = rule['custom'](text)
            else:
                found_entities = {
                    (match.group(), match.start(), match.end())
                    for pattern in rule.get('patterns', [])
                    for match in re.finditer(pattern, text, re.I)
                }

            for entity_value, start, end in found_entities:
                placeholder = self._get_placeholder(entity_value, entity_type)
                pending_replacements.append((start, end, placeholder))

        # Sort in reverse to not mess up indices
        pending_replacements.sort(reverse=True)
        for start, end, placeholder in pending_replacements:
            text = text[:start] + placeholder + text[end:]

        # Translate placeholders if requested
        if translate and lang != "en":
            text = self._translate_placeholders(text, lang)

        return text
