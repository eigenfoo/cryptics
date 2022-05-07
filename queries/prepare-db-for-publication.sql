CREATE TABLE new_clues (
    rowid INTEGER PRIMARY KEY,
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
    rowid,
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
    'square_pursuit'
);
DROP TABLE clues;
ALTER TABLE new_clues RENAME TO clues;

ALTER TABLE indicators RENAME TO indicators_by_clue;
ALTER TABLE indicators_unpivoted RENAME TO indicators;

ALTER TABLE charades RENAME TO charades_by_clue;
ALTER TABLE charades_unpivoted RENAME TO charades;

-- pandas.DataFrame.to_sql does not set a primary key, so we do that manually here
CREATE TABLE IF NOT EXISTS charades_new (rowid INTEGER PRIMARY KEY, charade TEXT, answer TEXT, clue_rowids TEXT);
INSERT INTO charades_new SELECT rowid, * from charades;
DROP TABLE charades;
ALTER TABLE charades_new RENAME TO charades;

CREATE TABLE IF NOT EXISTS indicators_new (rowid INTEGER PRIMARY KEY, wordplay TEXT, indicator TEXT, clue_rowids TEXT);
INSERT INTO indicators_new SELECT rowid, * from indicators;
DROP TABLE indicators;
ALTER TABLE indicators_new RENAME TO indicators;

-- To facilitate Datasette facets
CREATE INDEX clues_source_index ON clues ("source");
CREATE INDEX indicators_wordplay_index ON indicators ("wordplay");
CREATE INDEX indicators_by_clue_wordplay_index ON indicators_by_clue ("wordplay");

CREATE TABLE metadata (
    key TEXT PRIMARY KEY,
    value TEXT
) WITHOUT ROWID;
