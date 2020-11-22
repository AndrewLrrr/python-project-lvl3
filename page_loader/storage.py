import os
from typing import Union

DIRECTORY_ACCESS_RIGHTS = 0o755


def save(file_path: str, data: Union[str, bytes]) -> int:
    dir_path = os.path.dirname(file_path)

    if not os.path.exists(dir_path):
        os.makedirs(dir_path, DIRECTORY_ACCESS_RIGHTS)

    mode, encoding = ('w', 'utf8') if isinstance(data, str) else ('wb', None)
    with open(file_path, mode=mode, encoding=encoding) as f:
        return f.write(data)
