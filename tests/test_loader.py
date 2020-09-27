import os
import tempfile
from unittest import mock

from page_loader.loader import load_web_page


EXPECTED_RESPONSE_FILES = {
    k: os.path.abspath(p) for k, p in {
        'html': 'tests/fixtures/test.html',
        'link': 'tests/fixtures/style.css',
        'link2': 'tests/fixtures/style2.css',
        'img': 'tests/fixtures/image.png',
        'img2': 'tests/fixtures/image2.png',
        'img3': 'tests/fixtures/image3.png',
        'script': 'tests/fixtures/script.js',
        'script2': 'tests/fixtures/script2.js',
        'script3': 'tests/fixtures/script3.js',
    }.items()
}

EXPECTED_REQUEST_URLS = {
    'http://test.com/test': 'html',
    'http://test.com/test.html': 'html',
    'http://test.com/test.php?foo=bar': 'html',
    'http://test.com/local_path/style.css': 'link',
    'https://cdn.test.com/style2.css': 'link2',
    'http://test.com/test/local_path/images/image.png': 'img',
    'http://test.com/abs/local_path/images/image2.png': 'img2',
    'https://cdn.test.com/images/image3.png': 'img3',
    'http://test.com/test/local_path/scripts/script.js': 'script',
    'http://test.com/abs/local_path/scripts/script2.js': 'script2',
    'https://cdn.test.com/script3.js': 'script3',
}

EXPECTED_SAVED_FILE_PATHS = {
    'html': 'test-com-test.html',
    'link': 'test-com-test_files/test-com-local-path-style.css',
    'link2': 'test-com-test_files/cdn-test-com-style2.css',
    'img': 'test-com-test_files/local-path-images-image.png',
    'img2': 'test-com-test_files/abs-local-path-images-image2.png',
    'img3': 'test-com-test_files/cdn-test-com-images-image3.png',
    'script': 'test-com-test_files/local-path-scripts-script.js',
    'script2': 'test-com-test_files/abs-local-path-scripts-script2.js',
    'script3': 'test-com-test_files/cdn-test-com-script3.js',
}


class FakeResponse:
    def __init__(self, content, reason='', status_code=200):
        self.content = content
        self.reason = reason
        self.status_code = status_code
        try:
            self.text = content.decode('utf-8')
        except UnicodeDecodeError:
            self.text = ''


def read_file(file_path, mode='rb', *args, **kwargs):
    with open(file_path, mode=mode, *args, **kwargs) as f:
        return f.read()


def request_side_effect(url):
    content = read_file(
        EXPECTED_RESPONSE_FILES[EXPECTED_REQUEST_URLS[url]]
    )
    return FakeResponse(content=content)


def assert_modified_html_content(file_path):
    html = read_file(file_path, mode='r', encoding='utf8')
    for file_type, expected_file_path in EXPECTED_SAVED_FILE_PATHS.items():
        if file_type.startswith('html'):
            continue
        assert f'"{expected_file_path}"' in html


def assert_file_content(file_path, file_type):
    content = read_file(EXPECTED_RESPONSE_FILES[file_type])
    expected_content = read_file(file_path)
    assert content == expected_content


def assert_files(directory):
    for file_type, file_path in EXPECTED_SAVED_FILE_PATHS.items():
        file_path = os.path.join(directory, file_path)
        assert os.path.exists(file_path)
        if file_type.startswith('html'):
            assert_modified_html_content(file_path)
        else:
            assert_file_content(file_path, file_type)


@mock.patch('requests.get')
def test_load_web_page(requests_get):
    requests_get.side_effect = request_side_effect
    directory = tempfile.TemporaryDirectory()
    load_web_page('http://test.com/test', directory.name)
    assert_files(directory.name)
