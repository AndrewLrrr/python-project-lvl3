import os
import tempfile
from unittest import mock

from requests import HTTPError

import page_loader


EXPECTED_RESPONSE_FILES = {
    k: os.path.abspath(p) for k, p in {
        'html': 'tests/fixtures/test.html',
        'html2': 'tests/fixtures/empty.html',
        'link': 'tests/fixtures/style.css',
        'link2': 'tests/fixtures/style2.css',
        'img': 'tests/fixtures/image.png',
        'img2': 'tests/fixtures/image2.png',
        'img3': 'tests/fixtures/image2.png',
        'script': 'tests/fixtures/script.js',
        'script2': 'tests/fixtures/script2.js',
        'script3': 'tests/fixtures/script3.js',
    }.items()
}

EXPECTED_MODIFIED_URL_TEMPLATES = {
    'http://test.com/': 'test-com{}',
    'http://test.com/test.html': 'test-com-test{}',
    'http://test.com/test.php': 'test-com-test{}',
    'http://test.com/test.html?foo=bar&baz=test': 'test-com-test{}',
    'http://test.com/empty': 'test-com-empty{}',
}

EXPECTED_REQUEST_URLS = {
    'http://test.com/': 'html',
    'http://test.com/test.html': 'html',
    'http://test.com/test.php': 'html',
    'http://test.com/test.html?foo=bar&baz=test': 'html',
    'http://test.com/empty': 'html2',
    'http://test.com/local_path/style.css': 'link',
    'http://test.com/local_path/images/image.png': 'img',
    'http://test.com/abs/local_path/images/image2.png': 'img2',
    'http://test.com/abs/local_path/images/image2.png?v=123': 'img3',
    'http://test.com/local_path/scripts/script.js': 'script',
    'http://test.com/abs/local_path/scripts/script2.js': 'script2',
}

EXPECTED_SAVED_RESOURCE_PATHS = (
    ('link', 'test-com-local-path-style.css'),
    ('img', 'test-com-local-path-images-image.png'),
    ('img2', 'test-com-abs-local-path-images-image2.png'),
    ('img3', 'test-com-abs-local-path-images-image2_v2.png'),
    ('script', 'test-com-local-path-scripts-script.js'),
    ('script2', 'test-com-abs-local-path-scripts-script2.js'),
)

EXPECTED_SKIPPED_RESOURCE_PATHS = (
    'https://cdn.test.com/style2.css',
    'https://cdn.test.com/images/image3.png',
    'https://cdn.somesite.com/script3.js',
)


class FakeResponse:
    def __init__(self, url, content, reason='', status_code=200):
        self.url = url
        self.content = content
        self.reason = reason
        self.status_code = status_code
        try:
            self.text = content.decode('utf-8')
        except UnicodeDecodeError:
            self.text = ''

    def raise_for_status(self):
        if self.status_code > 400:
            raise HTTPError


def request_side_effect(url):
    content = read_file(
        EXPECTED_RESPONSE_FILES[EXPECTED_REQUEST_URLS[url]]
    )
    return FakeResponse(url=url, content=content)


def request_side_effect_with_errors(url):
    if url in (
        'http://test.com/local_path/images/image.png',
        'http://test.com/local_path/scripts/script.js',
    ):
        return FakeResponse(url=url, content=b'Not Found', status_code=404)

    return request_side_effect(url)


def read_file(file_path, mode='rb', *args, **kwargs):
    with open(file_path, mode=mode, *args, **kwargs) as f:
        return f.read()


def load_web_page(url_path):
    directory = tempfile.TemporaryDirectory()
    page_loader.download(url_path, directory.name)
    return directory


def assert_modified_html_content(url_path, directory):
    html_file_name = EXPECTED_MODIFIED_URL_TEMPLATES[url_path].format('.html')
    file_path = os.path.join(directory, html_file_name)
    html = read_file(file_path, mode='r', encoding='utf8')

    resource_directory = EXPECTED_MODIFIED_URL_TEMPLATES[url_path].format(
        '_files'
    )
    for file_type, file_name in EXPECTED_SAVED_RESOURCE_PATHS:
        resource_path = f'"{resource_directory}/{file_name}"'
        assert resource_path in html
    for file_url in EXPECTED_SKIPPED_RESOURCE_PATHS:
        assert file_url in html


def assert_resources_loaded(url_path, directory, skipped=None):
    skipped = [] if skipped is None else skipped
    resource_directory = EXPECTED_MODIFIED_URL_TEMPLATES[url_path].format(
        '_files'
    )
    for file_type, file_name in EXPECTED_SAVED_RESOURCE_PATHS:
        file_path = os.path.join(directory, resource_directory, file_name)
        if file_name not in skipped:
            assert os.path.exists(file_path)
            content = read_file(EXPECTED_RESPONSE_FILES[file_type])
            expected_content = read_file(file_path)
            assert content == expected_content
        else:
            assert not os.path.exists(file_path)


def assert_load_web_page(url_path):
    directory = load_web_page(url_path)
    assert_resources_loaded(url_path, directory.name)
    assert_modified_html_content(url_path, directory.name)


@mock.patch('requests.get')
def test_load_web_page(requests_get):
    requests_get.side_effect = request_side_effect
    assert_load_web_page('http://test.com/')


@mock.patch('requests.get')
def test_load_web_page_with_html_extension(requests_get):
    requests_get.side_effect = request_side_effect
    assert_load_web_page('http://test.com/test.html')


@mock.patch('requests.get')
def test_load_web_page_with_not_html_extension(requests_get):
    requests_get.side_effect = request_side_effect
    assert_load_web_page('http://test.com/test.php')


@mock.patch('requests.get')
def test_load_web_page_with_get_params(requests_get):
    requests_get.side_effect = request_side_effect
    assert_load_web_page('http://test.com/test.html?foo=bar&baz=test')


@mock.patch('requests.get')
def test_load_resources_with_http_errors(requests_get):
    requests_get.side_effect = request_side_effect_with_errors
    url_path = 'http://test.com/test.html'
    skipped_files = (
        'test-com-local-path-images-image.png',
        'test-com-local-path-scripts-script.js',
    )
    directory = load_web_page(url_path)
    assert_modified_html_content(url_path, directory.name)
    assert_resources_loaded(url_path, directory.name, skipped=skipped_files)


@mock.patch('requests.get')
def test_load_without_resources(requests_get):
    requests_get.side_effect = request_side_effect_with_errors
    url_path = 'http://test.com/empty'
    directory = load_web_page(url_path)

    resource_html = EXPECTED_MODIFIED_URL_TEMPLATES[url_path].format(
        '.html'
    )
    resource_directory = EXPECTED_MODIFIED_URL_TEMPLATES[url_path].format(
        '_files'
    )

    html_file_path = os.path.join(directory.name, resource_html)
    resources_path = os.path.join(directory.name, resource_directory)

    assert os.path.isfile(html_file_path)
    assert not os.path.exists(resources_path)
