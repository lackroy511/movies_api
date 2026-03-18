UPDATED_MOVIE_IDS = """
SELECT
    id
FROM
    content.film_work
WHERE
    updated_at > %s
ORDER BY
    id
LIMIT
    %s OFFSET %s
"""

MOVIE_IDS_FOR_UPDATED_PERSONS = """
SELECT
    DISTINCT film_work_id AS id
FROM
    content.person_film_work AS pfw
    JOIN content.person AS p ON p.id = pfw.person_id
WHERE
    p.updated_at > %s
ORDER BY
    film_work_id
LIMIT
    %s OFFSET %s;
"""

MOVIE_IDS_FOR_UPDATED_PERSON_ROLES = """
SELECT
    DISTINCT film_work_id AS id
FROM
    content.person_film_work
WHERE
    updated_at > %s
ORDER BY
    film_work_id
LIMIT
    %s OFFSET %s;
"""

MOVIE_IDS_FOR_UPDATED_GENRES = """
SELECT
    DISTINCT film_work_id AS id
FROM
    content.genre_film_work AS gfw
    JOIN content.genre AS g ON g.id = gfw.genre_id
WHERE
    g.updated_at > %s
ORDER BY
    film_work_id
LIMIT
    %s OFFSET %s;
"""

MOVIES_BY_IDS = """
SELECT
    fw.id AS id,
    fw.title,
    fw.description,
    fw.creation_date,
    fw.rating,
    fw.type,
    fw.created_at,
    fw.updated_at,
    COALESCE(
        jsonb_agg(
            DISTINCT jsonb_build_object(
                'id', p.id,
                'full_name', p.full_name,
                'role', pfw.role
            )
        ) FILTER (WHERE p.id IS NOT NULL),
        '[]' :: jsonb
    ) AS persons,
    COALESCE(
        jsonb_agg(DISTINCT g.name) FILTER (WHERE g.id IS NOT NULL),
        '[]' :: jsonb
    ) AS genres
FROM
    content.film_work fw
    LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
    LEFT JOIN content.person p ON p.id = pfw.person_id
    LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
    LEFT JOIN content.genre g ON g.id = gfw.genre_id
WHERE fw.id = ANY(%s)
GROUP BY fw.id;
"""