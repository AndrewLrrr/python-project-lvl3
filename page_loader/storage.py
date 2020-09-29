import os
from typing import Union

DIRECTORY_ACCESS_RIGHTS = 0o755


class StorageError(Exception):
    pass


def assert_directory(directory: str) -> None:
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
