# PSHIELD CLI

```
╔═══════════════════════════════════════════╗
║  ____  ____  _   _ ___ _____ _     ____   ║
║ |  _ \/ ___|| | | |_ _| ____| |   |  _ \  ║
║ | |_) \___ \| |_| || ||  _| | |   | | | | ║
║ |  __/ ___) |  _  || || |___| |___| |_| | ║
║ |_|   |____/|_| |_|___|_____|_____|____/  ║
║                                           ║
║  Protect sensitive data in your prompts   ║
╚═══════════════════════════════════════════╝
```

## Installation

```bash
# Install dependencies from root
pip install -r ../requirements.txt

# Install CLI tool
pip install -e .
```

## Usage

```bash
pshield -f document.txt

pshield -t "John sent $1,000 to jane@example.com"

pshield -f input.txt -o output.txt

echo "SSN: 123-45-6789" | pshield --no-logo

pshield -t "Sensitive data" --no-logo
```

## Options

- `-f, --file`: Input file path
- `-t, --text`: Input text string
- `-o, --output`: Output file (default: stdout)
- `--no-logo`: Suppress logo display
