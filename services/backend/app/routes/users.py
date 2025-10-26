from fastapi import APIRouter, Body, Depends, HTTPException, Path, Security
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import UUID4
from typing import List

from app.schemas import JWTAccessToken, JWTRefreshToken, JWTToken, RefreshToken, UserCreate, UserCreated, UserGet, UserChangePasswordIn, UserGrantPrivileges
from app.models import User
from app.services.users import create_user, change_password, get_access_token, grant_user, login_refresh_token, refresh_token, validate_access_token
from app.utils.contrib import get_current_user, get_current_admin, reusable_oauth2


router = APIRouter()


@router.post("/", response_model=UserCreated, status_code=201)
async def route_create_user(user: UserCreate):
    created_user = await create_user(user=user)
    if not created_user:
        raise HTTPException(status_code=400, detail="User registration failed.") 
    return created_user


@router.get("/me", response_model=UserGet, status_code=200)
async def route_get_user(user: User = Depends(get_current_user)):
    return user


# @router.patch("/me", response_model=UserGet, status_code=200)
# async def route_update_user_me(
#     profile_data: UserUpdateProfile,
#     current_user: User = Depends(get_current_user)
# ):
#     updated_user = await update_profile(
#         current_user=current_user,
#         profile_data=profile_data
#     )
#     return updated_user


@router.post("/me/change_password", status_code=200)
async def route_change_password(
    change_password_in: UserChangePasswordIn,
    current_user: User = Depends(get_current_user)
):
    return await change_password(change_password_in=change_password_in, current_user=current_user)


@router.post("/{user_uuid}/grant", response_model=UserGet, status_code=200)
async def route_grant_user_privileges(
    user_uuid: UUID4 = Path(..., title="UUID пользователя для изменения роли"),
    grant_data: UserGrantPrivileges = Body(...),
    current_admin: User = Depends(get_current_admin)
):
    updated_user = await grant_user(user_uuid=user_uuid, user_grant=grant_data)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found or role update failed.")
    return updated_user


@router.post("/access-token", response_model=JWTToken, status_code=200)
async def route_access_token(credentials: OAuth2PasswordRequestForm = Depends()):
    return await get_access_token(credentials=credentials)


@router.post("/refresh-token", response_model=JWTRefreshToken, status_code=200)
async def route_refresh_token(credentials: OAuth2PasswordRequestForm = Depends()):
    return await login_refresh_token(credentials=credentials)


@router.post("/refresh", response_model=JWTAccessToken, status_code=200)
async def route_refresh(token: RefreshToken):
    return await refresh_token(token=token)


@router.get("/validate")
async def validate_assess_token(
    token: str = Security(reusable_oauth2)
):
    return await validate_access_token(token=token)