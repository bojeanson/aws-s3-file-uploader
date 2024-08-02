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
	pylint src
	black . --check
	isort . --check --gitignore
	flake8 src
	flake8 tests

.PHONY: lint_code  ## Lint code
lint_code:
	black .
	isort . --gitignore
	flake8 .
	autoflake -i --remove-all-unused-imports -r --ignore-init-module-imports . --exclude venv

