import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
import uuid

from services.backend.app.utils.queue.queue import send_calculation_task
from services.backend.app.utils.queue.schemas import OrbitCalculationRequest, Observation


@pytest.fixture
def mock_redis_client():
    """Create a mock Redis client."""
    with patch('app.utils.queue.queue.redis_client') as mock_redis:
        yield mock_redis


@pytest.mark.asyncio
async def test_send_calculation_task_success(mock_redis_client):
    """Test successful sending of calculation task."""
    # Create test data
    task_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    
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
        options={"location_code": "500"}
    )
    
    # Configure mock
    mock_redis_client.xadd = AsyncMock(return_value=True)
    
    # Call the function
    result = await send_calculation_task(task_id, user_id, request)
    
    # Assertions
    assert result is True
    mock_redis_client.xadd.assert_called_once()
    
    # Check the call arguments
    call_args = mock_redis_client.xadd.call_args
    assert call_args[0][0] == "input_queue"
    
    message = call_args[0][1]
    assert message["task_id"] == task_id
    assert message["user_id"] == user_id
    assert "timestamp" in message
    assert len(message["observations"]) == 3
    assert message["options"] == {"location_code": "500"}


@pytest.mark.asyncio
async def test_send_calculation_task_empty_options(mock_redis_client):
    """Test sending calculation task with empty options."""
    # Create test data
    task_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    
    observations = [
        Observation(
            observation_time=datetime(2025, 1, 1, 12, 0, 0),
            ra=100.0,
            dec=10.0
        )
    ]
    
    request = OrbitCalculationRequest(
        observations=observations,
        options=None
    )
    
    # Configure mock
    mock_redis_client.xadd = AsyncMock(return_value=True)
    
    # Call the function
    result = await send_calculation_task(task_id, user_id, request)
    
    # Assertions
    assert result is True
    mock_redis_client.xadd.assert_called_once()
    
    # Check the call arguments
    call_args = mock_redis_client.xadd.call_args
    message = call_args[0][1]
    assert message["options"] == {}


@pytest.mark.asyncio
async def test_send_calculation_task_redis_error(mock_redis_client, caplog):
    """Test sending calculation task when Redis returns an error."""
    # Create test data
    task_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    
    observations = [
        Observation(
            observation_time=datetime(2025, 1, 1, 12, 0, 0),
            ra=100.0,
            dec=10.0
        )
    ]
    
    request = OrbitCalculationRequest(
        observations=observations,
        options={}
    )
    
    # Configure mock to raise an exception
    mock_redis_client.xadd.side_effect = Exception("Redis connection error")
    
    with caplog.at_level("ERROR"):
        # Call the function
        result = await send_calculation_task(task_id, user_id, request)
        
        # Assertions
        assert result is False
        assert "Redis sending error" in caplog.text
