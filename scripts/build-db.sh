#!/bin/bash

set -eu -o pipefail

rm -f clues.sqlite3
sqlite3 cryptics/cryptics.sqlite3 ".dump clues" | sqlite3 clues.sqlite3
sqlite3 clues.sqlite3 ".read queries/prepare-db-for-publication.sql"
sqlite3 clues.sqlite3 "
INSERT INTO metadata (key, value)
VALUES
    ('license', 'This dataset is made available under the Open Database License: http://opendatacommons.org/licenses/odbl/1.0/. Any rights in individual contents of the database are licensed under the Database Contents License: http://opendatacommons.org/licenses/dbcl/1.0/'),
    ('last_built', '$(date)')
"
sqlite3 clues.sqlite3 "VACUUM;"
sqlite-utils enable-fts clues.sqlite3 clues clue answer
