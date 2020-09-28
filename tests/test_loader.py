import os
import tempfile
from unittest import mock

import pytest

from page_loader.loader import load_web_page, LoadPageError

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
    'http://test.com/local_path/images/image.png': 'img',
    'http://test.com/abs/local_path/images/image2.png': 'img2',
    'https://cdn.test.com/images/image3.png': 'img3',
    'http://test.com/test/local_path/scripts/script.js': 'script',
    'http://test.com/local_path/scripts/script.js': 'script',
    'http://test.com/abs/local_path/scripts/script2.js': 'script2',
    'https://cdn.test.com/script3.js': 'script3',
}

EXPECTED_MODIFIED_URL_TEMPLATES = {
    'http://test.com/test': 'test-com-test{}',
    'http://test.com/test.html': 'test-com-test-html{}',
    'http://test.com/test.php?foo=bar': 'test-com-test-php-foo-bar{}',
}

EXPECTED_SAVED_RESOURCE_PATHS = {
    'link': 'test-com-local-path-style.css',
    'link2': 'cdn-test-com-style2.css',
    'img': 'local-path-images-image.png',
    'img2': 'abs-local-path-images-image2.png',
    'img3': 'cdn-test-com-images-image3.png',
    'script': 'local-path-scripts-script.js',
    'script2': 'abs-local-path-scripts-script2.js',
    'script3': 'cdn-test-com-script3.js',
}


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


def read_file(file_path, mode='rb', *args, **kwargs):
    with open(file_path, mode=mode, *args, **kwargs) as f:
        return f.read()


def request_side_effect(url):
    content = read_file(
        EXPECTED_RESPONSE_FILES[EXPECTED_REQUEST_URLS[url]]
    )
    return FakeResponse(url=url, content=content)


def request_404_side_effect(url):
    content = read_file(
        EXPECTED_RESPONSE_FILES[EXPECTED_REQUEST_URLS[url]]
    )
    return FakeResponse(
        url=url, content=content, reason='Page not found', status_code=404
    )


def assert_modified_html_content(directory, file_name, resource_directory):
    file_path = os.path.join(directory, file_name)
    html = read_file(file_path, mode='r', encoding='utf8')
    for file_type, file_name in EXPECTED_SAVED_RESOURCE_PATHS.items():
        resource_path = f'"{resource_directory}/{file_name}"'
        assert resource_path in html


def assert_resources_loaded(directory, resource_directory):
    for file_type, file_name in EXPECTED_SAVED_RESOURCE_PATHS.items():
        file_path = os.path.join(directory, resource_directory, file_name)
        assert os.path.exists(file_path)
        content = read_file(EXPECTED_RESPONSE_FILES[file_type])
        expected_content = read_file(file_path)
        assert content == expected_content


def assert_load_web_page(url):
    directory = tempfile.TemporaryDirectory()
    load_web_page(url, directory.name)

    resource_directory = EXPECTED_MODIFIED_URL_TEMPLATES[url].format('_files')
    assert_resources_loaded(directory.name, resource_directory)

    html_file_name = EXPECTED_MODIFIED_URL_TEMPLATES[url].format('.html')
    assert_modified_html_content(directory.name, html_file_name, resource_directory)


@mock.patch('requests.get')
def test_load_web_page(requests_get):
    requests_get.side_effect = request_side_effect
    assert_load_web_page('http://test.com/test')


@mock.patch('requests.get')
def test_load_html_web_page(requests_get):
    requests_get.side_effect = request_side_effect
    assert_load_web_page('http://test.com/test.html')


@mock.patch('requests.get')
def test_load_php_web_page_with_get_params(requests_get):
    requests_get.side_effect = request_side_effect
    assert_load_web_page('http://test.com/test.php?foo=bar')


@mock.patch('requests.get')
def test_directory_doesnt_exist(requests_get):
    requests_get.side_effect = request_side_effect
    with pytest.raises(LoadPageError) as excinfo:
        load_web_page('http://test.com/test', '/unexpected/directory')
    assert 'Directory `/unexpected/directory` does not exist' in str(excinfo.value)


@mock.patch('requests.get')
def test_directory_is_not_writable(requests_get):
    directory = tempfile.TemporaryDirectory()
    os.chmod(directory.name, 400)
    requests_get.side_effect = request_side_effect
    with pytest.raises(LoadPageError) as excinfo:
        load_web_page('http://test.com/test', directory.name)
    assert f'Directory `{directory.name}` is not writable' in str(excinfo.value)


@mock.patch('requests.get')
def test_404_error(requests_get):
    requests_get.side_effect = request_404_side_effect
    directory = tempfile.TemporaryDirectory()
    load_web_page('http://test.com/test', directory.name)
    assert not os.listdir(directory.name)
