from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app, get_db
from app.models import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}


def test_create_location():
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
    data = response.json()
    assert data["address"] == "1095 W Pender St, Vancouver, BC V6E 2M6"
    assert data["provider"] == "Manulife"
    assert "id" in data


def test_update_location():
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
