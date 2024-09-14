from fastapi import HTTPException, APIRouter

# import utilities for the mongo database
from bson.json_util import dumps
import json

#import models
from app.models.work_out import Plan

# import the dependencies for validating the token
from fastapi import Depends
from app.dependencies.auth_dependencies import get_current_user
from app.dependencies.db_dependencies import get_db
from pymongo.mongo_client import MongoClient
from typing import Annotated
from app.models.basic_auth_models import User

auth_dependency = Annotated[User, Depends(get_current_user)] # for use: current_user: auth_dependency
db_dependency = Annotated[MongoClient, Depends(get_db)] # for use: db: db_dependency

router = APIRouter(prefix="/api/plans", tags=["Plans"])

@router.post("/insert/plan", status_code=200)
async def insert_plan(db: db_dependency, current_user: str, plan: Plan):
    users_collection = db[current_user] # get access to the "user" collection
    plan = plan.model_dump() # convert the plan to a dictionary
    plan["type"] = "plan" # add the type of the plan
    response = users_collection.insert_one(plan) # insert the new plan
    return {"message": "Plan inserted successfully.",
            "plan_id": str(response.inserted_id)}


@router.get("/get/last/completed/plan", status_code=200)
async def get_last_completed_plan(db: db_dependency, current_user: str):
    """
    Get the last completed plan for the current user
    """
    users_collection = db[current_user]
    plans = users_collection.find({"type": "plan"}).sort("date", -1)
    completed_plans = []
    for plan in plans:
        completed = True
        for plan_workout in plan["plan"]:
            if plan_workout["completed"] == False:
                completed = False
                break
        if completed:
            return {"last_plan": json.loads(dumps(plan))}

    return {"message": "There are no completed plans."}
