import pytest
from pshield import PromptShield

@pytest.fixture
def shield():
    return PromptShield()

def test_email_replacement(shield):
    text = "john.doe@example.com email example"
    protected = shield.protect(text, translate=False)
    assert "[EMAIL_1]" in protected
    assert "john.doe@example.com" not in protected

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


def test_address_replacement(shield):
    text = "Send it to 123 Main St, Springfield, IL 62704."
    protected = shield.protect(text, translate=False)
    assert "[ADDRESS_1]" in protected
    assert "123 Main St, Springfield, IL 62704" not in protected

def test_date_replacement(shield):
    text = "The deadline is 2025-12-31 or 12/31/2025."
    protected = shield.protect(text, translate=False)
    assert "[DATE_1]" in protected
    assert "[DATE_2]" in protected
    assert "2025-12-31" not in protected
    assert "12/31/2025" not in protected

def test_credit_card_replacement(shield):
    text = "My card number is 4111 1111 1111 1111."
    protected = shield.protect(text, translate=False)
    assert "[CREDIT_CARD_1]" in protected
    assert "4111 1111 1111 1111" not in protected

def test_ssn_replacement(shield):
    text = "His SSN is 123-45-6789."
    protected = shield.protect(text, translate=False)
    assert "[SSN_1]" in protected
    assert "123-45-6789" not in protected

def test_ip_replacement(shield):
    text = "Server IPs are 192.168.0.1 and 2001:0db8:85a3:0000:0000:8a2e:0370:7334."
    protected = shield.protect(text, translate=False)
    assert "[IP_1]" in protected
    assert "[IP_2]" in protected
    assert "192.168.0.1" not in protected
    assert "2001:0db8:85a3:0000:0000:8a2e:0370:7334" not in protected

def test_url_replacement(shield):
    text = "Visit https://example.com or example.org for details."
    protected = shield.protect(text, translate=False)
    assert "[URL_1]" in protected
    assert "[URL_2]" in protected
    assert "https://example.com" not in protected
    assert "example.org" not in protected

def test_username_replacement(shield):
    text = "My username is @john_doe123."
    protected = shield.protect(text, translate=False)
    assert "[USERNAME_1]" in protected
    assert "john_doe123" not in protected

def test_cryptocurrency_address_replacement(shield):
    text = "Send BTC to 1BoatSLRHtKNngkdXEeobR76b53LETtpyT or ETH to 0x32be343b94f860124dc4fee278fdcbd38c102d88."
    protected = shield.protect(text, translate=False)
    assert "[CRYPTOCURRENCY_ADDRESS_1]" in protected
    assert "[CRYPTOCURRENCY_ADDRESS_2]" in protected
    assert "1BoatSLRHtKNngkdXEeobR76b53LETtpyT" not in protected
    assert "0x32be343b94f860124dc4fee278fdcbd38c102d88" not in protected

def test_token_replacement(shield):
    text = "The JWT is eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.K6w9D4p8..."
    protected = shield.protect(text, translate=False)
    assert "[TOKEN_1]" in protected
    assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.K6w9D4p8" not in protected