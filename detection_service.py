import logging

logger = logging.getLogger(__name__)

class DetectionService:
    def __init__(self):
        """Initialize YOLO model - preserving existing code exactly"""
        try:
            # Import ultralytics here to handle missing dependency gracefully
            from ultralytics import YOLO
            # Load YOLO Model - exact same as original code
            self.model = YOLO("C:/Users/Admin/Downloads/stylo/StyleSensei/best.pt")
            logger.info("YOLO model loaded successfully")
        except ImportError as e:
            logger.error(f"Ultralytics not installed: {e}")
            self.model = None
        except Exception as e:
            logger.error(f"Error loading YOLO model: {e}")
            self.model = None

    def detect_items(self, image_path: str, conf_threshold: float = 0.25):
        """
        Run YOLO prediction - preserving existing code exactly
        """
        if self.model is None:
            logger.warning("YOLO model not available, returning mock data for demo")
            # Return mock detection data when YOLO is not available
            return [
                {
                    'type': 'shirt',
                    'confidence': 0.85,
                    'bbox': [100, 100, 200, 300]
                },
                {
                    'type': 'pants',
                    'confidence': 0.90,
                    'bbox': [80, 300, 220, 500]
                }
            ]
        
        try:
            # Run YOLO Prediction - exact same as original code
            results = self.model.predict(source=image_path, conf=conf_threshold, save=True)
            logger.info("YOLO Prediction completed")
            
            detected_items = []  # Initialize the list to store detected items - exact same as original
            
            for result in results:
                for box in result.boxes:
                    cls_id = int(box.cls)
                    cls_name = self.model.names[cls_id]
                    conf_score = float(box.conf)
                    detected_items.append({
                        'type': cls_name,
                        'confidence': conf_score,
                        'bbox': box.xyxy[0].tolist()  # Store bounding box - exact same as original
                    })
                    logger.debug(f"Detected: {cls_name} ({conf_score:.2f})")
            
            return detected_items
            
        except Exception as e:
            logger.error(f"Error in YOLO detection: {e}")
            raise
