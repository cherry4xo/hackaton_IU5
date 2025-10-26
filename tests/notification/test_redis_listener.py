import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime
import json

from services.notification.app.redis_listener import listen_to_results, process_result_message


@pytest.mark.asyncio
async def test_listen_to_results_no_messages():
    """Test listener when no messages are available."""
    # Mock redis_client
    with patch('app.redis_listener.redis_client') as mock_redis_client:
        # Configure mocks
        mock_redis_client.xread = AsyncMock(return_value=None)  # No messages
        
        # Mock asyncio.sleep to break the infinite loop
        with patch('app.redis_listener.asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            mock_sleep.side_effect = Exception("Stop test")
            
            # Run the function and expect it to raise an exception
            with pytest.raises(Exception, match="Stop test"):
                await listen_to_results()
            
            # Assertions
            mock_redis_client.xread.assert_called_once()


@pytest.mark.asyncio
async def test_listen_to_results_continue_on_empty_response():
    """Test listener continues when receiving empty response."""
    # Mock redis_client
    with patch('app.redis_listener.redis_client') as mock_redis_client:
        # Configure mocks
        mock_redis_client.xread = AsyncMock(return_value=[])  # Empty response
        
        # Mock asyncio.sleep to break the infinite loop
        with patch('app.redis_listener.asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            mock_sleep.side_effect = Exception("Stop test")
            
            # Run the function and expect it to raise an exception
            with pytest.raises(Exception, match="Stop test"):
                await listen_to_results()
            
            # Assertions
            mock_redis_client.xread.assert_called_once()


@pytest.mark.asyncio
async def test_process_result_message_orbit_completed():
    """Test processing a completed orbit calculation task."""
    # Mock manager
    with patch('app.redis_listener.manager') as mock_manager:
        mock_manager.send_personal_message = AsyncMock()
        
        # Test data
        msg_data = {
            "task_id": "test_task_id",
            "user_id": "test_user_id",
            "status": "completed",
            "result": json.dumps({"orbit": {"semi_major_axis": 2.5}}),
            "error": "",
            "timestamp": "2025-01-01T12:00:00Z"
        }
        
        # Call the function
        await process_result_message("orbit_result_queue", msg_data)
        
        # Assertions
        mock_manager.send_personal_message.assert_called_once()
        
        # Check the notification content
        call_args = mock_manager.send_personal_message.call_args
        message = call_args[0][0]  # First positional argument
        user_id = call_args[0][1]  # Second positional argument
        
        assert user_id == "test_user_id"
        
        # Parse the message to verify its content
        notification = json.loads(message)
        assert notification["event"] == "orbit_calculation_completed"
        assert notification["task_id"] == "test_task_id"
        assert notification["status"] == "completed"
        assert notification["data"] == {"orbit": {"semi_major_axis": 2.5}}
        assert notification["error"] is None
        assert notification["timestamp"] is not None


@pytest.mark.asyncio
async def test_process_result_message_closest_approach_completed():
    """Test processing a completed closest approach calculation task."""
    # Mock manager
    with patch('app.redis_listener.manager') as mock_manager:
        mock_manager.send_personal_message = AsyncMock()
        
        # Test data
        msg_data = {
            "task_id": "test_task_id",
            "user_id": "test_user_id",
            "status": "completed",
            "result": json.dumps({"closest_approach": {"distance_au": 1.2}}),
            "error": "",
            "timestamp": "2025-01-01T12:00:00Z"
        }
        
        # Call the function
        await process_result_message("closest_approach_result_queue", msg_data)
        
        # Assertions
        mock_manager.send_personal_message.assert_called_once()
        
        # Check the notification content
        call_args = mock_manager.send_personal_message.call_args
        message = call_args[0][0]  # First positional argument
        user_id = call_args[0][1]  # Second positional argument
        
        assert user_id == "test_user_id"
        
        # Parse the message to verify its content
        notification = json.loads(message)
        assert notification["event"] == "closest_approach_calculation_completed"
        assert notification["task_id"] == "test_task_id"
        assert notification["status"] == "completed"
        assert notification["data"] == {"closest_approach": {"distance_au": 1.2}}
        assert notification["error"] is None
        assert notification["timestamp"] is not None


@pytest.mark.asyncio
async def test_process_result_message_legacy_completed():
    """Test processing a completed task from legacy queue."""
    # Mock manager
    with patch('app.redis_listener.manager') as mock_manager:
        mock_manager.send_personal_message = AsyncMock()
        
        # Test data
        msg_data = {
            "task_id": "test_task_id",
            "user_id": "test_user_id",
            "status": "completed",
            "result": json.dumps({"orbit": {"semi_major_axis": 2.5}}),
            "error": "",
            "timestamp": "2025-01-01T12:00:00Z"
        }
        
        # Call the function
        await process_result_message("result_queue", msg_data)
        
        # Assertions
        mock_manager.send_personal_message.assert_called_once()
        
        # Check the notification content
        call_args = mock_manager.send_personal_message.call_args
        message = call_args[0][0]  # First positional argument
        user_id = call_args[0][1]  # Second positional argument
        
        assert user_id == "test_user_id"
        
        # Parse the message to verify its content
        notification = json.loads(message)
        assert notification["event"] == "orbit_calculation_completed"
        assert notification["task_id"] == "test_task_id"
        assert notification["status"] == "completed"
        assert notification["data"] == {"orbit": {"semi_major_axis": 2.5}}
        assert notification["error"] is None
        assert notification["timestamp"] is not None


@pytest.mark.asyncio
async def test_process_result_message_orbit_failed():
    """Test processing a failed orbit calculation task."""
    # Mock manager
    with patch('app.redis_listener.manager') as mock_manager:
        mock_manager.send_personal_message = AsyncMock()
        
        # Test data
        msg_data = {
            "task_id": "test_task_id",
            "user_id": "test_user_id",
            "status": "failed",
            "result": "",
            "error": "Test error message",
            "timestamp": "2025-01-01T12:00:00Z"
        }
        
        # Call the function
        await process_result_message("orbit_result_queue", msg_data)
        
        # Assertions
        mock_manager.send_personal_message.assert_called_once()
        
        # Check the notification content
        call_args = mock_manager.send_personal_message.call_args
        message = call_args[0][0]  # First positional argument
        user_id = call_args[0][1]  # Second positional argument
        
        assert user_id == "test_user_id"
        
        # Parse the message to verify its content
        notification = json.loads(message)
        assert notification["event"] == "orbit_calculation_failed"
        assert notification["task_id"] == "test_task_id"
        assert notification["status"] == "failed"
        assert notification["data"] is None
        assert notification["error"] == "Test error message"
        assert notification["timestamp"] is not None


@pytest.mark.asyncio
async def test_process_result_message_closest_approach_failed():
    """Test processing a failed closest approach calculation task."""
    # Mock manager
    with patch('app.redis_listener.manager') as mock_manager:
        mock_manager.send_personal_message = AsyncMock()
        
        # Test data
        msg_data = {
            "task_id": "test_task_id",
            "user_id": "test_user_id",
            "status": "failed",
            "result": "",
            "error": "Test error message",
            "timestamp": "2025-01-01T12:00:00Z"
        }
        
        # Call the function
        await process_result_message("closest_approach_result_queue", msg_data)
        
        # Assertions
        mock_manager.send_personal_message.assert_called_once()
        
        # Check the notification content
        call_args = mock_manager.send_personal_message.call_args
        message = call_args[0][0]  # First positional argument
        user_id = call_args[0][1]  # Second positional argument
        
        assert user_id == "test_user_id"
        
        # Parse the message to verify its content
        notification = json.loads(message)
        assert notification["event"] == "closest_approach_calculation_failed"
        assert notification["task_id"] == "test_task_id"
        assert notification["status"] == "failed"
        assert notification["data"] is None
        assert notification["error"] == "Test error message"
        assert notification["timestamp"] is not None


@pytest.mark.asyncio
async def test_process_result_message_legacy_failed():
    """Test processing a failed task from legacy queue."""
    # Mock manager
    with patch('app.redis_listener.manager') as mock_manager:
        mock_manager.send_personal_message = AsyncMock()
        
        # Test data
        msg_data = {
            "task_id": "test_task_id",
            "user_id": "test_user_id",
            "status": "failed",
            "result": "",
            "error": "Test error message",
            "timestamp": "2025-01-01T12:00:00Z"
        }
        
        # Call the function
        await process_result_message("result_queue", msg_data)
        
        # Assertions
        mock_manager.send_personal_message.assert_called_once()
        
        # Check the notification content
        call_args = mock_manager.send_personal_message.call_args
        message = call_args[0][0]  # First positional argument
        user_id = call_args[0][1]  # Second positional argument
        
        assert user_id == "test_user_id"
        
        # Parse the message to verify its content
        notification = json.loads(message)
        assert notification["event"] == "orbit_calculation_failed"
        assert notification["task_id"] == "test_task_id"
        assert notification["status"] == "failed"
        assert notification["data"] is None
        assert notification["error"] == "Test error message"
        assert notification["timestamp"] is not None


@pytest.mark.asyncio
async def test_process_result_message_empty_result():
    """Test processing a completed task with empty result."""
    # Mock manager
    with patch('app.redis_listener.manager') as mock_manager:
        mock_manager.send_personal_message = AsyncMock()
        
        # Test data
        msg_data = {
            "task_id": "test_task_id",
            "user_id": "test_user_id",
            "status": "completed",
            "result": "",
            "error": "",
            "timestamp": "2025-01-01T12:00:00Z"
        }
        
        # Call the function
        await process_result_message("orbit_result_queue", msg_data)
        
        # Assertions
        mock_manager.send_personal_message.assert_called_once()
        
        # Check the notification content
        call_args = mock_manager.send_personal_message.call_args
        message = call_args[0][0]  # First positional argument
        
        # Parse the message to verify its content
        notification = json.loads(message)
        assert notification["event"] == "orbit_calculation_completed"
        assert notification["data"] is None  # Should be None when result is empty


@pytest.mark.asyncio
async def test_listen_to_results_multiple_queues():
    """Test listener processes messages from all queues."""
    # Mock redis_client
    with patch('app.redis_listener.redis_client') as mock_redis_client:
        # Configure mocks to return messages from different queues
        mock_redis_client.xread = AsyncMock(return_value=[
            ("result_queue", [("msg_id_1", {
                "task_id": "test_task_1",
                "user_id": "test_user_1",
                "status": "completed",
                "result": json.dumps({"orbit": {"semi_major_axis": 2.5}}),
                "error": "",
                "timestamp": "2025-01-01T12:00:00Z"
            })]),
            ("orbit_result_queue", [("msg_id_2", {
                "task_id": "test_task_2",
                "user_id": "test_user_2",
                "status": "completed",
                "result": json.dumps({"orbit": {"semi_major_axis": 3.0}}),
                "error": "",
                "timestamp": "2025-01-01T12:00:00Z"
            })]),
            ("closest_approach_result_queue", [("msg_id_3", {
                "task_id": "test_task_3",
                "user_id": "test_user_3",
                "status": "completed",
                "result": json.dumps({"closest_approach": {"distance_au": 1.2}}),
                "error": "",
                "timestamp": "2025-01-01T12:00:00Z"
            })])
        ])
        
        # Mock manager
        with patch('app.redis_listener.manager') as mock_manager:
            mock_manager.send_personal_message = AsyncMock()
            
            # Mock asyncio.sleep to break the infinite loop
            with patch('app.redis_listener.asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
                mock_sleep.side_effect = Exception("Stop test")
                
                # Run the function and expect it to raise an exception
                with pytest.raises(Exception, match="Stop test"):
                    await listen_to_results()
                
                # Assertions - should be called 3 times (once for each message)
                assert mock_manager.send_personal_message.call_count == 3
                mock_redis_client.xread.assert_called_once()


@pytest.mark.asyncio
async def test_listen_to_results_exception_handling():
    """Test listener handles exceptions gracefully."""
    # Mock redis_client to raise an exception
    with patch('app.redis_listener.redis_client') as mock_redis_client:
        mock_redis_client.xread.side_effect = Exception("Redis error")
        
        # Mock asyncio.sleep
        with patch('app.redis_listener.asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            # Configure mock to break the loop after a few calls
            call_count = 0
            def sleep_side_effect(*args, **kwargs):
                nonlocal call_count
                call_count += 1
                if call_count >= 2:
                    raise Exception("Stop test")
                return AsyncMock()()
            
            mock_sleep.side_effect = sleep_side_effect
            
            # Run the function and expect it to raise an exception
            with pytest.raises(Exception, match="Stop test"):
                await listen_to_results()
            
            # Assertions
            assert mock_redis_client.xread.call_count == 2
            assert mock_sleep.call_count == 2
