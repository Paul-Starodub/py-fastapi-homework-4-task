from datetime import date
from fastapi import UploadFile, Form, File, HTTPException
from pydantic import BaseModel, field_validator, HttpUrl
from validation import validate_name, validate_image, validate_gender, validate_birth_date


class ProfileRequestSchema(BaseModel):
    first_name: str
    last_name: str
    gender: str
    date_of_birth: date
    info: str
    avatar: UploadFile

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, value):
        return validate_name(value)

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, value):
        return validate_gender(value)

    @field_validator("date_of_birth")
    @classmethod
    def validate_birth_date(cls, value):
        return validate_birth_date(value)

    @field_validator("avatar")
    def validate_image(cls, value):
        return validate_image(value)


class ProfileResponseSchema(BaseModel):
    id: int
    first_name: str
    last_name: str
    gender: str
    date_of_birth: date
    info: str
    avatar: str

