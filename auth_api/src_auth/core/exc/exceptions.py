
class UserAlreadyExistsError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class InvalidTokenOrExpiredTokenError(Exception):
    pass