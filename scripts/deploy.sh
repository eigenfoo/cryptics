#!/bin/bash

set -eu -o pipefail

datasette publish heroku clues.sqlite3 \
    --extra-options "--setting allow_facet off --setting suggest_facets off --setting allow_download on" \
    --metadata metadata.json \
	--template-dir templates/ \
	--static static:static/ \
    --name cryptic-crossword-clues
