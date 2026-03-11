from datetime import date
from typing import Annotated

from fastapi import Form, HTTPException, status, UploadFile, File
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError

from schemas.profiles import ProfileRequestSchema


async def profile_form_data(
    first_name: Annotated[str, Form()],
    last_name: Annotated[str, Form()],
    gender: Annotated[str, Form()],
    info: Annotated[str, Form()],
    date_of_birth: Annotated[date, Form()],
    avatar: Annotated[UploadFile, File()],
) -> ProfileRequestSchema:

    try:
        return ProfileRequestSchema(
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            date_of_birth=date_of_birth,
            info=info,
            avatar=avatar,
        )

    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=jsonable_encoder(exc.errors()))
