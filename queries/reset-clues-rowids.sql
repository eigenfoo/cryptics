INSERT INTO clues_renumbered SELECT ROW_NUMBER() OVER (ORDER BY ROWID), * FROM clues;
DROP TABLE clues;
ALTER TABLE clues_renumbered RENAME TO clues;
