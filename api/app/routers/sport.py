from fastapi import HTTPException, APIRouter, Request
import bcrypt # for hashing passwords, see argon2-cffi for a better alternative
import os

# import utilities for the mongo database
from bson import ObjectId
from bson.json_util import dumps
import json

#import models
from app.models.users import UserRegistration
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

router = APIRouter(prefix="/api/sports", tags=["Sports"])

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

@router.get("/get/workouts", status_code=200)
async def get_workouts(db: db_dependency, current_user: str, format: str = "markdown", lang: str = "es"):
    """
    Get all the workouts for the current user in the specified format, either json or markdown, and in the specified language, either spanish or english.
    If the format is markdown, a markdown file will be created within the /code/workouts/ directory.
    """
    users_collection = db[current_user]
    workouts = users_collection.find().sort("date", -1)
    if format == "json":
        return {"workouts": json.loads(dumps(workouts))}
    elif format == "markdown" or format == "md":
        # create a markdown file with the workouts
        file_path = f"/code/workouts/workouts_{current_user}.md"
        if lang == "es":
            readme_content = f"# Entrenamientos de {current_user}\n\n"
        elif lang == "en":
            readme_content = f"# Workouts for {current_user}\n\n"
        else:
            raise HTTPException(status_code=400, detail="Invalid language. Use 'es' or 'en'")

        for workout in workouts:
            # get only the date dd/mm/yyyy
            workout['date'] = workout['date'].strftime("%d/%m/%Y")
            if workout["completed"]:
                readme_content += f"## {workout['date']} :heavy_check_mark: \n\n"
            else:
                readme_content += f"## {workout['date']} :clock1: \n\n"
            if lang == "es":
                readme_content += "| Ejercicio | Instrumentos | Series | Repeticiones | Descanso | Comentarios |\n"
                readme_content += "|-----------|-------------|--------|--------------|----------|-------------|\n"
            elif lang == "en":
                readme_content += "| Exercise | Instruments | Sets | Reps | Rest | Comments |\n"
                readme_content += "|----------|-------------|------|------|------|----------|\n"

            # add the exercises to the file
            for exercise in workout['exercises']:
                # crear dato de instrumentos a partir de la lista de diccionarios
                instruments = ""
                if exercise['instruments'] is None:
                    instruments = None
                else:
                    for instrument in exercise['instruments']:
                        name = instrument.get('name', '')
                        weight = instrument.get('weight')
                        detail = instrument.get('detail')

                        description = ""

                        if weight is not None and detail:
                            description = f"{name} ({weight} kg, {detail})"
                        elif weight is not None:
                            description = f"{name} ({weight} kg)"
                        elif detail:
                            description = f"{name} ({detail})"
                        else:
                            description = name

                        # add a comma if there are more instruments
                        if instrument != exercise['instruments'][-1]:
                            description += ", "

                        instruments += description

                readme_content += f"| {exercise['name']} | {instruments} | {exercise['sets']} | {exercise['reps']} | {exercise['rest_minutes']} | {exercise['comments']} |\n"
            readme_content += "\n"

        # Replace all the "None" values with "N/A"
        readme_content = readme_content.replace("None", "N/A")
        with open(file_path, "w") as file:
            file.write(readme_content)

        return {"message": "Markdown file created successfully.",
                "file_path": file_path}
    else:
        raise HTTPException(status_code=400, detail="Invalid format. Use 'json' or 'markdown'")
