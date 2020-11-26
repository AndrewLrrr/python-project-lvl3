import os
import re
from typing import Optional
from urllib.parse import urlparse

SAFE_PATH_CHARS = re.compile(r'[^A-Za-z0-9]+')


def to_file_name(url: str, force_extension: Optional[str] = None) -> str:
    extension = force_extension
    url_obj = urlparse(url)

    paths = os.path.splitext(url_obj.path)

    if len(paths) == 2 and extension is None:
        extension = paths[1].lstrip('.')

    url = '{}{}'.format(url_obj.netloc, paths[0])

    name = SAFE_PATH_CHARS.sub('-', url.strip('/'))

    return '{}.{}'.format(name, extension or 'html')


def to_dir_name(url: str) -> str:
    name = '{}_files'.format(to_file_name(url).split('.')[0])
    return name
