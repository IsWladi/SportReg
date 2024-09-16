from fastapi import HTTPException, APIRouter
from fastapi.responses import Response
from datetime import datetime, timedelta

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

router = APIRouter(prefix="/api/markdown", tags=["MarkDown"])

def transform_string_to_markdown_bytes(string_markdown: str):
    return string_markdown.encode("utf-8")

def get_normal_workout(workout, lang, current_user):
    readme_workout_content = ""

    # get only the date dd/mm/yyyy
    workout['date'] = workout['date'].strftime("%d/%m/%Y")

    if workout["completed"]:
        readme_workout_content += f"## {workout['date']} :heavy_check_mark: \n\n"
    else:
        readme_workout_content += f"## {workout['date']} :clock1: \n\n"
    if lang == "es":
        readme_workout_content += "| Ejercicio | Instrumentos | Series | Repeticiones | Descanso | Instrucción | Comentarios |\n"
        readme_workout_content += "|-----------|-------------|--------|--------------|----------|----------|-------------|\n"
    elif lang == "en":
        readme_workout_content += "| Exercise | Instruments | Sets | Reps | Rest | Instruction | Comments |\n"
        readme_workout_content += "|----------|-------------|------|------|------|----------|----------|\n"

    # add the exercises to the file
    for exercise in workout['exercises']:
        # crear dato de instrumentos a partir de la lista de diccionarios
        instruments = ""
        if "comments" not in exercise or exercise['comments'] is None:
            exercise['comments'] = "N/A"
        if "instruction" not in exercise or exercise['instruction'] is None:
            exercise['instruction'] = "N/A"
        if "instruments" not in exercise or exercise['instruments'] is None:
            instruments = "N/A"
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

        readme_workout_content += f"| {exercise['name']} | {instruments} | {exercise['sets']} | {exercise['reps']} | {exercise['rest_minutes']}m | {exercise['instruction']} | {exercise['comments']} |\n"
    return readme_workout_content

@router.get("/get/workouts",
            responses = {
                200: {
                "content": {"text/markdown": {}}
                }
            },
            response_class=Response
            )
async def get_workouts_markdown(db: db_dependency, current_user: str, lang: str = "es"):
    """
    Get all the workouts for the current user in markdown format.
    """
    users_collection = db[current_user]
    workouts = list(users_collection.find().sort("date", -1))
    if len(workouts) == 0:
        raise HTTPException(status_code=404, detail="No workouts found for this user")

    readme_content = ""

    if lang == "es":
        readme_content = f"# Entrenamientos de {current_user}\n\n"
    elif lang == "en":
        readme_content = f"# Workouts for {current_user}\n\n"
    else:
        raise HTTPException(status_code=400, detail="Invalid language. Use 'es' or 'en'")

    for workout in workouts:
        if "type" in workout:
            if workout["type"] == "plan":

                processed_workouts = []

                for plan_workout in workout["plan"]:
                    if plan_workout["day"] == 1:
                        plan_workout["date"] = workout["date"]
                    elif plan_workout["day"] > 1:
                        plan_workout["date"] = workout["date"] + timedelta(days=plan_workout["day"] - 1)

                    # delete "day" key
                    del plan_workout["day"]
                    processed_workouts.append(plan_workout)

                # order workout["plan"] by "date", major to minor
                processed_workouts.sort(key=lambda x: x["date"], reverse=True)

                for plan_workout in processed_workouts:
                    readme_content += get_normal_workout(plan_workout, lang, current_user)
                    readme_content += "\n"
        else:
            readme_content += get_normal_workout(workout, lang, current_user)
            readme_content += "\n"

    # Replace all the "None" values with "N/A"
    readme_content = readme_content.replace("None", "N/A").replace("N/Am", "N/A")

    return Response(content=transform_string_to_markdown_bytes(readme_content), media_type="text/markdown")
