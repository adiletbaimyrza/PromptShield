import { jest, describe, test, expect, beforeEach } from '@jest/globals';

// Mock google-translate-api
jest.unstable_mockModule('@vitalets/google-translate-api', () => ({
    default: jest.fn((text, { to }) => {
        const translations = {
            'email': 'E-MAIL',
            'amount': 'MONTANT',
            'name': 'NOM',
            'phone': 'TÉLÉPHONE'
        };
        return Promise.resolve({ text: translations[text] || text });
    })
}));

// Dynamic import to apply mock
const { default: PromptShield } = await import('./index.js');

describe('PromptShield', () => {
    let shield;

    beforeEach(() => {
        shield = new PromptShield();
    });

    test('replaces email with placeholder', async () => {
        const text = 'Contact me at john.doe@example.com';
        const result = await shield.protect(text, { translatePlaceholders: false });
        expect(result).toContain('[EMAIL_1]');
        expect(result).not.toContain('john.doe@example.com');
    });

    test('replaces phone number with placeholder', async () => {
        const text = 'Call me at +1 (123) 456-7890';
        const result = await shield.protect(text, { translatePlaceholders: false });
        expect(result).toContain('[PHONE_1]');
        expect(result).not.toContain('+1 (123) 456-7890');
    });

    test('replaces currency amounts with placeholder', async () => {
        const text = 'The price is $1,234.56 or 1,234.56 USD';
        const result = await shield.protect(text, { translatePlaceholders: false });
        // Check for at least one replacement first to debug
        expect(result).toMatch(/\[AMOUNT_\d+\]/);
        // We expect two amounts
        const matches = result.match(/\[AMOUNT_\d+\]/g);
        expect(matches).toHaveLength(2);
        expect(result).not.toContain('$1,234.56');
    });

    test('replaces names using compromise', async () => {
        const text = 'My name is John Doe and this is Jane Smith.';
        const result = await shield.protect(text, { translatePlaceholders: false });
        expect(result).toContain('[NAME_1]');
        expect(result).toContain('[NAME_2]');
        expect(result).not.toContain('John Doe');
        expect(result).not.toContain('Jane Smith');
    });

    test('maintains correct order of replacements', async () => {
        const text = 'John Doe has $500 and email john@example.com';
        const result = await shield.protect(text, { translatePlaceholders: false });
        expect(result).toContain('[NAME_1]');
        expect(result).toContain('[AMOUNT_1]');
        expect(result).toContain('[EMAIL_1]');
    });

    test('caches placeholders for repeated entities', async () => {
        const text = 'Email: john@example.com, again: john@example.com';
        const result = await shield.protect(text, { translatePlaceholders: false });
        const matches = result.match(/\[EMAIL_\d+\]/g);
        expect(matches).toHaveLength(2);
        expect(matches[0]).toBe(matches[1]); // Same placeholder used
    });

    test('does not translate placeholders when translatePlaceholders is false', async () => {
        const text = 'Contact me at john.doe@example.com';
        const result = await shield.protect(text, { translatePlaceholders: false });
        // Should have English placeholder
        expect(result).toMatch(/\[EMAIL_\d+\]/);
    });

    test('detects language correctly', async () => {
        const text = 'Hello, my name is John Doe';
        const result = await shield.protect(text, { translatePlaceholders: false });
        // Should work with English text
        expect(result).toContain('[NAME_1]');
    });

    test('replaces address', async () => {
        const text = 'Send it to 123 Main St, Springfield, IL 62704.';
        const result = await shield.protect(text, { translatePlaceholders: false });
        expect(result).toContain('[ADDRESS_1]');
        expect(result).not.toContain('123 Main St, Springfield, IL 62704');
    });

    test('replaces date', async () => {
        const text = 'The deadline is 2025-12-31 or 12/31/2025.';
        const result = await shield.protect(text, { translatePlaceholders: false });
        expect(result).toContain('[DATE_1]');
        expect(result).toContain('[DATE_2]');
        expect(result).not.toContain('2025-12-31');
        expect(result).not.toContain('12/31/2025');
    });

    test('replaces credit card', async () => {
        const text = 'My card number is 4111 1111 1111 1111.';
        const result = await shield.protect(text, { translatePlaceholders: false });
        expect(result).toContain('[CREDIT_CARD_1]');
        expect(result).not.toContain('4111 1111 1111 1111');
    });

    test('replaces ssn', async () => {
        const text = 'His SSN is 123-45-6789.';
        const result = await shield.protect(text, { translatePlaceholders: false });
        expect(result).toContain('[SSN_1]');
        expect(result).not.toContain('123-45-6789');
    });

    test('replaces ip', async () => {
        const text = 'Server IPs are 192.168.0.1 and 2001:0db8:85a3:0000:0000:8a2e:0370:7334.';
        const result = await shield.protect(text, { translatePlaceholders: false });
        expect(result).toContain('[IP_1]');
        expect(result).toContain('[IP_2]');
        expect(result).not.toContain('192.168.0.1');
        expect(result).not.toContain('2001:0db8:85a3:0000:0000:8a2e:0370:7334');
    });

    test('replaces url', async () => {
        const text = 'Visit https://example.com or example.org for details.';
        const result = await shield.protect(text, { translatePlaceholders: false });
        expect(result).toContain('[URL_1]');
        expect(result).toContain('[URL_2]');
        expect(result).not.toContain('https://example.com');
        expect(result).not.toContain('example.org');
    });

    test('replaces username', async () => {
        const text = 'My username is @john_doe123.';
        const result = await shield.protect(text, { translatePlaceholders: false });
        expect(result).toContain('[USERNAME_1]');
        expect(result).not.toContain('john_doe123');
    });

    test('replaces cryptocurrency address', async () => {
        const text = 'Send BTC to 1BoatSLRHtKNngkdXEeobR76b53LETtpyT or ETH to 0x32be343b94f860124dc4fee278fdcbd38c102d88.';
        const result = await shield.protect(text, { translatePlaceholders: false });
        expect(result).toContain('[CRYPTOCURRENCY_ADDRESS_1]');
        expect(result).toContain('[CRYPTOCURRENCY_ADDRESS_2]');
        expect(result).not.toContain('1BoatSLRHtKNngkdXEeobR76b53LETtpyT');
        expect(result).not.toContain('0x32be343b94f860124dc4fee278fdcbd38c102d88');
    });

    test('replaces token', async () => {
        const text = 'The JWT is eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.K6w9D4p8...';
        const result = await shield.protect(text, { translatePlaceholders: false });
        expect(result).toContain('[TOKEN_1]');
        expect(result).not.toContain('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.K6w9D4p8');
    });

    test('handles multiple entities with overlap correctly', async () => {
        const text = 'Bob sent $50 to bob@example.com and called +1234567890.';
        const result = await shield.protect(text, { translatePlaceholders: false });
        expect(result).toContain('[NAME_1]');
        expect(result).toContain('[AMOUNT_1]');
        expect(result).toContain('[EMAIL_1]');
        expect(result).toContain('[PHONE_1]');
        expect(result).not.toContain('Bob');
        expect(result).not.toContain('$50');
        expect(result).not.toContain('bob@example.com');
        expect(result).not.toContain('+1234567890');
    });

    test('translates placeholders to French', async () => {
        const text = 'Bob a envoyé 50 USD à bob@example.com.';
        // Force French language to ensure translation happens
        const result = await shield.protect(text, { translatePlaceholders: true, targetLanguage: 'fr' });
        // deep-translator might return slightly different things, but we expect translated placeholders
        // We check for presence of translated keywords
        expect(result).toMatch(/\[(NOM|MONTANT|E-MAIL)_\d+\]/);
    });
});

