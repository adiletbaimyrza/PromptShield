import spacy
import re
from langdetect import detect
from deep_translator import GoogleTranslator
from typing import Dict, List, Tuple, Any

PlaceholdersCache = Dict[str, Dict[str, Dict[str, str]]]
Rules = Dict[str, Dict[str, Any]]

class PromptShield:
    PLACEHOLDER_PATTERN = re.compile(r"\[(\w+)_\d+\]")

    def __init__(self, nlp=None):
        self.ner = nlp or spacy.load("en_core_web_sm")
        self.placeholders_cache: PlaceholdersCache = {}
        # Rules with priority (higher number = higher priority)
        self.rules: Rules = {
            'email': {
                'priority': 110,
                'patterns': [
                    r'(?:[a-z0-9!#$%&\'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&\'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])'
                ]
            },
            'token': {
                'priority': 105,
                'patterns': [
                    # JWT (Header.Payload.Signature) - relaxed to catch standard JWTs
                    r'\b[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\b',
                    # Common token formats
                    r'e[yw][A-Za-z0-9-_]+\.(?:e[yw][A-Za-z0-9-_]+)?\.[A-Za-z0-9-_]{2,}'
                ]
            },
            'ip': {
                'priority': 106,
                'patterns': [
                    r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
                    r'\b([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b'
                ]
            },
            'url': {
                'priority': 100,
                'patterns': [
                    r'https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)',
                    r'[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)'
                ]
            },
            'address': {
                'priority': 95,
                'patterns': [
                    r'\d{1,5}\s\w+(\s\w+){0,5},?\s\w+,\s[A-Z]{2}\s\d{5}'
                ]
            },
            'cryptocurrency_address': {
                'priority': 80,
                'patterns': [
                    r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b',
                    r'\bX[1-9A-HJ-NP-Za-km-z]{33}\b',
                    r'\b0x[0-9a-fA-F]{40}\b',
                    r'\bL[a-km-zA-HJ-NP-Z1-9]{26,33}\b',
                    r'\br[1-9A-HJ-NP-Za-km-z]{25,33}\b'
                ]
            },
            'credit_card': {
                'priority': 75,
                'patterns': [
                    r'\b(?:\d[ -]*?){13,16}\b',
                    r'\b[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}([A-Z0-9]?){0,16}\b',
                    r'\b[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?\b'
                ]
            },
            'ssn': {
                'priority': 70,
                'patterns': [
                    r'\b\d{3}-\d{2}-\d{4}\b'
                ]
            },
            'username': {
                'priority': 60,
                'patterns': [
                    r'@\w+'
                ]
            },
            'date': {
                'priority': 50,
                'patterns': [
                    r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
                    r'\b\d{4}-\d{2}-\d{2}\b'
                ]
            },
            'amount': {
                'priority': 40,
                'patterns': [
                    r'\$\s?\d+(?:,\d{3})*(?:\.\d{2})?',
                    r'\d+(?:,\d{3})*(?:\.\d{2})?\s?(?:USD|EUR|GBP|dollars?)',
                    r'(?:USD|EUR|GBP)\s?\d+'
                ]
            },
            'phone': {
                'priority': 30,
                'patterns': [
                    # More specific phone regex to reduce false positives
                    r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
                ]
            },
            'name': {
                'priority': 10,
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
                translated_type = GoogleTranslator(source='en', target=target_lang.lower()).translate(entity_type.lower())
                return f"[{translated_type.upper()}_{placeholder.split('_')[1][:-1]}]"
            except:
                return placeholder
        return self.PLACEHOLDER_PATTERN.sub(repl, text)

    def protect(self, text: str, translate=True) -> str:
        # Detect language
        try:
            lang = detect(text)
        except:
            lang = "en"

        all_matches = []

        # Collect all matches from all rules
        for entity_type, rule in self.rules.items():
            priority = rule.get('priority', 0)
            if 'custom' in rule:
                found_entities = rule['custom'](text)
                for value, start, end in found_entities:
                    all_matches.append({
                        'start': start,
                        'end': end,
                        'value': value,
                        'type': entity_type,
                        'priority': priority
                    })
            else:
                for pattern in rule.get('patterns', []):
                    for match in re.finditer(pattern, text, re.I):
                        all_matches.append({
                            'start': match.start(),
                            'end': match.end(),
                            'value': match.group(),
                            'type': entity_type,
                            'priority': priority
                        })

        # Sort matches:
        # 1. Start position (ascending)
        # 2. Priority (descending)
        # 3. Length (descending) - prefer longer matches if priorities are equal
        all_matches.sort(key=lambda x: (x['start'], -x['priority'], -(x['end'] - x['start'])))

        # Resolve overlaps
        final_matches = []
        last_end = 0

        # Since we sorted by start, we can iterate and check overlaps
        # But simply iterating isn't enough because a high priority match might start later but overlap
        # However, we want to prioritize higher priority matches regardless of position?
        # No, usually we scan left to right. If we have overlapping matches at the same position, priority wins.
        # If we have a match that starts later but overlaps a previous one, what do we do?
        # E.g. "123-456-7890" -> Phone vs "123" -> Number
        # Phone (prio 30) vs Number (prio ?).
        # Let's use a boolean mask or simply check against accepted matches.

        # Better approach: Sort by Priority DESC first, then Start ASC.
        # Then pick if not overlapping with already picked.
        all_matches.sort(key=lambda x: (-x['priority'], x['start'], -(x['end'] - x['start'])))

        accepted_matches = []
        occupied_indices = set()

        for match in all_matches:
            start, end = match['start'], match['end']
            # Check if any character in this range is already occupied
            is_occupied = False
            for i in range(start, end):
                if i in occupied_indices:
                    is_occupied = True
                    break
            
            if not is_occupied:
                accepted_matches.append(match)
                for i in range(start, end):
                    occupied_indices.add(i)

        # Sort accepted matches by start position for replacement
        accepted_matches.sort(key=lambda x: x['start'], reverse=True)

        for match in accepted_matches:
            start, end = match['start'], match['end']
            entity_value = match['value']
            entity_type = match['type']
            placeholder = self._get_placeholder(entity_value, entity_type)
            text = text[:start] + placeholder + text[end:]

        # Translate placeholders if requested
        if translate and lang != "en":
            text = self._translate_placeholders(text, lang)

        return text

