import argparse
import os

LOG_LEVELS = (
    'CRITICAL',
    'ERROR',
    'WARNING',
    'INFO',
    'DEBUG',
    'NOTSET',
)

DEFAULT_LOG_LEVEL = 'WARNING'

DEFAULT_DIRECTORY = os.getcwd()


def get_args_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'url',
        help='Site url with protocol (http or https)'
    )
    parser.add_argument(
        '-o', '--output',
        default=DEFAULT_DIRECTORY,
        help=f'Output directory. Default `{DEFAULT_DIRECTORY}`',
    )
    parser.add_argument(
        '-l', '--log-level',
        nargs='?',
        default=DEFAULT_LOG_LEVEL,
        choices=LOG_LEVELS,
        help=f'Log level. Default `{DEFAULT_LOG_LEVEL}`',
    )
    parser.add_argument(
        '-f', '--log-file',
        help='Log file',
    )

    return parser
