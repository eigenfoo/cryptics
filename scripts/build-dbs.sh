#!/bin/bash

set -eu -o pipefail

# Database for publication using Datasette
rm -f data.sqlite3
sqlite3 cryptics.sqlite3 ".dump clues" | sqlite3 data.sqlite3
sqlite3 cryptics.sqlite3 ".dump indicators" | sqlite3 data.sqlite3
sqlite3 cryptics.sqlite3 ".dump indicators_unpivoted" | sqlite3 data.sqlite3
sqlite3 cryptics.sqlite3 ".dump charades" | sqlite3 data.sqlite3
sqlite3 cryptics.sqlite3 ".dump charades_unpivoted" | sqlite3 data.sqlite3
sqlite3 data.sqlite3 ".read queries/prepare-db-for-publication.sql"
sqlite3 data.sqlite3 "
INSERT INTO metadata (key, value)
VALUES
    ('license', 'This dataset is made available under the Open Database License: http://opendatacommons.org/licenses/odbl/1.0/. Any rights in individual contents of the database are licensed under the Database Contents License: http://opendatacommons.org/licenses/dbcl/1.0/'),
    ('last_built', '$(date)')
"
sqlite3 data.sqlite3 "VACUUM;"
sqlite-utils enable-fts data.sqlite3 clues clue answer
sqlite-utils enable-fts data.sqlite3 indicators indicator
sqlite-utils enable-fts data.sqlite3 charades charade answer

# Database for sharing
rm -f data-annotated.sqlite3
sqlite3 cryptics.sqlite3 ".dump clues" | sqlite3 data-annotated.sqlite3
sqlite3 cryptics.sqlite3 ".dump indicators" | sqlite3 data-annotated.sqlite3
sqlite3 cryptics.sqlite3 ".dump indicators_unpivoted" | sqlite3 data-annotated.sqlite3
sqlite3 cryptics.sqlite3 ".dump charades" | sqlite3 data-annotated.sqlite3
sqlite3 cryptics.sqlite3 ".dump charades_unpivoted" | sqlite3 data.sqlite3
sqlite3 data-annotated.sqlite3 ".read queries/prepare-db-for-sharing.sql"
sqlite3 data-annotated.sqlite3 "
INSERT INTO metadata (key, value)
VALUES
    ('license', 'This dataset is made available under the Open Database License: http://opendatacommons.org/licenses/odbl/1.0/. Any rights in individual contents of the database are licensed under the Database Contents License: http://opendatacommons.org/licenses/dbcl/1.0/'),
    ('last_built', '$(date)')
"
sqlite3 data-annotated.sqlite3 "VACUUM;"
