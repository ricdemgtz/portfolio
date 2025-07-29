-- Selects the names of people.
-- Joins 'people' with 'stars' to link people to movies they starred in.
-- Joins the result with 'movies' to get movie titles.
-- Filters for the movie with the title 'Toy Story'.
SELECT name FROM people
JOIN stars ON people.id = stars.person_id
JOIN movies ON stars.movie_id = movies.id
WHERE title = 'Toy Story';
