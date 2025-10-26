import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch, MagicMock
import uuid

from services.calculation.app.calculator import process_task


@pytest.mark.asyncio
async def test_process_task_success():
    """Test successful orbit calculation task processing"""
    # Arrange
    task_data = {
        "task_id": str(uuid.uuid4()),
        "observations": [
            {
                "observation_time": datetime(2025, 1, 1, 12, 0, 0).isoformat(),
                "ra": 100.0,
                "dec": 10.0
            },
            {
                "observation_time": datetime(2025, 1, 2, 12, 0, 0).isoformat(),
                "ra": 101.0,
                "dec": 10.5
            },
            {
                "observation_time": datetime(2025, 1, 3, 12, 0, 0).isoformat(),
                "ra": 102.0,
                "dec": 11.0
            }
        ],
        "options": {
            "start_time": datetime(2025, 1, 1, 0, 0, 0).isoformat(),
            "end_time": datetime(2026, 1, 1, 0, 0, 0).isoformat(),
            "time_steps": 500
        }
    }

    # Mock the OrbitCalculator
    with patch('app.calculator.OrbitCalculator') as mock_orbit_calculator:
        mock_calculator_instance = Mock()
        mock_calculator_instance.calculate_orbit.return_value = {
            "semi_major_axis": 2.5,
            "eccentricity": 0.1,
            "inclination": 5.0,
            "longitude_ascending_node": 45.0,
            "argument_periapsis": 30.0,
            "periapsis_time": datetime(2025, 1, 15, 12, 0, 0)
        }
        mock_calculator_instance.calculate_closest_approach.return_value = {
            "time": datetime(2025, 6, 15, 12, 0, 0),
            "distance_au": 1.2,
            "distance_km": 179517444.0
        }
        mock_orbit_calculator.return_value = mock_calculator_instance

        # Mock the image processor
        with patch('app.calculator.get_image_processor') as mock_get_image_processor:
            mock_image_processor = Mock()
            mock_get_image_processor.return_value = mock_image_processor

            # Act
            result = await process_task(task_data)

            # Assert
            assert result["status"] == "completed"
            assert result["task_id"] == task_data["task_id"]
            assert "result" in result
            assert "orbit" in result["result"]
            assert "closest_approach" in result["result"]
            assert result["error"] is None

            # Verify orbit calculation was called with correct data
            mock_calculator_instance.calculate_orbit.assert_called_once_with(task_data["observations"])

            # Verify closest approach calculation was called with correct data
            mock_calculator_instance.calculate_closest_approach.assert_called_once()
            call_args = mock_calculator_instance.calculate_closest_approach.call_args
            assert call_args[1]["orbit_elements"] == mock_calculator_instance.calculate_orbit.return_value
            assert call_args[1]["start_time"] == datetime.fromisoformat(task_data["options"]["start_time"])
            assert call_args[1]["end_time"] == datetime.fromisoformat(task_data["options"]["end_time"])
            assert call_args[1]["time_steps"] == task_data["options"]["time_steps"]


@pytest.mark.asyncio
async def test_process_task_with_image_references():
    """Test orbit calculation with image references in observations"""
    # Arrange
    task_data = {
        "task_id": str(uuid.uuid4()),
        "observations": [
            {
                "observation_time": datetime(2025, 1, 1, 12, 0, 0).isoformat(),
                "ra": 100.0,
                "dec": 10.0,
                "image_reference": "observation_images/test1.jpg"
            },
            {
                "observation_time": datetime(2025, 1, 2, 12, 0, 0).isoformat(),
                "ra": 101.0,
                "dec": 10.5
                # No image reference
            },
            {
                "observation_time": datetime(2025, 1, 3, 12, 0, 0).isoformat(),
                "ra": 102.0,
                "dec": 11.0,
                "image_reference": "observation_images/test3.jpg"
            }
        ],
        "options": {}
    }

    # Mock the OrbitCalculator
    with patch('app.calculator.OrbitCalculator') as mock_orbit_calculator:
        mock_calculator_instance = Mock()
        mock_calculator_instance.calculate_orbit.return_value = {
            "semi_major_axis": 2.5,
            "eccentricity": 0.1,
            "inclination": 5.0,
            "longitude_ascending_node": 45.0,
            "argument_periapsis": 30.0,
            "periapsis_time": datetime(2025, 1, 15, 12, 0, 0)
        }
        mock_calculator_instance.calculate_closest_approach.return_value = {
            "time": datetime(2025, 6, 15, 12, 0, 0),
            "distance_au": 1.2,
            "distance_km": 179517444.0
        }
        mock_orbit_calculator.return_value = mock_calculator_instance

        # Mock the image processor
        with patch('app.calculator.get_image_processor') as mock_get_image_processor:
            mock_image_processor = Mock()
            # Configure mock to return specific coordinates for image references
            mock_image_processor.extract_coordinates_from_image.side_effect = [
                (150.0, -20.0),  # Coordinates for first image
                (152.0, -19.0)   # Coordinates for third image
            ]
            mock_get_image_processor.return_value = mock_image_processor

            # Act
            result = await process_task(task_data)

            # Assert
            assert result["status"] == "completed"
            assert result["task_id"] == task_data["task_id"]

            # Verify image processor was called for observations with image references
            assert mock_image_processor.extract_coordinates_from_image.call_count == 2
            mock_image_processor.extract_coordinates_from_image.assert_any_call("observation_images/test1.jpg")
            mock_image_processor.extract_coordinates_from_image.assert_any_call("observation_images/test3.jpg")

            # Verify orbit calculation was called with processed observations
            # The observations should have updated RA/Dec values for those with image references
            processed_observations = mock_calculator_instance.calculate_orbit.call_args[0][0]
            assert len(processed_observations) == 3
            
            # First observation should have updated coordinates from image
            assert processed_observations[0]["ra"] == 150.0
            assert processed_observations[0]["dec"] == -20.0
            assert processed_observations[0]["image_reference"] == "observation_images/test1.jpg"
            
            # Second observation should remain unchanged (no image reference)
            assert processed_observations[1]["ra"] == 101.0
            assert processed_observations[1]["dec"] == 10.5
            assert "image_reference" not in processed_observations[1]
            
            # Third observation should have updated coordinates from image
            assert processed_observations[2]["ra"] == 152.0
            assert processed_observations[2]["dec"] == -19.0
            assert processed_observations[2]["image_reference"] == "observation_images/test3.jpg"


@pytest.mark.asyncio
async def test_process_task_image_processing_failure():
    """Test orbit calculation when image processing fails"""
    # Arrange
    task_data = {
        "task_id": str(uuid.uuid4()),
        "observations": [
            {
                "observation_time": datetime(2025, 1, 1, 12, 0, 0).isoformat(),
                "ra": 100.0,
                "dec": 10.0,
                "image_reference": "observation_images/test1.jpg"
            },
            {
                "observation_time": datetime(2025, 1, 2, 12, 0, 0).isoformat(),
                "ra": 101.0,
                "dec": 10.5,
                "image_reference": "observation_images/test2.jpg"
            }
        ],
        "options": {}
    }

    # Mock the OrbitCalculator
    with patch('app.calculator.OrbitCalculator') as mock_orbit_calculator:
        mock_calculator_instance = Mock()
        mock_calculator_instance.calculate_orbit.return_value = {
            "semi_major_axis": 2.5,
            "eccentricity": 0.1,
            "inclination": 5.0,
            "longitude_ascending_node": 45.0,
            "argument_periapsis": 30.0,
            "periapsis_time": datetime(2025, 1, 15, 12, 0, 0)
        }
        mock_calculator_instance.calculate_closest_approach.return_value = {
            "time": datetime(2025, 6, 15, 12, 0, 0),
            "distance_au": 1.2,
            "distance_km": 179517444.0
        }
        mock_orbit_calculator.return_value = mock_calculator_instance

        # Mock the image processor with one failing extraction
        with patch('app.calculator.get_image_processor') as mock_get_image_processor:
            mock_image_processor = Mock()
            # Configure mock to raise an exception for the first image and return coordinates for the second
            mock_image_processor.extract_coordinates_from_image.side_effect = [
                Exception("Image processing error"),  # Failure for first image
                (152.0, -19.0)   # Success for second image
            ]
            mock_get_image_processor.return_value = mock_image_processor

            # Act
            result = await process_task(task_data)

            # Assert
            assert result["status"] == "completed"
            assert result["task_id"] == task_data["task_id"]

            # Verify orbit calculation was called with observations
            # The first observation should retain original coordinates due to processing failure
            # The second observation should have updated coordinates
            processed_observations = mock_calculator_instance.calculate_orbit.call_args[0][0]
            assert len(processed_observations) == 2
            
            # First observation should retain original coordinates due to processing failure
            assert processed_observations[0]["ra"] == 100.0
            assert processed_observations[0]["dec"] == 10.0
            assert processed_observations[0]["image_reference"] == "observation_images/test1.jpg"
            
            # Second observation should have updated coordinates from image
            assert processed_observations[1]["ra"] == 152.0
            assert processed_observations[1]["dec"] == -19.0
            assert processed_observations[1]["image_reference"] == "observation_images/test2.jpg"


@pytest.mark.asyncio
async def test_process_task_orbit_calculation_failure():
    """Test task processing when orbit calculation fails"""
    # Arrange
    task_data = {
        "task_id": str(uuid.uuid4()),
        "observations": [
            {
                "observation_time": datetime(2025, 1, 1, 12, 0, 0).isoformat(),
                "ra": 100.0,
                "dec": 10.0
            },
            {
                "observation_time": datetime(2025, 1, 2, 12, 0, 0).isoformat(),
                "ra": 101.0,
                "dec": 10.5
            },
            {
                "observation_time": datetime(2025, 1, 3, 12, 0, 0).isoformat(),
                "ra": 102.0,
                "dec": 11.0
            }
        ],
        "options": {}
    }

    # Mock the OrbitCalculator to raise an exception
    with patch('app.calculator.OrbitCalculator') as mock_orbit_calculator:
        mock_calculator_instance = Mock()
        mock_calculator_instance.calculate_orbit.side_effect = Exception("Orbit calculation error")
        mock_orbit_calculator.return_value = mock_calculator_instance

        # Mock the image processor
        with patch('app.calculator.get_image_processor') as mock_get_image_processor:
            mock_image_processor = Mock()
            mock_get_image_processor.return_value = mock_image_processor

            # Act
            result = await process_task(task_data)

            # Assert
            assert result["status"] == "failed"
            assert result["task_id"] == task_data["task_id"]
            assert result["result"] is None
            assert "Orbit calculation error" in result["error"]

            # Verify orbit calculation was attempted
            mock_calculator_instance.calculate_orbit.assert_called_once_with(task_data["observations"])


@pytest.mark.asyncio
async def test_process_task_closest_approach_failure():
    """Test task processing when closest approach calculation fails"""
    # Arrange
    task_data = {
        "task_id": str(uuid.uuid4()),
        "observations": [
            {
                "observation_time": datetime(2025, 1, 1, 12, 0, 0).isoformat(),
                "ra": 100.0,
                "dec": 10.0
            },
            {
                "observation_time": datetime(2025, 1, 2, 12, 0, 0).isoformat(),
                "ra": 101.0,
                "dec": 10.5
            },
            {
                "observation_time": datetime(2025, 1, 3, 12, 0, 0).isoformat(),
                "ra": 102.0,
                "dec": 11.0
            }
        ],
        "options": {}
    }

    # Mock the OrbitCalculator
    with patch('app.calculator.OrbitCalculator') as mock_orbit_calculator:
        mock_calculator_instance = Mock()
        mock_calculator_instance.calculate_orbit.return_value = {
            "semi_major_axis": 2.5,
            "eccentricity": 0.1,
            "inclination": 5.0,
            "longitude_ascending_node": 45.0,
            "argument_periapsis": 30.0,
            "periapsis_time": datetime(2025, 1, 15, 12, 0, 0)
        }
        mock_calculator_instance.calculate_closest_approach.side_effect = Exception("Closest approach error")
        mock_orbit_calculator.return_value = mock_calculator_instance

        # Mock the image processor
        with patch('app.calculator.get_image_processor') as mock_get_image_processor:
            mock_image_processor = Mock()
            mock_get_image_processor.return_value = mock_image_processor

            # Act
            result = await process_task(task_data)

            # Assert
            assert result["status"] == "failed"
            assert result["task_id"] == task_data["task_id"]
            assert result["result"] is None
            assert "Closest approach error" in result["error"]

            # Verify orbit calculation was called
            mock_calculator_instance.calculate_orbit.assert_called_once_with(task_data["observations"])
            
            # Verify closest approach calculation was attempted
            mock_calculator_instance.calculate_closest_approach.assert_called_once()


@pytest.mark.asyncio
async def test_process_task_default_options():
    """Test orbit calculation with default options"""
    # Arrange
    task_data = {
        "task_id": str(uuid.uuid4()),
        "observations": [
            {
                "observation_time": datetime(2025, 1, 1, 12, 0, 0).isoformat(),
                "ra": 100.0,
                "dec": 10.0
            },
            {
                "observation_time": datetime(2025, 1, 2, 12, 0, 0).isoformat(),
                "ra": 101.0,
                "dec": 10.5
            },
            {
                "observation_time": datetime(2025, 1, 3, 12, 0, 0).isoformat(),
                "ra": 102.0,
                "dec": 11.0
            }
        ]
        # No options provided - should use defaults
    }

    # Mock the OrbitCalculator
    with patch('app.calculator.OrbitCalculator') as mock_orbit_calculator:
        mock_calculator_instance = Mock()
        mock_calculator_instance.calculate_orbit.return_value = {
            "semi_major_axis": 2.5,
            "eccentricity": 0.1,
            "inclination": 5.0,
            "longitude_ascending_node": 45.0,
            "argument_periapsis": 30.0,
            "periapsis_time": datetime(2025, 1, 15, 12, 0, 0)
        }
        mock_calculator_instance.calculate_closest_approach.return_value = {
            "time": datetime(2025, 6, 15, 12, 0, 0),
            "distance_au": 1.2,
            "distance_km": 179517444.0
        }
        mock_orbit_calculator.return_value = mock_calculator_instance

        # Mock the image processor
        with patch('app.calculator.get_image_processor') as mock_get_image_processor:
            mock_image_processor = Mock()
            mock_get_image_processor.return_value = mock_image_processor

            # Act
            result = await process_task(task_data)

            # Assert
            assert result["status"] == "completed"
            
            # Verify closest approach calculation was called with default options
            mock_calculator_instance.calculate_closest_approach.assert_called_once()
            call_args = mock_calculator_instance.calculate_closest_approach.call_args
            # Check that default values were used
            assert call_args[1]["time_steps"] == 1000
            # start_time should be current time (approximately)
            # end_time should be one year from start_time
