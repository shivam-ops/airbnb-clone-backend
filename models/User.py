from pydantic import BaseModel, Field


class UserRegister(BaseModel):
    name: str = Field(..., max_length=100)
    email: str
    password: str = Field(..., max_length=128)

    class Config:
        schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "johndoe@example.com",
                "password": "secretpassword"
            }
        }


class UserLogin(BaseModel):
    email: str
    password: str

    class Config:
        schema_extra = {
            "example": {
                "email": "johndoe@example.com",
                "password": "secretpassword"
            }
        }

    # class Config:
    #     allow_population_by_field_name = True
    #     schema_extra = {
    #         "example": {
    #             "name": "Shivam Joshi",
    #             "email": "abc@gmail.com",
    #             "password": "abc123"
    #         }
    #     }


# class BookUpdate(BaseModel):
#     title: Optional[str]
#     author: Optional[str]
#     synopsis: Optional[str]
#
#     class Config:
#         schema_extra = {
#             "example": {
#                 "title": "Don Quixote",
#                 "author": "Miguel de Cervantes",
#                 "synopsis": "Don Quixote is a Spanish novel by Miguel de Cervantes..."
#             }
#         }
