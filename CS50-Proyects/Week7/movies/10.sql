-- Selects the unique names of people.
-- Joins 'people' with 'directors' to link people to movies they directed.
-- Joins the result with 'ratings' to get movie ratings.
-- Filters for movies with a rating of 9.0 or higher.
SELECT DISTINCT name FROM people
JOIN directors ON people.id = directors.person_id
JOIN ratings ON directors.movie_id = ratings.movie_id
WHERE rating >= 9.0;
