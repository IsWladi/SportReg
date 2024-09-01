from fastapi.testclient import TestClient

from ..main import app

client = TestClient(app)

def test_get_state_prod_or_develop():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"State": "Development"} # when running pytest, the environment variable PRODUCTION is not set to True, so the app is running in development mode
