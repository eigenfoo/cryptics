-- Deduplicate
DELETE FROM clues
WHERE ROWID NOT IN (
    SELECT MIN(ROWID)
    FROM clues
    GROUP BY source_url, clue, answer, definition, clue_number, puzzle_date, puzzle_name, puzzle_url
);

-- Reset ROWIDs
INSERT INTO clues_renumbered SELECT ROW_NUMBER() OVER (ORDER BY ROWID), * FROM clues;
DROP TABLE clues;
ALTER TABLE clues_renumbered RENAME TO clues;
