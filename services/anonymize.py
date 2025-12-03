import re
from langdetect import detect
from deep_translator import GoogleTranslator

# Legacy patterns and labels for backward compatibility
patterns = [
    r'\d{3}[- ]?\d{3}[- ]?\d{3}',
    r'\S*@\S*\.\S*',
    r'[A-ZĆŁŃŚŻŹ][a-zążźćęóńł]+ [A-ZĆŁŃŚŻŹ][a-zążźćęóńł]+',
    r'\d+[.,]\d{2}zł',
    r'\d{2}[.-]\d{2}[.-]\d{4}',
    r'\d{2}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}'
]

labels = ["NUMER TELEFONu", "MAIL", "OSOBA", "KWOTA", "DATA", "NUMER KONTA"]


def anonymize(text, r=None, n=None):
    """
    Anonymize sensitive information in text.
    
    If called with default parameters, uses the new TextAnonymizer with NLP.
    If called with custom patterns (r) and labels (n), uses legacy regex-based approach.
    """
    # If custom patterns provided, use legacy implementation
    if r is not None and n is not None:
        return _legacy_anonymize(text, r, n)
    
    # Try to use new TextAnonymizer
    try:
        from anonymizer import TextAnonymizer
        anonymizer = TextAnonymizer()
        return anonymizer.anonymize(text)
    except (ImportError, RuntimeError):
        # Fallback to legacy implementation if TextAnonymizer unavailable
        return _legacy_anonymize(text, patterns, labels)


def _legacy_anonymize(text, r=patterns, n=labels):
    """Legacy regex-based anonymization with translation."""
    for i in range(len(r)):
        pattern = r[i]
        lang = detect(text)
        label = GoogleTranslator(source="pl", target=lang).translate(n[i])
        number_map = {}
        i = 0

        def replace(number):
            nonlocal i
            number = re.sub("[- ]", "", number)
            if number not in number_map:
                number_map[number] = label + f"{i}"
                i += 1
            return number_map[number]

        text = re.sub(pattern, lambda m: replace(m.group(0)), text)

    return text

