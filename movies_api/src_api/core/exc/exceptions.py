

class BaseMoviesAPIError(Exception):
    pass


class UnauthorizedError(BaseMoviesAPIError):
    pass


class ForbiddenError(BaseMoviesAPIError):
    pass