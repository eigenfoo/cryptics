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

.PHONY: black
black:  # Format code in-place using black.
	black cryptics/

.PHONY: blackstyle
blackstyle:
	@printf "Checking code style with black...\n"
	black --check --diff cryptics/
	@printf "\033[1;34mBlack passes!\033[0m\n\n"

.PHONY: mypytypes
mypytypes:
	@printf "Checking code type signatures with mypy...\n"
	python -m mypy --ignore-missing-imports cryptics/
	@printf "\033[1;34mMypy passes!\033[0m\n\n"

.PHONY: lint
lint: blackstyle mypytypes  # Lint code using black and mypy.

.PHONY: build
build: build-db build-templates test-build  # Build SQLite database and documentation and test build.

build-db: clues.sqlite3

clues.sqlite3: cryptics/cryptics.sqlite3
	bash scripts/build-db.sh

build-templates: templates/index.html $(STATIC_TARGETS)

# Generalized rule: how to build a .html file from each .md
# Note: you will need pandoc 2 or greater for this to work
templates/index.html: docs/index.md template.html5 scripts/build-template.sh
	scripts/build-template.sh "$<" "$@"

templates/pages/%.html: docs/%.md template.html5 scripts/build-template.sh
	scripts/build-template.sh "$<" "$@"

.PHONY: test-build
test-build:
	bash scripts/test-build.sh

serve:
	datasette \
		--immutable clues.sqlite3 \
		--template-dir templates/ \
		--static static:static/ \
		--metadata metadata.json \
		--setting allow_facet off \
		--setting suggest_facets off \
		--setting allow_download on

.PHONY: deploy
deploy:  # Deploy Datasette project to Heroku.
	bash scripts/deploy.sh

.PHONY: clean
clean:  # Clean project directories.
	rm -vrf clues.sqlite3 templates/ cryptics.egg-info/ pip-wheel-metadata/ __pycache__/
	find cryptics/ -type d -name "__pycache__" -exec rm -vrf {} +
	find cryptics/ -type d -name "__pycache__" -delete
	find cryptics/ -type f -name "*.pyc" -delete
