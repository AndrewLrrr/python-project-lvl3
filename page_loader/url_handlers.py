import re
from urllib.parse import urlparse, urljoin

SYMBOLS_PATTERN = re.compile(r'[^A-Za-z0-9]+')

# Не все ОС любят слишком длинные имена файлов,
# поэтому ставим ограничение. Наиболее вероятно,
# избыточность дают гет-параметры в url, поэтому
# уникальность не должна пострадать
MAX_FILE_NAME_LENGTH = 128


def crop_file_or_dir_name(name: str) -> str:
    if len(name) > MAX_FILE_NAME_LENGTH:
        separator = '.' if '.' in name else '_'
        path, ext = name.split(separator)
        max_len = MAX_FILE_NAME_LENGTH - (len(ext) + 1)  # 1 - '.'
        name = '{}.{}'.format(name[:max_len], ext)
    return name


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

    name = SYMBOLS_PATTERN.sub('-', url.strip('/'))

    if ext and not is_html:
        name = '{}.{}'.format(name, ext)
    else:
        name = '{}.html'.format(name)

    return crop_file_or_dir_name(name)


def convert_url_to_dir_name(url: str) -> str:
    name = '{}_files'.format(
        convert_url_to_file_name(url, is_html=True).split('.')[0]
    )
    return crop_file_or_dir_name(name)


def url_is_valid(url: str) -> bool:
    url = urlparse(url)
    return url.scheme and url.netloc


def join_urls(base_url: str, resource_url: str) -> str:
    return urljoin(base_url, resource_url)
