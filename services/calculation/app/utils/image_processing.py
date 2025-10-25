import numpy as np
from PIL import Image
from skimage.feature import blob_log
from skimage.measure import regionprops
import logging
from typing import Optional, Tuple, Dict, List
from .minio_client import get_minio_client
import io

logger = logging.getLogger(__name__)

class ImageProcessor:
    """Basic image processor for astronomical images."""
    
    def __init__(self):
        self.minio_client = get_minio_client()
    
    def download_image(self, image_reference: str) -> Image.Image:
        """
        Download an image from MinIO storage.
        
        Args:
            image_reference: The MinIO object name
            
        Returns:
            PIL Image object
        """
        try:
            image_data = self.minio_client.download_image(image_reference)
            image = Image.open(io.BytesIO(image_data))
            return image
        except Exception as e:
            logger.error(f"Error downloading image {image_reference}: {e}")
            raise
    
    def detect_stars(self, image: Image.Image, threshold: float = 0.1) -> List[Dict]:
        """
        Detect stars in an astronomical image using Laplacian of Gaussian.
        
        Args:
            image: PIL Image object
            threshold: Detection threshold (0-1)
            
        Returns:
            List of detected star positions with properties
        """
        try:
            # Convert to grayscale if needed
            if image.mode != 'L':
                gray_image = image.convert('L')
            else:
                gray_image = image
            
            # Convert to numpy array
            img_array = np.array(gray_image)
            
            # Normalize to 0-1 range
            img_normalized = img_array.astype(float) / 255.0
            
            # Apply Laplacian of Gaussian blob detection
            blobs = blob_log(
                img_normalized,
                min_sigma=1,
                max_sigma=30,
                num_sigma=10,
                threshold=threshold
            )
            
            # Convert to list of dictionaries
            stars = []
            for blob in blobs:
                y, x, sigma = blob
                stars.append({
                    "x": float(x),
                    "y": float(y),
                    "sigma": float(sigma),
                    "radius": float(sigma * np.sqrt(2))
                })
            
            logger.info(f"Detected {len(stars)} stars in image")
            return stars
        except Exception as e:
            logger.error(f"Error detecting stars: {e}")
            return []
    
    def extract_coordinates_from_image(
        self, 
        image_reference: str,
        pixel_x: Optional[float] = None,
        pixel_y: Optional[float] = None
    ) -> Optional[Tuple[float, float]]:
        """
        Extract celestial coordinates (RA, Dec) from an image.
        
        Note: This is a simplified implementation that assumes:
        - The image center corresponds to a known RA/Dec
        - The image has known scale and orientation
        - For a production system, this would require proper WCS calibration
        
        Args:
            image_reference: MinIO object name
            pixel_x: X pixel coordinate (if None, uses image center)
            pixel_y: Y pixel coordinate (if None, uses image center)
            
        Returns:
            Tuple of (RA, Dec) in degrees, or None if processing fails
        """
        try:
            # Download and process image
            image = self.download_image(image_reference)
            width, height = image.size
            
            # Use center of image if coordinates not provided
            if pixel_x is None:
                pixel_x = width / 2.0
            if pixel_y is None:
                pixel_y = height / 2.0
            
            # For this basic implementation, we'll just return normalized coordinates
            # In a real system, this would involve:
            # 1. World Coordinate System (WCS) calibration
            # 2. Proper transformation from pixel to celestial coordinates
            # 3. Metadata extraction from FITS headers or other sources
            
            # Simple normalization (0-1) scaled to typical RA/Dec ranges
            # RA: 0-360 degrees, Dec: -90 to +90 degrees
            ra = (pixel_x / width) * 360.0
            dec = ((pixel_y / height) - 0.5) * 180.0
            
            logger.info(f"Extracted coordinates from image {image_reference}: RA={ra}, Dec={dec}")
            return (ra, dec)
        except Exception as e:
            logger.error(f"Error extracting coordinates from image {image_reference}: {e}")
            return None

# Global instance
image_processor: Optional[ImageProcessor] = None

def get_image_processor() -> ImageProcessor:
    """Get or create the global image processor instance."""
    global image_processor
    if image_processor is None:
        image_processor = ImageProcessor()
    return image_processor
