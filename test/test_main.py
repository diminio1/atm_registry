# test_main.py
import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker
from app.main import app, get_db
from app import models

# Create a new engine instance for the tests
test_engine = create_engine(os.environ["DATABASE_URL"], connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

models.Base.metadata.create_all(bind=test_engine)


# Override get_db dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    yield TestClient(app)


def test_post_and_read_main(client):
    response = client.post(
        "/locations/",
        json={
            "geometry": {
                "type": "Point",
                "coordinates": [49.2849777, -123.1189405]
            },
            "address": "1095 W Pender St, Vancouver, BC V6E 2M6",
            "provider": "Manulife"
        },
    )
    assert response.status_code == 200
    response = client.get("/locations/")
    assert response.status_code == 200
    assert response.json() == [{
        "id": 1,
        "geometry": {
            "type": "Point",
            "coordinates": [49.2849777, -123.1189405]
        },
        "address": "1095 W Pender St, Vancouver, BC V6E 2M6",
        "provider": "Manulife"
    }]


def test_update_location(client):
    create_response = client.post(
        "/locations/",
        json={
            "geometry": {
                "type": "Point",
                "coordinates": [49.2849777, -123.1189405]
            },
            "address": "1095 W Pender St, Vancouver, BC V6E 2M6",
            "provider": "Manulife"
        },
    )
    assert create_response.status_code == 200
    created_location = create_response.json()
    created_location_id = created_location["id"]

    update_response = client.put(
        f"/locations/{created_location_id}",
        json={
            "address": "Updated Address, Vancouver, BC",
            "provider": "Updated Provider"
        },
    )
    assert update_response.status_code == 200
    updated_location = update_response.json()

    # Assertions to ensure the location was updated correctly
    assert updated_location["id"] == created_location_id
    assert updated_location["address"] == "Updated Address, Vancouver, BC"
    assert updated_location["provider"] == "Updated Provider"
