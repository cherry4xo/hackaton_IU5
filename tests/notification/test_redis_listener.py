import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime
import json

from services.notification.app.redis_listener import listen_to_results


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
async def test_listen_to_results_completed_task():
    """Test listener processes a completed task."""
    # Mock redis_client
    with patch('app.redis_listener.redis_client') as mock_redis_client:
        # Configure mocks
        mock_redis_client.xread = AsyncMock(return_value=[
            ("result_queue", [("msg_id", {
                "task_id": "test_task_id",
                "user_id": "test_user_id",
                "status": "completed",
                "result": json.dumps({"orbit": {"semi_major_axis": 2.5}}),
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
                
                # Assertions
                mock_redis_client.xread.assert_called_once()
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
async def test_listen_to_results_failed_task():
    """Test listener processes a failed task."""
    # Mock redis_client
    with patch('app.redis_listener.redis_client') as mock_redis_client:
        # Configure mocks
        mock_redis_client.xread = AsyncMock(return_value=[
            ("result_queue", [("msg_id", {
                "task_id": "test_task_id",
                "user_id": "test_user_id",
                "status": "failed",
                "result": "",
                "error": "Test error message",
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
                
                # Assertions
                mock_redis_client.xread.assert_called_once()
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
async def test_listen_to_results_empty_result():
    """Test listener processes a completed task with empty result."""
    # Mock redis_client
    with patch('app.redis_listener.redis_client') as mock_redis_client:
        # Configure mocks
        mock_redis_client.xread = AsyncMock(return_value=[
            ("result_queue", [("msg_id", {
                "task_id": "test_task_id",
                "user_id": "test_user_id",
                "status": "completed",
                "result": "",
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
                
                # Assertions
                mock_redis_client.xread.assert_called_once()
                mock_manager.send_personal_message.assert_called_once()
                
                # Check the notification content
                call_args = mock_manager.send_personal_message.call_args
                message = call_args[0][0]  # First positional argument
                
                # Parse the message to verify its content
                notification = json.loads(message)
                assert notification["event"] == "orbit_calculation_completed"
                assert notification["data"] is None  # Should be None when result is empty


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
