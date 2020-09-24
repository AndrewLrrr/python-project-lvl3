import os
import re
from typing import Union
from urllib.parse import urlparse

DIRECTORY_ACCESS_RIGHTS = 0o755

SYMBOLS_PATTERN = re.compile(r'[^\w]+')


class StorageError(Exception):
    pass


def convert_url_to_file_path(url: str) -> str:
    url_obj = urlparse(url)

    split_path = url_obj.path.rsplit('.', 1)

    if len(split_path) == 2:
        path, ext = split_path
    else:
        path = split_path[0]
        ext = None

    if url_obj.netloc:
        path = f'{url_obj.netloc}{path}'

    path = SYMBOLS_PATTERN.sub('-', path)

    if ext:
        path = '{}.{}'.format(path, ext)
    else:
        path = '{}.html'.format(path)

    return path


def store_data(file_path: str, data: Union[str, bytes]) -> int:
    dir_path = os.path.dirname(file_path)

    if not os.path.exists(dir_path):
        os.makedirs(dir_path, DIRECTORY_ACCESS_RIGHTS)

    if not os.access(dir_path, os.W_OK):
        raise StorageError(f'Directory {dir_path} is not writable')

    mode = 'w' if isinstance(data, str) else 'wb'
    encoding = 'utf8' if mode == 'w' else None
    with open(file_path, mode=mode, encoding=encoding) as f:
        return f.write(data)
