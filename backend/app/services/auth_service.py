"""
Inicio de sesión y lectura del usuario a partir del token.
"""

from dataclasses import dataclass

from app.core.config import Settings
from app.core.security import InvalidTokenError, create_access_token, read_user_id_from_token, verify_password
from app.domain.errors import InvalidCredentialsError
from app.domain.models import User
from app.repositories.interfaces import UserRepository


@dataclass
class LoginResult:
    access_token: str
    user: User


class AuthService:

    def __init__(self, user_repository: UserRepository, settings: Settings):
        self.user_repository = user_repository
        self.settings = settings

    def login(self, email: str, plain_password: str) -> LoginResult:
        user = self.user_repository.get_by_email(email)

        # Mismo mensaje si no existe el usuario o si la contraseña está mal:
        # así no se revela qué correos están registrados.
        if user is None or not verify_password(plain_password, user.password_hash):
            raise InvalidCredentialsError("Correo o contraseña incorrectos.")

        access_token = create_access_token(user.id, user.role.value, self.settings)
        return LoginResult(access_token=access_token, user=user)

    def get_user_from_token(self, token: str) -> User:
        try:
            user_id = read_user_id_from_token(token, self.settings)
        except InvalidTokenError as error:
            raise InvalidCredentialsError("La sesión no es válida o venció. Volvé a iniciar sesión.") from error

        user = self.user_repository.get_by_id(user_id)

        if user is None:
            raise InvalidCredentialsError("La sesión no es válida o venció. Volvé a iniciar sesión.")

        return user
