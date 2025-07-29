-- Calculates the average rating.
-- Joins 'ratings' and 'movies' tables on their common movie ID.
-- Filters the joined data to only include movies released in 2012.
SELECT AVG(rating) FROM ratings
JOIN movies ON ratings.movie_id = movies.id
WHERE year = 2012;
