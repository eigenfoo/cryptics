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
    -- Sources to exclude
    'out_of_left_field',
    'square_pursuit',
    'the_browser'
)
ORDER BY puzzle_date DESC;
DROP TABLE clues;
ALTER TABLE new_clues RENAME TO clues;

ALTER TABLE indicators RENAME TO indicators_by_clue;
ALTER TABLE indicators_unpivoted RENAME TO indicators;

ALTER TABLE charades RENAME TO charades_by_clue;
ALTER TABLE charades_unpivoted RENAME TO charades;

-- To facilitate Datasette facets
CREATE INDEX clues_source_index ON clues ("source");
CREATE INDEX indicators_wordplay_index ON indicators ("wordplay");
CREATE INDEX indicators_by_clue_wordplay_index ON indicators_by_clue ("wordplay");

CREATE TABLE metadata (
    key TEXT PRIMARY KEY,
    value TEXT
) WITHOUT ROWID;
