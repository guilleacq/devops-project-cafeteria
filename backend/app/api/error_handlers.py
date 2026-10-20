"""
Traduce los errores del dominio a respuestas HTTP.

Toda respuesta de error tiene la misma forma:

    { "code": "ORDERING_CLOSED", "detail": "Ya no se puede pedir para ..." }
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.domain import errors


HTTP_STATUS_BY_ERROR = {
    errors.NotFoundError: 404,
    errors.InvalidCredentialsError: 401,
    errors.PermissionDeniedError: 403,
    errors.InvalidDataError: 422,
    errors.InvalidOrderError: 422,
    errors.OrderingClosedError: 422,
    errors.ProductSoldOutError: 409,
    errors.InvalidStatusChangeError: 409,
    errors.InvalidSettingError: 422,
}


def register_error_handlers(app: FastAPI) -> None:

    @app.exception_handler(errors.DomainError)
    async def handle_domain_error(request: Request, error: errors.DomainError) -> JSONResponse:
        http_status = HTTP_STATUS_BY_ERROR.get(type(error), 400)

        return JSONResponse(
            status_code=http_status,
            content={"code": error.code, "detail": error.message},
        )
