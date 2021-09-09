#!/bin/bash

set -eu -o pipefail

rm -rf clues.sqlite3
sqlite3 cryptics/cryptics.sqlite3 ".dump clues" | sqlite3 clues.sqlite3
sqlite3 clues.sqlite3 ".read cryptics/queries/scrub.sql"
sqlite3 clues.sqlite3 "vacuum;"
sqlite-utils enable-fts clues.sqlite3 clues clue answer
