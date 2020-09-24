from typing import List

from bs4 import BeautifulSoup


def parse(soup: BeautifulSoup) -> List[str]:
    return [tag.get('href') for tag in soup.find_all('link')]
