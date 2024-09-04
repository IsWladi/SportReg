from fastapi import HTTPException, APIRouter

# import utilities for the mongo database
from bson.json_util import dumps
import json

#import models
from app.models.work_out import Workout

# import the dependencies for validating the token
from fastapi import Depends
from app.dependencies.auth_dependencies import get_current_user
from app.dependencies.db_dependencies import get_db
from pymongo.mongo_client import MongoClient
from typing import Annotated
from app.models.basic_auth_models import User

auth_dependency = Annotated[User, Depends(get_current_user)] # for use: current_user: auth_dependency
db_dependency = Annotated[MongoClient, Depends(get_db)] # for use: db: db_dependency

router = APIRouter(prefix="/api/general", tags=["General"])

@router.post("/insert/workout", status_code=200)
async def insert_workout(db: db_dependency, current_user: str, work_out: Workout):
    users_collection = db[current_user] # get access to the "user" collection
    response = users_collection.insert_one(work_out.model_dump()) # insert the new workout
    return {"message": "Workout inserted successfully.",
            "workout_id": str(response.inserted_id)}

@router.get("/get/last/completed/workout", status_code=200)
async def get_last_completed_workout(db: db_dependency, current_user: str):
    """
    Get the last completed workout for the current user
    """
    users_collection = db[current_user]
    last_workout = users_collection.find({"completed": True}).sort("date", -1).limit(1)
    return {"last_workout": json.loads(dumps(last_workout))}

@router.get("/get/pending/workouts", status_code=200)
async def get_pending_workouts(db: db_dependency, current_user: str):
    """
    Get all the pending workouts for the current user
    """
    users_collection = db[current_user]
    pending_workouts = users_collection.find({"completed": False}, {"_id": 0}).sort("date", -1)
    return {"pending_workouts": json.loads(dumps(pending_workouts))}
