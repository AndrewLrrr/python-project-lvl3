import argparse


LOG_LEVELS = (
    'CRITICAL',
    'ERROR',
    'WARNING',
    'INFO',
    'DEBUG',
    'NOTSET',
)


def get_args_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'url',
        help='Site url with protocol (http or https)'
    )
    parser.add_argument(
        '-o', '--output',
        help='Set output directory',
    )
    parser.add_argument(
        '-l', '--log-level',
        nargs='?',
        default='WARNING',
        choices=LOG_LEVELS,
        help='Set log level',
    )
    parser.add_argument(
        '-f', '--log-file',
        help='Set log file',
    )

    return parser
