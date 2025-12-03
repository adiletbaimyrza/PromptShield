# PromptShield

Anonymize sensitive information in text prompts and documents using multiple interfaces: CLI, Web App, or Browser Extension.

![alt text](blob/cicd.png)
![alt text](blob/architecture.png)

## Features

- **NLP-based anonymization** using spaCy for accurate name detection
- **Regex-based detection** for emails, phone numbers, and monetary amounts
- **Persistent mappings** to maintain consistency across documents
- **Multiple interfaces**: CLI, Web App, Browser Extension

## Setup

### 1. Create and activate virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Download spaCy language model

```bash
python3 -m spacy download en_core_web_sm
```

## Usage

### CLI Tool

```bash
# Anonymize text directly
python3 cli.py -t "John Smith sent $50 to jane@example.com"

# Anonymize from file
python3 cli.py -f document.txt

# Save output to file
python3 cli.py -f document.txt -o anonymized.txt

# Use custom mapping file
python3 cli.py -t "Test data" --mapping-file custom_mappings.json
```

### Web Application

```bash
flask --app app run
```

Then navigate to `http://localhost:5000`

### Browser Extension Server

```bash
python3 extension_server.py
```

The extension will connect to `http://localhost:5000/anonymize`

## Demo

https://promptshield-wq0g.onrender.com/
