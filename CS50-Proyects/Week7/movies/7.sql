-- Selects movie titles and their ratings.
-- Joins 'movies' and 'ratings' tables on their common movie ID.
-- Filters for movies released in 2010.
-- Orders results first by rating (highest to lowest), then by title (alphabetically).
SELECT title, rating FROM movies
JOIN ratings ON movies.id = ratings.movie_id
WHERE year = 2010
ORDER BY rating DESC, title;
