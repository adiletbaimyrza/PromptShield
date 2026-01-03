# PromptShield (pshield)

A JavaScript/Node.js library that automatically detects and replaces sensitive information in text with placeholders.

## Features

- 🔒 Detects 20+ entity types (emails, phones, cards, names, locations, etc.)
- 🌍 Multi-language support with automatic placeholder translation
- 🎯 Uses compromise NLP for accurate name/location detection
- 🔄 Consistent placeholders across documents
- ⚡ Async/await API

## Installation

```bash
npm install pshield
```

## Quick Start

```javascript
import PromptShield from 'pshield';

const shield = new PromptShield();
const protected = await shield.protect("John sent $50 to jane@example.com");
// Output: "[NAME_1] sent [AMOUNT_1] to [EMAIL_1]"
```

## Usage

```javascript
// Disable translation (keep placeholders in English)
const protected = await shield.protect("Your text", false);

// Multi-language example
await shield.protect("Bob a envoyé 50 USD à bob@example.com");
// Returns: "[NOM_1] a envoyé [MONTANT_1] à [E-MAIL_1]"
```

## Supported Entities

**Personal**: Names, emails, phones, usernames  
**Financial**: Credit cards, CVV, expiry dates, amounts  
**Location**: Places, coordinates, IP addresses  
**Digital**: URLs, JWT tokens, Bitcoin/Ethereum addresses  
**Other**: Dates, memory sizes, alphanumeric codes

## API

### `new PromptShield()`

Creates a new PromptShield instance.

### `protect(text: string, translatePlaceholders: boolean = true): Promise<string>`

Replaces sensitive entities with placeholders.

- `text`: Input text to protect
- `translatePlaceholders`: Translate placeholders to detected language (default: `true`)

**Returns**: Promise resolving to protected text

## Requirements

Node.js 14+, ES modules support

## Links

- **GitHub**: https://github.com/adiletbaimyrza/promptshield
- **npm**: https://www.npmjs.com/package/pshield

## License

MIT
