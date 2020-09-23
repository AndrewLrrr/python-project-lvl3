import logging
import time

import requests


logger = logging.getLogger(__name__)


class RequestError(Exception):
    pass


class RequestConnectionError(RequestError):
    pass


def make_request(url: str, tries: int = 3, delay: int = 2) -> requests.Response:
    while tries > 0:
        try:
            response = requests.get(url)
            raise_for_status(response)
        except requests.ConnectionError as e:
            tries -= 1
            if tries == 0:
                raise RequestConnectionError('Connection error while connecting: {}'.format(str(e)))
            logging.warning('%s, Retrying in %d seconds...', str(e), delay)
            time.sleep(delay)
            delay *= 2
        else:
            return response


def raise_for_status(response):
    http_error_msg = ''
    if isinstance(response.reason, bytes):
        try:
            reason = response.reason.decode('utf-8')
        except UnicodeDecodeError:
            reason = response.reason.decode('iso-8859-1')
    else:
        reason = response.reason

    if 200 < response.status_code < 300:
        http_error_msg = '{} is not OK status for url: {}'.format(
            response.status_code, response.url
        )
    elif 300 <= response.status_code < 400:
        http_error_msg = '{} redirect for url: {}'.format(
            response.status_code, response.url
        )
    elif 400 <= response.status_code < 500:
        http_error_msg = '{} Client Error: {} for url: {}'.format(
            response.status_code, reason, response.url
        )
    elif 500 <= response.status_code < 600:
        http_error_msg = '{} Server Error: {} for url: {}'.format(
            response.status_code, reason, response.url
        )

    if http_error_msg:
        raise RequestError(http_error_msg)
