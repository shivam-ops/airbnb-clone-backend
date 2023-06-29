from datetime import date
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, Field, validator


def str_to_object_id(value: str) -> ObjectId:
    return ObjectId(value)


class ObjectIdStr(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        if not isinstance(value, ObjectId):
            try:
                value = str_to_object_id(value)
            except ValueError:
                raise ValueError("Invalid ObjectId")
        return value


class Booking(BaseModel):
    place: Optional[ObjectIdStr] = Field(None, description="Owner of the place (reference: Place collection)",
                                         alias="place")
    user: str
    checkIn: date
    checkOut: date
    name: str = Field(..., min_length=1, max_length=100)
    numberOfGuests: int = Field(..., ge=1, le=5)
    phoneNumber: str = Field(..., min_length=1, max_length=10)
    price: float

    @validator("place", pre=True, check_fields=False)
    def validate_owner(cls, value):
        if value is not None and isinstance(value, str):
            return str_to_object_id(value)
        return value

    class Config:
        schema_extra = {
            "example": {
                "place": "6123456789abcdef0123456",
                "user": "6123456789abcdef0123456",
                "checkIn": "2023-06-01",
                "checkOut": "2023-06-05",
                "name": "John Doe",
                "phoneNumber": "1234567890",
                "price": 100.0,
            }
        }
