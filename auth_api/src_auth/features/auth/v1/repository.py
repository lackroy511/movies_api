

class AuthRepoInterface:
    pass


class AuthRepo(AuthRepoInterface):
    pass


def get_auth_repository() -> AuthRepoInterface:
    return AuthRepo()