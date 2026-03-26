UPDATED_MOVIES = """
WITH changed_films AS (
    SELECT
        fw.id,
        fw.title,
        fw.description,
        fw.creation_date,
        fw.rating,
        fw.type,
        fw.created_at,
        fw.updated_at
    FROM content.film_work fw
    WHERE fw.updated_at > %s
       OR EXISTS (
            SELECT 1
            FROM content.person_film_work pfw
            JOIN content.person p ON p.id = pfw.person_id
            WHERE pfw.film_work_id = fw.id
              AND GREATEST(p.updated_at, pfw.updated_at) > %s
       )
       OR EXISTS (
            SELECT 1
            FROM content.genre_film_work gfw
            JOIN content.genre g ON g.id = gfw.genre_id
            WHERE gfw.film_work_id = fw.id
              AND g.updated_at > %s
       )
),

person_rows AS (
    SELECT DISTINCT
        pfw.film_work_id,
        p.id,
        p.full_name,
        pfw.role
    FROM content.person_film_work pfw
    JOIN content.person p ON p.id = pfw.person_id
    JOIN changed_films cf ON cf.id = pfw.film_work_id
),

persons_agg AS (
    SELECT
        film_work_id,
        jsonb_agg(
            jsonb_build_object(
                'id', id,
                'full_name', full_name,
                'role', role
            )
        ) AS persons
    FROM person_rows
    GROUP BY film_work_id
),

genre_rows AS (
    SELECT DISTINCT
        gfw.film_work_id,
        g.name
    FROM content.genre_film_work gfw
    JOIN content.genre g ON g.id = gfw.genre_id
    JOIN changed_films cf ON cf.id = gfw.film_work_id
),

genres_agg AS (
    SELECT
        film_work_id,
        jsonb_agg(name) AS genres
    FROM genre_rows
    GROUP BY film_work_id
)

SELECT
    fw.id,
    fw.title,
    fw.description,
    fw.creation_date,
    fw.rating,
    fw.type,
    fw.created_at,
    fw.updated_at,
    COALESCE(pa.persons, '[]'::jsonb) AS persons,
    COALESCE(ga.genres, '[]'::jsonb) AS genres
FROM changed_films fw
LEFT JOIN persons_agg pa ON pa.film_work_id = fw.id
LEFT JOIN genres_agg ga ON ga.film_work_id = fw.id
ORDER BY fw.id
LIMIT %s OFFSET %s;
"""


UPDATED_GENRES = """
SELECT
    id,
    name,
    description
FROM content.genre
WHERE updated_at > %s
ORDER BY id
LIMIT %s OFFSET %s;
"""

UPDATED_PERSONS = """
SELECT
    id,
    full_name
FROM content.person
WHERE updated_at > %s
ORDER BY id
LIMIT %s OFFSET %s;
"""