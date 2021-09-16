CREATE TABLE new_clues (
    clue TEXT,
    answer TEXT,
    definition TEXT,
    clue_number TEXT,
    puzzle_date TEXT,
    puzzle_name TEXT,
    source_url TEXT NOT NULL,
    source TEXT
);
INSERT INTO new_clues SELECT
    clue,
    answer,
    definition,
    clue_number,
    puzzle_date,
    puzzle_name,
    source_url,
    source
FROM clues
WHERE source NOT IN (
    'out_of_left_field',
    'square_pursuit',
    'the_browser'
);
DROP TABLE IF EXISTS clues;
ALTER TABLE new_clues RENAME TO clues;
CREATE INDEX clues_source_index ON clues ("source");

CREATE TABLE metadata (
    key TEXT PRIMARY KEY,
    value TEXT
) WITHOUT ROWID;
