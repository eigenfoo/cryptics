#!/bin/bash

set -eu -o pipefail

datasette publish heroku clues.sqlite3 \
    --extra-options "--setting suggest_facets off --setting allow_download on --setting max_csv_mb 0" \
    --metadata metadata.json \
    --template-dir templates/ \
    --static static:static/ \
    --install datasette-render-markdown \
    --name cryptic-crossword-clues
