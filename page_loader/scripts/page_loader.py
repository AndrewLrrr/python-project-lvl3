import logging
import sys

from page_loader.cli import parse_input_args
from page_loader.loader import load_web_page, LoadPageError
from page_loader import log_settings


def main():
    args = parse_input_args()

    logging.basicConfig(
        format=log_settings.LOG_FORMAT,
        datefmt=log_settings.LOG_DATE_FORMAT,
        level=log_settings.LOG_LEVELS[args.log_level],
        filename=args.log_file,
    )

    try:
        load_web_page(args.url, args.output)
    except LoadPageError as e:
        print(f'{str(e)}. See log for details', file=sys.stderr)


if __name__ == '__main__':
    sys.exit(main() or 0)
