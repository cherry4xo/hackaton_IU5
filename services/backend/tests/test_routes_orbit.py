import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from fastapi import HTTPException
from starlette import status
import uuid
from datetime import datetime
from io import BytesIO

from app.routes.orbit import router
from app.utils.queue.schemas import OrbitCalculationRequest, Observation
from app.models import CalculationTask, CalculationTaskStatus, Comets, User, Observations
from app.utils.queue.queue import send_calculation_task


@pytest.fixture
def mock_user():
    """Create a mock user."""
    user = Mock(spec=User)
    user.uuid = uuid.uuid4()
    return user


@pytest.fixture
def mock_observation():
    """Create a mock observation."""
    obs = Mock(spec=Observations)
    obs.uuid = uuid.uuid4()
    return obs


@pytest.fixture
def mock_comet():
    """Create a mock comet."""
    comet = Mock(spec=Comets)
    comet.uuid = uuid.uuid4()
    return comet


@pytest.mark.asyncio
async def test_upload_observation_image_success(mock_user):
    """Test successful image upload."""
    # Create a fake image
    image_data = BytesIO(b"fake image data")
    image_data.name = "test_image.jpg"
    
    # Mock dependencies
    with patch('app.routes.orbit.get_minio_client') as mock_get_minio_client, \
         patch('app.routes.orbit.get_current_user', return_value=mock_user), \
         patch('app.routes.orbit.Observations.get_or_none') as mock_get_obs:
        
        # Mock MinIO client
        mock_minio_client = Mock()
        mock_minio_client.upload_image.return_value = "http://minio:9000/orbit-images/test_image.jpg"
        mock_get_minio_client.return_value = mock_minio_client
        
        # Mock observation
        mock_observation = Mock()
        mock_observation.save = AsyncMock()
        mock_get_obs.return_value = mock_observation
        
        # Create a test client
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        # Make request
        response = client.post(
            "/orbit/upload-image",
            files={"file": ("test_image.jpg", image_data, "image/jpeg")},
            data={"observation_uuid": str(uuid.uuid4())}
        )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert "image_reference" in data
        assert "url" in data
        assert "width" in data
        assert "height" in data
        assert "format" in data
        assert "size" in data
        assert data["observation_updated"] is True


@pytest.mark.asyncio
async def test_upload_observation_image_invalid_format(mock_user):
    """Test image upload with invalid format."""
    # Create fake data with wrong content type
    data = BytesIO(b"fake data")
    data.name = "test_file.txt"
    
    with patch('app.routes.orbit.get_current_user', return_value=mock_user):
        # Create a test client
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        # Make request
        response = client.post(
            "/orbit/upload-image",
            files={"file": ("test_file.txt", data, "text/plain")}
        )
        
        # Assertions
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "supported" in data["detail"].lower()


@pytest.mark.asyncio
async def test_upload_observation_image_corrupted_file(mock_user):
    """Test image upload with corrupted image data."""
    # Create fake corrupted image data
    data = BytesIO(b"corrupted image data")
    data.name = "corrupted.jpg"
    
    with patch('app.routes.orbit.get_current_user', return_value=mock_user):
        # Create a test client
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        # Make request
        response = client.post(
            "/orbit/upload-image",
            files={"file": ("corrupted.jpg", data, "image/jpeg")}
        )
        
        # Assertions
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "invalid" in data["detail"].lower()


@pytest.mark.asyncio
async def test_upload_observation_image_without_observation(mock_user):
    """Test image upload without observation UUID."""
    image_data = BytesIO(b"fake image data")
    image_data.name = "test_image.jpg"
    
    with patch('app.routes.orbit.get_minio_client') as mock_get_minio_client, \
         patch('app.routes.orbit.get_current_user', return_value=mock_user):
        
        # Mock MinIO client
        mock_minio_client = Mock()
        mock_minio_client.upload_image.return_value = "http://minio:9000/orbit-images/test_image.jpg"
        mock_get_minio_client.return_value = mock_minio_client
        
        # Create a test client
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        # Make request
        response = client.post(
            "/orbit/upload-image",
            files={"file": ("test_image.jpg", image_data, "image/jpeg")}
        )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert "image_reference" in data
        assert "url" in data
        assert data["observation_updated"] is False


@pytest.mark.asyncio
async def test_upload_observation_image_minio_error(mock_user):
    """Test image upload when MinIO returns an error."""
    image_data = BytesIO(b"fake image data")
    image_data.name = "test_image.jpg"
    
    with patch('app.routes.orbit.get_current_user', return_value=mock_user), \
         patch('app.routes.orbit.get_minio_client') as mock_get_minio:
        
        # Mock MinIO client to raise an exception
        mock_minio_client = Mock()
        mock_minio_client.upload_image.side_effect = Exception("MinIO error")
        mock_get_minio.return_value = mock_minio_client
        
        # Create a test client
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        # Make request
        response = client.post(
            "/orbit/upload-image",
            files={"file": ("test_image.jpg", image_data, "image/jpeg")}
        )
        
        # Assertions
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "storage" in data["detail"].lower()


@pytest.mark.asyncio
async def test_calculate_orbit_success(mock_user, mock_comet):
    """Test successful orbit calculation."""
    # Create test data
    observations = [
        Observation(
            observation_time=datetime(2025, 1, 1, 12, 0, 0),
            ra=100.0,
            dec=10.0
        ),
        Observation(
            observation_time=datetime(2025, 1, 2, 12, 0, 0),
            ra=101.0,
            dec=10.5
        ),
        Observation(
            observation_time=datetime(2025, 1, 3, 12, 0, 0),
            ra=102.0,
            dec=11.0
        )
    ]
    
    request = OrbitCalculationRequest(
        observations=observations,
        options={}
    )
    
    # Mock dependencies
    with patch('app.routes.orbit.get_current_user', return_value=mock_user), \
         patch('app.routes.orbit.Comets.get_or_none', return_value=mock_comet), \
         patch('app.routes.orbit.CalculationTask.create') as mock_create_task, \
         patch('app.routes.orbit.send_calculation_task') as mock_send_task:
        
        # Mock task creation
        mock_task = AsyncMock()
        mock_task.uuid = str(uuid.uuid4())
        mock_task.status = CalculationTaskStatus.PROCESSING
        mock_task.created_at = datetime.now()
        mock_create_task.return_value = mock_task
        
        # Mock task sending
        mock_send_task.return_value = True
        
        # Create a test client
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        # Make request
        response = client.post(
            "/orbit/calculate",
            json=request.model_dump()
        )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert "status" in data
        assert "submitted_at" in data
        assert data["status"] == "processing"


@pytest.mark.asyncio
async def test_calculate_orbit_insufficient_observations(mock_user):
    """Test orbit calculation with insufficient observations."""
    # Create test data with only 2 observations (need at least 3)
    observations = [
        Observation(
            observation_time=datetime(2025, 1, 1, 12, 0, 0),
            ra=100.0,
            dec=10.0
        ),
        Observation(
            observation_time=datetime(2025, 1, 2, 12, 0, 0),
            ra=101.0,
            dec=10.5
        )
    ]
    
    request = OrbitCalculationRequest(
        observations=observations,
        options={}
    )
    
    with patch('app.routes.orbit.get_current_user', return_value=mock_user):
        # Create a test client
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        # Make request
        response = client.post(
            "/orbit/calculate",
            json=request.model_dump()
        )
        
        # Assertions
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "At least 3 observations" in data["detail"]


@pytest.mark.asyncio
async def test_calculate_orbit_comet_not_found(mock_user):
    """Test orbit calculation with non-existent comet UUID."""
    # Create test data
    observations = [
        Observation(
            observation_time=datetime(2025, 1, 1, 12, 0, 0),
            ra=100.0,
            dec=10.0
        ),
        Observation(
            observation_time=datetime(2025, 1, 2, 12, 0, 0),
            ra=101.0,
            dec=10.5
        ),
        Observation(
            observation_time=datetime(2025, 1, 3, 12, 0, 0),
            ra=102.0,
            dec=11.0
        )
    ]
    
    request = OrbitCalculationRequest(
        observations=observations,
        options={}
    )
    
    # Mock dependencies
    with patch('app.routes.orbit.get_current_user', return_value=mock_user), \
         patch('app.routes.orbit.Comets.get_or_none', return_value=None):
        
        # Create a test client
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        # Make request with non-existent comet UUID
        response = client.post(
            "/orbit/calculate?comet_uuid=invalid-uuid",
            json=request.model_dump()
        )
        
        # Assertions
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Comet not found" in data["detail"]


@pytest.mark.asyncio
async def test_calculate_orbit_queue_failure(mock_user, mock_comet):
    """Test orbit calculation when queue sending fails."""
    # Create test data
    observations = [
        Observation(
            observation_time=datetime(2025, 1, 1, 12, 0, 0),
            ra=100.0,
            dec=10.0
        ),
        Observation(
            observation_time=datetime(2025, 1, 2, 12, 0, 0),
            ra=101.0,
            dec=10.5
        ),
        Observation(
            observation_time=datetime(2025, 1, 3, 12, 0, 0),
            ra=102.0,
            dec=11.0
        )
    ]
    
    request = OrbitCalculationRequest(
        observations=observations,
        options={}
    )
    
    # Mock dependencies
    with patch('app.routes.orbit.get_current_user', return_value=mock_user), \
         patch('app.routes.orbit.Comets.get_or_none', return_value=mock_comet), \
         patch('app.routes.orbit.CalculationTask.create') as mock_create_task, \
         patch('app.routes.orbit.send_calculation_task') as mock_send_task:
        
        # Mock task creation
        mock_task = AsyncMock()
        mock_task.uuid = str(uuid.uuid4())
        mock_task.status = CalculationTaskStatus.PROCESSING
        mock_task.error_message = None
        mock_task.save = AsyncMock()
        mock_create_task.return_value = mock_task
        
        # Mock task sending to fail
        mock_send_task.return_value = False
        
        # Create a test client
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        # Make request
        response = client.post(
            "/orbit/calculate",
            json=request.model_dump()
        )
        
        # Assertions
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "Failed to send task to queue" in data["detail"]
        
        # Verify task status was updated
        assert mock_task.status == CalculationTaskStatus.FAILED
        assert mock_task.error_message == "Failed to send to queue"
        mock_task.save.assert_called_once()
