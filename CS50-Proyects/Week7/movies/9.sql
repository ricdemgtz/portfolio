-- Selects the unique names of people to avoid duplicates.
-- Joins 'people', 'stars', and 'movies' tables.
-- Filters for movies released in 2004.
-- Orders the results by the person's birth year.
SELECT DISTINCT name FROM people
JOIN stars ON people.id = stars.person_id
JOIN movies ON stars.movie_id = movies.id
WHERE year = 2004
ORDER BY birth;
