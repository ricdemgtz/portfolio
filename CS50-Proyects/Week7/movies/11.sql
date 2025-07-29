-- Selects movie titles.
-- Joins 'people', 'stars', 'movies', and 'ratings' to link an actor to their movie titles and ratings.
-- Filters for movies starring 'Chadwick Boseman'.
-- Orders the movies by rating from highest to lowest.
-- Limits the result to the top 5 movies.
SELECT title FROM people
JOIN stars ON people.id = stars.person_id
JOIN movies ON stars.movie_id = movies.id
JOIN ratings ON movies.id = ratings.movie_id
WHERE name = 'Chadwick Boseman'
ORDER BY rating DESC
LIMIT 5;
