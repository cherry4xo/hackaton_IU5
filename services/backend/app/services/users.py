from datetime import date, timedelta
from fastapi import HTTPException, Depends, Security
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import UUID4
from tortoise.exceptions import IntegrityError

from app.schemas import CredentialsSchema, RefreshToken, UserCreate, UserChangePasswordIn, UserGrantPrivileges
from app.models import User
from app.enums import UserRole
from app.utils import password
from app.utils.contrib import authenticate, get_current_user, validate_refresh_token, reusable_oauth2
from app.logger import log_calls

from app import settings
from app.utils.jwt import create_access_token, create_refresh_token

@log_calls
async def create_user(user: UserCreate):
    user_db = await User.get_by_email(email=user.email)
    
    if user_db is not None:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists"
        )
    
    user_db = await User.get_by_username(username=user.username)

    if user_db is not None:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists"
        )
    
    password_hash = password.get_password_hash(password=user.password)
    user_dict = user.model_dump(exclude=["password"])

    user_db = await User.create(**user_dict, password_hash=password_hash, registration_date=date.today())

    # metrics.backend_user_registrations_total.inc()
    return user_db


@log_calls
async def change_password(
    change_password_in: UserChangePasswordIn, 
    current_user: User = Depends(get_current_user)
):
    verified, updated_password_hash = password.verify_and_update_password(change_password_in.current_password, 
                                                                          current_user.password_hash)
    if not verified:
        raise HTTPException(
            status_code=401,
            detail="Entered current password is incorrect"
        )

    current_user.password_hash = password.get_password_hash(change_password_in.new_password)

    await current_user.save()


@log_calls
async def grant_user(user_uuid: UUID4, user_grant: UserGrantPrivileges):
    user = await User.get_or_none(uuid=user_uuid)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        target_role = UserRole(user_grant.role)
    except ValueError:
         raise HTTPException(
            status_code=400,
            detail="Invalid user role specified"
        )

    if user.role == target_role:
        return user

    user.role = target_role
    try:
        await user.save(update_fields=['role'])
    except Exception as e:
         print(f"Error saving new role for user {user.username}: {e}")
         raise HTTPException(status_code=500, detail="Failed to save user role.")

    return user


@log_calls
async def get_access_token(credentials: OAuth2PasswordRequestForm = Depends()):
    credentials = CredentialsSchema(email=credentials.username, password=credentials.password)
    user = await authenticate(credentials=credentials)

    if not user:
        raise HTTPException(
            status_code=400,
            detail="incorrect email or password"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)

    return {
        "access_token": create_access_token(data={"user_uuid": str(user.uuid)}, expires_delta=access_token_expires),
        "refresh_token": create_refresh_token(data={"user_uuid": str(user.uuid)}, expires_delta=refresh_token_expires),
        "token_type": "bearer"
    }


@log_calls
async def login_refresh_token(credentials: OAuth2PasswordRequestForm = Depends()):
    credentials = CredentialsSchema(email=credentials.username, password=credentials.password)
    user = await authenticate(credentials=credentials)

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Incorrect email or password"
        )
    refresh_token_expires = timedelta(minutes=settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES)

    return {
        "refresh_token": create_refresh_token(data={"user_uuid": str(user.uuid)}, expires_delta=refresh_token_expires),
        "token_type": "bearer"
    }


@log_calls
async def refresh_token(
    token: RefreshToken
):
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    user = await validate_refresh_token(token=token.refresh_token)

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="The user with uuid in token does not exist"
        )

    new_access_token = create_access_token(data={"user_uuid": str(user.uuid), "expires_delta": access_token_expires})

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }


@log_calls
async def validate_access_token(
    token: str = Security(reusable_oauth2)
):
    try:
        user = await get_current_user(token=token)
        return user
    except HTTPException as e:
        raise e 