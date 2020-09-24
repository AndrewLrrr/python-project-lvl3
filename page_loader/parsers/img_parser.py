from typing import List

from bs4 import BeautifulSoup


def parse(soup: BeautifulSoup) -> List[str]:
    return [tag.get('src') for tag in soup.find_all('img')]
