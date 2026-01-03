import nlp from 'compromise';
import { franc } from 'franc';
import translate from '@vitalets/google-translate-api';

class PromptShield {
  constructor() {
    this.PLACEHOLDER_PATTERN = /\[(\w+)_\d+\]/g;
    this.placeholdersCache = {};

    this.rules = {
      mem: {
        patterns: [
          /\b\d+(?:\.\d+)?\s*(?:B|KB|K|MB|M|GB|G|TB|T)\b/g
        ]
      },
      cvv: {
        patterns: [
          /\b(?:CVV|CVC)\s*[:\-]?\s*\d{3,4}\b/gi
        ]
      },
      exp: {
        patterns: [
          /\b(?:exp|expiry|expires)\s*[:\-]?\s*(0[1-9]|1[0-2])[\/\-](\d{2}|\d{4})\b/gi
        ]
      },
      card: {
        patterns: [
          /\b(?:\d{4}[- ]\d{4}[- ]\d{4}[- ]\d{4}|\d{16})\b/g
        ]
      },
      date: {
        patterns: [
          /\b(0?[1-9]|[12][0-9]|3[01])[\/\-](0?[1-9]|1[0-2])[\/\-]\d{4}\b/g,
          /\d{4}[\/\-](?:0?[1-9]|1[0-2])[\/\-](?:0?[1-9]|[12][0-9]|3[01])/g,
          /\b(0?[1-9]|[12][0-9]|3[01])(st|nd|rd|th)\b/g,
        ]
      },
      email: {
        patterns: [
          /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g
        ]
      },
      url: {
        patterns: [
          /https?:\/\/[^\s<>"{}|\\^`\[\]]+/g,
          /www\.[^\s<>"{}|\\^`\[\]]+/g,
        ]
      },
      ip: {
        patterns: [
          /\b(?:IP|ip)\s*[:\-]?\s*((?:\d{1,3}\.){3}\d{1,3})\b/g,
          /\b((?:\d{1,3}\.){3}\d{1,3})\b/g
        ]
      },
      phone: {
        patterns: [
          /\+?\d[\d\s\-\(\)]{8,}\d/g
        ]
      },
      amount: {
        patterns: [
          /[\$\€\£\₽\¥]\s?\d+(?:,\d{3})*(?:\.\d{2})?/g,
          /\d+(?:,\d{3})*(?:\.\d{2})?\s?(?:USD|EUR|GBP|JPY|AUD|CAD|RUB|CNY|dollars?)/g,
          /(?:USD|EUR|GBP|JPY|AUD|CAD|RUB|CNY)\s?\d+/g
        ]
      },
      place: {
        custom: (text) => {
          const doc = nlp(text);
          const places = doc.places().out('offsets');
          return places.map(p => {
            const start = p.offset.start;
            const length = p.offset.length;
            let actualText = p.text;
            let actualLength = length;
            while (actualText && /[.,!?;:]$/.test(actualText)) {
              actualText = actualText.slice(0, -1);
              actualLength--;
            }
            return [actualText, start, start + actualLength];
          });
        }
      },
      name: {
        custom: (text) => {
          const doc = nlp(text);
          const people = doc.people().out('offsets');
          return people.map(p => {
            const start = p.offset.start;
            const length = p.offset.length;
            let actualText = p.text;
            let actualLength = length;
            while (actualText && /[.,!?;:]$/.test(actualText)) {
              actualText = actualText.slice(0, -1);
              actualLength--;
            }
            return [actualText, start, start + actualLength];
          });
        }
      },
      jwt: {
        patterns: [
          /e[yw][A-Za-z0-9-_]+\.(?:e[yw][A-Za-z0-9-_]+)?\.[A-Za-z0-9-_]{2,}/g
        ]
      },
      btc_address: {
        patterns: [
          /\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b/g,
          /\bbc1[a-z0-9]{39,87}\b/g,
        ]
      },
      eth_address: {
        patterns: [
          /\b0x[a-fA-F0-9]{40}\b/g,
        ]
      },
      username: {
        patterns: [
          /@[A-Za-z0-9_]{1,15}\b/g,
          /u\/[A-Za-z0-9_-]{3,20}\b/g,
        ]
      },
      alnum_code: {
        patterns: [
          /\b(?=[A-Za-z0-9\-]*[A-Za-z])(?=[A-Za-z0-9\-]*\d)[A-Za-z0-9\-]+\b/g
        ],
        mode: 'normalize'
      },
      coors: {
        patterns: [/^-?\d{1,2}\.\d+,\s*-?\d{1,3}\.\d+$/g]
      }
    };
  }

  _getPlaceholder(entityValue, entityType) {
    if (!this.placeholdersCache[entityType]) {
      this.placeholdersCache[entityType] = { placeholders: {}, count: 0 };
    }

    const cache = this.placeholdersCache[entityType];

    if (!cache.placeholders[entityValue]) {
      cache.count += 1;
      cache.placeholders[entityValue] = `[${entityType.toUpperCase()}_${cache.count}]`;
    }

    return cache.placeholders[entityValue];
  }

  _normalizeAlnum(value) {
    return value.split('').map(c => {
      if (/[A-Za-z]/.test(c)) return 'A';
      if (/\d/.test(c)) return '0';
      return c;
    }).join('');
  }

  async _translatePlaceholders(text, targetLang) {
    const matches = [...text.matchAll(this.PLACEHOLDER_PATTERN)];
    const translations = await Promise.all(
      matches.map(async (match) => {
        const entityType = match[1];
        const idx = match[0].split('_')[1].replace(']', '');
        try {
          const translated = await translateText(entityType.toLowerCase(), targetLang);
          return `[${translated.toUpperCase()}_${idx}]`;
        } catch {
          return match[0];
        }
      })
    );

    let result = text;
    for (let i = matches.length - 1; i >= 0; i--) {
      const match = matches[i];
      result = result.slice(0, match.index) + translations[i] + result.slice(match.index + match[0].length);
    }
    return result;
  }

  async protect(text, translatePlaceholders = true) {
    let lang;
    try {
      lang = franc(text, { minLength: 3 }) || 'eng';
    } catch {
      lang = 'eng';
    }

    // Collect all entities from the ORIGINAL text first
    const allEntities = []; // Array of [start, end, entityValue, entityType, mode]

    for (const [entityType, rule] of Object.entries(this.rules)) {
      const mode = rule.mode || 'placeholder';
      if (rule.custom) {
        // NER-based detection
        const found = rule.custom(text);
        for (const [entityValue, start, end] of found) {
          allEntities.push([start, end, entityValue, entityType, mode]);
        }
      } else {
        // Regex-based detection
        for (const pattern of rule.patterns) {
          // Reset regex lastIndex for global patterns
          pattern.lastIndex = 0;
          const matches = [...text.matchAll(pattern)];
          for (const match of matches) {
            allEntities.push([match.index, match.index + match[0].length, match[0], entityType, mode]);
          }
        }
      }
    }

    // Remove overlapping entities (keep the first one found for each position)
    allEntities.sort((a, b) => a[0] - b[0] || b[1] - a[1]); // Sort by start, then by longest
    const nonOverlapping = [];
    let lastEnd = -1;
    for (const [start, end, entityValue, entityType, mode] of allEntities) {
      if (start >= lastEnd) {
        nonOverlapping.push([start, end, entityValue, entityType, mode]);
        lastEnd = end;
      }
    }

    // Apply replacements in reverse order to preserve indices
    nonOverlapping.sort((a, b) => b[0] - a[0]);
    for (const [start, end, entityValue, entityType, mode] of nonOverlapping) {
      let replacement;
      if (mode === 'normalize') {
        replacement = this._normalizeAlnum(entityValue);
      } else {
        replacement = this._getPlaceholder(entityValue, entityType);
      }
      text = text.slice(0, start) + replacement + text.slice(end);
    }

    if (translatePlaceholders && lang !== 'eng') {
      text = await this._translatePlaceholders(text, lang);
    }

    return text;
  }
}

// Helper function to translate text
async function translateText(text, targetLang) {
  try {
    const res = await translate(text, { to: targetLang });
    return res.text;
  } catch (err) {
    return text;
  }
}

export default PromptShield;
