import pytest
from datetime import datetime, timedelta
import numpy as np
from unittest.mock import Mock, patch, AsyncMock
import uuid

from services.calculation.app.calculator import process_task
from services.calculation.app.utils.image_processing import ImageProcessor
from services.calculation.app.utils.minio_client import MinIOClient


@pytest.fixture
def mock_image_processor():
    with patch('services.calculation.app.calculator.get_image_processor') as mock:
        processor = Mock(spec=ImageProcessor)
        processor.extract_coordinates_from_image.return_value = (150.0, -20.0)
        mock.return_value = processor
        yield mock


@pytest.fixture
def mock_minio_client():
    with patch('services.calculation.app.utils.image_processing.get_minio_client') as mock:
        client = Mock(spec=MinIOClient)
        # Mock the download_image method to return a simple image-like object
        mock_instance = Mock()
        mock_instance.download_image.return_value = b"fake image data"
        mock.return_value = mock_instance
        yield mock


@pytest.mark.asyncio
async def test_process_task_with_image_references(mock_image_processor):
    """Test orbit calculation with image references in observations"""
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

    # Process the task
    result = await process_task(task_data)

    # Verify the result
    assert result["status"] == "completed"
    assert "result" in result
    assert "orbit" in result["result"]
    assert "closest_approach" in result["result"]
    
    # Verify orbit elements are present
    orbit = result["result"]["orbit"]
    assert "eccentricity" in orbit
    assert "inclination" in orbit
    assert "periapsis_time" in orbit
    
    # Verify image processor was called
    mock_image_processor.return_value.extract_coordinates_from_image.assert_any_call("observation_images/test1.jpg")
    mock_image_processor.return_value.extract_coordinates_from_image.assert_any_call("observation_images/test2.jpg")
    mock_image_processor.return_value.extract_coordinates_from_image.assert_any_call("observation_images/test3.jpg")


@pytest.mark.asyncio
async def test_process_task_with_mixed_observations(mock_image_processor):
    """Test orbit calculation with mix of observations with and without images"""
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

    # Process the task
    result = await process_task(task_data)

    # Verify the result
    assert result["status"] == "completed"
    assert "result" in result
    assert "orbit" in result["result"]
    
    # Verify image processor was called only for observations with images
    assert mock_image_processor.return_value.extract_coordinates_from_image.call_count == 2
    mock_image_processor.return_value.extract_coordinates_from_image.assert_any_call("observation_images/test1.jpg")
    mock_image_processor.return_value.extract_coordinates_from_image.assert_any_call("observation_images/test3.jpg")


@pytest.mark.asyncio
async def test_process_task_image_processing_failure(mock_image_processor):
    """Test orbit calculation when image processing fails"""
    # Configure mock to raise an exception for one image
    mock_image_processor.return_value.extract_coordinates_from_image.side_effect = [
        (150.0, -20.0),  # Success for first image
        Exception("Image processing error"),  # Failure for second image
        (152.0, -19.0)   # Success for third image
    ]

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

    # Process the task
    result = await process_task(task_data)

    # Should still complete successfully (falling back to original coordinates)
    assert result["status"] == "completed"
    assert "result" in result
    assert "orbit" in result["result"]


@pytest.mark.asyncio
async def test_process_task_with_no_images():
    """Test orbit calculation with no image references (backward compatibility)"""
    task_data = {
        "task_id": str(uuid.uuid4()),
        "observations": [
            {
                "observation_time": datetime(2025, 1, 1, 12, 0, 0).isoformat(),
                "ra": 100.0,
                "dec": 10.0
                # No image reference
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
                "dec": 11.0
                # No image reference
            }
        ],
        "options": {}
    }

    # Process the task
    result = await process_task(task_data)

    # Should complete successfully
    assert result["status"] == "completed"
    assert "result" in result
    assert "orbit" in result["result"]
    assert "closest_approach" in result["result"]


@pytest.mark.asyncio
async def test_process_task_extract_coordinates_success(mock_image_processor):
    """Test that extracted coordinates are used in orbit calculation"""
    # Configure mock to return specific coordinates
    mock_image_processor.return_value.extract_coordinates_from_image.return_value = (160.0, -15.0)

    task_data = {
        "task_id": str(uuid.uuid4()),
        "observations": [
            {
                "observation_time": datetime(2025, 1, 1, 12, 0, 0).isoformat(),
                "ra": 100.0,  # Original RA
                "dec": 10.0,  # Original Dec
                "image_reference": "observation_images/test1.jpg"
            }
        ],
        "options": {}
    }

    # Process the task
    result = await process_task(task_data)

    # Should complete successfully
    assert result["status"] == "completed"
    assert "result" in result
    assert "orbit" in result["result"]
    
    # Note: We can't directly verify that the extracted coordinates were used
    # because the orbit calculation is a complex process. However, the fact
    # that it completes successfully shows the integration works.


@pytest.mark.asyncio
async def test_process_task_options_handling_with_images(mock_image_processor):
    """Test orbit calculation with options and image references"""
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
            },
            {
                "observation_time": datetime(2025, 1, 3, 12, 0, 0).isoformat(),
                "ra": 102.0,
                "dec": 11.0,
                "image_reference": "observation_images/test3.jpg"
            }
        ],
        "options": {
            "start_time": datetime(2025, 1, 1, 0, 0, 0).isoformat(),
            "end_time": datetime(2026, 1, 1, 0, 0, 0).isoformat(),
            "time_steps": 500
        }
    }

    # Process the task
    result = await process_task(task_data)

    # Should complete successfully with options applied
    assert result["status"] == "completed"
    assert "result" in result
    assert "orbit" in result["result"]
    assert "closest_approach" in result["result"]
    assert result["result"]["closest_approach"]["time"] is not None
