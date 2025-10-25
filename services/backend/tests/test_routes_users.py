import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from fastapi import HTTPException
import uuid

from app.routes.users import router
from app.schemas import UserCreate, UserCreated, UserGet, UserChangePasswordIn, UserGrantPrivileges
from app.models import User
from app.services.users import create_user, change_password, grant_user, update_profile
from app.utils.contrib import get_current_user, get_current_admin


@pytest.fixture
def mock_user():
    """Create a mock user."""
    user = Mock(spec=User)
    user.uuid = uuid.uuid4()
    user.username = "testuser"
    user.email = "test@example.com"
    user.role = "booker"
    return user


@pytest.fixture
def mock_admin():
    """Create a mock admin user."""
    user = Mock(spec=User)
    user.uuid = uuid.uuid4()
    user.username = "admin"
    user.email = "admin@example.com"
    user.role = "admin"
    return user


@pytest.mark.asyncio
async def test_route_create_user_success():
    """Test successful user creation."""
    # Create test data
    user_create = UserCreate(
        username="newuser",
        email="newuser@example.com",
        password="securepassword"
    )
    
    # Mock dependencies
    with patch('app.routes.users.create_user') as mock_create_user:
        # Mock created user
        created_user = UserCreated(
            uuid=str(uuid.uuid4()),
            username="newuser",
            email="newuser@example.com"
        )
        mock_create_user.return_value = created_user
        
        # Create a test client
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        # Make request
        response = client.post(
            "/",
            json=user_create.model_dump()
        )
        
        # Assertions
        assert response.status_code == 201
        data = response.json()
        assert "uuid" in data
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"


@pytest.mark.asyncio
async def test_route_create_user_failure():
    """Test user creation failure."""
    # Create test data
    user_create = UserCreate(
        username="newuser",
        email="newuser@example.com",
        password="securepassword"
    )
    
    # Mock dependencies
    with patch('app.routes.users.create_user') as mock_create_user:
        # Mock failure
        mock_create_user.return_value = None
        
        # Create a test client
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        # Make request
        response = client.post(
            "/",
            json=user_create.model_dump()
        )
        
        # Assertions
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "User registration failed" in data["detail"]


@pytest.mark.asyncio
async def test_route_get_user_success(mock_user):
    """Test successful user retrieval."""
    # Mock dependencies
    with patch('app.routes.users.get_current_user', return_value=mock_user):
        # Create a test client
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        # Make request
        response = client.get("/me")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_route_change_password_success(mock_user):
    """Test successful password change."""
    # Create test data
    change_password_data = UserChangePasswordIn(
        old_password="oldpassword",
        new_password="newpassword"
    )
    
    # Mock dependencies
    with patch('app.routes.users.get_current_user', return_value=mock_user), \
         patch('app.routes.users.change_password') as mock_change_password:
        # Mock success
        mock_change_password.return_value = {"message": "Password changed successfully"}
        
        # Create a test client
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        # Make request
        response = client.post(
            "/me/change_password",
            json=change_password_data.model_dump()
        )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "Password changed successfully"


@pytest.mark.asyncio
async def test_route_grant_user_privileges_success(mock_admin, mock_user):
    """Test successful granting of user privileges."""
    # Create test data
    user_uuid = str(uuid.uuid4())
    grant_data = UserGrantPrivileges(role="moderator")
    
    # Mock dependencies
    with patch('app.routes.users.get_current_admin', return_value=mock_admin), \
         patch('app.routes.users.grant_user') as mock_grant_user:
        # Mock updated user
        updated_user = UserGet(
            uuid=user_uuid,
            username="testuser",
            email="test@example.com",
            role="moderator"
        )
        mock_grant_user.return_value = updated_user
        
        # Create a test client
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        # Make request
        response = client.post(
            f"/{user_uuid}/grant",
            json=grant_data.model_dump()
        )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "moderator"


@pytest.mark.asyncio
async def test_route_grant_user_privileges_user_not_found(mock_admin):
    """Test granting privileges to non-existent user."""
    # Create test data
    user_uuid = str(uuid.uuid4())
    grant_data = UserGrantPrivileges(role="moderator")
    
    # Mock dependencies
    with patch('app.routes.users.get_current_admin', return_value=mock_admin), \
         patch('app.routes.users.grant_user') as mock_grant_user:
        # Mock failure
        mock_grant_user.return_value = None
        
        # Create a test client
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        # Make request
        response = client.post(
            f"/{user_uuid}/grant",
            json=grant_data.model_dump()
        )
        
        # Assertions
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "User not found" in data["detail"]
