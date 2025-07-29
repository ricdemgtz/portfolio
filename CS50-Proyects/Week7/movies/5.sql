-- Selects the 'title' and 'year' columns from the 'movies' table.
-- Filters for movies whose titles begin with "Harry Potter".
-- Orders the results chronologically by release year.
SELECT title, year FROM movies WHERE title LIKE 'Harry Potter%' ORDER BY year;
