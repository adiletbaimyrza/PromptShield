import spacy
from typing import Dict, Tuple, Set
import re

class TextAnonymizer:
    def __init__(self):

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

        #Todo: make a map and store mappings as a file to 'remember' names, like for two docs referencing the same John Smith as name1 in both.
        def _extract_emails(self, text: str) -> Set[Tuple[str, int, int]]:
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
            matches = set()
            for match in re.finditer(email_pattern, text):
                matches.add((match.group(), match.start(), match.end()))
            return matches
        # I think this is the easiest, so later I'll add more of those