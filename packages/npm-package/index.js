import nlp from 'compromise';
import { franc } from 'franc';
import translate from '@vitalets/google-translate-api';

class PromptShield {
  constructor() {
    this.PLACEHOLDER_PATTERN = /\[(\w+)_\d+\]/g;
    this.placeholdersCache = {};

    this.rules = {
      email: {
        patterns: [
          /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b/g
        ]
      },
      phone: {
        patterns: [
          /\+?\d[\d\s\-\(\)]{8,}\d/g
        ]
      },
      amount: {
        patterns: [
          /\$\s?\d+(?:,\d{3})*(?:\.\d{2})?/g,
          /\d+(?:,\d{3})*(?:\.\d{2})?\s?(?:USD|EUR|GBP|dollars?)/g,
          /(?:USD|EUR|GBP)\s?\d+/g
        ]
      },
      name: {
        custom: (text) => {
          const doc = nlp(text);
          const people = doc.people().out('offsets');
          return people.map(p => {
            const start = p.offset.start;
            const length = p.offset.length;
            // Remove trailing punctuation
            let actualText = p.text;
            let actualLength = length;
            while (actualText && /[.,!?;:]$/.test(actualText)) {
              actualText = actualText.slice(0, -1);
              actualLength--;
            }
            return [actualText, start, start + actualLength];
          });
        }
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

    const pendingReplacements = [];

    for (const [entityType, rule] of Object.entries(this.rules)) {
      let foundEntities = [];
      if (rule.custom) {
        foundEntities = rule.custom(text);
      } else {
        for (const pattern of rule.patterns) {
          const matches = [...text.matchAll(pattern)];
          foundEntities.push(...matches.map(m => [m[0], m.index, m.index + m[0].length]));
        }
      }

      for (const [entityValue, start, end] of foundEntities) {
        const placeholder = this._getPlaceholder(entityValue, entityType);
        pendingReplacements.push([start, end, placeholder]);
      }
    }

    // Sort in reverse order
    pendingReplacements.sort((a, b) => b[0] - a[0]);
    for (const [start, end, placeholder] of pendingReplacements) {
      text = text.slice(0, start) + placeholder + text.slice(end);
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
