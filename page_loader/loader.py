import logging
import os
from typing import List, Tuple
from urllib.parse import urljoin

import requests
from progress.bar import Bar

from page_loader import html, storage, url


def make_request(url_path: str) -> requests.Response:
    response = requests.get(url_path)
    response.raise_for_status()
    return response


def assert_directory(directory: str) -> None:
    if not os.path.exists(directory):
        raise FileNotFoundError(f'No such file or directory: `{directory}`')

    if not os.path.isdir(directory):
        raise NotADirectoryError(f'Not a directory: `{directory}`')

    if not os.access(directory, os.W_OK):
        raise PermissionError(f'Read-only file system: `{directory}`')


def download_resources(
        url_path: str, directory: str, resources: List[Tuple[str, str]]
) -> None:
    with Bar('Processing', max=len(resources)) as bar:
        for resource_url, resource_path in resources:
            logging.info('Start load resource `%s`', resource_url)
            resource_path = os.path.join(directory, resource_path)
            try:
                response = make_request(urljoin(url_path, resource_url))
                storage.save(resource_path, response.content)
            except requests.HTTPError as e:
                logging.warning(str(e))
                continue
            bar.next()
            logging.info(
                'Resource loaded `%s` -> `%s`', resource_url, resource_path
            )


def download(url_path: str, directory: str) -> str:
    logging.info('Start load web page `%s` to `%s`', url_path, directory)

    directory = os.path.abspath(directory)
    assert_directory(directory)

    response = make_request(url_path)
    html_content, resources = html.process(url_path, response.content)

    file_name = url.to_file_name(url_path, force_extension='html')
    abs_file_path = os.path.join(directory, file_name)
    storage.save(abs_file_path, html_content)

    if resources:
        download_resources(url_path, directory, resources)

    logging.info('Web page loaded `%s` -> `%s`', url_path, abs_file_path)

    return abs_file_path
