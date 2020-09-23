import os
import re
from typing import Union
from urllib.parse import urlparse

URL_SYMBOLS_PATTERN = '^[]'
DIRECTORY_ACCESS_RIGHTS = 0o755

IS_FILE_PATTERN = re.compile(r'\.\w+$')
SYMBOLS_PATTERN = re.compile(r'[^\w]+', re.IGNORECASE)


def convert_url_to_file_path(url: str, is_html=True) -> str:
    url_obj = urlparse(url)
    path = url_obj.path

    file_name = None
    if IS_FILE_PATTERN.search(path):
        path, file_name = path.rsplit('/', 1)

    if not is_html:
        path = '{}_files'.format(path)

    if file_name:
        file_name, ext = path.rsplit('.', 1)
        file_name = '{}.{}'.format(SYMBOLS_PATTERN.sub(path, '-'), ext)
        path = os.path.join(path, file_name)

    if is_html and not IS_FILE_PATTERN.search(path):
        path = '{}.html'.format(path)

    return path


def store_data(file_path: str, data: Union[str, bytes]) -> int:
    dir_path = os.path.dirname(file_path)

    if not os.path.exists(dir_path):
        os.makedirs(dir_path, DIRECTORY_ACCESS_RIGHTS)

    mode = 'r' if isinstance(data, str) else 'rb'
    with open(file_path, mode=mode, encoding='utf8') as f:
        return f.write(data)
