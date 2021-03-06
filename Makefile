.DEFAULT_GOAL = help

PYTHON := python3
PIP := pip
CONDA := conda
SHELL := bash

.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
.DELETE_ON_ERROR:
MAKEFLAGS += --no-builtin-rules

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
	rm -rf venv/
	${PYTHON} -m venv venv/
	source venv/bin/activate
	${PIP} install -U pip
	${PIP} install -r requirements.txt
	deactivate
	@printf "\n\nVirtual environment created! \033[1;34mRun \`source venv/bin/activate\` to activate it.\033[0m\n\n\n"

.PHONY: black
black:  # Format code in-place using black.
	black cryptics/ *.py

.PHONY: lint
lint:  # Lint code using black.
	@printf "Checking code style with black...\n"
	black --check --diff cryptics/
	@printf "\033[1;34mBlack passes!\033[0m\n\n"

.PHONY: update
update:  # Scrape and parse unprocessed blog posts.
	${PYTHON} cryptics/amuselabs.py
	${PYTHON} cryptics/jsons.py
	${PYTHON} cryptics/main.py --sleep-interval=1

.PHONY: build
build: clean build-dbs build-templates test-build  # Build database and documentation for publication.

build-dbs: data.sqlite3

data.sqlite3: cryptics.sqlite3
	${PYTHON} cryptics/indicators.py
	bash scripts/build-dbs.sh

build-templates: $(STATIC_TARGETS)

# Generalized rule: how to build a .html file from each .md
# Note: you will need pandoc 2 or greater for this to work
templates/index.html: docs/index.md template.html5 scripts/build-template.sh
	scripts/build-template.sh "$<" "$@"

templates/pages/%.html: docs/%.md template.html5 scripts/build-template.sh
	scripts/build-template.sh "$<" "$@"

.PHONY: test-build
test-build:
	bash scripts/test-build.sh

.PHONY: serve
serve:  # Serve Datasette locally.
	datasette \
		--immutable data.sqlite3 \
		--template-dir templates/ \
		--plugins-dir plugins/ \
		--static static:static/ \
		--metadata metadata.json \
		--setting suggest_facets off \
		--setting allow_download on \
		--setting truncate_cells_html 0 \
		--setting max_csv_mb 0

.PHONY: deploy
deploy:  clean build  # Deploy Datasette project to Heroku.
	bash scripts/deploy.sh

.PHONY: clean
clean:  # Clean project directories.
	rm -rf data.sqlite3 data-annotated.sqlite3 $(STATIC_TARGETS) cryptics.egg-info/ pip-wheel-metadata/ __pycache__/
	find cryptics/ -type d -name "__pycache__" -exec rm -rf {} +
	find cryptics/ -type d -name "__pycache__" -delete
	find cryptics/ -type f -name "*.pyc" -delete

.PHONY: quota
quota:  # Show Heroku dynos and remaining free dyno hours.
	heroku ps --app cryptic-crossword-clues
