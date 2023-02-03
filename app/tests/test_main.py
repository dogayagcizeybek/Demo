from fastapi.testclient import TestClient
import json

from app.main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World2!"}
    response2 = client.get("/people")
    assert response2.status_code == 200
    item_dict = json.loads(response2.json())
    assert len(item_dict) > 0