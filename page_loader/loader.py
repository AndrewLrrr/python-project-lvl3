import logging
import os
from typing import List, Union
from urllib.parse import urlparse

from requests import Response

from page_loader import client, storage
from page_loader.parsers import html_parser

logger = logging.getLogger(__name__)


class LoadPageError(Exception):
    pass


def make_request_wrapper(url: str) -> Response:
    try:
        return client.make_request(url)
    except client.RequestError as e:
        logger.exception(str(e))
        raise LoadPageError(str(e))


def store_data_wrapper(file_name: str, path: List[str], data: Union[str, bytes]) -> str:
    file_path = os.path.join(*path, file_name)
    try:
        storage.store_data(file_path, data)
    except (OSError, PermissionError) as e:
        logger.exception(str(e))
        raise LoadPageError(str(e))
    return file_path


def collect_resources(content: str) -> List[str]:
    resources = []
    parsed_data = html_parser.parse(content)
    resources.extend(
        *parsed_data[html_parser.IMG_TAG],
        *parsed_data[html_parser.LINK_TAG],
        *parsed_data[html_parser.SCRIPT_TAG],
    )
    return resources


def load_resource(url: str, directory: str) -> None:
    response = make_request_wrapper(url)

    file_name = storage.convert_url_to_file_path(url, is_html=False)

    file_path = store_data_wrapper(file_name, [directory], response.content)

    logger.info('Load resource `%s` -> `%s`', url, file_path)


def load_web_page(url: str, directory: str) -> None:
    logger.info('Start load web page `%s` to `%s`', url, directory)

    response = make_request_wrapper(url)

    resources = collect_resources(response.text)

    file_name = storage.convert_url_to_file_path(url, is_html=True)

    file_path = store_data_wrapper(file_name, [directory], response.text)

    logger.info('Load html `%s` -> `%s`', url, file_path)

    url_obj = urlparse(url)

    for resource_url in resources:
        if not resource_url.startswith('http'):
            resource_url = '{}://{}/{}'.format(
                url_obj.scheme, url_obj.netlock, resource_url.lstrip('/')
            )
        load_resource(resource_url, directory)
