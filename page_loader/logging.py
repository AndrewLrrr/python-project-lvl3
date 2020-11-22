import logging


LOG_FORMAT = '%(asctime)s %(message)s'
LOG_DATE_FORMAT = '%H:%M:%S %d/%m/%Y'


def setup(log_level: str, **kwargs) -> None:
    logging.basicConfig(
        format=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT,
        level=logging.getLevelName(log_level),
        **kwargs,
    )
