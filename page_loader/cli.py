import argparse

from page_loader import log_settings


def parse_input_args():
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
        default=log_settings.INFO,
        choices=sorted(log_settings.LOG_LEVELS.keys()),
        help='Set log level',
    )
    parser.add_argument(
        '-f', '--log-file',
        help='Set log file',
    )

    return parser.parse_args()
