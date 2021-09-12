CREATE TABLE new_clues (
    clue TEXT,
    answer TEXT,
    definition TEXT,
    clue_number TEXT,
    puzzle_date TEXT,
    puzzle_name TEXT,
    puzzle_url TEXT,
    source_url TEXT NOT NULL
);
INSERT INTO new_clues SELECT
    clue,
    answer,
    definition,
    clue_number,
    puzzle_date,
    puzzle_name,
    puzzle_url,
    source_url
FROM clues
WHERE source NOT IN (
    'out_of_left_field',
    'square_pursuit',
    'the_browser'
);
DROP TABLE IF EXISTS clues;
ALTER TABLE new_clues RENAME TO clues;

CREATE TABLE metadata (
    key TEXT PRIMARY KEY,
    value TEXT
) WITHOUT ROWID;