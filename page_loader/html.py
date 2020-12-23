import os
from collections import defaultdict
from typing import Dict, List, Tuple, Union
from urllib.parse import urlparse, urljoin

from bs4 import BeautifulSoup

from page_loader import url

IMG_TAG = 'img'
LINK_TAG = 'link'
SCRIPT_TAG = 'script'


TAG_ATTRS = {
    IMG_TAG: 'src',
    LINK_TAG: 'href',
    SCRIPT_TAG: 'src',
}


def get_resources(soup: BeautifulSoup) -> Dict[str, List[str]]:
    return {
        tag: [node.get(attr) for node in soup.find_all(tag)]
        for tag, attr in TAG_ATTRS.items()
    }


def process_resources(
        url_path: str, resources: Dict[str, List[str]]
) -> Dict[str, List[Tuple[str, str]]]:
    processed_resources = defaultdict(list)
    url_obj = urlparse(url_path)
    directory = url.to_dir_name(url_path)

    for tag, resource_urls in resources.items():
        for resource_url in resource_urls:
            if not resource_url:
                continue
            resource_url_obj = urlparse(resource_url)
            if (
                url_obj.netloc == resource_url_obj.netloc
                or resource_url_obj.netloc == ''  # noqa: W503
            ):
                resource_path = url.to_file_name(
                    urljoin(url_path, resource_url)
                )
                resource_path = os.path.join(directory, resource_path)
                processed_resources[tag].append((resource_url, resource_path))
    return processed_resources


def replace_resources(
        soup: BeautifulSoup, resources: Dict[str, List[Tuple[str, str]]]
) -> BeautifulSoup:
    for resource_tag, resources_to_replace in resources.items():
        for resource_url, resource_path in resources_to_replace:
            attr_value = {TAG_ATTRS[resource_tag]: resource_url}
            node = soup.find(resource_tag, attrs=attr_value)
            node[TAG_ATTRS[resource_tag]] = resource_path
    return soup


def process(
        url_path: str, html: Union[str, bytes]
) -> Tuple[str, List[Tuple[str, str]]]:
    soup = BeautifulSoup(html, 'html.parser')
    resources = process_resources(url_path, get_resources(soup))
    soup = replace_resources(soup, resources)
    resources = [
        (resource_url, resource_path)
        for resource_items in resources.values()
        for resource_url, resource_path in resource_items
    ]
    return soup.prettify(formatter='html5'), resources
