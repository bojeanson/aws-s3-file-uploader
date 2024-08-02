.DEFAULT_GOAL: help
.EXPORT_ALL_VARIABLES:
.ONESHELL:
.SHELLFLAGS = -ec
.SILENT:
SHELL := /bin/sh

help:
	echo "Please use \`make \033[36m<target>\033[0m\`"
	echo "\t where \033[36m<target>\033[0m is one of"
	grep -E '^\.PHONY: [a-zA-Z_-]+ .*?## .*$$' $(MAKEFILE_LIST) \
		| sort | awk 'BEGIN {FS = "(: |##)"}; {printf "• \033[36m%-30s\033[0m %s\n", $$2, $$3}'


.PHONY: install  ## Install dependencies
install:
	pip install --upgrade pip poetry
	poetry install -v --all-extras
	pip list --outdated

.PHONY: linter_checks  ## Check code format
linter_checks:
	poetry run pylint src
	poetry run black . --check
	poetry run isort . --check --gitignore
	poetry run flake8 src
	poetry run flake8 tests

.PHONY: lint_code  ## Lint code
lint_code:
	poetry run black .
	poetry run isort . --gitignore
	poetry run flake8 .
	poetry run autoflake -i --remove-all-unused-imports -r --ignore-init-module-imports . --exclude venv


.PHONY: unit_test  ## Run unit tests
unit_test:
	poetry run pytest