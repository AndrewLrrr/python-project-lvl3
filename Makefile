lint:
	poetry run flake8 page_loader

test:
	poetry run pytest -o log_cli=True -o log_cli_level=10 --cov=page_loader --cov-report=term-missing

build:
	poetry build

publish:
	poetry publish -r avatara_page-loader
