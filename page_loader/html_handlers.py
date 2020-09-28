from typing import Dict, List

from bs4 import BeautifulSoup


IMG_TAG = 'img'
LINK_TAG = 'link'
SCRIPT_TAG = 'script'


TAG_ATTRS = {
    IMG_TAG: 'src',
    LINK_TAG: 'href',
    SCRIPT_TAG: 'src',
}


def parse_html(soup: BeautifulSoup) -> Dict[str, List[str]]:
    return {
        tag: filter(None, [node.get(attr) for node in soup.find_all(tag)])
        for tag, attr in TAG_ATTRS.items()
    }


def modify_html(soup: BeautifulSoup, resources: Dict[str, Dict[str, str]]) -> None:  # noqa: E501
    for resource_tag, resources_to_replace in resources.items():
        for resource_url, resource_path in resources_to_replace.items():
            attr_value = {TAG_ATTRS[resource_tag]: resource_url}
            node = soup.find(resource_tag, attrs=attr_value)
            node[TAG_ATTRS[resource_tag]] = resource_path
