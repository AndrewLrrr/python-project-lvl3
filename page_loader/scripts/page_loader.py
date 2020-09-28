import argparse
import logging
import sys

from page_loader.loader import load_web_page, LoadPageError
from page_loader import log_settings


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
        default=log_settings.LOG_LEVELS[log_settings.INFO],
        choices=sorted(log_settings.LOG_LEVELS.keys()),
        help='Set log level',
    )
    parser.add_argument(
        '-f', '--log-file',
        help='Set log file',
    )

    args = parser.parse_args()

    logging.basicConfig(
        format=log_settings.LOG_FORMAT,
        datefmt=log_settings.LOG_DATE_FORMAT,
        level=args.log_level,
        filename=args.log_file,
    )

    logger = logging.getLogger(__name__)

    try:
        load_web_page(args.url, args.output)
    except LoadPageError as e:
        print(f'{str(e)}. See log for details', file=sys.stderr)
    except Exception as e:
        logger.exception(str(e))
        print(f'Unexpected error. See log for details', file=sys.stderr)


if __name__ == '__main__':
    sys.exit(main() or 0)
