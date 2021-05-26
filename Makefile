.DEFAULT_GOAL = help

PYTHON := python
PIP := pip
CONDA := conda
SHELL := bash

.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
.DELETE_ON_ERROR:
MAKEFLAGS += --no-builtin-rules

.PHONY: help
help:
	@printf "Usage:\n"
	@grep -E '^[a-zA-Z_-]+:.*?# .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?# "}; {printf "\033[1;34mmake %-10s\033[0m%s\n", $$1, $$2}'

.PHONY: conda
conda:  # Set up a conda environment for development.
	@printf "Creating conda environment...\n"
	${CONDA} create --yes --name env-cryptic-info python=3.6
	${CONDA} activate env-cryptic-info
	${PIP} install -U pip
	${PIP} install -r requirements.txt
	${CONDA} deactivate
	@printf "\n\nConda environment created! \033[1;34mRun \`conda activate env-cryptic-info\` to activate it.\033[0m\n\n\n"

.PHONY: venv
venv:  # Set up a Python virtual environment for development.
	@printf "Creating Python virtual environment...\n"
	rm -rf venv/
	${PYTHON} -m venv venv/
	source venv/bin/activate
	${PIP} install -U pip
	${PIP} install -r requirements.txt
	deactivate
	@printf "\n\nVirtual environment created! \033[1;34mRun \`source venv/bin/activate\` to activate it.\033[0m\n\n\n"

.PHONY: blackstyle
blackstyle:
	@printf "Checking code style with black...\n"
	black --check --diff cryptic_info/
	@printf "\033[1;34mBlack passes!\033[0m\n\n"

.PHONY: pylintstyle
pylintstyle:
	@printf "Checking code style with pylint...\n"
	pylint cryptic_info/
	@printf "\033[1;34mPylint passes!\033[0m\n\n"

.PHONY: pydocstyle
pydocstyle:
	@printf "Checking documentation with pydocstyle...\n"
	pydocstyle --convention=numpy --match='(?!parallel_sampling).*\.py' cryptic_info/
	@printf "\033[1;34mPydocstyle passes!\033[0m\n\n"

.PHONY: mypytypes
mypytypes:
	@printf "Checking code type signatures with mypy...\n"
	python -m mypy --ignore-missing-imports cryptic_info/
	@printf "\033[1;34mMypy passes!\033[0m\n\n"

.PHONY: black
black:  # Format code in-place using black.
	black cryptic_info/

.PHONY: lint
lint: blackstyle pylintstyle pydocstyle mypytypes  # Lint code using black, pylint, pydocstyle and mypy.

.PHONY: check
check: lint test  # Both lint and test code. Runs `make lint` followed by `make test`.

.PHONY: clean
clean:  # Clean project directories.
	rm -rf dist/ site/ cryptic_info.egg-info/ pip-wheel-metadata/ __pycache__/ testing-report.html coverage.xml
	find cryptic_info/ -type d -name "__pycache__" -exec rm -rf {} +
	find cryptic_info/ -type d -name "__pycache__" -delete
	find cryptic_info/ -type f -name "*.pyc" -delete
	${MAKE} -C docs/ clean
