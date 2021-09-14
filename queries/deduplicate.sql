DELETE FROM clues
WHERE rowid NOT IN (
    SELECT MIN(rowid)
    FROM clues
    GROUP BY source_url, clue, answer, definition, clue_number, puzzle_date, puzzle_name, puzzle_url
);
