.PHONY: build lint run test test-cov update-template

build:
	poetry run python -m build

install:
	poetry install
	poetry run pre-commit install
	poetry run pre-commit install-hooks

lint:
	poetry run pre-commit run -a
	poetry run pytest --dead-fixtures

test:
	poetry run pytest


test-cov:
	 poetry run pytest --cov=easyhooks


update-template:
	poetry run cruft update
