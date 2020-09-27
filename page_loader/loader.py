import logging
import os
from typing import Union
from urllib.parse import urlparse

from bs4 import BeautifulSoup
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
        logger.exception(str(e))


def store_data_wrapper(file_path: str, data: Union[str, bytes]) -> None:
    # Сохраняем файл на диске, при ошибке пишем в лог
    # и останавливаем загрузку, т.к., вероятно, ошибка будет
    # аффектить все остальные файлы
    try:
        storage.store_data(file_path, data)
    except (IOError, OSError, PermissionError) as e:
        logger.exception(str(e))
        raise LoadPageError(str(e))


def assert_directory_wrapper(directory: str) -> None:
    try:
        storage.assert_directory(directory)
    except storage.StorageError as e:
        logger.exception(str(e))
        raise LoadPageError(str(e))


def build_full_resource_url(url: str, resource_url: str) -> str:
    # Если url полный, возвращаем его
    if resource_url.startswith('http'):
        return resource_url

    url_obj = urlparse(url)

    # Если путь абсолютный, добавляем протокол и домен
    if resource_url.startswith('/'):
        return '{}://{}{}'.format(
            url_obj.scheme, url_obj.netloc, resource_url
        )

    # Если путь относительный, то добавляем протокол, домен и путь
    return '{}://{}{}/{}'.format(
        url_obj.scheme, url_obj.netloc, url_obj.path, resource_url
    )


def load_resource(url: str, resource_url: str, directory: str) -> str:
    logger.info('Start load resource `%s`', resource_url)

    response = make_request_wrapper(build_full_resource_url(url, resource_url))

    resource_subdir = storage.convert_url_to_dir_name(url)

    resource_file_name = storage.convert_url_to_file_name(
        resource_url, is_html=False
    )

    resource_file_path = os.path.join(resource_subdir, resource_file_name)

    abs_resource_file_path = os.path.join(directory, resource_file_path)

    store_data_wrapper(abs_resource_file_path, response.content)

    logger.info(
        'Resource loaded `%s` -> `%s`', resource_url, abs_resource_file_path
    )

    return resource_file_path


def load_web_page(url: str, directory: str) -> None:
    if not validate_url(url):
        raise LoadPageError(f'Invalid url `{url}`')

    logger.info('Start load web page `%s` to `%s`', url, directory)

    resources_to_replace = {}

    directory = os.path.abspath(directory)

    assert_directory_wrapper(directory)

    response = make_request_wrapper(url)

    soup = BeautifulSoup(response.text, 'html.parser')

    resources = html_handlers.parse_html(soup)

    for resource_tag, resource_urls in resources.items():
        resources_to_replace[resource_tag] = {}
        for resource_url in resource_urls:
            resource_file_path = load_resource(url, resource_url, directory)
            resources_to_replace[resource_tag][resource_url] = resource_file_path

    html_handlers.modify_html(soup, resources_to_replace)

    file_name = storage.convert_url_to_file_name(url, is_html=True)

    abs_file_path = os.path.join(directory, file_name)

    store_data_wrapper(abs_file_path, str(soup))

    logger.info('Web page loaded `%s` -> `%s`', url, abs_file_path)
