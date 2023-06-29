from typing import List, Optional

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


class Place(BaseModel):
    owner: Optional[ObjectIdStr] = Field(None, description="Owner of the place (reference: User collection)",
                                         alias="owner")
    title: str = Field(..., max_length=255, description="Title of the place")
    address: str = Field(..., max_length=255, description="Address of the place")
    photos: List[str] = Field(..., description="List of place photos")
    description: str = Field(..., max_length=1000, description="Description of the place")
    amenities: List[str] = Field(..., description="List of place amenities")
    extraInfo: str = Field(None, description="Additional information about the place")
    checkIn: str = Field(..., description="Check-in time")
    checkOut: str = Field(..., description="Check-out time")
    maxGuests: int = Field(..., description="Maximum number of guests the place can accommodate")
    price: int = Field(..., description="Price of the place")

    @validator("owner", pre=True)
    def validate_owner(cls, value):
        if value is not None and isinstance(value, str):
            return str_to_object_id(value)
        return value

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }
        schema_extra = {
            "example": {
                "owner": "605aa046717b8d24acded5a3",
                "title": "Cozy Apartment",
                "address": "123 Main Street",
                "photos": ["photo1.jpg", "photo2.jpg"],
                "description": "A cozy apartment with all the amenities",
                "amenities": ["WiFi", "TV", "Kitchen"],
                "extraInfo": "No pets allowed",
                "checkIn": 14,
                "checkOut": 11,
                "maxGuests": 4,
                "price": 100
            }
        }
