import sys

from page_loader import cli, download, logging


def main():
    args = cli.get_args_parser().parse_args()
    logging.setup(args.log_level, filename=args.log_file)

    try:
        path = download(args.url, args.output)
    except Exception as e:
        import logging as logger
        logger.error(str(e))
        logger.debug(str(e), exc_info=True)
        sys.exit(1)
    else:
        print(f'Success! File path: {path}')


if __name__ == '__main__':
    main()
