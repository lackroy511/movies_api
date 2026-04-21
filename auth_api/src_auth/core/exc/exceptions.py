
class UserAlreadyExistsError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class InvalidTokenOrExpiredTokenError(Exception):
    pass


class RoleNotFoundError(Exception):
    pass


class UserOrRoleNotFoundError(Exception):
    pass


class RoleAlreadyAssignedError(Exception):
    pass


class RoleAlreadyExistsError(Exception):
    pass