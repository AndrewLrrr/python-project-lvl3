# Проект: Загрузчик страниц

[![Build Status](https://travis-ci.org/AndrewLrrr/python-project-lvl3.svg?branch=master)](https://travis-ci.org/AndrewLrrr/python-project-lvl3)
[![Maintainability](https://api.codeclimate.com/v1/badges/2d1e1a8bc96a1705794b/maintainability)](https://codeclimate.com/github/AndrewLrrr/python-project-lvl3/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/2d1e1a8bc96a1705794b/test_coverage)](https://codeclimate.com/github/AndrewLrrr/python-project-lvl3/test_coverage)

## Описание
Утилита для скачивания указанного адреса из сети. Принцип ее работы очень похож на то, что делает браузер при сохранении страниц сайтов.

Возможности утилиты:

- Можно указать папку, в которую нужно положить готовый файл.
- Утилита скачивает все ресурсы (теги img, link и script) указанные на странице и меняет страницу так, что начинает ссылаться на локальные версии.

## Работа с проектом:
### Установка зависимостей:
```
poetry install
```
---
### Тесты:
```
make test
```
---
### Кодстайл:
```
make lint
```

## Сборка и публикация пакета:
### Установка репозитория:
```
poetry config repositories.avatara_page-loader https://test.pypi.org/legacy/
```
---
### Установка доступа к репозиторию:
```
poetry config http-basic.avatara_page-loader {login} {password}
```
---
### Сборка пакета:
```
make build
```
---
### Публикация пакета:
```
make publish
```

## Загрузка опубликованного пакета:
```
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple avatara_page-loader
```

## Примеры использования:
### Установка пакета:
<a href="https://asciinema.org/a/t24QbdmyZdXAdN8wWviuWZj9t" target="_blank"><img src="https://asciinema.org/a/t24QbdmyZdXAdN8wWviuWZj9t.svg" /></a>

### Загрузка страницы:
<a href="https://asciinema.org/a/m9dA0WdfPgw1tpy2f1hHBog2p" target="_blank"><img src="https://asciinema.org/a/m9dA0WdfPgw1tpy2f1hHBog2p.svg" /></a>

### Загрузка страницы с включенным логированием уровня debug и записью лога в файл:
<a href="https://asciinema.org/a/zrdSrpqlNFt5WQ9KCh0ZVm9i0" target="_blank"><img src="https://asciinema.org/a/zrdSrpqlNFt5WQ9KCh0ZVm9i0.svg" /></a>
