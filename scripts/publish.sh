#!/bin/bash

set -eu -o pipefail

rm -rf content.sqlite3
sqlite3 cryptics/cryptics.sqlite3 ".dump clues" | sqlite3 content.sqlite3
sqlite3 content.sqlite3 ".read cryptics/queries/scrub.sql"

# markdown-to-sqlite content.sqlite3 datasheet docs/datasheet.md

sqlite3 content.sqlite3 "vacuum;"

