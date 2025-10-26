import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime
import json

from services.calculation.app.worker import run_worker


@pytest.mark.asyncio
async def test_run_worker_initialization():
    """Test worker initialization."""
    # Mock the init function
    with patch('worker.init') as mock_init:
        # Mock redis_client
        with patch('worker.redis_client') as mock_redis_client:
            # Configure mocks to exit early
            mock_init.side_effect = Exception("Stop test")
            
            # Run the function and expect it to raise an exception
            with pytest.raises(Exception, match="Stop test"):
                await run_worker()
            
            # Assertions
            mock_init.assert_called_once()


@pytest.mark.asyncio
async def test_run_worker_no_messages():
    """Test worker when no messages are available."""
    # Mock the init function
    with patch('worker.init') as mock_init:
        # Mock redis_client
        with patch('worker.redis_client') as mock_redis_client:
            # Configure mocks
            mock_redis_client.xread = AsyncMock(return_value=None)  # No messages
            
            # Mock asyncio.sleep to break the infinite loop
            with patch('worker.asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
                mock_sleep.side_effect = Exception("Stop test")
                
                # Run the function and expect it to raise an exception
                with pytest.raises(Exception, match="Stop test"):
                    await run_worker()
                
                # Assertions
                mock_init.assert_called_once()
                mock_redis_client.xread.assert_called_once()


@pytest.mark.asyncio
async def test_run_worker_continue_on_empty_response():
    """Test worker continues when receiving empty response."""
    # Mock the init function
    with patch('worker.init') as mock_init:
        # Mock redis_client
        with patch('worker.redis_client') as mock_redis_client:
            # Configure mocks
            mock_redis_client.xread = AsyncMock(return_value=[])  # Empty response
            
            # Mock asyncio.sleep to break the infinite loop
            with patch('worker.asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
                mock_sleep.side_effect = Exception("Stop test")
                
                # Run the function and expect it to raise an exception
                with pytest.raises(Exception, match="Stop test"):
                    await run_worker()
                
                # Assertions
                mock_init.assert_called_once()
                mock_redis_client.xread.assert_called_once()


@pytest.mark.asyncio
async def test_run_worker_task_not_found():
    """Test worker when task is not found in database."""
    # Mock the init function
    with patch('worker.init') as mock_init:
        # Mock redis_client
        with patch('worker.redis_client') as mock_redis_client:
            # Configure mocks
            mock_redis_client.xread = AsyncMock(return_value=[
                ("input_queue", [("msg_id", {"task_id": "test_task_id"})])
            ])
            
            # Mock CalculationTask
            with patch('worker.CalculationTask') as mock_calculation_task:
                mock_calculation_task.get_or_none = AsyncMock(return_value=None)  # Task not found
                
                # Mock asyncio.sleep to break the infinite loop
                with patch('worker.asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
                    mock_sleep.side_effect = Exception("Stop test")
                    
                    # Run the function and expect it to raise an exception
                    with pytest.raises(Exception, match="Stop test"):
                        await run_worker()
                    
                    # Assertions
                    mock_init.assert_called_once()
                    mock_redis_client.xread.assert_called_once()
                    mock_calculation_task.get_or_none.assert_called_once_with(uuid="test_task_id")


@pytest.mark.asyncio
async def test_run_worker_task_processing_success():
    """Test worker successfully processes a task."""
    # Mock the init function
    with patch('worker.init') as mock_init:
        # Mock redis_client
        with patch('worker.redis_client') as mock_redis_client:
            # Configure mocks
            mock_redis_client.xread = AsyncMock(return_value=[
                ("input_queue", [("msg_id", {"task_id": "test_task_id"})])
            ])
            
            # Mock CalculationTask
            with patch('worker.CalculationTask') as mock_calculation_task:
                mock_task = AsyncMock()
                mock_task.status = "pending"
                mock_task.save = AsyncMock()
                mock_task.comet = None
                mock_task.user_id = "test_user_id"
                mock_task.created_at = datetime.now()
                mock_calculation_task.get_or_none = AsyncMock(return_value=mock_task)
                
                # Mock process_task
                with patch('worker.process_task') as mock_process_task:
                    mock_process_task.return_value = {
                        "status": "completed",
                        "result": {
                            "orbit": {
                                "semi_major_axis": 2.5,
                                "eccentricity": 0.1,
                                "inclination": 5.0,
                                "longitude_ascending_node": 45.0,
                                "argument_periapsis": 30.0,
                                "periapsis_time": datetime.now()
                            },
                            "closest_approach": {
                                "time": datetime.now(),
                                "distance_au": 1.2,
                                "distance_km": 179517444.0
                            }
                        },
                        "error": None
                    }
                    
                    # Mock Comets
                    with patch('worker.Comets') as mock_comets:
                        mock_comet = AsyncMock()
                        mock_comet.id = "test_comet_id"
                        mock_comets.create = AsyncMock(return_value=mock_comet)
                        
                        # Mock Orbits
                        with patch('worker.Orbits') as mock_orbits:
                            mock_orbit = AsyncMock()
                            mock_orbit.id = "test_orbit_id"
                            mock_orbits.create = AsyncMock(return_value=mock_orbit)
                            
                            # Mock Close_approaches
                            with patch('worker.Close_approaches') as mock_close_approaches:
                                mock_close_approach = AsyncMock()
                                mock_close_approach.id = "test_ca_id"
                                mock_close_approaches.create = AsyncMock(return_value=mock_close_approach)
                                
                                # Mock asyncio.sleep to break the infinite loop
                                with patch('worker.asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
                                    mock_sleep.side_effect = Exception("Stop test")
                                    
                                    # Run the function and expect it to raise an exception
                                    with pytest.raises(Exception, match="Stop test"):
                                        await run_worker()
                                    
                                    # Assertions
                                    mock_init.assert_called_once()
                                    mock_redis_client.xread.assert_called_once()
                                    mock_calculation_task.get_or_none.assert_called_once_with(uuid="test_task_id")
                                    mock_task.save.assert_called()  # Called at least once to update status
                                    mock_process_task.assert_called_once()
                                    mock_comets.create.assert_called_once()
                                    mock_orbits.create.assert_called_once()
                                    mock_close_approaches.create.assert_called_once()
                                    mock_redis_client.xadd.assert_called_once()


@pytest.mark.asyncio
async def test_run_worker_task_processing_failure():
    """Test worker handles task processing failure."""
    # Mock the init function
    with patch('worker.init') as mock_init:
        # Mock redis_client
        with patch('worker.redis_client') as mock_redis_client:
            # Configure mocks
            mock_redis_client.xread = AsyncMock(return_value=[
                ("input_queue", [("msg_id", {"task_id": "test_task_id"})])
            ])
            
            # Mock CalculationTask
            with patch('worker.CalculationTask') as mock_calculation_task:
                mock_task = AsyncMock()
                mock_task.status = "pending"
                mock_task.save = AsyncMock()
                mock_task.comet = None
                mock_task.user_id = "test_user_id"
                mock_calculation_task.get_or_none = AsyncMock(return_value=mock_task)
                
                # Mock process_task to return a failure
                with patch('worker.process_task') as mock_process_task:
                    mock_process_task.return_value = {
                        "status": "failed",
                        "result": None,
                        "error": "Test error message"
                    }
                    
                    # Mock asyncio.sleep to break the infinite loop
                    with patch('worker.asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
                        mock_sleep.side_effect = Exception("Stop test")
                        
                        # Run the function and expect it to raise an exception
                        with pytest.raises(Exception, match="Stop test"):
                            await run_worker()
                        
                        # Assertions
                        mock_init.assert_called_once()
                        mock_redis_client.xread.assert_called_once()
                        mock_calculation_task.get_or_none.assert_called_once_with(uuid="test_task_id")
                        mock_task.save.assert_called()  # Called at least once to update status
                        mock_process_task.assert_called_once()
                        # Error message should be set
                        assert mock_task.error_message == "Test error message"
                        mock_redis_client.xadd.assert_called_once()


@pytest.mark.asyncio
async def test_run_worker_existing_comet():
    """Test worker when comet already exists."""
    # Mock the init function
    with patch('worker.init') as mock_init:
        # Mock redis_client
        with patch('worker.redis_client') as mock_redis_client:
            # Configure mocks
            mock_redis_client.xread = AsyncMock(return_value=[
                ("input_queue", [("msg_id", {"task_id": "test_task_id"})])
            ])
            
            # Mock CalculationTask with existing comet
            with patch('worker.CalculationTask') as mock_calculation_task:
                mock_comet = AsyncMock()
                mock_comet.id = "existing_comet_id"
                
                mock_task = AsyncMock()
                mock_task.status = "pending"
                mock_task.save = AsyncMock()
                mock_task.comet = mock_comet  # Existing comet
                mock_task.user_id = "test_user_id"
                mock_task.created_at = datetime.now()
                mock_calculation_task.get_or_none = AsyncMock(return_value=mock_task)
                
                # Mock process_task
                with patch('worker.process_task') as mock_process_task:
                    mock_process_task.return_value = {
                        "status": "completed",
                        "result": {
                            "orbit": {
                                "semi_major_axis": 2.5,
                                "eccentricity": 0.1,
                                "inclination": 5.0,
                                "longitude_ascending_node": 45.0,
                                "argument_periapsis": 30.0,
                                "periapsis_time": datetime.now()
                            },
                            "closest_approach": {
                                "time": datetime.now(),
                                "distance_au": 1.2,
                                "distance_km": 179517444.0
                            }
                        },
                        "error": None
                    }
                    
                    # Mock Orbits
                    with patch('worker.Orbits') as mock_orbits:
                        mock_orbit = AsyncMock()
                        mock_orbit.id = "test_orbit_id"
                        mock_orbits.create = AsyncMock(return_value=mock_orbit)
                        
                        # Mock Close_approaches
                        with patch('worker.Close_approaches') as mock_close_approaches:
                            mock_close_approach = AsyncMock()
                            mock_close_approach.id = "test_ca_id"
                            mock_close_approaches.create = AsyncMock(return_value=mock_close_approach)
                            
                            # Mock asyncio.sleep to break the infinite loop
                            with patch('worker.asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
                                mock_sleep.side_effect = Exception("Stop test")
                                
                                # Run the function and expect it to raise an exception
                                with pytest.raises(Exception, match="Stop test"):
                                    await run_worker()
                                
                                # Assertions
                                mock_init.assert_called_once()
                                mock_redis_client.xread.assert_called_once()
                                mock_calculation_task.get_or_none.assert_called_once_with(uuid="test_task_id")
                                mock_task.save.assert_called()  # Called at least once to update status
                                mock_process_task.assert_called_once()
                                # Comet should not be created since it already exists
                                mock_orbits.create.assert_called_once()
                                mock_close_approaches.create.assert_called_once()
                                mock_redis_client.xadd.assert_called_once()


@pytest.mark.asyncio
async def test_run_worker_exception_handling():
    """Test worker handles exceptions gracefully."""
    # Mock the init function
    with patch('worker.init') as mock_init:
        # Mock redis_client to raise an exception
        with patch('worker.redis_client') as mock_redis_client:
            mock_redis_client.xread.side_effect = Exception("Redis error")
            
            # Mock asyncio.sleep
            with patch('worker.asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
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
                    await run_worker()
                
                # Assertions
                mock_init.assert_called_once()
                assert mock_redis_client.xread.call_count == 2
                assert mock_sleep.call_count == 2
