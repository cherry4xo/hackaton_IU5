import io
from minio import Minio
from minio.error import S3Error
from PIL import Image
import logging
from typing import Optional, Tuple
from app.settings import MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_BUCKET_NAME, MINIO_SECURE

logger = logging.getLogger(__name__)

class MinIOClient:
    def __init__(self):
        self.client = Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=MINIO_SECURE
        )
        self.bucket_name = MINIO_BUCKET_NAME
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Ensure the bucket exists, creating it if necessary."""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Created MinIO bucket: {self.bucket_name}")
            else:
                logger.info(f"MinIO bucket already exists: {self.bucket_name}")
        except S3Error as e:
            logger.error(f"Error ensuring bucket exists: {e}")
            raise
    
    def upload_image(self, image_data: bytes, object_name: str, content_type: str = "image/jpeg") -> str:
        """
        Upload an image to MinIO.
        
        Args:
            image_data: The image data as bytes
            object_name: The name to store the object under
            content_type: The MIME type of the image
            
        Returns:
            The URL of the uploaded image
        """
        try:
            # Upload the image
            self.client.put_object(
                self.bucket_name,
                object_name,
                io.BytesIO(image_data),
                length=len(image_data),
                content_type=content_type
            )
            
            # Generate and return the URL
            url = f"{'https' if MINIO_SECURE else 'http'}://{MINIO_ENDPOINT}/{self.bucket_name}/{object_name}"
            logger.info(f"Successfully uploaded image: {object_name}")
            return url
        except S3Error as e:
            logger.error(f"Error uploading image: {e}")
            raise
    
    def download_image(self, object_name: str) -> bytes:
        """
        Download an image from MinIO.
        
        Args:
            object_name: The name of the object to download
            
        Returns:
            The image data as bytes
        """
        try:
            response = self.client.get_object(self.bucket_name, object_name)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            logger.error(f"Error downloading image: {e}")
            raise
    
    def get_image_info(self, object_name: str) -> dict:
        """
        Get information about an image stored in MinIO.
        
        Args:
            object_name: The name of the object
            
        Returns:
            Dictionary with image information
        """
        try:
            stat = self.client.stat_object(self.bucket_name, object_name)
            return {
                "name": object_name,
                "size": stat.size,
                "last_modified": stat.last_modified,
                "etag": stat.etag,
                "content_type": stat.content_type
            }
        except S3Error as e:
            logger.error(f"Error getting image info: {e}")
            raise
    
    def delete_image(self, object_name: str) -> bool:
        """
        Delete an image from MinIO.
        
        Args:
            object_name: The name of the object to delete
            
        Returns:
            True if deletion was successful
        """
        try:
            self.client.remove_object(self.bucket_name, object_name)
            logger.info(f"Successfully deleted image: {object_name}")
            return True
        except S3Error as e:
            logger.error(f"Error deleting image: {e}")
            raise

# Global instance of the MinIO client
minio_client: Optional[MinIOClient] = None

def get_minio_client() -> MinIOClient:
    """Get or create the global MinIO client instance."""
    global minio_client
    if minio_client is None:
        minio_client = MinIOClient()
    return minio_client
