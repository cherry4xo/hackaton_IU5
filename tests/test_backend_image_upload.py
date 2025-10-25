import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
from fastapi import FastAPI, UploadFile
from fastapi.testclient import TestClient
from io import BytesIO
import uuid

from services.backend.app.routes.orbit import router as orbit_router
from services.backend.app.models import User, Observations, Comets, Observatories
from services.backend.app.utils.minio_client import MinIOClient


@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(orbit_router)
    return app


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def mock_user():
    user = Mock(spec=User)
    user.uuid = str(uuid.uuid4())
    return user


@pytest.fixture
def mock_observation():
    obs = Mock(spec=Observations)
    obs.uuid = str(uuid.uuid4())
    return obs


@pytest.fixture
def mock_minio_client():
    with patch('services.backend.app.routes.orbit.get_minio_client') as mock:
        client = Mock(spec=MinIOClient)
        client.upload_image.return_value = "http://minio:9000/orbit-images/test_image.jpg"
        mock.return_value = client
        yield mock


@pytest.mark.asyncio
async def test_upload_image_success(client, mock_user, mock_minio_client):
    """Test successful image upload"""
    # Create a fake image
    image_data = BytesIO(b"fake image data")
    image_data.name = "test_image.jpg"
    
    with patch('services.backend.app.routes.orbit.get_current_user', return_value=mock_user):
        with patch('services.backend.app.routes.orbit.Observations.get_or_none') as mock_get_obs:
            mock_observation = Mock()
            mock_get_obs.return_value = mock_observation
            
            response = client.post(
                "/orbit/upload-image",
                files={"file": ("test_image.jpg", image_data, "image/jpeg")},
                data={"observation_uuid": str(uuid.uuid4())}
            )
    
    assert response.status_code == 200
    data = response.json()
    assert "image_reference" in data
    assert "url" in data
    assert "width" in data
    assert "height" in data
    assert "format" in data
    assert data["observation_updated"] is True


@pytest.mark.asyncio
async def test_upload_image_invalid_format(client, mock_user):
    """Test image upload with invalid format"""
    # Create fake data with wrong content type
    data = BytesIO(b"fake data")
    data.name = "test_file.txt"
    
    with patch('services.backend.app.routes.orbit.get_current_user', return_value=mock_user):
        response = client.post(
            "/orbit/upload-image",
            files={"file": ("test_file.txt", data, "text/plain")}
        )
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "supported" in data["detail"].lower()


@pytest.mark.asyncio
async def test_upload_image_corrupted_file(client, mock_user):
    """Test image upload with corrupted image data"""
    # Create fake corrupted image data
    data = BytesIO(b"corrupted image data")
    data.name = "corrupted.jpg"
    
    with patch('services.backend.app.routes.orbit.get_current_user', return_value=mock_user):
        response = client.post(
            "/orbit/upload-image",
            files={"file": ("corrupted.jpg", data, "image/jpeg")}
        )
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "invalid" in data["detail"].lower()


@pytest.mark.asyncio
async def test_upload_image_without_observation(client, mock_user, mock_minio_client):
    """Test image upload without observation UUID"""
    image_data = BytesIO(b"fake image data")
    image_data.name = "test_image.jpg"
    
    with patch('services.backend.app.routes.orbit.get_current_user', return_value=mock_user):
        response = client.post(
            "/orbit/upload-image",
            files={"file": ("test_image.jpg", image_data, "image/jpeg")}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert "image_reference" in data
    assert "url" in data
    assert data["observation_updated"] is False


@pytest.mark.asyncio
async def test_upload_image_minio_error(client, mock_user):
    """Test image upload when MinIO returns an error"""
    image_data = BytesIO(b"fake image data")
    image_data.name = "test_image.jpg"
    
    with patch('services.backend.app.routes.orbit.get_current_user', return_value=mock_user):
        with patch('services.backend.app.routes.orbit.get_minio_client') as mock_get_minio:
            mock_client = Mock(spec=MinIOClient)
            mock_client.upload_image.side_effect = Exception("MinIO error")
            mock_get_minio.return_value = mock_client
            
            response = client.post(
                "/orbit/upload-image",
                files={"file": ("test_image.jpg", image_data, "image/jpeg")}
            )
    
    assert response.status_code == 500
    data = response.json()
    assert "detail" in data
    assert "storage" in data["detail"].lower()
