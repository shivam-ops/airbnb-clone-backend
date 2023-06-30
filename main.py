import json
import os.path
import tempfile
import time
import urllib.request
from typing import List

from PIL import Image
import jwt
from bson import ObjectId
from fastapi import FastAPI, status, HTTPException, Response, Request, Cookie, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import dotenv_values
from passlib.context import CryptContext
from passlib.handlers import bcrypt
from pymongo import MongoClient
from starlette.responses import JSONResponse
from dotenv import load_dotenv
from models.Booking import Booking
from models.Place import Place
from models.User import UserLogin
from models.User import UserRegister
import bcrypt
import os

#mongodb credential from env file
load_dotenv()
mongo_db_connection_string = os.getenv("MONGO_DB_CONNECTION_STRING")
mongo_db_name = os.getenv("MONGO_DB_NAME")


SECRET_KEY = "sjdflaskdjlnksioewirusjkczxnklsjf"
ALGORITHM = "HS256"

app = FastAPI()

# Get the absolute path to the 'uploads' directory
current_dir = os.path.dirname(os.path.abspath(__file__))
uploads_dir = os.path.join(current_dir, "uploads")

# Upload images
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# Configure CORS
origins = [
    "http://localhost:5173",
    'http://127.0.0.1:5173',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Set-Cookie"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password_token(plain_password, hashed_password):
    encoded_plain_password = plain_password.encode("utf-8")
    encoded_hashed_password = hashed_password.encode("utf-8")
    return bcrypt.checkpw(encoded_plain_password, encoded_hashed_password)


def create_access_token(data):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


env_vars = dotenv_values()

client = MongoClient(mongo_db_connection_string)
db = client[mongo_db_name]
users_collection = db["users"]
places_collection = db["places"]
bookings_collection = db["bookings"]


@app.get("/", status_code=200)
def hello_world():
    return {"Hello": "World!"}


@app.post("/api/register", response_description="Register a user", status_code=status.HTTP_201_CREATED)
async def register(user: UserRegister):
    if not user.name or not user.email or not user.password:
        raise HTTPException(status_code=400, detail="Please provide name, email, and password")

    existing_user = users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user.password)
    user_data = {"name": user.name, "email": user.email, "password": hashed_password}

    try:
        users_collection.insert_one(user_data)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error occurred during registration") from e

    return {"message": "User registered successfully"}


@app.post("/api/login", response_description="User login", status_code=status.HTTP_200_OK)
async def login(user: UserLogin, response: Response):
    existing_user = users_collection.find_one({"email": user.email})
    if not existing_user or not verify_password_token(user.password, existing_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password! Please try again")

    user_email = existing_user['email']
    user_id = str(existing_user['_id'])
    current_timestamp = int(time.time())

    token = create_access_token({"email": user_email, "id": user_id, "iat": current_timestamp})
    existing_user["token"] = token
    response.set_cookie(key="access_token", value=token)
    existing_user["_id"] = str(existing_user["_id"])

    return existing_user


@app.get("/api/profile", response_description="Get logged in user profile", status_code=status.HTTP_200_OK)
async def get_profile(token: str = Cookie(default=None, alias="access_token")):
    if token:
        try:
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
            user_id = decoded_token.get("id")
            iat = decoded_token.get("iat")
            if user_id:
                user = users_collection.find_one({"_id": ObjectId(user_id)})
                if user:
                    return {"name": user["name"], "email": user["email"], "_id": str(user["_id"]), "iat": iat}
        except jwt.exceptions.PyJWTError as e:
            raise HTTPException(status_code=401, detail="Invalid token") from e
    return None


@app.post("/api/logout", response_description="User logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response, token: str = Cookie(default=None, alias="access_token")):
    if token:
        try:
            response.delete_cookie("access_token")
            return {"message": "Logout successfully"}
        except jwt.exceptions.PyJWTError as e:
            raise HTTPException(status_code=401, detail="Invalid token") from e
    return {"message": "No token provided"}


# Create a temporary directory for testing
temp_dir = tempfile.TemporaryDirectory()


@app.post("/api/upload-by-link", response_description="Upload photos by a link", status_code=status.HTTP_201_CREATED)
async def upload_by_link(request: Request):
    data = await request.json()
    links = data.get("link")

    if isinstance(links, str):
        links = [links]

    filenames = []

    for link in links:
        try:
            timestamp = str(int(time.time() * 1000))
            filename = f"photo{timestamp}.jpg"
            # destination = os.path.join(temp_dir.name, filename)  # testing
            destination = os.path.join("uploads", filename)
            urllib.request.urlretrieve(link, destination)
            filenames.append(filename)
        except Exception as e:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"error": str(e)})
    return filenames


@app.post("/api/upload", response_description="Upload photos from your device", status_code=status.HTTP_201_CREATED)
async def upload_photo(photos: List[UploadFile] = File(...)):
    uploaded_files = []

    for photo in photos:
        try:
            timestamp = str(int(time.time() * 1000))
            contents = await photo.read()
            filename = f"photo{timestamp}.jpg"

            # Perform validation check on the file
            image = Image.open(photo.file)
            image.verify()  # Raises an exception if the file is not a valid image

            with open(f"uploads/{filename}", "wb") as f:
                f.write(contents)

            uploaded_files.append(filename)
        except (IOError, SyntaxError, Image.DecompressionBombError, Exception) as e:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"error": "Please upload valid photo"})

    return uploaded_files


@app.post("/api/places", response_description="Register places", status_code=status.HTTP_201_CREATED)
async def create_place(place: Place, token: str = Cookie(default=None, alias="access_token")):
    if not (
            place.title and place.address and place.photos and place.description and
            place.amenities and place.extraInfo and place.checkIn and place.checkOut and
            place.maxGuests
    ):
        raise HTTPException(status_code=400, detail="Please provide all required fields")

    # Validate title length
    if len(place.title) < 5:
        raise HTTPException(status_code=400, detail="Title should be a minimum of 5 characters")

    # Validate address length
    if len(place.address) < 10:
        raise HTTPException(status_code=400, detail="Address should be a minimum of 10 characters")

    # Validate description length
    if len(place.description) < 50:
        raise HTTPException(status_code=400, detail="Description should be a minimum of 50 characters")

    # Validate extraInfo length
    if len(place.extraInfo) < 50:
        raise HTTPException(status_code=400, detail="Extra info should be a minimum of 50 characters")

    existing_place = places_collection.find_one({"title": place.title})
    if existing_place:
        raise HTTPException(status_code=400, detail="Place already registered")
    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
    user_id = decoded_token.get("id")

    place.owner = ObjectId(user_id)

    place_data = {
        "owner": ObjectId(user_id),
        "title": place.title,
        "address": place.address,
        "photos": place.photos,
        "description": place.description,
        "amenities": place.amenities,
        "extraInfo": place.extraInfo,
        "checkIn": place.checkIn,
        "checkOut": place.checkOut,
        "maxGuests": place.maxGuests,
        "price": place.price
    }

    try:
        places_collection.insert_one(place_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error occurred while registration") from e

    place_data["_id"] = str(place_data["_id"])
    place_data["owner"] = str(place_data["owner"])

    return place_data


@app.get("/api/user_places", response_description="Get all registered places by user", status_code=status.HTTP_200_OK)
async def get_user_places(token: str = Cookie(default=None, alias="access_token")):
    if not token:
        raise HTTPException(status_code=401, detail="Token is missing")

    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        user_id = decoded_token.get("id")

        places = list(places_collection.find({"owner": ObjectId(user_id)}))
        places = json.loads(json.dumps(places, default=str))
        return places

    except jwt.exceptions.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.get("/api/places/{id}", response_description="Edit a place", status_code=status.HTTP_200_OK)
async def get_place_by_id(id: str):
    place = places_collection.find_one({"_id": ObjectId(id)})
    place = json.loads(json.dumps(place, default=str))
    if place:
        return place
    else:
        raise HTTPException(status_code=404, detail="Place not found")


@app.put("/api/places", response_description="Update a place", status_code=status.HTTP_200_OK)
async def update_place(request: Request, place: Place, token: str = Cookie(default=None, alias="access_token")):
    if not (
            place.title and place.address and place.photos and place.description and
            place.amenities and place.extraInfo and place.checkIn and place.checkOut and
            place.maxGuests
    ):
        raise HTTPException(status_code=400, detail="Please provide all required fields")

    # Validate title length
    if len(place.title) < 5:
        raise HTTPException(status_code=400, detail="Title should be a minimum of 5 characters")

    # Validate address length
    if len(place.address) < 10:
        raise HTTPException(status_code=400, detail="Address should be a minimum of 10 characters")

    # Validate description length
    if len(place.description) < 50:
        raise HTTPException(status_code=400, detail="Description should be a minimum of 50 characters")

    # Validate extraInfo length
    if len(place.extraInfo) < 50:
        raise HTTPException(status_code=400, detail="Extra info should be a minimum of 50 characters")

    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
    user_id = decoded_token.get("id")

    place_body = await request.json()
    place_id = place_body["id"]
    print(place_id)
    place_doc = places_collection.find_one({"_id": ObjectId(place_id)})
    if place_doc and str(place_doc["owner"]) == user_id:
        place_doc["title"] = place.title
        place_doc["address"] = place.address
        place_doc["photos"] = place.photos
        place_doc["description"] = place.description
        place_doc["amenities"] = place.amenities
        place_doc["extraInfo"] = place.extraInfo
        place_doc["checkIn"] = place.checkIn
        place_doc["checkOut"] = place.checkOut
        place_doc["maxGuests"] = place.maxGuests
        place_doc["price"] = place.price

        places_collection.update_one({"_id": ObjectId(place_id)}, {"$set": place_doc})
        return "Place updated successfully"
    else:
        raise HTTPException(status_code=403, detail="Unauthorized")


@app.get("/api/places", response_description="Get places", status_code=status.HTTP_200_OK)
async def get_places(page: int = 1, limit: int = 8):
    try:
        skip = (page - 1) * limit
        places = places_collection.find().skip(skip).limit(limit)
        places_json = json.dumps(list(places), default=str)
        places_decoded = json.loads(places_json)
        return places_decoded
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"error": str(e)})


@app.post("/api/bookings", response_description="Booking a place", status_code=status.HTTP_201_CREATED)
async def book_place(booking: Booking):
    existing_booking = bookings_collection.find_one({
        "place": str(booking.place),
        "user": booking.user,
        "checkIn": str(booking.checkIn),
        "checkOut": str(booking.checkOut)
    })

    if existing_booking:
        raise HTTPException(status_code=400, detail="Booking already exists. Try again!")

    booking_data = {
        "place": str(booking.place),
        "user": booking.user,
        "checkIn": str(booking.checkIn),
        "checkOut": str(booking.checkOut),
        "name": booking.name,
        "numberOfGuests": booking.numberOfGuests,
        "phoneNumber": booking.phoneNumber,
        "price": booking.price
    }

    place_data = places_collection.find_one(ObjectId(booking.place))

    if booking.numberOfGuests > place_data.get("maxGuests"):
        raise HTTPException(status_code=400, detail="Max guests exceeded. Try again")

    try:
        result = bookings_collection.insert_one(booking_data)
        booking_data["_id"] = str(result.inserted_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error occurred while making a booking")

    return booking_data


@app.get("/api/bookings", response_description="Get all bookings", status_code=status.HTTP_200_OK)
async def get_bookings(token: str = Cookie(default=None, alias="access_token")):
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        user_id = decoded_token.get("id")
        bookings = list(bookings_collection.find({"user": user_id}))

        populated_bookings = []

        for booking in bookings:
            place_id = booking.get("place")
            if place_id:
                place = places_collection.find_one({"_id": ObjectId(place_id)})
                if place:
                    booking["place"] = place
            populated_bookings.append(booking)
        user_bookings = json.loads(json.dumps(populated_bookings, default=str))
        return user_bookings
    except jwt.exceptions.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.delete("/api/bookings/{booking_id}", response_description="Cancel a booking", status_code=status.HTTP_200_OK)
async def cancel_booking(booking_id: str):
    print(booking_id)
    existing_booking = bookings_collection.find_one({"_id": ObjectId(booking_id)})
    if not existing_booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    try:
        bookings_collection.delete_one({"_id": ObjectId(booking_id)})
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error occurred while canceling the booking")

    return {"message": "Booking canceled successfully"}


@app.delete("/api/places/{place_id}", response_description="Delete a place", status_code=status.HTTP_200_OK)
async def delete_place(place_id: str):
    print(place_id)
    existing_place = places_collection.find({"_id": ObjectId(place_id)})
    if not existing_place:
        raise HTTPException(status_code=404, detail="Place not found")

    try:
        places_collection.delete_one({"_id": ObjectId(place_id)})
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error occurred while deleting the place")

    return {"message": "Place deleted successfully"}
