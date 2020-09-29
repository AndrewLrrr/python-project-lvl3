import re
from urllib.parse import urlparse, urljoin

SYMBOLS_PATTERN = re.compile(r'[^A-Za-z0-9]+')

# Не все ОС любят слишком длинные имена файлов,
# поэтому ставим ограничение. Наиболее вероятно,
# избыточность дают гет-параметры в url, поэтому
# уникальность не должна пострадать
MAX_FILE_NAME_LENGTH = 128


def convert_url_to_file_name(url: str, is_html: bool = False) -> str:
    url_obj = urlparse(url)

    split_path = url_obj.path.rsplit('.', 1)

    ext = None
    # Если в url есть расширение и это не html,
    # то убираем его, чтобы добавить в конце
    if len(split_path) == 2 and not is_html:
        ext = split_path[1]
        url = url.replace(f'.{ext}', '')

    if url_obj.scheme:
        url = url.split('//')[-1]

    path = SYMBOLS_PATTERN.sub('-', url.strip('/'))

    if ext and not is_html:
        path = '{}.{}'.format(path, ext)
    else:
        path = '{}.html'.format(path)

    if len(path) > MAX_FILE_NAME_LENGTH:
        path, ext = path.split('.')
        max_len = MAX_FILE_NAME_LENGTH - (len(ext) + 1)  # 1 - '.'
        path = '{}.{}'.format(path[:max_len], ext)

    return path


def convert_url_to_dir_name(url: str) -> str:
    return '{}_files'.format(
        convert_url_to_file_name(url, is_html=True).split('.')[0]
    )


def url_is_valid(url: str) -> bool:
    url = urlparse(url)
    return url.scheme and url.netloc


def join_urls(base_url: str, resource_url: str) -> str:
    return urljoin(base_url, resource_url)
