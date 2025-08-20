import logging
from PIL import Image

logger = logging.getLogger(__name__)

class ImageProcessor:
    """Simplified image processor for development."""
    
    def __init__(self):
        logger.info("Image processor initialized (mock mode)")
    
    def preprocess_skin_image(self, image: Image.Image) -> Image.Image:
        """Mock skin image preprocessing."""
        return image.resize((224, 224))
    
    def preprocess_radiology_image(self, image: Image.Image, scan_type: str) -> Image.Image:
        """Mock radiology image preprocessing."""
        return image.resize((224, 224))
    
    def load_dicom(self, file_path: str) -> Image.Image:
        """Mock DICOM loading."""
        return Image.new('RGB', (512, 512), color='black')
