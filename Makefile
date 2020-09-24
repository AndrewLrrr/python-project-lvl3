lint:
	poetry run flake8 gendiff

test:
	poetry run pytest --cov ./page_loader

build:
	poetry build

publish:
	poetry publish -r avatara_page-loader
