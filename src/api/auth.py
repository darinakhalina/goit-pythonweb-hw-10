from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
import logging

from src.schemas.users import UserCreate, UserBase
from src.schemas.token import Token
from src.services.auth import create_access_token, Hash, get_email_from_token
from src.services.users import UserService
from src.services.email import send_email
from src.database.db import get_db


class HTTPConflictRequestException(HTTPException):
    def __init__(self, detail: str | None = None) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail or "Conflict",
        )


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserBase, status_code=status.HTTP_201_CREATED)
async def register_user(
    user: UserCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user_service = UserService(db)
    email_user = await user_service.get_user_by_email(user.email)

    if email_user:
        raise HTTPConflictRequestException("Cannot create user, email already in use.")

    username_user = await user_service.get_user_by_username(user.username)

    if username_user:
        raise HTTPConflictRequestException(
            "Cannot create user, username already exists."
        )

    user.password = Hash().get_password_hash(user.password)
    new_user = await user_service.create_user(user)

    background_tasks.add_task(
        send_email, str(new_user.email), str(new_user.username), str(request.base_url)
    )

    logger.info(f'Email sent for "{new_user.username}".')

    return new_user


@router.post("/login", response_model=Token)
async def login_user(
    request_form: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    user_service = UserService(db)
    user = await user_service.get_user_by_username(request_form.username)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not confirmed",
            headers={"WWW-Authenticate": "Bearer"},
        )

    password_verified = Hash().verify_password(request_form.password, user.password)

    if not password_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = {"sub": user.username}
    access_token = await create_access_token(payload)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/verify_email/{token}")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    email = await get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )

    if bool(user.confirmed):
        return {"message": "Email is already confirmed."}

    await user_service.verify_email(email)
    logger.info(f"Email address {email} verified.")
    return {"message": "Email has been successfully confirmed."}
