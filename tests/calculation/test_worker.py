from unittest import mock
import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime
import json

from services.calculation.app.worker import run_worker, handle_orbit_calculation, handle_closest_approach, process_single_task
from services.calculation.app.enums import CalculationTaskType


@pytest.mark.asyncio
async def test_run_worker_initialization():
    """Test worker initialization."""
    # Mock the init function
    with patch('services.calculation.app.worker.init') as mock_init:
        # Mock redis_client
        with patch('services.calculation.app.worker.redis_client') as mock_redis_client:
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
    with patch('services.calculation.app.worker.init') as mock_init:
        # Mock redis_client
        with patch('services.calculation.app.worker.redis_client') as mock_redis_client:
            # Configure mocks
            mock_redis_client.xread = AsyncMock(return_value=None)  # No messages
            
            # Mock asyncio.sleep to break the infinite loop
            with patch('services.calculation.app.worker.asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
                mock_sleep.side_effect = Exception("Stop test")
                
                # Run the function and expect it to raise an exception
                with pytest.raises(Exception, match="Stop test"):
                    await run_worker()
                
                # Assertions
                mock_init.assert_called_once()
                # Should call xread for each queue
                assert mock_redis_client.xread.call_count == 3


@pytest.mark.asyncio
async def test_run_worker_continue_on_empty_response():
    """Test worker continues when receiving empty response."""
    # Mock the init function
    with patch('services.calculation.app.worker.init') as mock_init:
        # Mock redis_client
        with patch('services.calculation.app.worker.redis_client') as mock_redis_client:
            # Configure mocks
            mock_redis_client.xread = AsyncMock(return_value=[])  # Empty response
            
            # Mock asyncio.sleep to break the infinite loop
            with patch('services.calculation.app.worker.asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
                mock_sleep.side_effect = Exception("Stop test")
                
                # Run the function and expect it to raise an exception
                with pytest.raises(Exception, match="Stop test"):
                    await run_worker()
                
                # Assertions
                mock_init.assert_called_once()
                # Should call xread for each queue
                assert mock_redis_client.xread.call_count == 3


@pytest.mark.asyncio
async def test_run_worker_task_not_found():
    """Test worker when task is not found in database."""
    # Mock the init function
    with patch('services.calculation.app.worker.init') as mock_init:
        # Mock redis_client
        with patch('services.calculation.app.worker.redis_client') as mock_redis_client:
            # Configure mocks
            mock_redis_client.xread = AsyncMock(return_value=[
                ("input_queue", [("msg_id", {"task_id": "test_task_id"})])
            ])
            
            # Mock CalculationTask
            with patch('services.calculation.app.worker.CalculationTask') as mock_calculation_task:
                mock_calculation_task.get_or_none = AsyncMock(return_value=None)  # Task not found
                
                # Mock asyncio.sleep to break the infinite loop
                with patch('services.calculation.app.worker.asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
                    mock_sleep.side_effect = Exception("Stop test")
                    
                    # Run the function and expect it to raise an exception
                    with pytest.raises(Exception, match="Stop test"):
                        await run_worker()
                    
                    # Assertions
                    mock_init.assert_called_once()
                    mock_redis_client.xread.assert_called()
                    mock_calculation_task.get_or_none.assert_called_once_with(uuid="test_task_id")


@pytest.mark.asyncio
async def test_handle_orbit_calculation_success():
    """Test handle_orbit_calculation successfully processes orbit calculation."""
    # Mock task data
    task_data = {
        "task_id": "test_task_id",
        "observations": [
            {"observation_time": datetime.now().isoformat(), "ra": 100.0, "dec": 10.0},
            {"observation_time": datetime.now().isoformat(), "ra": 101.0, "dec": 10.5},
            {"observation_time": datetime.now().isoformat(), "ra": 102.0, "dec": 11.0}
        ]
    }
    
    # Mock CalculationTask
    mock_task = AsyncMock()
    mock_task.status = "pending"
    mock_task.save = AsyncMock()
    mock_task.comet = None
    mock_task.user_id = "test_user_id"
    mock_task.created_at = datetime.now()
    
    # Mock calculate_orbit_task
    with patch('services.calculation.app.worker.calculate_orbit_task') as mock_calculate_orbit_task:
        mock_calculate_orbit_task.return_value = {
            "status": "completed",
            "result": {
                "orbit": {
                    "semi_major_axis": 2.5,
                    "eccentricity": 0.1,
                    "inclination": 5.0,
                    "longitude_ascending_node": 45.0,
                    "argument_periapsis": 30.0,
                    "periapsis_time": datetime.now()
                }
            },
            "error": None
        }
        
        # Mock Comets
        with patch('services.calculation.app.worker.Comets') as mock_comets:
            mock_comet = AsyncMock()
            mock_comet.id = "test_comet_id"
            mock_comets.create = AsyncMock(return_value=mock_comet)
            
            # Mock Orbits
            with patch('services.calculation.app.worker.Orbits') as mock_orbits:
                mock_orbit = AsyncMock()
                mock_orbit.id = "test_orbit_id"
                mock_orbits.create = AsyncMock(return_value=mock_orbit)
                
                # Call the function
                result = await handle_orbit_calculation(task_data, mock_task)
                
                # Assertions
                assert result["status"] == "completed"
                mock_calculate_orbit_task.assert_called_once_with(task_data)
                mock_task.save.assert_called()
                mock_comets.create.assert_called_once()
                mock_orbits.create.assert_called_once()


@pytest.mark.asyncio
async def test_handle_closest_approach_success():
    """Test handle_closest_approach successfully processes closest approach calculation."""
    # Mock task data
    task_data = {
        "task_id": "test_task_id",
        "orbit_elements": {
            "semi_major_axis": 2.5,
            "eccentricity": 0.1,
            "inclination": 5.0,
            "longitude_ascending_node": 45.0,
            "argument_periapsis": 30.0,
            "periapsis_time": datetime.now()
        }
    }
    
    # Mock CalculationTask
    mock_task = AsyncMock()
    mock_task.status = "pending"
    mock_task.save = AsyncMock()
    mock_task.comet = AsyncMock()
    mock_task.orbit = AsyncMock()
    
    # Mock calculate_closest_approach_task
    with patch('services.calculation.app.worker.calculate_closest_approach_task') as mock_calculate_closest_approach_task:
        mock_calculate_closest_approach_task.return_value = {
            "status": "completed",
            "result": {
                "closest_approach": {
                    "time": datetime.now(),
                    "distance_au": 1.2,
                    "distance_km": 179517444.0
                }
            },
            "error": None
        }
        
        # Mock Close_approaches
        with patch('services.calculation.app.worker.Close_approaches') as mock_close_approaches:
            mock_close_approach = AsyncMock()
            mock_close_approach.id = "test_ca_id"
            mock_close_approaches.create = AsyncMock(return_value=mock_close_approach)
            
            # Call the function
            result = await handle_closest_approach(task_data, mock_task)
            
            # Assertions
            assert result["status"] == "completed"
            mock_calculate_closest_approach_task.assert_called_once_with(task_data)
            mock_task.save.assert_called()
            mock_close_approaches.create.assert_called_once()


@pytest.mark.asyncio
async def test_process_single_task_orbit_calculation():
    """Test process_single_task for orbit calculation queue."""
    # Mock redis_client
    with patch('services.calculation.app.worker.redis_client') as mock_redis_client:
        # Configure mocks
        mock_redis_client.xread = AsyncMock(return_value=[
            ("orbit_calculation_queue", [("msg_id", {"task_id": "test_task_id"})])
        ])
        
        # Mock CalculationTask
        with patch('services.calculation.app.worker.CalculationTask') as mock_calculation_task:
            mock_task = AsyncMock()
            mock_task.status = "pending"
            mock_task.save = AsyncMock()
            mock_task.comet = None
            mock_task.user_id = "test_user_id"
            mock_task.created_at = datetime.now()
            mock_calculation_task.get_or_none = AsyncMock(return_value=mock_task)
            
            # Mock handle_orbit_calculation
            with patch('services.calculation.app.worker.handle_orbit_calculation') as mock_handle_orbit_calculation:
                mock_handle_orbit_calculation.return_value = {
                    "status": "completed",
                    "result": {
                        "orbit": {
                            "semi_major_axis": 2.5,
                            "eccentricity": 0.1,
                            "inclination": 5.0,
                            "longitude_ascending_node": 45.0,
                            "argument_periapsis": 30.0,
                            "periapsis_time": datetime.now()
                        }
                    },
                    "error": None
                }
                
                # Mock Comets
                with patch('services.calculation.app.worker.Comets') as mock_comets:
                    mock_comet = AsyncMock()
                    mock_comet.id = "test_comet_id"
                    mock_comets.create = AsyncMock(return_value=mock_comet)
                    
                    # Mock Orbits
                    with patch('services.calculation.app.worker.Orbits') as mock_orbits:
                        mock_orbit = AsyncMock()
                        mock_orbit.id = "test_orbit_id"
                        mock_orbits.create = AsyncMock(return_value=mock_orbit)
                        
                        # Mock xadd
                        mock_redis_client.xadd = AsyncMock()
                        
                        # Call the function
                        await process_single_task("orbit_calculation_queue", CalculationTaskType.ORBIT_CALCULATION, {"orbit_calculation_queue": "$"})
                        
                        # Assertions
                        mock_redis_client.xread.assert_called_once_with(
                            {"orbit_calculation_queue": "$"},
                            count=1,
                            block=1000
                        )
                        mock_calculation_task.get_or_none.assert_called_once_with(uuid="test_task_id")
                        mock_handle_orbit_calculation.assert_called_once()
                        mock_redis_client.xadd.assert_called_once_with(
                            "orbit_result_queue",
                            {
                                "task_id": "test_task_id",
                                "status": "completed",
                                "user_id": "test_user_id",
                                "result": json.dumps({"orbit": {
                                    "semi_major_axis": 2.5,
                                    "eccentricity": 0.1,
                                    "inclination": 5.0,
                                    "longitude_ascending_node": 45.0,
                                    "argument_periapsis": 30.0,
                                    "periapsis_time": mock_handle_orbit_calculation.return_value["result"]["orbit"]["periapsis_time"]
                                }}),
                                "error": "",
                                "timestamp": mock.ANY
                            }
                        )


@pytest.mark.asyncio
async def test_process_single_task_closest_approach():
    """Test process_single_task for closest approach queue."""
    # Mock redis_client
    with patch('services.calculation.app.worker.redis_client') as mock_redis_client:
        # Configure mocks
        mock_redis_client.xread = AsyncMock(return_value=[
            ("closest_approach_queue", [("msg_id", {"task_id": "test_task_id"})])
        ])
        
        # Mock CalculationTask
        with patch('services.calculation.app.worker.CalculationTask') as mock_calculation_task:
            mock_task = AsyncMock()
            mock_task.status = "pending"
            mock_task.save = AsyncMock()
            mock_task.comet = AsyncMock()
            mock_task.orbit = AsyncMock()
            mock_task.user_id = "test_user_id"
            mock_calculation_task.get_or_none = AsyncMock(return_value=mock_task)
            
            # Mock handle_closest_approach
            with patch('services.calculation.app.worker.handle_closest_approach') as mock_handle_closest_approach:
                mock_handle_closest_approach.return_value = {
                    "status": "completed",
                    "result": {
                        "closest_approach": {
                            "time": datetime.now(),
                            "distance_au": 1.2,
                            "distance_km": 179517444.0
                        }
                    },
                    "error": None
                }
                
                # Mock Close_approaches
                with patch('services.calculation.app.worker.Close_approaches') as mock_close_approaches:
                    mock_close_approach = AsyncMock()
                    mock_close_approach.id = "test_ca_id"
                    mock_close_approaches.create = AsyncMock(return_value=mock_close_approach)
                    
                    # Mock xadd
                    mock_redis_client.xadd = AsyncMock()
                    
                    # Call the function
                    await process_single_task("closest_approach_queue", CalculationTaskType.CLOSEST_APPROACH, {"closest_approach_queue": "$"})
                    
                    # Assertions
                    mock_redis_client.xread.assert_called_once_with(
                        {"closest_approach_queue": "$"},
                        count=1,
                        block=1000
                    )
                    mock_calculation_task.get_or_none.assert_called_once_with(uuid="test_task_id")
                    mock_handle_closest_approach.assert_called_once()
                    mock_redis_client.xadd.assert_called_once_with(
                        "closest_approach_result_queue",
                        {
                            "task_id": "test_task_id",
                            "status": "completed",
                            "user_id": "test_user_id",
                            "result": json.dumps({"closest_approach": mock_handle_closest_approach.return_value["result"]["closest_approach"]}),
                            "error": "",
                            "timestamp": mock.ANY
                        }
                    )


@pytest.mark.asyncio
async def test_process_single_task_legacy():
    """Test process_single_task for legacy input queue."""
    # Mock redis_client
    with patch('services.calculation.app.worker.redis_client') as mock_redis_client:
        # Configure mocks
        mock_redis_client.xread = AsyncMock(return_value=[
            ("input_queue", [("msg_id", {"task_id": "test_task_id"})])
        ])
        
        # Mock CalculationTask
        with patch('services.calculation.app.worker.CalculationTask') as mock_calculation_task:
            mock_task = AsyncMock()
            mock_task.status = "pending"
            mock_task.save = AsyncMock()
            mock_task.comet = None
            mock_task.user_id = "test_user_id"
            mock_task.created_at = datetime.now()
            mock_calculation_task.get_or_none = AsyncMock(return_value=mock_task)
            
            # Mock process_task
            with patch('services.calculation.app.worker.process_task') as mock_process_task:
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
                with patch('services.calculation.app.worker.Comets') as mock_comets:
                    mock_comet = AsyncMock()
                    mock_comet.id = "test_comet_id"
                    mock_comets.create = AsyncMock(return_value=mock_comet)
                    
                    # Mock Orbits
                    with patch('services.calculation.app.worker.Orbits') as mock_orbits:
                        mock_orbit = AsyncMock()
                        mock_orbit.id = "test_orbit_id"
                        mock_orbits.create = AsyncMock(return_value=mock_orbit)
                        
                        # Mock Close_approaches
                        with patch('services.calculation.app.worker.Close_approaches') as mock_close_approaches:
                            mock_close_approach = AsyncMock()
                            mock_close_approach.id = "test_ca_id"
                            mock_close_approaches.create = AsyncMock(return_value=mock_close_approach)
                            
                            # Mock xadd
                            mock_redis_client.xadd = AsyncMock()
                            
                            # Call the function
                            await process_single_task("input_queue", None)
                            
                            # Assertions
                            mock_redis_client.xread.assert_called_once_with(
                                {"input_queue": "$"},
                                count=1,
                                block=1000
                            )
                            mock_calculation_task.get_or_none.assert_called_once_with(uuid="test_task_id")
                            mock_process_task.assert_called_once()
                            mock_redis_client.xadd.assert_called_once_with(
                                "result_queue",
                                {
                                    "task_id": "test_task_id",
                                    "status": "completed",
                                    "user_id": "test_user_id",
                                    "result": json.dumps({
                                        "orbit": {
                                            "semi_major_axis": 2.5,
                                            "eccentricity": 0.1,
                                            "inclination": 5.0,
                                            "longitude_ascending_node": 45.0,
                                            "argument_periapsis": 30.0,
                                            "periapsis_time": mock_process_task.return_value["result"]["orbit"]["periapsis_time"]
                                        },
                                        "closest_approach": mock_process_task.return_value["result"]["closest_approach"]
                                    }),
                                    "error": "",
                                    "timestamp": mock.ANY
                                }
                            )


@pytest.mark.asyncio
async def test_run_worker_exception_handling():
    """Test worker handles exceptions gracefully."""
    # Mock the init function
    with patch('services.calculation.app.worker.init') as mock_init:
        # Mock redis_client to raise an exception
        with patch('services.calculation.app.worker.redis_client') as mock_redis_client:
            mock_redis_client.xread.side_effect = Exception("Redis error")
            
            # Mock asyncio.sleep
            with patch('services.calculation.app.worker.asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
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
                assert mock_redis_client.xread.call_count >= 2
                assert mock_sleep.call_count >= 2
