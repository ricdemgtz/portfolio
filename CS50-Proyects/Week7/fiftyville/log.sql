-- Keep a log of any SQL queries you execute as you solve the mystery.

-- Keep a log of all SQL queries that you run to solve the mystery.

-- Step 1: Get a general sense of the crime from the crime scene reports.
-- I know the crime happened on July 28, 2024, on Humphrey Street.
SELECT description
FROM crime_scene_reports
WHERE year = 2024 AND month = 7 AND day = 28 AND street = 'Humphrey Street';
-- Result: Theft took place at 10:15am at the Humphrey Street bakery.
-- Interviews were conducted with three witnesses who were present at the time.
-- Each of their interview transcripts mentions the bakery. This is my next lead.

-- Step 2: Investigate the witness interviews from the bakery.
-- I'll look for all interviews on that day to find the ones that mention "bakery".
SELECT name, transcript
FROM interviews
WHERE year = 2024 AND month = 7 AND day = 28 AND transcript LIKE '%bakery%';
-- Results provide three key pieces of information from three witnesses:
-- Witness 1 (Ruth): Sometime within ten minutes of the theft (10:15-10:25am), the thief got into a car in the bakery parking lot and drove away.
--    -> This points to the 'bakery_security_logs' table.
-- Witness 2 (Eugene): Before arriving at the bakery, he saw the thief at an ATM on Leggett Street withdrawing some money.
--    -> This points to the 'atm_transactions' table.
-- Witness 3 (Raymond): The thief called someone as they were leaving the bakery. The call lasted less than a minute. They said they were planning to take the earliest flight out of Fiftyville tomorrow (July 29, 2024) and asked the person on the other end to purchase the flight ticket.
--    -> This points to 'phone_calls', 'flights', 'passengers', and identifies the accomplice.

-- Now I have four leads to follow to build a list of suspects. The thief must satisfy all four conditions.

-- Lead 1: Check the bakery security logs for cars leaving between 10:15 and 10:25 AM.
SELECT license_plate
FROM bakery_security_logs
WHERE year = 2024 AND month = 7 AND day = 28 AND hour = 10 AND minute BETWEEN 15 AND 25;

-- Lead 2: Check ATM transactions on Leggett Street for withdrawals on the morning of July 28.
SELECT account_number
FROM atm_transactions
WHERE year = 2024 AND month = 7 AND day = 28 AND atm_location = 'Leggett Street' AND transaction_type = 'withdraw';

-- Lead 3: Check phone calls on July 28 that were less than a minute long.
SELECT caller
FROM phone_calls
WHERE year = 2024 AND month = 7 AND day = 28 AND duration < 60;

-- Lead 4: Find the passengers on the earliest flight out of Fiftyville on July 29.
-- First, find the ID of the Fiftyville airport.
SELECT id FROM airports WHERE city = 'Fiftyville';
-- Result: Fiftyville airport ID is 8.

-- Next, find the earliest flight on July 29 from Fiftyville.
SELECT id
FROM flights
WHERE origin_airport_id = 8 AND year = 2024 AND month = 7 AND day = 29
ORDER BY hour, minute
LIMIT 1;
-- Result: The earliest flight has an ID of 36.

-- Now, get the passport numbers of all passengers on that flight.
SELECT passport_number
FROM passengers
WHERE flight_id = 36;

-- Now I will combine all these clues to find the thief.
-- The thief's information must be present in all four lists I've generated.
-- I'll find the names of people who match all the criteria.
SELECT p.name
FROM people p
JOIN bank_accounts ba ON p.id = ba.person_id
WHERE p.license_plate IN (
    SELECT license_plate FROM bakery_security_logs
    WHERE year = 2024 AND month = 7 AND day = 28 AND hour = 10 AND minute BETWEEN 15 AND 25
)
AND ba.account_number IN (
    SELECT account_number FROM atm_transactions
    WHERE year = 2024 AND month = 7 AND day = 28 AND atm_location = 'Leggett Street' AND transaction_type = 'withdraw'
)
AND p.phone_number IN (
    SELECT caller FROM phone_calls
    WHERE year = 2024 AND month = 7 AND day = 28 AND duration < 60
)
AND p.passport_number IN (
    SELECT passport_number FROM passengers
    WHERE flight_id = 36
);
-- Result: This query returns a single name: Bruce.
-- So, the THIEF is Bruce.

-- Now I need to find the city Bruce escaped to.
-- I'll find the destination of flight 36.
SELECT city
FROM airports
WHERE id = (SELECT destination_airport_id FROM flights WHERE id = 36);
-- Result: The destination city is New York City.

-- Finally, I need to find the accomplice.
-- The accomplice is the person who received the short phone call from Bruce on the day of the theft.
SELECT p.name
FROM people p
JOIN phone_calls pc ON p.phone_number = pc.receiver
WHERE pc.year = 2024 AND pc.month = 7 AND pc.day = 28 AND pc.duration < 60
AND pc.caller = (SELECT phone_number FROM people WHERE name = 'Bruce');
-- Result: The receiver of the call was Robin.
-- So, the ACCOMPLICE is Robin.

-- Mystery solved.
