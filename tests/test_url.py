import page_loader


def test_url_to_file_name():
    url = 'http://test.com/style.css'
    expected = 'test-com-style.css'
    assert expected == page_loader.url.to_file_name(url)


def test_url_to_file_name_with_ext():
    url = 'http://test.com/test.php'
    expected = 'test-com-test.html'
    assert expected == page_loader.url.to_file_name(url, force_extension='html')


def test_url_to_file_name_without_ext():
    url = 'http://test.com/test'
    expected = 'test-com-test.html'
    assert expected == page_loader.url.to_file_name(url)


def test_url_to_dir_name():
    url = 'http://test.com/test.php'
    expected = 'test-com-test_files'
    assert expected == page_loader.url.to_dir_name(url)
