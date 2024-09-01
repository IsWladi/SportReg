import pytest

from fastapi.testclient import TestClient

from app.main import app

from pydantic import BaseModel

# DB connection
from app.dependencies.db_dependencies import get_db

# import test data
from app.tests.test_routers.data_parameterization import data_params_test_register_valid_user


class User(BaseModel):
    username: str
    password: str

def delete_user_if_exist(username: str):
    """
    This function is used to delete a user if it exists
    Returns: True if user exists and was deleted, False if user does not exist
    """
    db = get_db()
    # validate if user exists
    user = db.users.find_one({"username": username})
    if user:
        db.users.delete_one({"username": username})
        return True

    return False


@pytest.mark.parametrize("username, password", data_params_test_register_valid_user)
def test_register_valid_user(username, password):
    client = TestClient(app)
    body = User(username=username, password=password).model_dump()
    delete_user_if_exist(body["username"])  # to avoid conflicts

    response = client.post("api/auth/register", json=body)
    print(response.text)  # debug
    assert response.status_code == 200
