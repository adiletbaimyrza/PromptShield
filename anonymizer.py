import spacy
import json
import os
from pathlib import Path
from typing import Dict, Tuple, Set
import re

class TextAnonymizer:
    def __init__(self, mapping_file: str = ".anonymizer_mappings.json"):

        self.mapping_file = Path(mapping_file)
        self.name_mappings: Dict[str, str] = {} # nlp
        self.email_mappings: Dict[str, str] = {} #simple regex
        self.phone_mappings: Dict[str, str] = {} #regexable esp for the multinational ones
        self.address_mappings: Dict[str, str] = {} # nlp ?
        self.amount_mask = "amt"

        self.name_counter = 0
        self.email_counter = 0
        self.phone_counter = 0
        self.address_counter = 0
        # Later I guess we could swap to our own logic, for now this lib will do. emails can be regexed, but I don't think anything else can be understood without context like [A-Z]*+ [A-z]*+\. will match John Smith
        # But it will also match Jagiellonian University. One of them is a person's name the other Isn't
        # Also more languages than just core english should be implemented. So maybe I should make it as an input param.
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

    #Todo: make a map and store mappings as a file to 'remember' names, like for two docs referencing the same John Smith as name1 in both.
    def _extract_emails(self, text: str) -> Set[Tuple[str, int, int]]:
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
        matches = set()
        for match in re.finditer(email_pattern, text):
            matches.add((match.group(), match.start(), match.end()))
        return matches
    # I think this is the easiest, so later I'll add more of those
    def _extract_phones(self, text: str) -> Set[Tuple[str, int, int]]:
        phone_patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}'
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
    #
    # Todo: extract_addresses
    def _extract_addresses(self, text: str) -> Set[Tuple[str, int, int]]:
        pass
    #
    # Todo: improve name extraction logic. Currently: "John paid him $20. Then Jane paid him $5" would think that Then Jane is a person
    #
    def _extract_names(self, text: str) -> Set[Tuple[str, int, int]]:
        doc = self.nlp(text)
        matches = set()
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                matches.add((ent.text, ent.start_char, ent.end_char))
        return matches

    def anonymize(self, text: str) -> str:
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