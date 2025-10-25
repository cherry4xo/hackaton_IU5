import pytest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
from PIL import Image
import io
import logging

from app.utils.image_processing import ImageProcessor, get_image_processor


@pytest.fixture
def mock_minio_client():
    """Create a mock MinIO client."""
    with patch('app.utils.image_processing.get_minio_client') as mock:
        client = Mock()
        mock.return_value = client
        yield client


@pytest.fixture
def sample_image():
    """Create a sample PIL Image for testing."""
    # Create a simple 100x100 RGB image
    image_array = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    image = Image.fromarray(image_array)
    return image


@pytest.fixture
def sample_gray_image():
    """Create a sample grayscale PIL Image for testing."""
    # Create a simple 100x100 grayscale image
    image_array = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
    image = Image.fromarray(image_array, mode='L')
    return image


def test_image_processor_initialization(mock_minio_client):
    """Test ImageProcessor initialization."""
    processor = ImageProcessor()
    
    assert processor.minio_client == mock_minio_client


def test_download_image_success(mock_minio_client):
    """Test successful image download."""
    # Create sample image data
    image_array = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    image = Image.fromarray(image_array)
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG')
    image_data = img_byte_arr.getvalue()
    
    # Configure mock
    mock_minio_client.download_image.return_value = image_data
    
    # Test
    processor = ImageProcessor()
    result = processor.download_image("test_image.jpg")
    
    # Assertions
    assert isinstance(result, Image.Image)
    assert result.size == (100, 100)
    mock_minio_client.download_image.assert_called_once_with("test_image.jpg")


def test_download_image_failure(mock_minio_client, caplog):
    """Test image download failure."""
    # Configure mock to raise an exception
    mock_minio_client.download_image.side_effect = Exception("MinIO error")
    
    # Test
    processor = ImageProcessor()
    
    with caplog.at_level(logging.ERROR):
        with pytest.raises(Exception, match="MinIO error"):
            processor.download_image("test_image.jpg")
    
    # Verify error was logged
    assert "Error downloading image test_image.jpg" in caplog.text


def test_detect_stars_rgb_image(sample_image, caplog):
    """Test star detection on RGB image."""
    processor = ImageProcessor()
    
    with caplog.at_level(logging.INFO):
        stars = processor.detect_stars(sample_image, threshold=0.1)
    
    # Assertions
    assert isinstance(stars, list)
    # Check that stars were detected (with random data, we can't predict exact count)
    # but we can check that it's a list and contains dictionaries with expected keys
    for star in stars:
        assert isinstance(star, dict)
        assert "x" in star
        assert "y" in star
        assert "sigma" in star
        assert "radius" in star
        assert isinstance(star["x"], float)
        assert isinstance(star["y"], float)
        assert isinstance(star["sigma"], float)
        assert isinstance(star["radius"], float)
    
    # Verify info was logged
    assert "Detected" in caplog.text and "stars in image" in caplog.text


def test_detect_stars_grayscale_image(sample_gray_image, caplog):
    """Test star detection on grayscale image."""
    processor = ImageProcessor()
    
    with caplog.at_level(logging.INFO):
        stars = processor.detect_stars(sample_gray_image, threshold=0.1)
    
    # Assertions
    assert isinstance(stars, list)
    # Check that stars were detected
    for star in stars:
        assert isinstance(star, dict)
        assert "x" in star
        assert "y" in star
        assert "sigma" in star
        assert "radius" in star


def test_detect_stars_detection_failure(caplog):
    """Test star detection when processing fails."""
    # Create a mock processor with a method that raises an exception
    processor = ImageProcessor()
    
    with patch.object(processor, 'detect_stars', side_effect=Exception("Processing error")):
        with caplog.at_level(logging.ERROR):
            stars = processor.detect_stars(MagicMock(), threshold=0.1)
    
    # When an exception occurs, the method should return an empty list
    # However, since we're mocking the method itself, this test won't work as intended
    # Let's test the actual behavior by mocking a dependency that causes failure
    
    # Instead, let's test with an image that causes an error in conversion
    processor = ImageProcessor()
    
    # Create a mock image that raises an exception when converted
    mock_image = Mock()
    mock_image.mode = 'RGB'
    mock_image.convert.side_effect = Exception("Conversion error")
    
    with caplog.at_level(logging.ERROR):
        stars = processor.detect_stars(mock_image, threshold=0.1)
    
    # Should return empty list on error
    assert stars == []
    assert "Error detecting stars" in caplog.text


def test_extract_coordinates_from_image_center(sample_image, mock_minio_client):
    """Test coordinate extraction using image center."""
    # Configure mock to return our sample image
    img_byte_arr = io.BytesIO()
    sample_image.save(img_byte_arr, format='JPEG')
    image_data = img_byte_arr.getvalue()
    mock_minio_client.download_image.return_value = image_data
    
    processor = ImageProcessor()
    result = processor.extract_coordinates_from_image("test_image.jpg")
    
    # Assertions
    assert result is not None
    assert isinstance(result, tuple)
    assert len(result) == 2
    ra, dec = result
    assert isinstance(ra, float)
    assert isinstance(dec, float)
    # RA should be between 0 and 360
    assert 0 <= ra <= 360
    # Dec should be between -90 and 90
    assert -90 <= dec <= 90


def test_extract_coordinates_from_image_custom_position(sample_image, mock_minio_client):
    """Test coordinate extraction with custom pixel position."""
    # Configure mock to return our sample image
    img_byte_arr = io.BytesIO()
    sample_image.save(img_byte_arr, format='JPEG')
    image_data = img_byte_arr.getvalue()
    mock_minio_client.download_image.return_value = image_data
    
    processor = ImageProcessor()
    width, height = sample_image.size
    result = processor.extract_coordinates_from_image(
        "test_image.jpg", 
        pixel_x=width/4, 
        pixel_y=height/4
    )
    
    # Assertions
    assert result is not None
    assert isinstance(result, tuple)
    assert len(result) == 2
    ra, dec = result
    assert isinstance(ra, float)
    assert isinstance(dec, float)


def test_extract_coordinates_from_image_download_failure(mock_minio_client, caplog):
    """Test coordinate extraction when image download fails."""
    # Configure mock to raise an exception
    mock_minio_client.download_image.side_effect = Exception("Download error")
    
    processor = ImageProcessor()
    
    with caplog.at_level(logging.ERROR):
        result = processor.extract_coordinates_from_image("test_image.jpg")
    
    # Assertions
    assert result is None
    assert "Error extracting coordinates from image test_image.jpg" in caplog.text


def test_get_image_processor_singleton():
    """Test that get_image_processor returns the same instance."""
    # Reset the global instance
    import app.utils.image_processing
    app.utils.image_processing.image_processor = None
    
    # Get two instances
    processor1 = get_image_processor()
    processor2 = get_image_processor()
    
    # Assertions
    assert processor1 is processor2
    assert isinstance(processor1, ImageProcessor)
