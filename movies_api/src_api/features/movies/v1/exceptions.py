class ErrorMessages:
    MOVIE_NOT_FOUND = "Movie not found"
    FORBIDDEN_ERROR = "Forbidden error"


class MovieNotFoundError(Exception):
    pass