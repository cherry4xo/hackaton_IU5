import pytest
from unittest.mock import Mock, patch, MagicMock, call
import io
from PIL import Image
import logging

from app.utils.minio_client import MinIOClient, get_minio_client


@pytest.fixture
def mock_minio_client():
    """Create a mock MinIO client."""
    with patch('app.utils.minio_client.Minio') as mock_minio_class:
        mock_client_instance = Mock()
        mock_minio_class.return_value = mock_client_instance
        client = MinIOClient()
        yield client, mock_client_instance


def test_minio_client_initialization():
    """Test MinIOClient initialization."""
    with patch('app.utils.minio_client.Minio') as mock_minio_class:
        mock_client_instance = Mock()
        mock_minio_class.return_value = mock_client_instance
        
        # Mock settings
        with patch('app.utils.minio_client.MINIO_ENDPOINT', 'test-endpoint'), \
             patch('app.utils.minio_client.MINIO_ACCESS_KEY', 'test-access-key'), \
             patch('app.utils.minio_client.MINIO_SECRET_KEY', 'test-secret-key'), \
             patch('app.utils.minio_client.MINIO_SECURE', True), \
             patch('app.utils.minio_client.MINIO_BUCKET_NAME', 'test-bucket'):
            
            client = MinIOClient()
            
            # Verify Minio was called with correct parameters
            mock_minio_class.assert_called_once_with(
                'test-endpoint',
                access_key='test-access-key',
                secret_key='test-secret-key',
                secure=True
            )
            
            # Verify bucket name is set correctly
            assert client.bucket_name == 'test-bucket'


def test_ensure_bucket_exists_when_not_exists(caplog):
    """Test _ensure_bucket_exists when bucket doesn't exist."""
    with patch('app.utils.minio_client.Minio') as mock_minio_class:
        mock_client_instance = Mock()
        mock_minio_class.return_value = mock_client_instance
        
        # Configure mock to return False for bucket_exists
        mock_client_instance.bucket_exists.return_value = False
        
        with patch('app.utils.minio_client.MINIO_BUCKET_NAME', 'test-bucket'), \
             caplog.at_level(logging.INFO):
            client = MinIOClient()
            
            # Verify make_bucket was called
            mock_client_instance.make_bucket.assert_called_once_with('test-bucket')
            
            # Verify log message
            assert "Created MinIO bucket: test-bucket" in caplog.text


def test_ensure_bucket_exists_when_already_exists(caplog):
    """Test _ensure_bucket_exists when bucket already exists."""
    with patch('app.utils.minio_client.Minio') as mock_minio_class:
        mock_client_instance = Mock()
        mock_minio_class.return_value = mock_client_instance
        
        # Configure mock to return True for bucket_exists
        mock_client_instance.bucket_exists.return_value = True
        
        with patch('app.utils.minio_client.MINIO_BUCKET_NAME', 'test-bucket'), \
             caplog.at_level(logging.INFO):
            client = MinIOClient()
            
            # Verify make_bucket was not called
            mock_client_instance.make_bucket.assert_not_called()
            
            # Verify log message
            assert "MinIO bucket already exists: test-bucket" in caplog.text


def test_ensure_bucket_exists_error(caplog):
    """Test _ensure_bucket_exists when an error occurs."""
    with patch('app.utils.minio_client.Minio') as mock_minio_class:
        mock_client_instance = Mock()
        mock_minio_class.return_value = mock_client_instance
        
        # Configure mock to raise an exception
        from minio.error import S3Error
        mock_client_instance.bucket_exists.side_effect = S3Error(
            code='TestError',
            message='Test error message',
            resource='test-resource',
            request_id='test-request-id',
            host_id='test-host-id',
            response=None
        )
        
        with patch('app.utils.minio_client.MINIO_BUCKET_NAME', 'test-bucket'), \
             caplog.at_level(logging.ERROR):
            with pytest.raises(S3Error):
                MinIOClient()
            
            # Verify log message
            assert "Error ensuring bucket exists" in caplog.text


def test_upload_image_success(mock_minio_client):
    """Test successful image upload."""
    client, mock_client_instance = mock_minio_client
    
    # Create sample image data
    image_array = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    image = Image.fromarray(image_array)
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG')
    image_data = img_byte_arr.getvalue()
    
    # Configure mocks
    with patch('app.utils.minio_client.MINIO_BUCKET_NAME', 'test-bucket'), \
         patch('app.utils.minio_client.MINIO_ENDPOINT', 'test-endpoint'), \
         patch('app.utils.minio_client.MINIO_SECURE', True):
        url = client.upload_image(image_data, 'test-image.jpg', 'image/jpeg')
    
    # Assertions
    assert url == 'https://test-endpoint/test-bucket/test-image.jpg'
    
    # Verify put_object was called with correct parameters
    mock_client_instance.put_object.assert_called_once()
    call_args = mock_client_instance.put_object.call_args
    assert call_args[0][0] == 'test-bucket'
    assert call_args[0][1] == 'test-image.jpg'
    assert call_args[0][3] == len(image_data)
    assert call_args[1]['content_type'] == 'image/jpeg'


def test_upload_image_http_endpoint(mock_minio_client):
    """Test image upload with HTTP endpoint."""
    client, mock_client_instance = mock_minio_client
    
    # Create sample image data
    image_data = b'test image data'
    
    # Configure mocks for HTTP (not HTTPS)
    with patch('app.utils.minio_client.MINIO_BUCKET_NAME', 'test-bucket'), \
         patch('app.utils.minio_client.MINIO_ENDPOINT', 'test-endpoint'), \
         patch('app.utils.minio_client.MINIO_SECURE', False):
        url = client.upload_image(image_data, 'test-image.jpg')
    
    # Assertions
    assert url == 'http://test-endpoint/test-bucket/test-image.jpg'


def test_upload_image_error(mock_minio_client, caplog):
    """Test image upload when an error occurs."""
    client, mock_client_instance = mock_minio_client
    
    # Create sample image data
    image_data = b'test image data'
    
    # Configure mock to raise an exception
    from minio.error import S3Error
    mock_client_instance.put_object.side_effect = S3Error(
        code='TestError',
        message='Test error message',
        resource='test-resource',
        request_id='test-request-id',
        host_id='test-host-id',
        response=None
    )
    
    with patch('app.utils.minio_client.MINIO_BUCKET_NAME', 'test-bucket'), \
         caplog.at_level(logging.ERROR):
        with pytest.raises(S3Error):
            client.upload_image(image_data, 'test-image.jpg')
        
        # Verify log message
        assert "Error uploading image" in caplog.text


def test_download_image_success(mock_minio_client):
    """Test successful image download."""
    client, mock_client_instance = mock_minio_client
    
    # Create sample image data
    image_data = b'test image data'
    
    # Create a mock response object
    mock_response = Mock()
    mock_response.read.return_value = image_data
    mock_response.close = Mock()
    mock_response.release_conn = Mock()
    
    # Configure mock
    mock_client_instance.get_object.return_value = mock_response
    
    with patch('app.utils.minio_client.MINIO_BUCKET_NAME', 'test-bucket'):
        result = client.download_image('test-image.jpg')
    
    # Assertions
    assert result == image_data
    mock_client_instance.get_object.assert_called_once_with('test-bucket', 'test-image.jpg')
    mock_response.close.assert_called_once()
    mock_response.release_conn.assert_called_once()


def test_download_image_error(mock_minio_client, caplog):
    """Test image download when an error occurs."""
    client, mock_client_instance = mock_minio_client
    
    # Configure mock to raise an exception
    from minio.error import S3Error
    mock_client_instance.get_object.side_effect = S3Error(
        code='TestError',
        message='Test error message',
        resource='test-resource',
        request_id='test-request-id',
        host_id='test-host-id',
        response=None
    )
    
    with patch('app.utils.minio_client.MINIO_BUCKET_NAME', 'test-bucket'), \
         caplog.at_level(logging.ERROR):
        with pytest.raises(S3Error):
            client.download_image('test-image.jpg')
        
        # Verify log message
        assert "Error downloading image" in caplog.text


def test_get_image_info_success(mock_minio_client):
    """Test successful image info retrieval."""
    client, mock_client_instance = mock_minio_client
    
    # Create a mock stat object
    mock_stat = Mock()
    mock_stat.size = 1024
    mock_stat.last_modified = '2025-01-01T12:00:00Z'
    mock_stat.etag = 'test-etag'
    mock_stat.content_type = 'image/jpeg'
    
    # Configure mock
    mock_client_instance.stat_object.return_value = mock_stat
    
    with patch('app.utils.minio_client.MINIO_BUCKET_NAME', 'test-bucket'):
        result = client.get_image_info('test-image.jpg')
    
    # Assertions
    assert isinstance(result, dict)
    assert result['name'] == 'test-image.jpg'
    assert result['size'] == 1024
    assert result['last_modified'] == '2025-01-01T12:00:00Z'
    assert result['etag'] == 'test-etag'
    assert result['content_type'] == 'image/jpeg'
    
    mock_client_instance.stat_object.assert_called_once_with('test-bucket', 'test-image.jpg')


def test_get_image_info_error(mock_minio_client, caplog):
    """Test image info retrieval when an error occurs."""
    client, mock_client_instance = mock_minio_client
    
    # Configure mock to raise an exception
    from minio.error import S3Error
    mock_client_instance.stat_object.side_effect = S3Error(
        code='TestError',
        message='Test error message',
        resource='test-resource',
        request_id='test-request-id',
        host_id='test-host-id',
        response=None
    )
    
    with patch('app.utils.minio_client.MINIO_BUCKET_NAME', 'test-bucket'), \
         caplog.at_level(logging.ERROR):
        with pytest.raises(S3Error):
            client.get_image_info('test-image.jpg')
        
        # Verify log message
        assert "Error getting image info" in caplog.text


def test_delete_image_success(mock_minio_client, caplog):
    """Test successful image deletion."""
    client, mock_client_instance = mock_minio_client
    
    with patch('app.utils.minio_client.MINIO_BUCKET_NAME', 'test-bucket'), \
         caplog.at_level(logging.INFO):
        result = client.delete_image('test-image.jpg')
    
    # Assertions
    assert result is True
    mock_client_instance.remove_object.assert_called_once_with('test-bucket', 'test-image.jpg')
    assert "Successfully deleted image: test-image.jpg" in caplog.text


def test_delete_image_error(mock_minio_client, caplog):
    """Test image deletion when an error occurs."""
    client, mock_client_instance = mock_minio_client
    
    # Configure mock to raise an exception
    from minio.error import S3Error
    mock_client_instance.remove_object.side_effect = S3Error(
        code='TestError',
        message='Test error message',
        resource='test-resource',
        request_id='test-request-id',
        host_id='test-host-id',
        response=None
    )
    
    with patch('app.utils.minio_client.MINIO_BUCKET_NAME', 'test-bucket'), \
         caplog.at_level(logging.ERROR):
        with pytest.raises(S3Error):
            client.delete_image('test-image.jpg')
        
        # Verify log message
        assert "Error deleting image" in caplog.text


def test_get_minio_client_singleton():
    """Test that get_minio_client returns the same instance."""
    # Reset the global instance
    import app.utils.minio_client
    app.utils.minio_client.minio_client = None
    
    # Patch Minio class to avoid actual initialization
    with patch('app.utils.minio_client.Minio'):
        with patch('app.utils.minio_client.MINIO_ENDPOINT', 'test-endpoint'), \
             patch('app.utils.minio_client.MINIO_ACCESS_KEY', 'test-access-key'), \
             patch('app.utils.minio_client.MINIO_SECRET_KEY', 'test-secret-key'), \
             patch('app.utils.minio_client.MINIO_SECURE', True), \
             patch('app.utils.minio_client.MINIO_BUCKET_NAME', 'test-bucket'):
            
            # Get two instances
            client1 = get_minio_client()
            client2 = get_minio_client()
            
            # Assertions
            assert client1 is client2
            assert isinstance(client1, MinIOClient)
