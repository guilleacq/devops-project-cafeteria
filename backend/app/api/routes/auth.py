from fastapi import APIRouter, Depends

from app.api.dependencies import get_auth_service, get_current_user
from app.api.presenters import present_user
from app.api.schemas import LoginRequest, LoginResponse, UserResponse
from app.domain.models import User
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, auth_service: AuthService = Depends(get_auth_service)):
    login_result = auth_service.login(request.email, request.password)

    return LoginResponse(
        access_token=login_result.access_token,
        user=present_user(login_result.user),
    )


@router.get("/me", response_model=UserResponse)
def who_am_i(current_user: User = Depends(get_current_user)):
    return present_user(current_user)
