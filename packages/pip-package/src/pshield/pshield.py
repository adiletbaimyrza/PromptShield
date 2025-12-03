import spacy
import json
import os
from pathlib import Path
from typing import Dict, Tuple, Set
import re
from langdetect import detect
from deep_translator import GoogleTranslator


class PromptShield:
    def __init__(self, mapping_file: str = ".anonymizer_mappings.json"):
        self.mapping_file = Path(mapping_file)
        self.name_mappings: Dict[str, str] = {}
        self.email_mappings: Dict[str, str] = {}
        self.phone_mappings: Dict[str, str] = {}
        self.address_mappings: Dict[str, str] = {}
        self.amount_mask = "amt"

        self.name_counter = 0
        self.email_counter = 0
        self.phone_counter = 0
        self.address_counter = 0
        
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            raise RuntimeError(
                "spaCy model 'en_core_web_sm' not found. "
                "Install it with: python -m spacy download en_core_web_sm"
                "or install it with: pip -r requirements.txt"
            )

    def _save_mappings(self):
        data = {
            'names': self.name_mappings,
            'emails': self.email_mappings,
            'phones': self.phone_mappings,
            'addresses': self.address_mappings,
            'name_counter': self.name_counter,
            'email_counter': self.email_counter,
            'phone_counter': self.phone_counter,
            'address_counter': self.address_counter
        }
        with open(self.mapping_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def _get_or_create_mapping(self, entity: str, entity_type: str) -> str:
        if entity_type == 'name':
            if entity not in self.name_mappings:
                self.name_counter += 1
                self.name_mappings[entity] = f"name{self.name_counter}"
            return self.name_mappings[entity]
        elif entity_type == 'email':
            if entity not in self.email_mappings:
                self.email_counter += 1
                self.email_mappings[entity] = f"email{self.email_counter}"
            return self.email_mappings[entity]
        elif entity_type == 'phone':
            if entity not in self.phone_mappings:
                self.phone_counter += 1
                self.phone_mappings[entity] = f"phone{self.phone_counter}"
            return self.phone_mappings[entity]
        elif entity_type == 'address':
            if entity not in self.address_mappings:
                self.address_counter += 1
                self.address_mappings[entity] = f"address{self.address_counter}"
            return self.address_mappings[entity]
        return entity

    def _extract_emails(self, text: str) -> Set[Tuple[str, int, int]]:
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
        matches = set()
        for match in re.finditer(email_pattern, text):
            matches.add((match.group(), match.start(), match.end()))
        return matches

    def _extract_phones(self, text: str) -> Set[Tuple[str, int, int]]:
        phone_patterns = [
            r'\+?\d{1,3}[-.\\s]?\(?\d{1,4}\)?[-.\\s]?\d{1,4}[-.\\s]?\d{1,9}',
            r'\(?\d{3}\)?[-.\\s]?\d{3}[-.\\s]?\d{4}',
            r'\d{3}[-.\\s]?\d{3}[-.\\s]?\d{4}'
        ]
        matches = set()
        for pattern in phone_patterns:
            for match in re.finditer(pattern, text):
                phone = match.group()
                if len(re.sub(r'\D', '', phone)) >= 10:
                    matches.add((phone, match.start(), match.end()))
        return matches

    def _extract_amounts(self, text: str) -> Set[Tuple[str, int, int]]:
        amount_patterns = [
            r'\$\s?\d+(?:,\d{3})*(?:\.\d{2})?',
            r'\d+(?:,\d{3})*(?:\.\d{2})?\s?(?:USD|EUR|GBP|dollars?|euros?|pounds?)',
            r'(?:USD|EUR|GBP)\s?\d+(?:,\d{3})*(?:\.\d{2})?'
        ]
        matches = set()
        for pattern in amount_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                matches.add((match.group(), match.start(), match.end()))
        return matches

    def _extract_addresses(self, text: str) -> Set[Tuple[str, int, int]]:
        pass

    def _extract_names(self, text: str) -> Set[Tuple[str, int, int]]:
        doc = self.nlp(text)
        matches = set()
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                matches.add((ent.text, ent.start_char, ent.end_char))
        return matches

    def anonymize(self, text: str) -> str:
        """Anonymize sensitive information in text."""
        replacements = []

        emails = self._extract_emails(text)
        for email, start, end in emails:
            masked = self._get_or_create_mapping(email.lower(), 'email')
            replacements.append((start, end, masked))

        phones = self._extract_phones(text)
        for phone, start, end in phones:
            normalized_phone = re.sub(r'\D', '', phone)
            masked = self._get_or_create_mapping(normalized_phone, 'phone')
            replacements.append((start, end, masked))

        amounts = self._extract_amounts(text)
        for amount, start, end in amounts:
            replacements.append((start, end, self.amount_mask))

        names = self._extract_names(text)
        for name, start, end in names:
            masked = self._get_or_create_mapping(name, 'name')
            replacements.append((start, end, masked))

        replacements.sort(key=lambda x: x[0], reverse=True)

        result = text
        for start, end, replacement in replacements:
            result = result[:start] + replacement + result[end:]

        self._save_mappings()

        return result

    def protect(self, prompt: str) -> str:
        """Alias for anonymize method for backward compatibility."""
        return self.anonymize(prompt)

    def anonymize_with_translation(self, text: str, patterns: list = None, labels: list = None) -> str:
        """
        Legacy anonymization with language detection and translation.
        
        Args:
            text: Text to anonymize
            patterns: List of regex patterns (uses defaults if None)
            labels: List of Polish labels to translate (uses defaults if None)
        
        Returns:
            Anonymized text with translated labels
        """
        # Default patterns for Polish-style anonymization
        default_patterns = [
            r'\d{3}[- ]?\d{3}[- ]?\d{3}',
            r'\S*@\S*\.\S*',
            r'[A-ZĆŁŃŚŻŹ][a-zążźćęóńł]+ [A-ZĆŁŃŚŻŹ][a-zążźćęóńł]+',
            r'\d+[.,]\d{2}zł',
            r'\d{2}[.-]\d{2}[.-]\d{4}',
            r'\d{2}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}'
        ]
        
        default_labels = ["NUMER TELEFONu", "MAIL", "OSOBA", "KWOTA", "DATA", "NUMER KONTA"]
        
        patterns = patterns or default_patterns
        labels = labels or default_labels
        
        for idx in range(len(patterns)):
            pattern = patterns[idx]
            lang = detect(text)
            label = GoogleTranslator(source="pl", target=lang).translate(labels[idx])
            number_map = {}
            counter = 0

            def replace(match):
                nonlocal counter
                number = re.sub("[- ]", "", match)
                if number not in number_map:
                    number_map[number] = label + f"{counter}"
                    counter += 1
                return number_map[number]

            text = re.sub(pattern, lambda m: replace(m.group(0)), text)

        return text