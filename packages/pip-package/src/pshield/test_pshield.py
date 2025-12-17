import pytest
from pshield import PromptShield

@pytest.fixture
def shield():
    return PromptShield()


VALID_EMAILS = [
    "simple@example.com",
    "very.common@example.com",
    "FirstName.LastName@EasierReading.org",
    "x@example.com",
    "long.email-address-with-hyphens@and.subdomains.example.com",
    "user.name+tag+sorting@example.com",
    "name/surname@example.com",
    "example@s.example",
    "mailhost!username@example.org",
    "user%example.com@example.org",
    "user-@example.org",
]

@pytest.mark.parametrize("email", VALID_EMAILS)
def test_email_replacement(email, shield):
    text = f"Contact me at {email}"
    protected = shield.protect(text, translate=False)

    assert email not in protected
    assert "[EMAIL_" in protected

PHONE_NUMBERS = [
    "+1 415 555 2671",           # US international format
    "415-555-2671",              # US standard with hyphens
    "(415) 555-2671",            # US with parentheses
    "001-415-555-2671",          # International dialing prefix
    "+44 20 7946 0958",          # UK London
    "020 7946 0958",             # UK local format
    "+91-9876543210",            # India
    "09876543210",                # India local
    "+61 2 9876 5432",           # Australia
    "(02) 9876 5432",            # Australia local
    "+81-90-1234-5678",          # Japan mobile
    "090-1234-5678",             # Japan local
    "+49 30 12345678",           # Germany Berlin
    "030 12345678",               # Germany local
    "+33 1 23 45 67 89",         # France
    "01 23 45 67 89",             # France local
    "+7 495 123-45-67",          # Russia Moscow
    "8 (495) 123-45-67",         # Russia local
    "+55 11 91234-5678",         # Brazil mobile
    "(11) 91234-5678",           # Brazil local
]

@pytest.mark.parametrize("phone", PHONE_NUMBERS)
def test_phone_replacement(phone, shield):
    text = f"Call me at {phone}."
    protected = shield.protect(text, translate=False)

    assert phone not in protected
    assert "[PHONE_" in protected

AMOUNTS = [
    "$123.45",
    "100 USD",
    "200.00 EUR",
    "£50.25",
    "GBP 75",
    "300 dollars",
    "€99.99",
    "USD 1500",
    "1,234.56 USD",
    "JPY 5000",
]

@pytest.mark.parametrize("amount", AMOUNTS)
def test_amount_replacement(amount, shield):
    text = f"The price is {amount}."
    protected = shield.protect(text, translate=False)

    # The amount should be replaced
    assert amount not in protected

    # There should be a placeholder for the amount
    assert "[AMOUNT_" in protected


def test_name_replacement(shield):
    text = "Bob and Bobby are here in the House."
    protected = shield.protect(text, translate=False)
    assert "[NAME_1]" in protected
    assert "[NAME_2]" in protected
    assert "Bob" not in protected
    assert "Bobby" not in protected
    assert "House" in protected  # non-PERSON entity remains

def test_multiple_entities(shield):
    text = "Bob sent $50 to bob@example.com and called +1234567890."
    protected = shield.protect(text, translate=False)
    # check all placeholder types exist
    assert "[NAME_1]" in protected
    assert "[AMOUNT_1]" in protected
    assert "[EMAIL_1]" in protected
    assert "[PHONE_1]" in protected
    # check original values removed
    assert "Bob" not in protected
    assert "$50" not in protected
    assert "bob@example.com" not in protected
    assert "+1234567890" not in protected

def test_translation_to_french(shield):
    text = "Bob a envoyé 50 USD à bob@example.com."
    protected = shield.protect(text, translate=True)
    # placeholders should now be translated to French
    # deep-translator returns lowercase translation; our class converts to uppercase
    assert "[NOM_1]" in protected
    assert "[MONTANT_1]" in protected
    assert "[E-MAIL_1]" in protected
    # original text removed
    assert "Bob" not in protected
    assert "$50" not in protected
    assert "bob@example.com" not in protected

def test_translation_with_multiple_languages(shield):
    # Spanish sentence
    text = "Carlos pagó 100 USD a maria@example.com."
    protected = shield.protect(text, translate=True)
    assert "[NOMBRE_1]" in protected
    assert "[CANTIDAD_1]" in protected
    assert "[CORREO ELECTRÓNICO_1]" in protected
    # original text removed
    assert "Carlos" not in protected
    assert "100 USD" not in protected
    assert "maria@example.com" not in protected

def test_no_translation_for_english(shield):
    text = "Bob sent $50 to bob@example.com."
    protected = shield.protect(text, translate=False)
    # placeholders remain in English
    assert "[NAME_1]" in protected
    assert "[AMOUNT_1]" in protected
    assert "[EMAIL_1]" in protected

def test_jwt_replacement(shield):
    jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9." \
                "eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWUsImlhdCI6MTUxNjIzOTAyMn0." \
                "KMUFsIDTnFmyG3nMiGM6H9FNFUROf3wh7SmqJp-QV30"
    
    text = f"The user's token is {jwt_token}."
    protected = shield.protect(text, translate=False)

    assert jwt_token not in protected
    assert "[JWT_" in protected
