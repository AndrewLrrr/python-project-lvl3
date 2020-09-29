import os
import re
from typing import Union
from urllib.parse import urlparse

DIRECTORY_ACCESS_RIGHTS = 0o755

SYMBOLS_PATTERN = re.compile(r'[^A-Za-z0-9]+')


class StorageError(Exception):
    pass


def convert_url_to_file_name(url: str, is_html: bool = False) -> str:
    url_obj = urlparse(url)

    split_path = url_obj.path.rsplit('.', 1)

    ext = None
    # Если в url есть расширение и это не html,
    # то убираем его, чтобы добавить в конце
    if len(split_path) == 2 and not is_html:
        ext = split_path[1]
        url = url.replace(f'.{ext}', '')

    if url_obj.scheme:
        url = url.split('//')[-1]

    path = SYMBOLS_PATTERN.sub('-', url.strip('/'))

    if ext and not is_html:
        path = '{}.{}'.format(path, ext)
    else:
        path = '{}.html'.format(path)

    return path


def convert_url_to_dir_name(url: str) -> str:
    return '{}_files'.format(
        convert_url_to_file_name(url, is_html=True).split('.')[0]
    )


def assert_directory(directory: str):
    if not os.path.exists(directory):
        raise StorageError(f'Directory `{directory}` does not exist')

    if not os.access(directory, os.X_OK | os.W_OK):
        raise StorageError(f'Directory `{directory}` is not writable')


def store_data(file_path: str, data: Union[str, bytes]) -> int:
    dir_path = os.path.dirname(file_path)

    if not os.path.exists(dir_path):
        os.makedirs(dir_path, DIRECTORY_ACCESS_RIGHTS)

    mode = 'w' if isinstance(data, str) else 'wb'
    encoding = 'utf8' if mode == 'w' else None
    with open(file_path, mode=mode, encoding=encoding) as f:
        return f.write(data)
