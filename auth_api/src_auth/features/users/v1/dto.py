from dataclasses import dataclass


@dataclass
class CreateUserDTO:
    email: str
    first_name: str
    last_name: str | None
    password_hash: str
    
    # TODO: изменить на False после реализации регистрации через email
    is_active: bool = True
