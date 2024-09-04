from fastapi import HTTPException, APIRouter

import datetime
import pytz

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

@router.post("/schedule/again/last/completed/workout", status_code=200)
async def schedule_again_last_completed_workout(db: db_dependency, current_user: str, date: datetime.datetime = datetime.datetime.now(tz=pytz.timezone('America/Santiago')).strftime('%Y-%m-%d')):
    """
    Schedule again the last completed workout for the current user. the date is optional and by default is the current date. Also, the comments are not included in the scheduled workout.
    """
    users_collection = db[current_user]
    last_workout = users_collection.find({"completed": True},{"date": 0, "completed": 0, "_id":0}).sort("date", -1).limit(1)
    last_workout = json.loads(dumps(last_workout))[0]

    scheduled_workout = {}
    scheduled_workout["date"] = date
    scheduled_workout["exercises"] = last_workout["exercises"]
    # delete "comments" from the exercises
    for exercise in scheduled_workout["exercises"]:
        # validate if the key exists
        if "comments" in exercise:
            del exercise["comments"]
    scheduled_workout["completed"] = False

    response = users_collection.insert_one(scheduled_workout)
    return {"message": "Workout scheduled successfully.",
            "workout_id": str(response.inserted_id)}

