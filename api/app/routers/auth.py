from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import HTTPException, APIRouter, Request, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
import bcrypt # for hashing passwords, see argon2-cffi for a better alternative

#import models
from app.models.users import UserRegistration
from app.models.basic_auth_models import Token, TokenData, User

#Constants for JWT
from app.dependencies.db_dependencies import get_db
from app.settings import Oauth2Settings
ALGORITHM = Oauth2Settings.ALGORITHM.value
SECRET_KEY = Oauth2Settings.SECRET_KEY.value
ACCESS_TOKEN_EXPIRE_MINUTES = Oauth2Settings.ACCESS_TOKEN_EXPIRE_MINUTES.value

#database dependency
from pymongo.mongo_client import MongoClient
db_dependency = Annotated[MongoClient, Depends(get_db)] # for use: db: db_dependency

router = APIRouter(prefix="/api/auth", tags=["Basic Auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token") # if there is a prefix in the router, it should be added here

# Verify if the username and password are correct and return the username if it is correct
def authenticate_user(username: str, password: str, db: MongoClient):
    #get user from database
    finded_user = None
    users_collection = db["users"]

    # validate user if exists
    user = users_collection.find_one({ "username": username })
    if user is None:
        return False # user not found
    finded_user = { "username":user["username"], "hashed_password":user["hashed_password"] }

    # check password
    if bcrypt.checkpw(password.encode('utf-8'), finded_user["hashed_password"].encode('utf-8')):
        return username
    else: # password incorrect
        return False

# Create a JWT for being returned to the user in the login route
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/token")
async def login(db: db_dependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
	user = authenticate_user(form_data.username, form_data.password, db)
	if not user:
		raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
	access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
	access_token = create_access_token(
        data={"sub": user}, expires_delta=access_token_expires
    )
	return Token(access_token=access_token, token_type="bearer")

# to do: validate that the user does not exist before creating it
@router.post("/register")
async def register(db: db_dependency, user: UserRegistration):
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())

    users_collection = db["users"]

    # validate user if exists
    finded_user = users_collection.find_one({ "username": user.username })
    if finded_user:
        raise HTTPException(status_code=409, detail="User already exists")
    users_collection.insert_one(
            {"username": user.username,
             "hashed_password": hashed_password.decode('utf-8'),
             "fecha_registro": user.fecha_registro
             })

    usuario_check = users_collection.find_one({"username": user.username})
    if usuario_check:
        return str(usuario_check["_id"])
    else:
        raise HTTPException(status_code=500, detail="Error creating user")
