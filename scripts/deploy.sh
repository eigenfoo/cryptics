#!/bin/bash

set -eu -o pipefail

datasette publish heroku data.sqlite3 \
    --extra-options "--setting suggest_facets off --setting allow_download on --setting truncate_cells_html 0 --setting max_csv_mb 0 --setting sql_time_limit_ms 2000" \
    --metadata metadata.json \
    --template-dir templates/ \
    --plugins-dir plugins/ \
    --static static:static/ \
    --install datasette-render-markdown \
    --name cryptic-crossword-clues
