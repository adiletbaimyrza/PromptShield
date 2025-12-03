import sys
import argparse
from pathlib import Path
from anonymizer import TextAnonymizer

def main():

    parser = argparse.ArgumentParser(
        description='Anonymize sensitive information in text prompts/documents',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
    Examples:
      python cli.py -f document.txt
      python cli.py -t "John sent $1,000 to Jane"
            '''
    )

    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument(
        '-f', '--file',
        type=str,
        help='Enter filename as input'
    )
    input_group.add_argument(
        '-t', '--text',
        type=str,
        help='Text input'
    )
    parser.add_argument(
        '--mapping-file',
        type=str,
        default='.anonymizer_mappings.json',
        help='Custom mapping file location (default: .anonymizer_mappings.json)'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output file (default: stdout)'
    )

    args = parser.parse_args()
    anonymizer = TextAnonymizer(mapping_file=args.mapping_file)

    #Todo: Logic and implementation, for now this does nothing.

    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"Error: File '{args.file}' not found.", file=sys.stderr)
            return 1
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    elif args.text:
        text = args.text
    else:
        if sys.stdin.isatty():
            parser.print_help()
            return 1
        text = sys.stdin.read()

    if not text.strip():
        print("Error: No input text provided.", file=sys.stderr)
        return 1

    try:
        anonymized_text = anonymizer.anonymize(text)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1

    if args.output:
        output_path = Path(args.output)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(anonymized_text)
        print(f"Anonymized text written to '{args.output}'", file=sys.stderr)
    else:
        print(anonymized_text)

    return 0

if __name__ == '__main__':
    sys.exit(main())