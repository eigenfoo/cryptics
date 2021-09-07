-- https://www.fifteensquared.net/
CREATE TABLE IF NOT EXISTS raw_fifteensquared (
    url PRIMARY KEY,
    datetime_requested TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    html TEXT,
    is_parsed BOOLEAN DEFAULT FALSE,
    datetime_parsed TIMESTAMP DEFAULT NULL
);
CREATE INDEX IF NOT EXISTS raw_fifteensquared_url_index ON raw_fifteensquared (url);
CREATE TABLE IF NOT EXISTS parsed_fifteensquared (
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
  FOREIGN KEY (source_url) REFERENCES raw_fifteensquared (url)
);

-- https://times-xwd-times.livejournal.com/
CREATE TABLE IF NOT EXISTS raw_times_xwd_times (
    url PRIMARY KEY,
    datetime_requested TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    html TEXT,
    is_parsed BOOLEAN DEFAULT FALSE,
    datetime_parsed TIMESTAMP DEFAULT NULL
);
CREATE INDEX IF NOT EXISTS raw_times_xwd_times_url_index ON raw_times_xwd_times (url);
CREATE TABLE IF NOT EXISTS parsed_times_xwd_times (
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
  FOREIGN KEY (source_url) REFERENCES raw_times_xwd_times (url)
);

-- http://bigdave44.com/
CREATE TABLE IF NOT EXISTS raw_bigdave44 (
    url PRIMARY KEY,
    datetime_requested TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    html TEXT,
    is_parsed BOOLEAN DEFAULT FALSE,
    datetime_parsed TIMESTAMP DEFAULT NULL
);
CREATE INDEX IF NOT EXISTS raw_bigdave44_url_index ON raw_bigdave44 (url);
CREATE TABLE IF NOT EXISTS parsed_bigdave44 (
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
  FOREIGN KEY (source_url) REFERENCES raw_bigdave44 (url)
);

-- Cru Cryptics
-- https://archive.nytimes.com/www.nytimes.com/premium/xword/cryptic-archive.html
CREATE TABLE IF NOT EXISTS parsed_cru_cryptics (
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
  datetime_reviewed TIMESTAMP DEFAULT NULL
);

-- The Browser
-- https://thebrowser.com/crossword-archive/
CREATE TABLE IF NOT EXISTS parsed_the_browser (
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
  datetime_reviewed TIMESTAMP DEFAULT NULL
);

-- Out of Left Field
-- https://www.leftfieldcryptics.com/
-- https://www.patreon.com/leftfieldcryptics/posts
CREATE TABLE IF NOT EXISTS parsed_out_of_left_field (
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
  datetime_reviewed TIMESTAMP DEFAULT NULL
);

-- Square Pursuit
-- https://squarepursuit.com/
CREATE TABLE IF NOT EXISTS parsed_square_pursuit (
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
  datetime_reviewed TIMESTAMP DEFAULT NULL
);

CREATE VIEW IF NOT EXISTS clues AS
SELECT *
FROM parsed_fifteensquared
UNION ALL
    SELECT *
    FROM parsed_times_xwd_times
UNION ALL
    SELECT *
    FROM parsed_bigdave44
UNION ALL
    SELECT *
    FROM parsed_cru_cryptics
UNION ALL
    SELECT *
    FROM parsed_the_browser
UNION ALL
    SELECT *
    FROM parsed_out_of_left_field
UNION ALL
    SELECT *
    FROM parsed_square_pursuit
;