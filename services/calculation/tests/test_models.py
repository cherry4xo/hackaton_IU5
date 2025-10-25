import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime, date
import uuid

from app.models import (
    CalculationTaskStatus,
    BaseModel,
    TimestampMixin,
    User,
    Observatories,
    Comets,
    Observations,
    Orbits,
    Close_approaches,
    CalculationTask
)
from app.enums import UserRole
from app.schemas import UserCreate


def test_calculation_task_status_enum():
    """Test CalculationTaskStatus enum values."""
    assert CalculationTaskStatus.PROCESSING == "processing"
    assert CalculationTaskStatus.COMPLETED == "completed"
    assert CalculationTaskStatus.FAILED == "failed"


@pytest.mark.asyncio
async def test_base_model_to_dict():
    """Test BaseModel to_dict method."""
    # Create a mock model instance
    class TestModel(BaseModel):
        id = 1
        name = "test"
        
        class Meta:
            db_fields = ["id", "name"]
            backward_fk_fields = []
    
    model = TestModel()
    result = await model.to_dict()
    
    # Assertions
    assert isinstance(result, dict)
    assert result["id"] == 1
    assert result["name"] == "test"


def test_timestamp_mixin():
    """Test TimestampMixin fields."""
    # Create a class that inherits from TimestampMixin
    class TestModel(TimestampMixin):
        pass
    
    # Check that the fields exist
    assert hasattr(TestModel, 'created_at')
    assert hasattr(TestModel, 'updated_at')


@pytest.mark.asyncio
async def test_user_create():
    """Test User.create method."""
    # Create a UserCreate schema
    user_create = UserCreate(
        username="testuser",
        email="test@example.com",
        password="testpassword"
    )
    
    # Mock password hashing
    with patch('app.models.password.get_password_hash') as mock_get_password_hash:
        mock_get_password_hash.return_value = "hashed_password"
        
        # Mock the model constructor
        with patch('app.models.User') as mock_user_class:
            mock_user_instance = Mock()
            mock_user_class.return_value = mock_user_instance
            
            # Call the method
            result = await User.create(user_create)
            
            # Assertions
            mock_get_password_hash.assert_called_once_with(password="testpassword")
            # We can't easily assert the model creation without actually creating it
            # but we can check that the method returns something
            assert result is not None


@pytest.mark.asyncio
async def test_user_get_by_uuid():
    """Test User.get_by_uuid method."""
    # Create a test UUID
    test_uuid = uuid.uuid4()
    
    # Mock the get_or_none method
    with patch('app.models.User.get_or_none') as mock_get_or_none:
        mock_user = Mock()
        mock_get_or_none.return_value = mock_user
        
        # Call the method
        result = await User.get_by_uuid(test_uuid)
        
        # Assertions
        assert result == mock_user
        mock_get_or_none.assert_called_once_with(uuid=test_uuid)


@pytest.mark.asyncio
async def test_user_get_by_uuid_not_found():
    """Test User.get_by_uuid method when user is not found."""
    # Create a test UUID
    test_uuid = uuid.uuid4()
    
    # Mock the get_or_none method to return None
    with patch('app.models.User.get_or_none') as mock_get_or_none:
        mock_get_or_none.return_value = None
        
        # Call the method
        result = await User.get_by_uuid(test_uuid)
        
        # Assertions
        assert result is None
        mock_get_or_none.assert_called_once_with(uuid=test_uuid)


@pytest.mark.asyncio
async def test_user_get_by_username():
    """Test User.get_by_username method."""
    test_username = "testuser"
    
    # Mock the get_or_none method
    with patch('app.models.User.get_or_none') as mock_get_or_none:
        mock_user = Mock()
        mock_get_or_none.return_value = mock_user
        
        # Call the method
        result = await User.get_by_username(test_username)
        
        # Assertions
        assert result == mock_user
        mock_get_or_none.assert_called_once_with(username=test_username)


@pytest.mark.asyncio
async def test_user_get_by_username_not_found():
    """Test User.get_by_username method when user is not found."""
    test_username = "testuser"
    
    # Mock the get_or_none method to return None
    with patch('app.models.User.get_or_none') as mock_get_or_none:
        mock_get_or_none.return_value = None
        
        # Call the method
        result = await User.get_by_username(test_username)
        
        # Assertions
        assert result is None
        mock_get_or_none.assert_called_once_with(username=test_username)


@pytest.mark.asyncio
async def test_user_get_by_email():
    """Test User.get_by_email method."""
    test_email = "test@example.com"
    
    # Mock the get_or_none method
    with patch('app.models.User.get_or_none') as mock_get_or_none:
        mock_user = Mock()
        mock_get_or_none.return_value = mock_user
        
        # Call the method
        result = await User.get_by_email(test_email)
        
        # Assertions
        assert result == mock_user
        mock_get_or_none.assert_called_once_with(email=test_email)


@pytest.mark.asyncio
async def test_user_get_by_email_not_found():
    """Test User.get_by_email method when user is not found."""
    test_email = "test@example.com"
    
    # Mock the get_or_none method to return None
    with patch('app.models.User.get_or_none') as mock_get_or_none:
        mock_get_or_none.return_value = None
        
        # Call the method
        result = await User.get_by_email(test_email)
        
        # Assertions
        assert result is None
        mock_get_or_none.assert_called_once_with(email=test_email)


def test_user_str():
    """Test User.__str__ method."""
    # Create a mock user
    user = Mock()
    user.username = "testuser"
    user.role = Mock()
    user.role.value = "moderator"
    
    # Call the method
    result = User.__str__(user)
    
    # Assertions
    assert result == "testuser (moderator)"


def test_observatories_model():
    """Test Observatories model fields."""
    # Check that the model has the expected fields
    assert hasattr(Observatories, 'uuid')
    assert hasattr(Observatories, 'code')
    assert hasattr(Observatories, 'name')
    assert hasattr(Observatories, 'latitude')
    assert hasattr(Observatories, 'longitude')
    assert hasattr(Observatories, 'elevation_m')
    
    # Check meta table name
    assert Observatories.Meta.table == "Observatories"


def test_comets_model():
    """Test Comets model fields."""
    # Check that the model has the expected fields
    assert hasattr(Comets, 'uuid')
    assert hasattr(Comets, 'designation')
    assert hasattr(Comets, 'name')
    assert hasattr(Comets, 'discovered_by')
    assert hasattr(Comets, 'discovery_date')
    
    # Check meta table name
    assert Comets.Meta.table == "Comets"


def test_observations_model():
    """Test Observations model fields."""
    # Check that the model has the expected fields
    assert hasattr(Observations, 'uuid')
    assert hasattr(Observations, 'comet_id')
    assert hasattr(Observations, 'observatory_id')
    assert hasattr(Observations, 'observer_id')
    assert hasattr(Observations, 'observation_time')
    assert hasattr(Observations, 'ra_deg')
    assert hasattr(Observations, 'dec_deg')
    assert hasattr(Observations, 'altitude_deg')
    assert hasattr(Observations, 'azimuth_deg')
    assert hasattr(Observations, 'processed')
    
    # Check meta table name
    assert Observations.Meta.table == "Observations"


def test_orbits_model():
    """Test Orbits model fields."""
    # Check that the model has the expected fields
    assert hasattr(Orbits, 'uuid')
    assert hasattr(Orbits, 'comet_id')
    assert hasattr(Orbits, 'semi_major_axis')
    assert hasattr(Orbits, 'eccentricity')
    assert hasattr(Orbits, 'inclination')
    assert hasattr(Orbits, 'longitude_ascending_node')
    assert hasattr(Orbits, 'argument_periapsis')
    assert hasattr(Orbits, 'periapsis_time')
    assert hasattr(Orbits, 'epoch')
    assert hasattr(Orbits, 'method')
    assert hasattr(Orbits, 'is_hyperbolic')
    
    # Check meta table name
    assert Orbits.Meta.table == "Orbits"


def test_close_approaches_model():
    """Test Close_approaches model fields."""
    # Check that the model has the expected fields
    assert hasattr(Close_approaches, 'uuid')
    assert hasattr(Close_approaches, 'comet_id')
    assert hasattr(Close_approaches, 'approach_time')
    assert hasattr(Close_approaches, 'distance_au')
    assert hasattr(Close_approaches, 'distance_km')
    assert hasattr(Close_approaches, 'orbit_id')
    
    # Check meta table name
    assert Close_approaches.Meta.table == "Close_approaches"


def test_calculation_task_model():
    """Test CalculationTask model fields."""
    # Check that the model has the expected fields
    assert hasattr(CalculationTask, 'uuid')
    assert hasattr(CalculationTask, 'user')
    assert hasattr(CalculationTask, 'comet')
    assert hasattr(CalculationTask, 'status')
    assert hasattr(CalculationTask, 'observation_start_time')
    assert hasattr(CalculationTask, 'observation_end_time')
    assert hasattr(CalculationTask, 'location_code')
    assert hasattr(CalculationTask, 'error_message')
    assert hasattr(CalculationTask, 'orbit')
    assert hasattr(CalculationTask, 'close_approach')
    assert hasattr(CalculationTask, 'raw_observations')
    
    # Check meta table name
    assert CalculationTask.Meta.table == "calculation_tasks"
    
    # Check default status
    assert CalculationTask.status.default == CalculationTaskStatus.PROCESSING
