CREATE TABLE new_clues (
    source TEXT,
    clue TEXT,
    answer TEXT,
    definition TEXT,
    clue_number TEXT,
    puzzle_date TEXT,
    puzzle_name TEXT,
    puzzle_url TEXT
);
INSERT INTO new_clues SELECT
    source,
    clue,
    answer,
    definition,
    clue_number,
    puzzle_date,
    puzzle_name,
    puzzle_url
FROM clues;
DROP TABLE IF EXISTS clues;
ALTER TABLE new_clues RENAME TO clues;

DELETE FROM clues WHERE source IN (
    'out_of_left_field',
    'square_pursuit',
    'the_browser'
);