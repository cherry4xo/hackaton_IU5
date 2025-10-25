import pytest
from unittest.mock import Mock, AsyncMock
from fastapi import WebSocket

from app.connections import ConnectionManager


@pytest.fixture
def manager():
    """Create a ConnectionManager instance."""
    return ConnectionManager()


@pytest.fixture
def mock_websocket():
    """Create a mock WebSocket."""
    websocket = Mock(spec=WebSocket)
    websocket.accept = AsyncMock()
    websocket.send_text = AsyncMock()
    return websocket


@pytest.mark.asyncio
async def test_connect_new_user(manager, mock_websocket):
    """Test connecting a new user."""
    user_id = "test_user_1"
    
    # Connect the user
    await manager.connect(mock_websocket, user_id)
    
    # Assertions
    mock_websocket.accept.assert_called_once()
    assert user_id in manager.active_connections
    assert mock_websocket in manager.active_connections[user_id]


@pytest.mark.asyncio
async def test_connect_existing_user(manager, mock_websocket):
    """Test connecting an existing user with another WebSocket."""
    user_id = "test_user_1"
    
    # Create first websocket
    websocket1 = Mock(spec=WebSocket)
    websocket1.accept = AsyncMock()
    
    # Connect first websocket
    await manager.connect(websocket1, user_id)
    
    # Connect second websocket
    await manager.connect(mock_websocket, user_id)
    
    # Assertions
    assert user_id in manager.active_connections
    assert len(manager.active_connections[user_id]) == 2
    assert websocket1 in manager.active_connections[user_id]
    assert mock_websocket in manager.active_connections[user_id]


def test_disconnect_single_connection(manager, mock_websocket):
    """Test disconnecting a user with a single connection."""
    user_id = "test_user_1"
    
    # Manually add the connection
    manager.active_connections[user_id] = {mock_websocket}
    
    # Disconnect the user
    manager.disconnect(mock_websocket, user_id)
    
    # Assertions
    assert user_id not in manager.active_connections


def test_disconnect_multiple_connections(manager, mock_websocket):
    """Test disconnecting a user with multiple connections."""
    user_id = "test_user_1"
    
    # Create another websocket
    websocket2 = Mock(spec=WebSocket)
    
    # Manually add the connections
    manager.active_connections[user_id] = {mock_websocket, websocket2}
    
    # Disconnect one websocket
    manager.disconnect(mock_websocket, user_id)
    
    # Assertions
    assert user_id in manager.active_connections
    assert len(manager.active_connections[user_id]) == 1
    assert websocket2 in manager.active_connections[user_id]
    assert mock_websocket not in manager.active_connections[user_id]


def test_disconnect_nonexistent_user(manager, mock_websocket):
    """Test disconnecting a user that doesn't exist."""
    user_id = "nonexistent_user"
    
    # This should not raise an exception
    manager.disconnect(mock_websocket, user_id)
    
    # Assertions
    assert user_id not in manager.active_connections


def test_disconnect_nonexistent_connection(manager, mock_websocket):
    """Test disconnecting a connection that doesn't exist for a user."""
    user_id = "test_user_1"
    websocket2 = Mock(spec=WebSocket)
    
    # Manually add one connection
    manager.active_connections[user_id] = {mock_websocket}
    
    # Try to disconnect a different websocket
    manager.disconnect(websocket2, user_id)
    
    # Assertions
    assert user_id in manager.active_connections
    assert len(manager.active_connections[user_id]) == 1
    assert mock_websocket in manager.active_connections[user_id]


@pytest.mark.asyncio
async def test_send_personal_message_success(manager, mock_websocket):
    """Test sending a personal message successfully."""
    user_id = "test_user_1"
    message = "Test message"
    
    # Manually add the connection
    manager.active_connections[user_id] = {mock_websocket}
    
    # Send the message
    await manager.send_personal_message(message, user_id)
    
    # Assertions
    mock_websocket.send_text.assert_called_once_with(message)


@pytest.mark.asyncio
async def test_send_personal_message_multiple_connections(manager):
    """Test sending a personal message to a user with multiple connections."""
    user_id = "test_user_1"
    message = "Test message"
    
    # Create websockets
    websocket1 = Mock(spec=WebSocket)
    websocket1.send_text = AsyncMock()
    websocket2 = Mock(spec=WebSocket)
    websocket2.send_text = AsyncMock()
    
    # Manually add the connections
    manager.active_connections[user_id] = {websocket1, websocket2}
    
    # Send the message
    await manager.send_personal_message(message, user_id)
    
    # Assertions
    websocket1.send_text.assert_called_once_with(message)
    websocket2.send_text.assert_called_once_with(message)


@pytest.mark.asyncio
async def test_send_personal_message_user_not_found(manager, mock_websocket):
    """Test sending a personal message to a user that doesn't exist."""
    user_id = "nonexistent_user"
    message = "Test message"
    
    # This should not raise an exception
    await manager.send_personal_message(message, user_id)
    
    # Assertions
    mock_websocket.send_text.assert_not_called()


@pytest.mark.asyncio
async def test_send_personal_message_connection_error(manager, mock_websocket):
    """Test sending a personal message when a connection has an error."""
    user_id = "test_user_1"
    message = "Test message"
    
    # Configure mock to raise an exception
    mock_websocket.send_text.side_effect = Exception("Connection error")
    
    # Manually add the connection
    manager.active_connections[user_id] = {mock_websocket}
    
    # Send the message
    await manager.send_personal_message(message, user_id)
    
    # Assertions
    mock_websocket.send_text.assert_called_once_with(message)
    # The connection should be removed after the error
    assert user_id not in manager.active_connections
