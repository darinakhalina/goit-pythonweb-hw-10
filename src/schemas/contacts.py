from datetime import date
from pydantic import BaseModel, Field, EmailStr, ConfigDict


class ContactBase(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr = Field(max_length=200)
    phone: str = Field(min_length=3, max_length=50)
    birthday: date


class ContactUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = Field(default=None, max_length=180)
    phone: str | None = Field(default=None, min_length=3, max_length=80)
    birthday: date | None = None


class ContactResponse(ContactBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
