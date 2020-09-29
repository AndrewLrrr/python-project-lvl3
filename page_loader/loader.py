import logging
import os
from typing import Dict
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from progress.bar import Bar
from requests import Response

from page_loader import client, storage
from page_loader import html_handlers

logger = logging.getLogger(__name__)


class LoadPageError(Exception):
    pass


def validate_url(url: str) -> bool:
    url = urlparse(url)
    return url.scheme and url.netloc


def make_request_wrapper(url: str) -> Response:
    # Делаем запрос веб-ресурса, при ошибке пишем в лог,
    # но не останавливаем загрузку страницы, даем загрузиться
    # остальным ресурсам т.к. ошибка может быть не критичной,
    # 302 или 404, например.
    try:
        return client.make_request(url)
    except client.RequestError as e:
        logger.error(str(e))


def assert_directory_wrapper(directory: str) -> None:
    try:
        storage.assert_directory(directory)
    except storage.StorageError as e:
        logger.error(str(e))
        raise LoadPageError(str(e))


def build_full_resource_url(url: str, resource_url: str) -> str:
    # Если url полный, возвращаем его
    if resource_url.startswith('http'):
        return resource_url

    url_obj = urlparse(url)

    # Отдельно обрабатываем протокол-относительные пути
    # для них добавляем текущий протокол соединения
    if resource_url.startswith('//'):
        return '{}:{}'.format(
            url_obj.scheme, resource_url
        )

    # Если путь абсолютный, добавляем протокол и домен
    if resource_url.startswith('/'):
        return '{}://{}{}'.format(
            url_obj.scheme, url_obj.netloc, resource_url
        )

    # Если путь относительный, то добавляем протокол, домен и путь без файла
    path = url_obj.path
    if '.' in os.path.basename(path):
        path = os.path.dirname(path)
    return '{}://{}'.format(
        url_obj.scheme, '/'.join(
            filter(
                None, map(
                    lambda s: s.strip('/'), [url_obj.netloc, path, resource_url]  # noqa: E501
                )
            )
        )
    )


def load_resources(url: str, soup: BeautifulSoup, directory: str) -> Dict[str, Dict[str, str]]:  # noqa: E501
    # Будем грузить все ресурсы, которые нашел парсер,
    # а не только относительные, учитывая,
    # что сейчас мало кто делает такие пути
    resources_to_replace = {}
    resources = html_handlers.parse_html(soup)

    resources_count = sum([len(r) for r in resources.values()])
    bar = Bar('Processing', max=resources_count)

    for resource_tag, resource_urls in resources.items():
        resources_to_replace[resource_tag] = {}
        for resource_url in resource_urls:
            resource_file_path = load_resource(url, resource_url, directory)
            bar.next()
            if resource_file_path:
                resources_to_replace[resource_tag][resource_url] = resource_file_path  # noqa: E501

    bar.finish()

    return resources_to_replace


def load_resource(url: str, resource_url: str, directory: str) -> str:
    logger.debug('Start load resource `%s`', resource_url)

    response = make_request_wrapper(build_full_resource_url(url, resource_url))

    if not response:
        return ''

    resource_subdir = storage.convert_url_to_dir_name(url)

    resource_file_name = storage.convert_url_to_file_name(
        resource_url, is_html=False
    )

    resource_file_path = os.path.join(resource_subdir, resource_file_name)

    abs_resource_file_path = os.path.join(directory, resource_file_path)

    storage.store_data(abs_resource_file_path, response.content)

    logger.debug(
        'Resource loaded `%s` -> `%s`', resource_url, abs_resource_file_path
    )

    return resource_file_path


def load_web_page(url: str, directory: str) -> None:
    if not validate_url(url):
        raise LoadPageError(f'Invalid url `{url}`')

    logger.info('Start load web page `%s` to `%s`', url, directory)

    directory = os.path.abspath(directory)

    assert_directory_wrapper(directory)

    response = make_request_wrapper(url)

    if not response:
        return

    soup = BeautifulSoup(response.content, 'html.parser')

    resources_to_replace = load_resources(url, soup, directory)

    html_handlers.modify_html(soup, resources_to_replace)

    file_name = storage.convert_url_to_file_name(url, is_html=True)

    abs_file_path = os.path.join(directory, file_name)

    storage.store_data(abs_file_path, str(soup))

    logger.info('Web page loaded `%s` -> `%s`', url, abs_file_path)
