import logging

CRITICAL = 'critical'
ERROR = 'error'
WARNING = 'warning'
INFO = 'info'
DEBUG = 'debug'
NOTSET = 'notset'

LOG_LEVELS = {
    CRITICAL: logging.CRITICAL,
    ERROR: logging.ERROR,
    WARNING: logging.WARNING,
    INFO: logging.INFO,
    DEBUG: logging.DEBUG,
    NOTSET: logging.NOTSET,
}

LOG_FORMAT = '%(asctime)s %(message)s'
LOG_DATE_FORMAT = '%H:%M:%S %d/%m/%Y'
