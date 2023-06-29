import jwt
from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from passlib.context import CryptContext
from pymongo.collection import Collection

from pymongo.errors import DuplicateKeyError

from models.User import User

router = APIRouter()

SECRET_KEY = "sjdflaskdjlnksioewirusjkczxnklsjf"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password_token(plain_password, hashed_password):
    return jwt.encode({"password": plain_password}, hashed_password)


def create_access_token(data):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/register", response_description="Register a user", status_code=status.HTTP_201_CREATED,
             response_model=User)
def register(user: User):
    name = user.name
    email = user.email
    password = user.password

    if not name or not email or not password:
        return {"message": "Please provide name, email, and password"}

    try:
        user_data = {"name": name, "email": email, "password": password}
        app.users_collection.insert_one(user_data)
        return {"message": "User registered successfully"}
    except DuplicateKeyError:
        return {"message": "Email already exists. Please choose a different email."}
