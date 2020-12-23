import os
import tempfile

import pytest

import page_loader


def test_directory_doesnt_exist():
    with pytest.raises(FileNotFoundError) as excinfo:
        page_loader.download('http://test.com/test', '/unexpected/directory')
    assert 'No such file or directory: `/unexpected/directory`' in str(excinfo.value)  # noqa: E501


def test_directory_is_file():
    directory = os.path.abspath('tests/fixtures/test.html')
    with pytest.raises(NotADirectoryError) as excinfo:
        page_loader.download('http://test.com/test', directory)
    assert f'Not a directory: `{directory}`' in str(excinfo.value)


def test_directory_is_not_writable():
    directory = tempfile.TemporaryDirectory()
    os.chmod(directory.name, 0o400)
    with pytest.raises(PermissionError) as excinfo:
        page_loader.download('http://test.com/test', directory.name)
    assert f'Read-only file system: `{directory.name}`' in str(excinfo.value)
