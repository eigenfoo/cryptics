.DEFAULT_GOAL = help

PYTHON := python
PIP := pip
CONDA := conda
SHELL := bash

.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
.DELETE_ON_ERROR:
MAKEFLAGS += --no-builtin-rules

STATIC_SOURCES := docs/index.md docs/datasheet.md
STATIC_TARGETS := templates/index.html templates/pages/datasheet.html

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
	rm -vrf venv/
	${PYTHON} -m venv venv/
	source venv/bin/activate
	${PIP} install -U pip
	${PIP} install -r requirements.txt
	deactivate
	@printf "\n\nVirtual environment created! \033[1;34mRun \`source venv/bin/activate\` to activate it.\033[0m\n\n\n"

.PHONY: blackstyle
blackstyle:
	@printf "Checking code style with black...\n"
	black --check --diff cryptics/
	@printf "\033[1;34mBlack passes!\033[0m\n\n"

.PHONY: pylintstyle
pylintstyle:
	@printf "Checking code style with pylint...\n"
	pylint cryptics/
	@printf "\033[1;34mPylint passes!\033[0m\n\n"

.PHONY: pydocstyle
pydocstyle:
	@printf "Checking documentation with pydocstyle...\n"
	pydocstyle --convention=numpy --match='(?!parallel_sampling).*\.py' cryptics/
	@printf "\033[1;34mPydocstyle passes!\033[0m\n\n"

.PHONY: mypytypes
mypytypes:
	@printf "Checking code type signatures with mypy...\n"
	python -m mypy --ignore-missing-imports cryptics/
	@printf "\033[1;34mMypy passes!\033[0m\n\n"

.PHONY: black
black:  # Format code in-place using black.
	black cryptics/

.PHONY: lint
lint: blackstyle pylintstyle pydocstyle mypytypes  # Lint code using black, pylint, pydocstyle and mypy.

.PHONY: check
check: lint test  # Both lint and test code. Runs `make lint` followed by `make test`.

.PHONY: build
build: build-templates build-db  # Build SQLite database and static documentation pages.

.PHONY: build-db
build-db:
	bash scripts/build-db.sh

build-templates: templates/index.html $(STATIC_TARGETS)

# Generalized rule: how to build a .html file from each .md
# Note: you will need pandoc 2 or greater for this to work
templates/index.html: docs/index.md template.html5 scripts/build-template.sh
	scripts/build-template.sh "$<" "$@"

templates/pages/%.html: docs/%.md template.html5 scripts/build-template.sh
	scripts/build-template.sh "$<" "$@"

serve:
	datasette \
		--immutable clues.sqlite3 \
		--template-dir templates/ \
		--static static:static/ \
		--metadata metadata.json \
		--setting allow_facet off \
		--setting suggest_facets off \
		--setting allow_download on

.PHONY: clean
clean:  # Clean project directories.
	rm -vrf templates/ dist/ site/ cryptics.egg-info/ pip-wheel-metadata/ __pycache__/ testing-report.html coverage.xml
	find cryptics/ -type d -name "__pycache__" -exec rm -vrf {} +
	find cryptics/ -type d -name "__pycache__" -delete
	find cryptics/ -type f -name "*.pyc" -delete
