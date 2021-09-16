CREATE TABLE IF NOT EXISTS html (
    source TEXT,
    url PRIMARY KEY,
    datetime_requested TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    html TEXT,
    is_parsed BOOLEAN DEFAULT FALSE,
    datetime_parsed TIMESTAMP DEFAULT NULL
);
CREATE TABLE IF NOT EXISTS puz (
    source TEXT,
    url PRIMARY KEY,
    datetime_requested TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    puz BLOB,
    is_parsed BOOLEAN DEFAULT FALSE,
    datetime_parsed TIMESTAMP DEFAULT NULL
);
CREATE TABLE IF NOT EXISTS clues (
    source TEXT,
    clue TEXT,
    answer TEXT,
    definition TEXT,
    annotation TEXT,
    clue_number TEXT,
    puzzle_date TEXT,
    puzzle_name TEXT,
    puzzle_url TEXT,
    source_url TEXT NOT NULL,
    is_reviewed BOOLEAN DEFAULT FALSE,
    datetime_reviewed TIMESTAMP DEFAULT NULL,
    FOREIGN KEY (source_url) REFERENCES html (url)
);
