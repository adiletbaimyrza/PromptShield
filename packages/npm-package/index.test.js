import { jest, describe, test, expect, beforeEach } from '@jest/globals';
import PromptShield from './index.js';

describe('PromptShield', () => {
    let shield;

    beforeEach(() => {
        shield = new PromptShield();
    });

    // =========================
    // Email Tests
    // =========================

    const VALID_EMAILS = [
        'simple@example.com',
        'very.common@example.com',
        'FirstName.LastName@EasierReading.org',
        'x@example.com',
        'long.email-address-with-hyphens@and.subdomains.example.com',
        'user.name+tag+sorting@example.com',
        'name/surname@example.com',
        'example@s.example',
        'mailhost!username@example.org',
        'user%example.com@example.org',
        'user-@example.org',
    ];

    test.each(VALID_EMAILS)('replaces email: %s', async (email) => {
        const text = `Contact me at ${email}`;
        const result = await shield.protect(text, false);
        expect(result).not.toContain(email);
        expect(result).toContain('[EMAIL_');
    });

    // =========================
    // Phone Tests
    // =========================

    const PHONE_NUMBERS = [
        '+1 415 555 2671',
        '415-555-2671',
        '(415) 555-2671',
        '001-415-555-2671',
        '+44 20 7946 0958',
        '020 7946 0958',
        '+91-9876543210',
        '09876543210',
        '+61 2 9876 5432',
        '(02) 9876 5432',
        '+81-90-1234-5678',
        '090-1234-5678',
        '+49 30 12345678',
        '030 12345678',
        '+33 1 23 45 67 89',
        '01 23 45 67 89',
        '+7 495 123-45-67',
        '8 (495) 123-45-67',
        '+55 11 91234-5678',
        '(11) 91234-5678',
    ];

    test.each(PHONE_NUMBERS)('replaces phone: %s', async (phone) => {
        const text = `Call me at ${phone}.`;
        const result = await shield.protect(text, false);
        expect(result).not.toContain(phone);
        expect(result).toContain('[PHONE_');
    });

    // =========================
    // Amount Tests
    // =========================

    const AMOUNTS = [
        '$123.45',
        '100 USD',
        '200.00 EUR',
        '£50.25',
        'GBP 75',
        '300 dollars',
        '€99.99',
        'USD 1500',
        '1,234.56 USD',
        'JPY 5000',
    ];

    test.each(AMOUNTS)('replaces amount: %s', async (amount) => {
        const text = `The price is ${amount}.`;
        const result = await shield.protect(text, false);
        expect(result).not.toContain(amount);
        expect(result).toContain('[AMOUNT_');
    });

    // =========================
    // Name Tests
    // =========================

    test('replaces names', async () => {
        const text = 'Bob and Bobby are here in the House.';
        const result = await shield.protect(text, false);
        expect(result).toContain('[NAME_');
        expect(result).not.toContain('Bob');
    });

    test('replaces multiple entities', async () => {
        const text = 'Bob sent $50 to bob@example.com and called +1234567890.';
        const result = await shield.protect(text, false);
        expect(result).toContain('[NAME_1]');
        expect(result).toContain('[AMOUNT_1]');
        expect(result).toContain('[EMAIL_1]');
        expect(result).toContain('[PHONE_1]');
        expect(result).not.toContain('Bob');
        expect(result).not.toContain('$50');
        expect(result).not.toContain('bob@example.com');
        expect(result).not.toContain('+1234567890');
    });

    test('no translation for English', async () => {
        const text = 'Bob sent $50 to bob@example.com.';
        const result = await shield.protect(text, false);
        expect(result).toContain('[NAME_1]');
        expect(result).toContain('[AMOUNT_1]');
        expect(result).toContain('[EMAIL_1]');
    });

    // =========================
    // JWT Tests
    // =========================

    test('replaces JWT token', async () => {
        const jwtToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.' +
            'eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWUsImlhdCI6MTUxNjIzOTAyMn0.' +
            'KMUFsIDTnFmyG3nMiGM6H9FNFUROf3wh7SmqJp-QV30';
        const text = `The user's token is ${jwtToken}.`;
        const result = await shield.protect(text, false);
        expect(result).not.toContain(jwtToken);
        expect(result).toContain('[JWT_');
    });

    // =========================
    // Memory Size Tests
    // =========================

    const MEMORY_SIZES = [
        '512MB',
        '1GB',
        '256 KB',
        '2TB',
        '64 M',
        '128 G',
        '4 T',
        '16B',
    ];

    test.each(MEMORY_SIZES)('replaces memory size: %s', async (mem) => {
        const text = `The server has ${mem} of RAM.`;
        const result = await shield.protect(text, false);
        expect(result).not.toContain(mem);
        expect(result).toContain('[MEM_');
    });

    // =========================
    // CVV Tests
    // =========================

    const CVV_CODES = [
        'CVV: 123',
        'CVC: 4567',
        'CVV-456',
        'CVC 789',
    ];

    test.each(CVV_CODES)('replaces CVV: %s', async (cvv) => {
        const text = `The security code is ${cvv}.`;
        const result = await shield.protect(text, false);
        expect(result).not.toContain(cvv);
        expect(result).toContain('[CVV_');
    });

    // =========================
    // Expiry Date Tests
    // =========================

    const EXPIRY_DATES = [
        'exp: 12/25',
        'expiry: 01/2027',
        'expires 06-24',
        'exp: 03/26',
    ];

    test.each(EXPIRY_DATES)('replaces expiry: %s', async (exp) => {
        const text = `Card ${exp}.`;
        const result = await shield.protect(text, false);
        expect(result).not.toContain(exp);
        expect(result).toContain('[EXP_');
    });

    // =========================
    // Credit Card Tests
    // =========================

    const CREDIT_CARDS = [
        '4111-1111-1111-1111',
        '4111 1111 1111 1111',
        '4111111111111111',
        '5500-0000-0000-0004',
    ];

    test.each(CREDIT_CARDS)('replaces credit card: %s', async (card) => {
        const text = `My card number is ${card}.`;
        const result = await shield.protect(text, false);
        expect(result).not.toContain(card);
        expect(result).toContain('[CARD_');
    });

    // =========================
    // Date Tests
    // =========================

    const DATES = [
        '25/12/2024',
        '2024/01/15',
        '01-06-2023',
        '3rd',
        '21st',
    ];

    test.each(DATES)('replaces date: %s', async (date) => {
        const text = `The event is on ${date}.`;
        const result = await shield.protect(text, false);
        expect(result).not.toContain(date);
        expect(result).toContain('[DATE_');
    });

    // =========================
    // URL Tests
    // =========================

    const URLS = [
        'https://example.com/path',
        'http://subdomain.example.org/page?query=1',
        'www.google.com',
        'https://api.service.io/v1/users',
    ];

    test.each(URLS)('replaces URL: %s', async (url) => {
        const text = `Visit ${url} for more info.`;
        const result = await shield.protect(text, false);
        expect(result).not.toContain(url);
        expect(result).toContain('[URL_');
    });

    // =========================
    // IP Address Tests
    // =========================

    const IP_ADDRESSES = [
        'IP: 192.168.1.1',
        'ip-10.0.0.1',
        '192.168.0.100',
        '8.8.8.8',
    ];

    test.each(IP_ADDRESSES)('replaces IP: %s', async (ip) => {
        const text = `Connect to ${ip}.`;
        const result = await shield.protect(text, false);
        expect(result).not.toContain(ip);
        expect(result).toContain('[IP_');
    });

    // =========================
    // Place Tests (NER-based)
    // =========================

    test('replaces places', async () => {
        const text = 'I visited Paris and London last summer.';
        const result = await shield.protect(text, false);
        expect(result).toContain('[PLACE_');
    });

    test('replaces country names', async () => {
        const text = 'She moved to Germany from Japan.';
        const result = await shield.protect(text, false);
        expect(result).toContain('[PLACE_');
    });

    // =========================
    // Bitcoin Address Tests
    // =========================

    const BTC_ADDRESSES = [
        '1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2',
        '3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy',
        'bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq',
    ];

    test.each(BTC_ADDRESSES)('replaces BTC address: %s', async (btc) => {
        const text = `Send BTC to ${btc}.`;
        const result = await shield.protect(text, false);
        expect(result).not.toContain(btc);
        expect(result).toContain('[BTC_ADDRESS_');
    });

    // =========================
    // Ethereum Address Tests
    // =========================

    const ETH_ADDRESSES = [
        '0x742d35Cc6634C0532925a3b844Bc9e7595f8f3E2',
        '0xde0B295669a9FD93d5F28D9Ec85E40f4cb697BAe',
    ];

    test.each(ETH_ADDRESSES)('replaces ETH address: %s', async (eth) => {
        const text = `Send ETH to ${eth}.`;
        const result = await shield.protect(text, false);
        expect(result).not.toContain(eth);
        expect(result).toContain('[ETH_ADDRESS_');
    });

    // =========================
    // Username Tests
    // =========================

    const USERNAMES = [
        '@johndoe',
        '@Tech_News',
        'u/reddit_user',
        'u/python-dev',
    ];

    test.each(USERNAMES)('replaces username: %s', async (username) => {
        const text = `Follow me at ${username}.`;
        const result = await shield.protect(text, false);
        expect(result).not.toContain(username);
        expect(result).toContain('[USERNAME_');
    });

    // =========================
    // Alphanumeric Code Tests
    // =========================

    const ALNUM_CODES = [
        'ABC-123',
        'XY789Z',
        'Order-2024-ABC',
    ];

    test.each(ALNUM_CODES)('normalizes alphanumeric code: %s', async (code) => {
        const text = `Your code is ${code}.`;
        const result = await shield.protect(text, false);
        expect(result).not.toContain(code);
        // Check normalization happened
        expect(result).toMatch(/[A0]/);
    });

    // =========================
    // Coordinates Tests
    // =========================

    const COORDINATES = [
        '40.7128, -74.0060',
        '-33.8688, 151.2093',
        '51.5074, -0.1278',
    ];

    test.each(COORDINATES)('replaces coordinates: %s', async (coords) => {
        const text = coords; // Coordinates pattern requires entire line match
        const result = await shield.protect(text, false);
        expect(result).not.toContain(coords);
        expect(result).toContain('[COORS_');
    });

    // =========================
    // Edge Case Tests
    // =========================

    test('handles empty string', async () => {
        const text = '';
        const result = await shield.protect(text, false);
        expect(result).toBe('');
    });

    test('handles text with no sensitive data', async () => {
        const text = 'This is a normal sentence with no sensitive information.';
        const result = await shield.protect(text, false);
        expect(result).toBe(text);
    });

    test('handles overlapping entities', async () => {
        const text = 'Contact support@company.com at +1234567890.';
        const result = await shield.protect(text, false);
        expect(result).toContain('[EMAIL_');
        expect(result).toContain('[PHONE_');
    });

    test('uses same placeholder for repeated entities', async () => {
        const text = 'Email alice@test.com then email alice@test.com again.';
        const result = await shield.protect(text, false);
        const matches = result.match(/\[EMAIL_1\]/g);
        expect(matches).toHaveLength(2);
    });

    // =========================
    // Original Tests (preserved)
    // =========================

    test('maintains correct order of replacements', async () => {
        const text = 'John Doe has $500 and email john@example.com';
        const result = await shield.protect(text, false);
        expect(result).toContain('[NAME_');
        expect(result).toContain('[AMOUNT_');
        expect(result).toContain('[EMAIL_');
    });

    test('caches placeholders for repeated entities', async () => {
        const text = 'Email: john@example.com, again: john@example.com';
        const result = await shield.protect(text, false);
        const matches = result.match(/\[EMAIL_\d+\]/g);
        expect(matches).toHaveLength(2);
        expect(matches[0]).toBe(matches[1]);
    });

    test('does not translate placeholders when translatePlaceholders is false', async () => {
        const text = 'Contact me at john.doe@example.com';
        const result = await shield.protect(text, false);
        expect(result).toMatch(/\[EMAIL_\d+\]/);
    });

    test('detects language correctly', async () => {
        const text = 'Hello, my name is John Doe';
        const result = await shield.protect(text, false);
        expect(result).toContain('[NAME_');
    });
});
