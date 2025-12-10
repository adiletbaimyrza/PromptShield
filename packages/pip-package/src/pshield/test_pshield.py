import pytest
from pshield import PromptShield

@pytest.fixture
def shield():
    return PromptShield()

def test_email_replacement(shield):
    text = "Contact me at test@example.com."
    protected = shield.protect(text, translate=False)
    assert "[EMAIL_1]" in protected
    assert "test@example.com" not in protected

def test_phone_replacement(shield):
    text = "Call me at +1 234-567-8900."
    protected = shield.protect(text, translate=False)
    assert "[PHONE_1]" in protected
    assert "+1 234-567-8900" not in protected

def test_amount_replacement(shield):
    text = "The price is $123.45 or 100 USD."
    protected = shield.protect(text, translate=False)
    assert "[AMOUNT_1]" in protected or "[AMOUNT_2]" in protected
    assert "$123.45" not in protected
    assert "100 USD" not in protected

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
