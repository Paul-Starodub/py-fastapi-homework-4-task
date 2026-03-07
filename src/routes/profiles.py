from datetime import date
from fastapi import APIRouter, Depends, status, HTTPException, UploadFile, File, Form
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from config import get_jwt_auth_manager
from database import get_db, UserModel, UserProfileModel
from schemas.profiles import ProfileRequestSchema
from sqlalchemy import select
from security.http import get_token
from security.interfaces import JWTAuthManagerInterface


router = APIRouter()


@router.post("/users/{user_id}/profile/", status_code=status.HTTP_201_CREATED)
async def create_profile(
    user_id: int,
    first_name: str = Form(...),
    last_name: str = Form(...),
    gender: str = Form(...),
    date_of_birth: date = Form(...),
    info: str = Form(...),
    avatar: UploadFile = File(...),
    token: str = Depends(get_token),
    jwt_manager: JWTAuthManagerInterface = Depends(get_jwt_auth_manager),
    db: AsyncSession = Depends(get_db),
):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header is missing")
    try:
        jwt_manager.verify_access_token_or_raise(token)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    try:
        input_profile = ProfileRequestSchema(
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            date_of_birth=date_of_birth,
            info=info,
            avatar=avatar,
        )
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=jsonable_encoder(exc.errors()))
    stmt = select(UserModel).filter_by(id=user_id)
    result = await db.execute(stmt)
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or not active.")
    stmt = select(UserProfileModel).filter_by(user_id=user_id)
    result = await db.execute(stmt)
    exc_profile = result.scalars().first()
    if exc_profile:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already has a profile.")
    profile = UserProfileModel(
        user_id=user_id,
        first_name=input_profile.first_name,
        last_name=input_profile.last_name,
        gender=input_profile.gender,
        date_of_birth=input_profile.date_of_birth,
        info=input_profile.info,
    )
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile
