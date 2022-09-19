.DEFAULT_GOAL = help

PYTHON := python3
PIP := pip

STATIC_TARGETS := templates/index.html templates/pages/datasheet.html

.ONESHELL:
.SHELLFLAGS := -e -c
.DELETE_ON_ERROR:
.MAKEFLAGS += --no-builtin-rules

.PHONY: help
help:
	@printf "Usage:\n"
	@grep -E '^[a-zA-Z_-]+:.*?# .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?# "}; {printf "\033[1;34mmake %-10s\033[0m%s\n", $$1, $$2}'

.PHONY: venv
venv:  # Set up a Python virtual environment for development.
	@printf "Creating Python virtual environment...\n"
	rm -rf venv/
	${PYTHON} -m venv venv/
	. venv/bin/activate
	${PIP} install -U pip
	${PIP} install -r requirements.txt
	mypy --install-types --non-interactive --ignore-missing-imports cryptics/
	pre-commit install
	deactivate
	@printf "\n\nVirtual environment created! \033[1;34mRun \`source venv/bin/activate\` to activate it.\033[0m\n\n\n"

.PHONY: format
format: # Format code in-place using pre-commit.
	pre-commit run --all-files

.PHONY: test
test:  # Run mypy and pytest tests.
	mypy --ignore-missing-imports --package cryptics
	mypy --ignore-missing-imports tests/
	pytest tests/

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
deploy:  clean build  # Deploy Datasette project to Fly.
	bash scripts/deploy.sh

.PHONY: clean
clean:  # Clean project directories.
	rm -rf data.sqlite3 data-annotated.sqlite3 $(STATIC_TARGETS) cryptics.egg-info/ pip-wheel-metadata/ __pycache__/
	find cryptics/ -type d -name "__pycache__" -exec rm -rf {} +
	find cryptics/ -type d -name "__pycache__" -delete
	find cryptics/ -type f -name "*.pyc" -delete
