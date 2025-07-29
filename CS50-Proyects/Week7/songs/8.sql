-- Selects song names from the 'songs' table.
-- The WHERE clause uses the LIKE operator to find any song
-- whose name contains the substring "feat.". The '%' are wildcards.
SELECT name FROM songs WHERE name LIKE '%feat.%';
