"""
Errores del dominio.

Los servicios lanzan estos errores con un mensaje pensado para mostrarle
al usuario. La capa de API los traduce a códigos HTTP
(ver `api/error_handlers.py`).

Cada error tiene un `code` fijo que el frontend puede usar para decidir
qué mostrar, sin tener que comparar textos.
"""


class DomainError(Exception):
    code = "DOMAIN_ERROR"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class NotFoundError(DomainError):
    code = "NOT_FOUND"


class InvalidCredentialsError(DomainError):
    code = "INVALID_CREDENTIALS"


class PermissionDeniedError(DomainError):
    code = "PERMISSION_DENIED"


class InvalidDataError(DomainError):
    code = "INVALID_DATA"


class InvalidOrderError(DomainError):
    code = "INVALID_ORDER"


class OrderingClosedError(DomainError):
    code = "ORDERING_CLOSED"


class ProductSoldOutError(DomainError):
    code = "PRODUCT_SOLD_OUT"


class InvalidStatusChangeError(DomainError):
    code = "INVALID_STATUS_CHANGE"


class InvalidSettingError(DomainError):
    code = "INVALID_SETTING"
