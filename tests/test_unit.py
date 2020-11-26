import os
import tempfile
from unittest import mock

import pytest

import page_loader


def test_url_to_file_name():
    url = 'http://test.com/style.css'
    expected = 'test-com-style.css'
    assert expected == page_loader.url.to_file_name(url)


def test_url_to_file_name_with_ext():
    url = 'http://test.com/test.php'
    expected = 'test-com-test-php.html'
    assert expected == page_loader.url.to_file_name(url, extension='html')


def test_url_to_dir_name():
    url = 'http://test.com/test.php'
    expected = 'test-com-test-php_files'
    assert expected == page_loader.url.to_dir_name(url)


def test_handle_resources():
    url_path = 'http://test.com/test.html'

    resources = {
        page_loader.html.IMG_TAG: [
            '/f/img1.jpg',
            '/f/img2.jpg',
            '/f/img1.jpg',
            '',
            'http://test.com/img.png',
            'http://cdn.test.com/img.png',
            'http://site.com/img.png',
        ],
        page_loader.html.LINK_TAG: [
            '/f/style.css',
            '/f/style2.css',
            'http://test.com/style.css',
            'http://cdn.test.com/style.css',
        ],
        page_loader.html.SCRIPT_TAG: [
            '/f/script.js',
            'http://cdn.test.com/script.js',
        ],
    }

    expected = {
        page_loader.html.IMG_TAG: {
            '/f/img1.jpg': 'test-com-test-html_files/f-img1.jpg',
            '/f/img2.jpg': 'test-com-test-html_files/f-img2.jpg',
            'http://test.com/img.png': 'test-com-test-html_files/test-com-img.png'
        },
        page_loader.html.LINK_TAG: {
            '/f/style.css': 'test-com-test-html_files/f-style.css',
            '/f/style2.css': 'test-com-test-html_files/f-style2.css',
            'http://test.com/style.css': 'test-com-test-html_files/test-com-style.css',
        },
        page_loader.html.SCRIPT_TAG: {
            '/f/script.js': 'test-com-test-html_files/f-script.js',
        },
    }

    assert expected == page_loader.handle_resources(url_path, resources)


@mock.patch('page_loader.url.to_file_name')
def test_handle_resources_with_versions(url_to_file_name):
    def side_effect(url, extension=None):
        if url == 'http://test.com/':
            return 'test-com'
        else:
            return 'the-same-file-path-{ext}.{ext}'.format(ext=url.rsplit('.', 1)[1])

    url_to_file_name.side_effect = side_effect

    resources = {
        page_loader.html.IMG_TAG: [
            '/long_path1.jpg',
            '/long_path2.jpg',
            '/long_path3.jpg',
        ],
        page_loader.html.LINK_TAG: [
            '/long_path1.css',
            '/long_path2.css',
        ],
        page_loader.html.SCRIPT_TAG: [
            '/long_path1.js',
            '/long_path2.js',
        ],
    }

    expected = {
        page_loader.html.IMG_TAG: {
            '/long_path1.jpg': 'test-com_files/the-same-file-path-jpg.jpg',
            '/long_path2.jpg': 'test-com_files/the-same-file-path-jpg_v2.jpg',
            '/long_path3.jpg': 'test-com_files/the-same-file-path-jpg_v3.jpg',
        },
        page_loader.html.LINK_TAG: {
            '/long_path1.css': 'test-com_files/the-same-file-path-css.css',
            '/long_path2.css': 'test-com_files/the-same-file-path-css_v2.css',
        },
        page_loader.html.SCRIPT_TAG: {
            '/long_path1.js': 'test-com_files/the-same-file-path-js.js',
            '/long_path2.js': 'test-com_files/the-same-file-path-js_v2.js',
        },
    }

    assert expected == page_loader.handle_resources('http://test.com/', resources)


def test_directory_doesnt_exist():
    with pytest.raises(NotADirectoryError) as excinfo:
        page_loader.download('http://test.com/test', '/unexpected/directory')
    assert 'Directory `/unexpected/directory` does not exist' in str(excinfo.value)


def test_directory_is_not_writable():
    directory = tempfile.TemporaryDirectory()
    os.chmod(directory.name, 0o400)
    with pytest.raises(PermissionError) as excinfo:
        page_loader.download('http://test.com/test', directory.name)
    assert f'Directory `{directory.name}` is not writable' in str(excinfo.value)
