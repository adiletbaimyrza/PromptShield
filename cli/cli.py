import sys
import argparse
from pathlib import Path
from pshield import PromptShield

LOGO = r"""
╔═══════════════════════════════════════════╗
║  ____  ____  _   _ ___ _____ _     ____   ║
║ |  _ \/ ___|| | | |_ _| ____| |   |  _ \  ║
║ | |_) \___ \| |_| || ||  _| | |   | | | | ║
║ |  __/ ___) |  _  || || |___| |___| |_| | ║
║ |_|   |____/|_| |_|___|_____|_____|____/  ║
║                                           ║
║  Protect sensitive data in your prompts   ║
╚═══════════════════════════════════════════╝
"""

def main():
    parser = argparse.ArgumentParser(
        description='Anonymize sensitive information in text prompts/documents',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='Examples:\n  pshield -f document.txt\n  pshield -t "John sent $1,000 to Jane"'
    )

    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument('-f', '--file', help='Input file path')
    input_group.add_argument('-t', '--text', help='Input text string')
    parser.add_argument('-o', '--output', help='Output file (default: stdout)')
    parser.add_argument('--no-logo', action='store_true', help='Suppress logo display')

    args = parser.parse_args()

    if not args.no_logo and sys.stdout.isatty():
        print(LOGO)

    try:
        anonymizer = PromptShield()
    except OSError as e:
        if "Can't find model 'en_core_web_sm'" in str(e):
            print("Error: spaCy model not found. Install it with:", file=sys.stderr)
            print(" python -m spacy download en_core_web_sm", file=sys.stderr)
            return 1
        raise

    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"Error: File '{args.file}' not found.", file=sys.stderr)
            return 1
        text = file_path.read_text(encoding='utf-8')
    elif args.text:
        text = args.text
    else:
        if sys.stdin.isatty():
            parser.print_help()
            return 1
        text = sys.stdin.read()

    if not text.strip():
        print("Error: No input provided.", file=sys.stderr)
        return 1

    try:
        anonymized_text = anonymizer.protect(text)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if args.output:
        Path(args.output).write_text(anonymized_text, encoding='utf-8')
        print(f"✓ Anonymized text written to '{args.output}'", file=sys.stderr)
    else:
        print(anonymized_text)

    return 0

if __name__ == '__main__':
    sys.exit(main())