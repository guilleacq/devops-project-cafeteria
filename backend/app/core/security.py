"""
Contraseñas y tokens.

- Las contraseñas se guardan con PBKDF2 (de la librería estándar de Python),
  nunca en texto plano.
- Al iniciar sesión se entrega un JWT que contiene el id y el rol del usuario.
"""

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import Settings


PASSWORD_HASH_ALGORITHM = "sha256"
PASSWORD_HASH_ITERATIONS = 200_000


# ---------------------------------------------------------------------------
# Contraseñas
# ---------------------------------------------------------------------------

def hash_password(plain_password: str) -> str:
    """Devuelve un texto con el formato `iteraciones$salt$hash`."""
    salt = secrets.token_hex(16)
    password_hash = _derive_hash(plain_password, salt, PASSWORD_HASH_ITERATIONS)

    return f"{PASSWORD_HASH_ITERATIONS}${salt}${password_hash}"


def verify_password(plain_password: str, stored_hash: str) -> bool:
    iterations, salt, expected_hash = stored_hash.split("$")
    calculated_hash = _derive_hash(plain_password, salt, int(iterations))

    return hmac.compare_digest(calculated_hash, expected_hash)


def _derive_hash(plain_password: str, salt: str, iterations: int) -> str:
    derived_bytes = hashlib.pbkdf2_hmac(
        PASSWORD_HASH_ALGORITHM,
        plain_password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations,
    )
    return derived_bytes.hex()


# ---------------------------------------------------------------------------
# Tokens (JWT)
# ---------------------------------------------------------------------------

class InvalidTokenError(Exception):
    pass


def create_access_token(user_id: int, role: str, settings: Settings) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expiration_minutes)

    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": expires_at,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def read_user_id_from_token(token: str, settings: Settings) -> int:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return int(payload["sub"])

    except (jwt.PyJWTError, KeyError, ValueError) as error:
        raise InvalidTokenError("Token inválido o vencido.") from error
