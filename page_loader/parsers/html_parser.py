from typing import Dict, List

from bs4 import BeautifulSoup

from page_loader import parsers


IMG_TAG = 'img'
LINK_TAG = 'link'
SCRIPT_TAG = 'script'


PARSERS = {
    IMG_TAG: parsers.img_parser,
    LINK_TAG: parsers.link_parser,
    SCRIPT_TAG: parsers.script_parser,
}


def parse(html: str) -> Dict[str, List[str]]:
    soup = BeautifulSoup(html, 'html.parser')
    return {
        tag: parser.parse(soup)
        for tag, parser in PARSERS.items()
    }
