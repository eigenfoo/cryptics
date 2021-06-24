CREATE TABLE IF NOT EXISTS fifteensquared (
    url PRIMARY KEY,
    datetime_requested TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    html TEXT
);
