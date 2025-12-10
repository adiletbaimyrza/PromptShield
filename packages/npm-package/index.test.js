import { jest, describe, test, expect, beforeEach } from '@jest/globals';
import PromptShield from './index.js';

describe('PromptShield', () => {
    let shield;

    beforeEach(() => {
        shield = new PromptShield();
    });

    test('replaces email with placeholder', async () => {
        const text = 'Contact me at john.doe@example.com';
        const result = await shield.protect(text, false);
        expect(result).toContain('[EMAIL_1]');
        expect(result).not.toContain('john.doe@example.com');
    });

    test('replaces phone number with placeholder', async () => {
        const text = 'Call me at +1 (123) 456-7890';
        const result = await shield.protect(text, false);
        expect(result).toContain('[PHONE_1]');
        expect(result).not.toContain('+1 (123) 456-7890');
    });

    test('replaces currency amounts with placeholder', async () => {
        const text = 'The price is $1,234.56 or 1,234.56 USD';
        const result = await shield.protect(text, false);
        expect(result).toContain('[AMOUNT_1]');
        expect(result).toContain('[AMOUNT_2]');
        expect(result).not.toContain('$1,234.56');
    });

    test('replaces names using compromise', async () => {
        const text = 'My name is John Doe and this is Jane Smith.';
        const result = await shield.protect(text, false);
        expect(result).toContain('[NAME_1]');
        expect(result).toContain('[NAME_2]');
        expect(result).not.toContain('John Doe');
        expect(result).not.toContain('Jane Smith');
    });

    test('maintains correct order of replacements', async () => {
        const text = 'John Doe has $500 and email john@example.com';
        const result = await shield.protect(text, false);
        expect(result).toContain('[NAME_1]');
        expect(result).toContain('[AMOUNT_1]');
        expect(result).toContain('[EMAIL_1]');
    });

    test('caches placeholders for repeated entities', async () => {
        const text = 'Email: john@example.com, again: john@example.com';
        const result = await shield.protect(text, false);
        const matches = result.match(/\[EMAIL_\d+\]/g);
        expect(matches).toHaveLength(2);
        expect(matches[0]).toBe(matches[1]); // Same placeholder used
    });

    test('does not translate placeholders when translatePlaceholders is false', async () => {
        const text = 'Contact me at john.doe@example.com';
        const result = await shield.protect(text, false);
        // Should have English placeholder
        expect(result).toMatch(/\[EMAIL_\d+\]/);
    });

    test('detects language correctly', async () => {
        const text = 'Hello, my name is John Doe';
        const result = await shield.protect(text, false);
        // Should work with English text
        expect(result).toContain('[NAME_1]');
    });
});

