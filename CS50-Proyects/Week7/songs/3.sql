-- Selects the 'name' column from the 'songs' table.
-- Orders the results by 'duration_ms' in descending order.
-- Limits the output to the top 5 results.
SELECT name FROM songs ORDER BY duration_ms DESC LIMIT 5;
