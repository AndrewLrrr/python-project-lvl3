import logging
import os
from collections import namedtuple
from typing import List, Union
from urllib.parse import urlparse

from requests import Response

from page_loader import client, storage
from page_loader.parsers import html_parser


logger = logging.getLogger(__name__)


class LoadPageError(Exception):
    pass


def url_filter(url: str) -> bool:
    # Собираем только локальные ресурсы (ссылки без указания домена)
    url = urlparse(url)
    return not url.scheme and not url.netloc


def build_full_url(url_obj: namedtuple, resource_path: str) -> str:
    return '{}://{}/{}'.format(
        url_obj.scheme, url_obj.netloc, resource_path.lstrip('/')
    )


def validate_url(url: str) -> bool:
    url = urlparse(url)
    return url.scheme and url.netloc


def make_request_wrapper(url: str) -> Response:
    # Делаем запрос веб-ресурса, при ошибке пишем в лог,
    # но не останавливаем загруску страницы, даем загрузится
    # остальным ресурсам
    try:
        return client.make_request(url)
    except client.RequestError as e:
        logger.exception(str(e))


def store_data_wrapper(file_name: str, path: List[str], data: Union[str, bytes]) -> str:
    # Сохраняем файл на диске, при ошибке пишем в лог
    # и останавливаем загрузку, т.к., веротяно, ошибка будет
    # аффектить все остальные файлы
    file_path = os.path.join(*path, file_name)
    file_path = os.path.abspath(file_path)
    try:
        storage.store_data(file_path, data)
    except (storage.StorageError, IOError, OSError, PermissionError) as e:
        logger.exception(str(e))
        raise LoadPageError(str(e))
    return file_path


def collect_resources(content: str) -> List[str]:
    return [
        resource for resources in html_parser.parse(content).values()
        for resource in resources
    ]


def load_resource(url: str, directory: str) -> None:
    if not validate_url(url):
        raise LoadPageError(f'Invalid url `{url}`')

    response = make_request_wrapper(url)

    file_name = storage.convert_url_to_file_path(url)

    file_path = store_data_wrapper(file_name, [directory], response.content)

    logger.info('Loaded resource `%s` -> `%s`', url, file_path)


def load_web_page(url: str, directory: str) -> None:
    if not validate_url(url):
        raise LoadPageError(f'Invalid url `{url}`')

    logger.info('Start load web page `%s` to `%s`', url, directory)

    response = make_request_wrapper(url)

    resources = filter(url_filter, collect_resources(response.text))

    file_name = storage.convert_url_to_file_path(url)

    file_path = store_data_wrapper(file_name, [directory], response.text)

    logger.info('Loaded html `%s` -> `%s`', url, file_path)

    url_obj = urlparse(url)

    directory = os.path.join(directory, '{}_files'.format(file_path.split('.')[0]))

    for resource_path in resources:
        load_resource(build_full_url(url_obj, resource_path), directory)

    logger.info('Finish load web page')
