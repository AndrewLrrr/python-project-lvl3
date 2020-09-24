import argparse
import logging
import sys

from page_loader.loader import load_resource, load_web_page, LoadPageError
from page_loader.log_settings import INFO, LOG_LEVELS, LOG_FORMAT, LOG_DATE_FORMAT


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('url')
    parser.add_argument(
        '-o', '--output',
        help='Set output directory',
    )
    parser.add_argument(
        '-l', '--log-level',
        nargs='?',
        default=INFO,
        choices=sorted(LOG_LEVELS.keys()),
        help='Set log level',
    )
    parser.add_argument(
        '-f', '--log-file',
        help='Set log file',
    )
    parser.add_argument(
        '-n', '--no-parse',
        help='',
        # ...
    )

    args = parser.parse_args()

    logging.basicConfig(
        format=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT,
        level=args.log_level,
        filename=args.log_file,
    )

    # Выключаем парсинг, чтобы можно было при необходимости "дозагрузить"
    # какие-то ресурсы дополнительно
    handler = load_web_page if args.no_parse else load_resource

    try:
        handler(args.url, args.output)
    except LoadPageError as e:
        print(f'{str(e)}. See log for details', file=sys.stderr)


if __name__ == '__main__':
    sys.exit(main() or 0)
