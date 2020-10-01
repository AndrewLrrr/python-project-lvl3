import logging
import time

import requests


logger = logging.getLogger(__name__)


RETRY_TRIES = 3
RETRY_DELAY = 2


class RequestError(Exception):
    pass


class RequestClientError(RequestError):
    pass


class RequestServerError(RequestError):
    pass


class RequestConnectionError(RequestError):
    pass


def make_request(url: str, tries: int = RETRY_TRIES, delay: int = RETRY_DELAY) -> requests.Response:  # noqa: E501
    # Делаем ретрай при ошибках сервера или при проблемах с коннектом,
    # есть шанс, что удасться загрузить файл
    while tries > 0:
        try:
            response = requests.get(url)
            raise_for_status(response)
        except (RequestServerError, requests.ConnectionError) as e:
            tries -= 1
            if tries == 0:
                raise
            logging.warning('%s, Retrying in %d seconds...', str(e), delay)
            time.sleep(delay)
            delay *= 2
        else:
            return response


def raise_for_status(response: requests.Response) -> None:
    # Расширяем дефолтный raise_for_status, чтобы иметь возможность
    # отлавливать статусы 200 < q < 400 и различать ошибки клиента и сервера
    http_error_msg = ''
    if isinstance(response.reason, bytes):
        try:
            reason = response.reason.decode('utf-8')
        except UnicodeDecodeError:
            reason = response.reason.decode('iso-8859-1')
    else:
        reason = response.reason

    error = RequestError

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
        error = RequestClientError
    elif 500 <= response.status_code < 600:
        http_error_msg = '{} Server Error: {} for url: {}'.format(
            response.status_code, reason, response.url
        )
        error = RequestServerError

    if http_error_msg:
        raise error(http_error_msg)
