from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_jwt_auth_manager
from database import get_db, UserModel, UserProfileModel
from dependencies import profile_form_data
from schemas.profiles import ProfileRequestSchema
from security.http import get_token
from security.interfaces import JWTAuthManagerInterface

router = APIRouter()



@router.post("/users/{user_id}/profile/", status_code=status.HTTP_201_CREATED)
async def create_profile(
    user_id: int,
    data: Annotated[ProfileRequestSchema, Depends(profile_form_data)],
    token: Annotated[str, Depends(get_token)],
    jwt_manager: Annotated[JWTAuthManagerInterface, Depends(get_jwt_auth_manager)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is missing"
        )

    try:
        jwt_manager.verify_access_token_or_raise(token)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc)
        )

    stmt = select(UserModel).filter_by(id=user_id)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or not active."
        )

    stmt = select(UserProfileModel).filter_by(user_id=user_id)
    result = await db.execute(stmt)
    exc_profile = result.scalars().first()

    if exc_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has a profile."
        )

    profile = UserProfileModel(
        user_id=user_id,
        first_name=data.first_name,
        last_name=data.last_name,
        gender=data.gender,
        date_of_birth=data.date_of_birth,
        info=data.info,
    )

    db.add(profile)
    await db.commit()
    await db.refresh(profile)

    return profile
