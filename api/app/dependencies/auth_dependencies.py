from typing import Annotated

from fastapi import HTTPException, Request, Depends
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from app.routers.auth import  oauth2_scheme

#import models
from app.models.basic_auth_models import TokenData, User

#import constants
from app.settings import Oauth2Settings, DatabaseSettings
ALGORITHM = Oauth2Settings.ALGORITHM.value
SECRET_KEY = Oauth2Settings.SECRET_KEY.value

#database dependency
from app.dependencies.db_dependencies import get_db
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os

db_dependency = Annotated[MongoClient, Depends(get_db)] # for use: db: db_dependency

# Verify if the username exists in the database
def get_user(username: str, db: MongoClient ):
    users_collection = db["users"] # get access to the "users" collection

    # check if the username exists in the database
    user = users_collection.find_one({"username": username})
    if user is None:
        return False # the username does not exist
    return User(username=user["username"])

# Verify if the user is authenticated with the jwt token and return the username if it is authenticated
# It is a dependency for authenticated routes
# Why is it async?: I don't know, but it is in the FastAPI tutorial
async def get_current_user(db: db_dependency,token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username, db=db)
    if user is None:
        raise credentials_exception
    return user

