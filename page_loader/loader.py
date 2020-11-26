import logging
import os
from collections import defaultdict
from typing import Dict, List
from urllib.parse import urljoin, urlsplit

import requests
from progress.bar import Bar

from page_loader import html, storage, url


def make_request(url_path: str) -> requests.Response:
    response = requests.get(url_path)
    response.raise_for_status()
    return response


def assert_directory(directory: str) -> None:
    if not os.path.exists(directory):
        raise FileNotFoundError(f'Directory `{directory}` does not exist')

    if not os.path.isdir(directory):
        raise NotADirectoryError(f'Path `{directory}` is not a directory')

    if not os.access(directory, os.W_OK):
        raise PermissionError(f'Directory `{directory}` is not writable')


def handle_resources(
        url_path: str,
        resources: Dict[str, List[str]]
) -> Dict[str, Dict[str, str]]:
    paths_versions = defaultdict(int)
    filtered_resources = defaultdict(dict)
    url_obj = urlsplit(url_path)
    directory = url.to_dir_name(url_path)

    for tag, resource_urls in resources.items():
        for resource_url in resource_urls:
            if (
                not resource_url
                or resource_url in filtered_resources[tag]
            ):
                continue

            resource_url_obj = urlsplit(resource_url)
            if (
                url_obj.netloc == resource_url_obj.netloc
                or resource_url_obj.netloc == ''
            ):
                resource_path = url.to_file_name(resource_url)
                if resource_path in paths_versions:
                    version = paths_versions[resource_path]
                    paths_versions[resource_path] += 1
                    resource_path, ext = os.path.splitext(resource_path)
                    resource_path = '{path}_v{ver}{ext}'.format(
                        path=resource_path,
                        ver=version + 1,
                        ext=ext,
                    )
                else:
                    paths_versions[resource_path] += 1
                resource_path = os.path.join(directory, resource_path)
                filtered_resources[tag][resource_url] = resource_path

    return filtered_resources


def download_resources(
        url_path: str,
        directory: str,
        resources: Dict[str, Dict[str, str]]
) -> None:
    resources_count = sum([len(r) for r in resources.values()])

    with Bar('Processing', max=resources_count) as bar:
        for resource_items in resources.values():
            for resource_url, resource_path in resource_items.items():
                resource_path = os.path.join(directory, resource_path)
                try:
                    download_resource(url_path, resource_url, resource_path)
                except requests.HTTPError as e:
                    logging.warning(str(e))
                    continue
                bar.next()


def download_resource(
        url_path: str,
        resource_url: str,
        resource_path: str
) -> None:
    logging.info('Start load resource `%s`', resource_url)

    resource_url = urljoin(url_path, resource_url)
    response = make_request(resource_url)
    storage.save(resource_path, response.content)

    logging.info('Resource loaded `%s` -> `%s`', resource_url, resource_path)


def download(url_path: str, directory: str) -> str:
    logging.info('Start load web page `%s` to `%s`', url_path, directory)

    directory = os.path.abspath(directory)
    assert_directory(directory)

    response = make_request(url_path)
    html_content = response.content
    resources = handle_resources(url_path, html.get_resources(html_content))

    file_name = url.to_file_name(url_path, extension='html')
    abs_file_path = os.path.join(directory, file_name)
    html_content = html.replace_resources(html_content, resources)
    storage.save(abs_file_path, html_content)

    download_resources(url_path, directory, resources)

    logging.info('Web page loaded `%s` -> `%s`', url_path, abs_file_path)

    return abs_file_path
