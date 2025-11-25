import argparse
import sys
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

    args = parser.parse_args()
    anonymizer = TextAnonymizer()

    #Todo: Logic and implementation, for now this does nothing.



if __name__ == '__main__':
    sys.exit(main())