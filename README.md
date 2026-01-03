# PromptShield

A comprehensive solution for protecting sensitive information in text prompts. Automatically detects and replaces personal data, financial information, and other sensitive entities with placeholders across multiple platforms and interfaces.

![Architecture](blob/architecture.png)
![CI/CD](blob/cicd.png)

## Features

- 🔒 **20+ Entity Types**: Detects emails, phones, credit cards, names, locations, JWT tokens, crypto addresses, and more
- 🌍 **Multi-language Support**: Automatically detects language and translates placeholders
- 🎯 **NLP-based Detection**: Uses spaCy (Python) and compromise (JavaScript) for accurate name/location detection
- 🔄 **Consistent Placeholders**: Same entity values receive the same placeholder across documents
- 🚀 **Multiple Interfaces**: Use via CLI, Web App, Browser Extension, or as a library

## Project Structure

```
PromptShield/
├── packages/
│   ├── pip-package/      # Python package (PyPI: pshield)
│   └── npm-package/      # JavaScript/Node.js package (npm: pshield)
├── cli/                  # Command-line interface
├── extension/            # Browser extension (Chrome/Firefox)
├── app.py                # Web application (Flask)
└── extension_server.py   # Extension backend server
```

## Quick Start

### Python Package

```bash
pip install pshield
python -m spacy download en_core_web_sm
```

```python
from pshield import PromptShield
shield = PromptShield()
result = shield.protect("John sent $50 to jane@example.com")
# Output: "[NAME_1] sent [AMOUNT_1] to [EMAIL_1]"
```

📖 **[Python Package Documentation](packages/pip-package/README.md)**

### JavaScript/Node.js Package

```bash
npm install pshield
```

```javascript
import PromptShield from 'pshield';
const shield = new PromptShield();
const result = await shield.protect("John sent $50 to jane@example.com");
// Output: "[NAME_1] sent [AMOUNT_1] to [EMAIL_1]"
```

📖 **[JavaScript Package Documentation](packages/npm-package/README.md)**

### CLI Tool

```bash
pip install -e cli/
pshield -t "John sent $50 to jane@example.com"
pshield -f document.txt -o protected.txt
```

📖 **[CLI Documentation](cli/README.md)**

### Web Application

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
flask --app app run
```

Visit `http://localhost:5000`

### Browser Extension

1. Start the backend server:
   ```bash
   python extension_server.py
   ```

2. Load the extension in your browser (see extension docs)

📖 **[Extension Documentation](extension/How2Use.md)**

## Supported Entities

**Personal**: Names, emails, phones, usernames  
**Financial**: Credit cards, CVV, expiry dates, monetary amounts  
**Location**: Places, GPS coordinates, IP addresses  
**Digital**: URLs, JWT tokens, Bitcoin/Ethereum addresses  
**Other**: Dates, memory sizes, alphanumeric codes

## Documentation

- 📦 **[Python Package](packages/pip-package/README.md)** - Install from PyPI, usage examples, API reference
- 📦 **[JavaScript Package](packages/npm-package/README.md)** - Install from npm, async API, usage examples
- 💻 **[CLI Tool](cli/README.md)** - Command-line interface documentation
- 🌐 **[Browser Extension](extension/How2Use.md)** - Installation and usage guide
- 🔧 **[Python Package Setup](packages/pip-package/SETUP.md)** - Development setup and publishing guide
- 🔧 **[JavaScript Package Setup](packages/npm-package/SETUP.md)** - Development setup and publishing guide

## Demo

Live demo: https://promptshield-wq0g.onrender.com/

## Requirements

**Python Package**: Python 3.9+, spaCy >= 3.7.0, langdetect >= 1.0.9, deep-translator >= 1.11.4  
**JavaScript Package**: Node.js 14+, ES modules support

## License

MIT License

## Links

- **GitHub**: https://github.com/adiletbaimyrza/promptshield
- **PyPI**: https://pypi.org/project/pshield/
- **npm**: https://www.npmjs.com/package/pshield
- **Issues**: https://github.com/adiletbaimyrza/promptshield/issues
