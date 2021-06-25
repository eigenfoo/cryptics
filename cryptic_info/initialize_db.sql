-- https://www.fifteensquared.net/
CREATE TABLE IF NOT EXISTS fifteensquared (
    url PRIMARY KEY,
    datetime_requested TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    html TEXT
);
CREATE INDEX IF NOT EXISTS fifteensquared_url_index ON fifteensquared (url);

-- https://times-xwd-times.livejournal.com/
CREATE TABLE IF NOT EXISTS times_xwd_times (
    url PRIMARY KEY,
    datetime_requested TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    html TEXT
);
CREATE INDEX IF NOT EXISTS times_xwd_times_url_index ON times_xwd_times (url);

-- http://bigdave44.com/
CREATE TABLE IF NOT EXISTS bigdave44 (
    url PRIMARY KEY,
    datetime_requested TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    html TEXT
);
CREATE INDEX IF NOT EXISTS bigdave44_url_index ON bigdave44 (url);
