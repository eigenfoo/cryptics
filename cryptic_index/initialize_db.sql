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
  FOREIGN KEY (source_url) REFERENCES raw_bigdave44 (url)
);

PRAGMA VACUUM;
PRAGMA OPTIMIZE;
