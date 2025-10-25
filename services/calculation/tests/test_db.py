import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import logging
from fastapi import FastAPI

from app.db import (
    get_tortoise_config,
    register_db,
    upgrade_db,
    create_default_moderator_user,
    init,
    TORTOISE_ORM,
    AERICH_COMMAND,
    MODELS_MIGRATION_PATH
)
from app.enums import UserRole
from app.models import User
from app.schemas import UserCreate


def test_get_tortoise_config():
    """Test get_tortoise_config function."""
    with patch('app.db.settings') as mock_settings:
        mock_settings.DB_CONNECTIONS = {"default": "sqlite://:memory:"}
        
        config = get_tortoise_config()
        
        # Assertions
        assert isinstance(config, dict)
        assert "connections" in config
        assert "apps" in config
        assert config["connections"] == {"default": "sqlite://:memory:"}
        assert "models" in config["apps"]
        assert config["apps"]["models"]["models"] == ["app.models", "aerich.models"]
        assert config["apps"]["models"]["default_connection"] == "default"


def test_register_db():
    """Test register_db function."""
    app = FastAPI()
    
    with patch('app.db.settings') as mock_settings:
        mock_settings.DB_URL = "sqlite://:memory:"
        
        with patch('app.db.register_tortoise') as mock_register_tortoise:
            register_db(app)
            
            # Assertions
            mock_register_tortoise.assert_called_once()
            call_args = mock_register_tortoise.call_args
            assert call_args[0][0] == app
            assert call_args[1]['config'] == TORTOISE_ORM
            assert call_args[1]['generate_schemas'] is True
            assert call_args[1]['add_exception_handlers'] is True


@pytest.mark.asyncio
async def test_upgrade_db_success(caplog):
    """Test successful database upgrade."""
    app = FastAPI()
    
    # Mock settings
    with patch('app.db.settings') as mock_settings:
        mock_settings.DB_URL = "sqlite://:memory:"
        
        # Mock AERICH_COMMAND
        with patch('app.db.AERICH_COMMAND') as mock_aerich_command:
            mock_aerich_command.location = "/tmp/migrations"
            mock_aerich_command.app = "models"
            
            with patch('app.db.MODELS_MIGRATION_PATH', '/tmp/migrations/models'), \
                 patch('app.db.os') as mock_os, \
                 caplog.at_level(logging.INFO):
                
                # Configure mocks
                mock_os.makedirs = Mock()
                mock_os.path.isdir.return_value = True
                
                mock_aerich_command.init_db = AsyncMock()
                mock_aerich_command.init = AsyncMock()
                mock_aerich_command.upgrade = AsyncMock()
                
                # Run the function
                await upgrade_db(app)
                
                # Assertions
                mock_os.makedirs.assert_called_once_with('/tmp/migrations', exist_ok=True)
                mock_aerich_command.init_db.assert_called_once_with(safe=True)
                mock_aerich_command.init.assert_called_once()
                mock_aerich_command.upgrade.assert_called_once_with(run_in_transaction=True)


@pytest.mark.asyncio
async def test_upgrade_db_directory_creation_failure(caplog):
    """Test database upgrade when directory creation fails."""
    app = FastAPI()
    
    # Mock settings
    with patch('app.db.settings') as mock_settings:
        mock_settings.DB_URL = "sqlite://:memory:"
        
        # Mock AERICH_COMMAND
        with patch('app.db.AERICH_COMMAND') as mock_aerich_command:
            mock_aerich_command.location = "/tmp/migrations"
            mock_aerich_command.app = "models"
            
            with patch('app.db.MODELS_MIGRATION_PATH', '/tmp/migrations/models'), \
                 patch('app.db.os') as mock_os, \
                 caplog.at_level(logging.ERROR):
                
                # Configure mocks to raise an exception
                mock_os.makedirs.side_effect = OSError("Permission denied")
                
                # Run the function and expect it to raise an exception
                with pytest.raises(OSError):
                    await upgrade_db(app)
                
                # Assertions
                mock_os.makedirs.assert_called_once_with('/tmp/migrations', exist_ok=True)


@pytest.mark.asyncio
async def test_upgrade_db_migration_directory_not_found(caplog):
    """Test database upgrade when migration directory is not found."""
    app = FastAPI()
    
    # Mock settings
    with patch('app.db.settings') as mock_settings:
        mock_settings.DB_URL = "sqlite://:memory:"
        
        # Mock AERICH_COMMAND
        with patch('app.db.AERICH_COMMAND') as mock_aerich_command:
            mock_aerich_command.location = "/tmp/migrations"
            mock_aerich_command.app = "models"
            
            with patch('app.db.MODELS_MIGRATION_PATH', '/tmp/migrations/models'), \
                 patch('app.db.os') as mock_os, \
                 caplog.at_level(logging.ERROR):
                
                # Configure mocks
                mock_os.makedirs = Mock()
                mock_os.path.isdir.return_value = False  # Directory not found
                
                mock_aerich_command.init_db = AsyncMock()
                mock_aerich_command.init = AsyncMock()
                
                # Run the function and expect it to raise an exception
                with pytest.raises(FileNotFoundError):
                    await upgrade_db(app)
                
                # Assertions
                mock_os.makedirs.assert_called_once_with('/tmp/migrations', exist_ok=True)
                mock_aerich_command.init_db.assert_called_once_with(safe=True)
                mock_aerich_command.init.assert_called_once()


@pytest.mark.asyncio
async def test_create_default_moderator_user_success_existing_user():
    """Test create_default_moderator_user when user already exists."""
    # Mock settings
    with patch('app.db.settings') as mock_settings:
        mock_settings.DEFAULT_MODERATOR_PASSWORD = "test_password"
        mock_settings.DEFAULT_MODERATOR_USERNAME = "test_moderator"
        mock_settings.DEFAULT_MODERATOR_EMAIL = "moderator@test.com"
        
        # Mock User model
        with patch('app.db.User') as mock_user_class:
            mock_existing_user = AsyncMock()
            mock_existing_user.role = UserRole.MODERATOR
            mock_user_class.get_by_username = AsyncMock(return_value=mock_existing_user)
            
            # Run the function
            result = await create_default_moderator_user()
            
            # Assertions
            assert result == mock_existing_user
            mock_user_class.get_by_username.assert_called_once_with("test_moderator")


@pytest.mark.asyncio
async def test_create_default_moderator_user_success_existing_user_wrong_role():
    """Test create_default_moderator_user when user exists but has wrong role."""
    # Mock settings
    with patch('app.db.settings') as mock_settings:
        mock_settings.DEFAULT_MODERATOR_PASSWORD = "test_password"
        mock_settings.DEFAULT_MODERATOR_USERNAME = "test_moderator"
        mock_settings.DEFAULT_MODERATOR_EMAIL = "moderator@test.com"
        
        # Mock User model
        with patch('app.db.User') as mock_user_class:
            mock_existing_user = AsyncMock()
            mock_existing_user.role = UserRole.BOOKER  # Wrong role
            mock_existing_user.save = AsyncMock()
            mock_user_class.get_by_username = AsyncMock(return_value=mock_existing_user)
            
            # Run the function
            result = await create_default_moderator_user()
            
            # Assertions
            assert result == mock_existing_user
            mock_user_class.get_by_username.assert_called_once_with("test_moderator")
            assert mock_existing_user.role == UserRole.MODERATOR
            mock_existing_user.save.assert_called_once_with(update_fields=['role', 'updated_at'])


@pytest.mark.asyncio
async def test_create_default_moderator_user_success_new_user():
    """Test create_default_moderator_user when creating a new user."""
    # Mock settings
    with patch('app.db.settings') as mock_settings:
        mock_settings.DEFAULT_MODERATOR_PASSWORD = "test_password"
        mock_settings.DEFAULT_MODERATOR_USERNAME = "test_moderator"
        mock_settings.DEFAULT_MODERATOR_EMAIL = "moderator@test.com"
        
        # Mock User model
        with patch('app.db.User') as mock_user_class:
            mock_user_class.get_by_username = AsyncMock(return_value=None)
            mock_new_user = AsyncMock()
            mock_new_user.save = AsyncMock()
            mock_user_class.create = AsyncMock(return_value=mock_new_user)
            
            # Run the function
            result = await create_default_moderator_user()
            
            # Assertions
            assert result == mock_new_user
            mock_user_class.get_by_username.assert_called_once_with("test_moderator")
            mock_user_class.create.assert_called_once()
            assert mock_new_user.role == UserRole.MODERATOR
            mock_new_user.save.assert_called_once()


@pytest.mark.asyncio
async def test_create_default_moderator_user_no_password(caplog):
    """Test create_default_moderator_user when password is not set."""
    # Mock settings
    with patch('app.db.settings') as mock_settings:
        mock_settings.DEFAULT_MODERATOR_PASSWORD = ""  # Empty password
        mock_settings.DEFAULT_MODERATOR_USERNAME = "test_moderator"
        mock_settings.DEFAULT_MODERATOR_EMAIL = "moderator@test.com"
        
        with caplog.at_level(logging.WARNING):
            # Run the function
            result = await create_default_moderator_user()
            
            # Assertions
            assert result is None
            assert "DEFAULT_MODERATOR_PASSWORD environment variable not set" in caplog.text


@pytest.mark.asyncio
async def test_create_default_moderator_user_creation_failure(caplog):
    """Test create_default_moderator_user when user creation fails."""
    # Mock settings
    with patch('app.db.settings') as mock_settings:
        mock_settings.DEFAULT_MODERATOR_PASSWORD = "test_password"
        mock_settings.DEFAULT_MODERATOR_USERNAME = "test_moderator"
        mock_settings.DEFAULT_MODERATOR_EMAIL = "moderator@test.com"
        
        # Mock User model to raise an exception
        with patch('app.db.User') as mock_user_class:
            mock_user_class.get_by_username = AsyncMock(side_effect=Exception("Database error"))
            
            with caplog.at_level(logging.ERROR):
                # Run the function and expect it to raise an exception
                with pytest.raises(Exception):
                    await create_default_moderator_user()
                
                # Assertions
                assert "Failed to create default moderator user" in caplog.text


@pytest.mark.asyncio
async def test_init_success():
    """Test successful initialization."""
    app = FastAPI()
    
    with patch('app.db.upgrade_db') as mock_upgrade_db, \
         patch('app.db.register_db') as mock_register_db, \
         patch('app.db.create_default_moderator_user') as mock_create_default_moderator_user, \
         patch('app.db.logger') as mock_logger:
        
        # Configure mocks
        mock_upgrade_db = AsyncMock()
        mock_create_default_moderator_user = AsyncMock()
        
        # Run the function
        await init(app)
        
        # Assertions
        mock_upgrade_db.assert_called_once_with(app)
        mock_register_db.assert_called_once_with(app)
        mock_create_default_moderator_user.assert_called_once()
        mock_logger.debug.assert_called_once_with("Connected to db")
