-- Selects song names from the 'songs' table.
-- The WHERE clause filters for songs where 'artist_id' matches the 'id'
-- returned by a subquery that finds the artist ID for "Post Malone".
SELECT name FROM songs
WHERE artist_id = (SELECT id FROM artists WHERE name = 'Post Malone');
