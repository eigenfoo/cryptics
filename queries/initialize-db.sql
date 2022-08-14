CREATE TABLE IF NOT EXISTS raw (
    source TEXT,
    location PRIMARY KEY,
    datetime_requested TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    content_type TEXT,
    content BLOB,
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
CREATE TABLE IF NOT EXISTS indicators (
    clue_rowid INT PRIMARY KEY,
    alternation TEXT DEFAULT '',
    anagram TEXT DEFAULT '',
    container TEXT DEFAULT '',
    deletion TEXT DEFAULT '',
    hidden TEXT DEFAULT '',
    homophone TEXT DEFAULT '',
    insertion TEXT DEFAULT '',
    reversal TEXT DEFAULT '',
    FOREIGN KEY (clue_rowid) REFERENCES clues (rowid)
);
CREATE TABLE IF NOT EXISTS charades (
    clue_rowid INT,
    charade TEXT DEFAULT '',
    answer TEXT DEFAULT '',
    FOREIGN KEY (clue_rowid) REFERENCES clues (rowid)
);
