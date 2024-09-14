from pydantic import BaseModel, validator
from typing import Union, Optional
import datetime
import pytz

class Instrument(BaseModel):
    name: str
    weight: Optional[float] = None
    detail: Optional[str] = None

class Exercise(BaseModel):
    name: str
    sets: int
    # repetitions can be an int or a string, int from 0 or higher, string with number followed by "m" or "s"
    reps: Union[int, str]
    instruments: Optional[list[Instrument]] = None
    rest_minutes: str
    comments: Optional[str] = None

    @validator('reps')
    def validate_repetitions(cls, v):
        if isinstance(v, int):
            if v < 0:
                raise ValueError('The number of reps must be 0 or greater.')
        elif isinstance(v, str):
            if not v[:-1].isdigit() and v[-1] in ['m', 's']:
                raise ValueError('Reps must be a number followed by "m" or "s".')
        else:
            raise ValueError('Reps must be an integer or a valid string.')
        return v

class Workout(BaseModel):
    date: datetime.datetime = datetime.datetime.now(
        tz=pytz.timezone('America/Santiago')).strftime('%Y-%m-%d')
    exercises: list[Exercise]
    completed: Optional[bool] = False

class WorkoutPlan(BaseModel):
    day: int = 1 # 1 represents the first day of the plan (initial_date), 2 the second day, and so on
    exercises: list[Exercise]
    completed: Optional[bool] = False

class Plan(BaseModel):
    date: datetime.datetime = datetime.datetime.now(
        tz=pytz.timezone('America/Santiago')).strftime('%Y-%m-%d')
    plan: list[WorkoutPlan]
    general_comments: Optional[str] = None

