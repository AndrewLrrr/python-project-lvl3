import os
import tempfile
from unittest import mock

from page_loader.loader import load_web_page

EXPECTED_RESPONSE_FILES = {
    k: os.path.abspath(p) for k, p in {
        'html': 'tests/fixtures/test.html',
        'css': 'tests/fixtures/style.css',
        'jpg': 'tests/fixtures/image.jpg',
        'js': 'tests/fixtures/script.js',
    }.items()
}

EXPECTED_REQUEST_URLS = {
    'http://test.com/test': 'html',
    'http://test.com/test.html': 'html',
    'http://test.com/local_path/style.css': 'css',
    'http://test.com/local_path/images/image.jpg': 'jpg',
    'http://test.com/local_path/scripts/script.js': 'js',
}

EXPECTED_SAVED_FILE_PATHS = {
    'html': '/test-com-test.html',
    'css': '/test-com-test_files/local-path-style.css',
    'jpg': '/test-com-test_files/local-path-images-image.jpg',
    'js': '/test-com-test_files/local-path-scripts-script.js',
}


class FakeResponse:
    def __init__(self, content, reason='', status_code=200):
        self.content = content
        self.text = content.decode('utf-8')
        self.reason = reason
        self.status_code = status_code


def read_file(file_path, mode):
    with open(file_path, mode=mode) as f:
        return f.read()


def request_side_effect(url):
    content = read_file(
        EXPECTED_RESPONSE_FILES[EXPECTED_REQUEST_URLS[url]],
        mode='rb',
    )
    return FakeResponse(content=content)


def assert_files_created(directory):
    for file_path in EXPECTED_SAVED_FILE_PATHS:
        file_path = os.path.join(directory, file_path)
        assert os.path.exists(file_path)


@mock.patch('requests.get')
def test_load_web_page(requests_get):
    requests_get.side_effect = request_side_effect
    directory = tempfile.TemporaryDirectory()
    load_web_page('http://test.com/test', directory.name)
