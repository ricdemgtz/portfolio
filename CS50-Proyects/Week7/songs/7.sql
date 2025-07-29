-- Calculates the average energy for a specific set of songs.
-- The set is determined by a WHERE clause that filters for songs where 'artist_id'
-- matches the 'id' of "Drake", found via a subquery.
SELECT AVG(energy) FROM songs
WHERE artist_id = (SELECT id FROM artists WHERE name = 'Drake');
