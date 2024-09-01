from pydantic import BaseModel, Field
import datetime
from typing import List
from app.settings import ModelConstraintsSettings

class Usuario(BaseModel):
    username: str
    hashed_password: str
    email: str
    fecha_registro: str


class UserRegistration(BaseModel):
    username: str = Field(..., min_length=ModelConstraintsSettings.min_length_username.value,
                          max_length=ModelConstraintsSettings.max_length_username.value,
                          pattern=ModelConstraintsSettings.username_regex.value)

    password: str = Field(..., min_length=ModelConstraintsSettings.min_length_password.value,
                          max_length=ModelConstraintsSettings.max_length_password.value,
                          pattern=ModelConstraintsSettings.password_regex.value)
    fecha_registro: datetime.datetime = datetime.datetime.now(
        tz=datetime.timezone.utc)
