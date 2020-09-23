import argparse
import logging
import sys


from page_loader.loader import load_web_page, LoadPageError
from page_loader.log_settings import INFO, LOG_LEVELS, LOG_FORMAT, LOG_DATE_FORMAT


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('url')
    parser.add_argument(
        '-o', '--output',
        help='set output directory',
    )
    parser.add_argument(
        '-l', '--log-level',
        nargs='?',
        default=INFO,
        choices=sorted(LOG_LEVELS.keys()),
        help='set log level',
    )
    parser.add_argument(
        '-f', '--log-file',
        help='set log file',
    )

    args = parser.parse_args()

    logging.basicConfig(
        format=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT,
        level=args.log_level,
        filename=args.log_file,
    )

    try:
        load_web_page(args.url, args.output)
    except LoadPageError as e:
        print(f'{str(e)}. See log to details', file=sys.stderr)


if __name__ == '__main__':
    main()
