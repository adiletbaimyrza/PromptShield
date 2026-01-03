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


# =========================
# Memory Size Tests
# =========================

MEMORY_SIZES = [
    "512MB",
    "1GB",
    "256 KB",
    "2TB",
    "64 M",
    "128 G",
    "4 T",
    "16B",
]

@pytest.mark.parametrize("mem", MEMORY_SIZES)
def test_memory_replacement(mem, shield):
    text = f"The server has {mem} of RAM."
    protected = shield.protect(text, translate=False)
    assert mem not in protected
    assert "[MEM_" in protected


# =========================
# CVV Tests
# =========================

CVV_CODES = [
    "CVV: 123",
    "CVC: 4567",
    "CVV-456",
    "CVC 789",
]

@pytest.mark.parametrize("cvv", CVV_CODES)
def test_cvv_replacement(cvv, shield):
    text = f"The security code is {cvv}."
    protected = shield.protect(text, translate=False)
    assert cvv not in protected
    assert "[CVV_" in protected


# =========================
# Expiry Date Tests
# =========================

EXPIRY_DATES = [
    "exp: 12/25",
    "expiry: 01/2027",
    "expires 06-24",
    "exp: 03/26",
]

@pytest.mark.parametrize("exp", EXPIRY_DATES)
def test_expiry_replacement(exp, shield):
    text = f"Card {exp}."
    protected = shield.protect(text, translate=False)
    assert exp not in protected
    assert "[EXP_" in protected


# =========================
# Credit Card Tests
# =========================

CREDIT_CARDS = [
    "4111-1111-1111-1111",
    "4111 1111 1111 1111",
    "4111111111111111",
    "5500-0000-0000-0004",
]

@pytest.mark.parametrize("card", CREDIT_CARDS)
def test_credit_card_replacement(card, shield):
    text = f"My card number is {card}."
    protected = shield.protect(text, translate=False)
    assert card not in protected
    assert "[CARD_" in protected


# =========================
# Date Tests
# =========================

DATES = [
    "25/12/2024",
    "2024/01/15",
    "01-06-2023",
    "3rd",
    "21st",
]

@pytest.mark.parametrize("date", DATES)
def test_date_replacement(date, shield):
    text = f"The event is on {date}."
    protected = shield.protect(text, translate=False)
    assert date not in protected
    assert "[DATE_" in protected


# =========================
# URL Tests
# =========================

URLS = [
    "https://example.com/path",
    "http://subdomain.example.org/page?query=1",
    "www.google.com",
    "https://api.service.io/v1/users",
]

@pytest.mark.parametrize("url", URLS)
def test_url_replacement(url, shield):
    text = f"Visit {url} for more info."
    protected = shield.protect(text, translate=False)
    assert url not in protected
    assert "[URL_" in protected


# =========================
# IP Address Tests
# =========================

IP_ADDRESSES = [
    "IP: 192.168.1.1",
    "ip-10.0.0.1",
    "192.168.0.100",
    "8.8.8.8",
]

@pytest.mark.parametrize("ip", IP_ADDRESSES)
def test_ip_replacement(ip, shield):
    text = f"Connect to {ip}."
    protected = shield.protect(text, translate=False)
    assert ip not in protected
    assert "[IP_" in protected


# =========================
# Place Tests (NER-based)
# =========================

def test_place_replacement(shield):
    text = "I visited Paris and London last summer."
    protected = shield.protect(text, translate=False)
    assert "[PLACE_" in protected
    # At least one city should be replaced
    assert "Paris" not in protected or "London" not in protected


def test_place_country(shield):
    text = "She moved to Germany from Japan."
    protected = shield.protect(text, translate=False)
    assert "[PLACE_" in protected


# =========================
# Bitcoin Address Tests
# =========================

BTC_ADDRESSES = [
    "1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2",
    "3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy",
    "bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq",
]

@pytest.mark.parametrize("btc", BTC_ADDRESSES)
def test_btc_address_replacement(btc, shield):
    text = f"Send BTC to {btc}."
    protected = shield.protect(text, translate=False)
    assert btc not in protected
    assert "[BTC_ADDRESS_" in protected


# =========================
# Ethereum Address Tests
# =========================

ETH_ADDRESSES = [
    "0x742d35Cc6634C0532925a3b844Bc9e7595f8f3E2",
    "0xde0B295669a9FD93d5F28D9Ec85E40f4cb697BAe",
]

@pytest.mark.parametrize("eth", ETH_ADDRESSES)
def test_eth_address_replacement(eth, shield):
    text = f"Send ETH to {eth}."
    protected = shield.protect(text, translate=False)
    assert eth not in protected
    assert "[ETH_ADDRESS_" in protected


# =========================
# Username Tests (Social Media Handles)
# =========================

USERNAMES = [
    "@johndoe",
    "@Tech_News",
    "u/reddit_user",
    "u/python-dev",
]

@pytest.mark.parametrize("username", USERNAMES)
def test_username_replacement(username, shield):
    text = f"Follow me at {username}."
    protected = shield.protect(text, translate=False)
    assert username not in protected
    assert "[USERNAME_" in protected


# =========================
# Alphanumeric Code Tests
# =========================

ALNUM_CODES = [
    "ABC-123",
    "XY789Z",
    "Order-2024-ABC",
]

@pytest.mark.parametrize("code", ALNUM_CODES)
def test_alnum_code_normalization(code, shield):
    text = f"Your code is {code}."
    protected = shield.protect(text, translate=False)
    # alnum_code uses normalize mode, not placeholder
    # Letters become 'A', digits become '0'
    assert code not in protected
    # Check that some normalization happened (A's and 0's present)
    assert "A" in protected or "0" in protected


# =========================
# Coordinates Tests
# =========================

COORDINATES = [
    "40.7128, -74.0060",
    "-33.8688, 151.2093",
    "51.5074, -0.1278",
]

@pytest.mark.parametrize("coords", COORDINATES)
def test_coordinates_replacement(coords, shield):
    text = coords  # Coordinates pattern requires entire line match
    protected = shield.protect(text, translate=False)
    assert coords not in protected
    assert "[COORS_" in protected


# =========================
# Edge Case Tests
# =========================

def test_empty_string(shield):
    text = ""
    protected = shield.protect(text, translate=False)
    assert protected == ""


def test_no_sensitive_data(shield):
    text = "This is a normal sentence with no sensitive information."
    protected = shield.protect(text, translate=False)
    assert protected == text


def test_overlapping_entities(shield):
    # Test that overlapping entities are handled correctly
    text = "Contact support@company.com at +1234567890."
    protected = shield.protect(text, translate=False)
    assert "[EMAIL_" in protected
    assert "[PHONE_" in protected


def test_repeated_entity_same_placeholder(shield):
    # Same entity value should get the same placeholder
    text = "Email alice@test.com then email alice@test.com again."
    protected = shield.protect(text, translate=False)
    # Count occurrences of EMAIL_1 - should be 2
    assert protected.count("[EMAIL_1]") == 2
